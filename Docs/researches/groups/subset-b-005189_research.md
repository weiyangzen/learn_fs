# subset-b-005189 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/imx_dsp_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/imx_dsp_rproc.c

## Purpose

`imx_dsp_rproc.c` is the NXP i.MX HiFi4 DSP remoteproc driver. It registers an `imx-dsp-rproc` platform driver for i.MX8QXP, i.MX8QM, i.MX8MP, and i.MX8ULP DSP instances and binds the Linux remoteproc core to SoC-specific DSP reset/start/stop mechanisms, memory carveouts, mailbox/IPI handling, firmware loading, power domains, runtime PM, and system suspend/resume.

The driver is specialized for Xtensa HiFi DSP firmware. It uses SoC address translation tables to expose DSP-owned SRAM/IRAM and DDR windows as remoteproc carveouts, implements 32-bit-only copy and memset helpers for IRAM, handles a DSP-specific resource-table feature that can skip firmware-ready confirmation, and expects optional mailbox channels for kicks, virtqueue notifications, doorbells, and PM acknowledgements.

## Important APIs, types, and functions

- `struct imx_dsp_rproc` is the runtime state: regmap or reset-control start path, `rproc`, SoC config, five optional clocks, mailbox channels (`tx`, `rx`, `rxdb`), PM domains, SCU handle, virtqueue work item, suspend completion, and flags.
- `struct imx_dsp_rproc_dcfg` wraps the common `struct imx_rproc_dcfg` with an optional DSP reset callback.
- `struct fw_rsc_imx_dsp` is a DSP-specific resource-table entry with NXP magic, version, and feature bits. `FEATURE_SKIP_FW_CONFIRMATION` clears `WAIT_FW_CONFIRMATION`.
- `imx8mp_dsp_reset()` resets via DAP debug power control and the `runstall` reset control. `imx8ulp_dsp_reset()` resets/stalls through SIM LPAV sysctrl bits and an SMC call for DSP XRDC setup.
- Start/stop backends are `imx_dsp_rproc_mmio_start/stop()`, `imx_dsp_rproc_reset_ctrl_start/stop()`, and `imx_dsp_rproc_scu_api_start/stop()`.
- `imx_dsp_rproc_add_carveout()` registers DSP-owned address table entries and DT reserved-memory regions with remoteproc and coredump support.
- `imx_dsp_rproc_elf_load_segments()` is a custom ELF loader using `imx_dsp_rproc_memcpy()` and `imx_dsp_rproc_memset()` instead of generic byte writes.
- `imx_dsp_rproc_mbox_alloc()` requests `tx`, `rx`, and `rxdb` channels; `no_mailboxes` switches to a no-op allocator.
- System sleep is handled by `imx_dsp_suspend()` and `imx_dsp_resume()`, including optional mailbox PM handshakes and asynchronous firmware reload after power loss.

## Control flow

Probe gets the matched SoC config, parses `firmware-name`, allocates the `rproc`, initializes `WAIT_FW_CONFIRMATION`, selects mailbox allocation behavior, detects the platform control mode, attaches PM domains, gets clocks, initializes the PM completion, registers the remoteproc, sets Xtensa ELF coredump metadata, and enables runtime PM.

Remoteproc prepare registers carveouts and takes a runtime PM reference. Runtime resume allocates mailbox channels and enables clocks, so the mailbox power domain can idle when the DSP is not prepared. Firmware load optionally resets the DSP, clears existing carveout mappings when offline, then loads each PT_LOAD segment with the custom aligned writer. Start calls the selected SoC backend and, unless the firmware resource table disabled it, waits up to `REMOTE_READY_WAIT_MAX_RETRIES` for the `rxdb` doorbell callback to set `REMOTE_IS_READY`. Kicks send the virtqueue id over `tx`.

Inbound `rx` messages either complete the PM suspend/resume handshake for `RP_MBOX_SUSPEND_ACK` and `RP_MBOX_RESUME_ACK`, or schedule work that services vqid 0 and 1 while holding the remoteproc lock and checking `RPROC_RUNNING`. The `rxdb` mailbox has no payload and only marks the remote as ready. Stop calls the selected backend unless the state is already `RPROC_CRASHED`, then clears `REMOTE_IS_READY`.

System suspend sends `RP_MBOX_SUSPEND_SYSTEM` and waits briefly for an ACK when the DSP is running, mailboxes are present, and firmware confirmation is enabled. It then forces runtime suspend, intentionally powering off the DSP domain. Resume forces runtime resume and, if the DSP had been running, requests firmware asynchronously, reloads segments, starts the core, and kicks vqid 0.

## State and persistence behavior

Driver state is transient in `struct imx_dsp_rproc`; persistent remote state lives in SoC reset/stall registers, SCU-controlled CPU state, clocks, power domains, mailbox FIFOs, and DSP memory. `REMOTE_IS_READY` and `WAIT_FW_CONFIRMATION` are in-memory flags and are reset by stop or resource-table parsing. Carveouts are recreated by prepare and carry coredump segment registrations. Runtime suspend frees mailbox channels and disables clocks; system suspend assumes DSP memory can be lost and reloads firmware on resume.

The address tables define persistent memory topology for each SoC. Entries flagged `ATT_OWN` become carveouts; `ATT_IRAM` marks instruction memory that requires aligned writes. Reserved-memory regions are translated from system address to DSP device address before registration.

## Dependencies and integration points

The file depends on Linux remoteproc, firmware ELF helpers, mailbox, regmap/syscon, reset, clock, runtime PM, PM domains, SCU firmware, ARM SMCCC, and the local shared `imx_rproc.h` address/control config. It integrates with DT through compatible strings, `firmware-name`, `mbox-names`, `fsl,dsp-ctrl`, `runstall`, clocks, PM domains, and reserved-memory phandles. Remote clients see standard remoteproc/rpmsg behavior, while the DSP firmware must match the mailbox and resource-table conventions used here.

## Risks and edge cases

- `imx_dsp_rproc_memcpy()` and `imx_dsp_rproc_memset()` require 32-bit-aligned destinations. A firmware segment ending at an unaligned address is handled by read-modify-write, but an unaligned destination causes load failure.
- `affected_mask = GENMASK(8 * r, 0)` appears to cover one extra bit for partial writes where `r` bytes should normally map to bits `8 * r - 1:0`; this is worth hardware-focused validation.
- `imx8mp_dsp_reset()` maps the DAP region with `ioremap_wc()` and does not check for a NULL mapping before dereferencing.
- `imx_dsp_rproc_free_mbox()` unconditionally calls `mbox_free_channel()` on all channel pointers, so its safety depends on the mailbox API tolerating NULL.
- The module-level function pointer `imx_dsp_rproc_mbox_init` is selected from the global `no_mailboxes` parameter, so all instances share the same mailbox policy.
- A missing `rxdb` mailbox makes `imx_dsp_rproc_ready()` return success immediately; this is intentional for no-doorbell systems but weakens readiness detection.
- `imx_dsp_load_firmware()` runs asynchronously during resume and calls `rproc->ops->start()` directly; failures leave runtime PM already resumed and need careful recovery testing.

## Test signals

Build with i.MX remoteproc, mailbox, SCU, reset, and PM options enabled. DT boot tests should cover all four compatibles and both mailbox and `no_mailboxes` modes. Firmware tests should include resource tables with and without the NXP DSP entry, aligned and partial PT_LOAD segments, IRAM writes, vqid kicks, ready doorbell timeout, suspend/resume ACK timeout, watchdog/crash stop behavior, and coredump segment registration. Hardware register checks should confirm reset/stall bits, SCU start/stop, runtime PM clock gating, and firmware reload after system resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/imx_dsp_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/imx_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/imx_rproc.c

## Purpose

`imx_rproc.c` is the generic NXP i.MX Cortex-M remoteproc driver. It supports i.MX6SX, i.MX7D, i.MX7ULP, i.MX8MQ/MM/MN/MP, i.MX8QM/QXP, i.MX8ULP, i.MX93, and i.MX95 M-core variants through SoC-specific address tables and start/stop operations. It bridges the remoteproc core to SRC/GPR MMIO reset bits, ARM SMCCC firmware calls, i.MX SCU APIs, and i.MX System Manager SCMI CPU/LMM protocols.

The driver handles address translation from remote M-core device addresses to system bus addresses, maps TCM/OCRAM/reserved-memory regions, registers carveouts and coredump segments, attaches to already-running firmware, wires mailbox virtqueue interrupts, and manages shutdown/restart mailbox mode for SoCs that require system-off handling.

## Important APIs, types, and functions

- `struct imx_rproc` stores regmaps, rproc pointer, SoC config, mapped memory slots, clock, mailbox channels, workqueue, resource-table mapping, SCU state, power-domain list, platform ops, core index, and System Manager control flags.
- Address translation is table-driven through `struct imx_rproc_att` from `imx_rproc.h`; this file defines tables for each supported SoC and core variant.
- Platform operation groups are `imx_rproc_ops_mmio`, `imx_rproc_ops_arm_smc`, `imx_rproc_ops_scu_api`, `imx_rproc_ops_sm_lmm`, and `imx_rproc_ops_sm_cpu`.
- `imx_rproc_da_to_sys()` translates remote device addresses to system addresses and handles dual-core i.MX8QM `ATT_CORE()` filters. `imx_rproc_da_to_va()` maps translated system addresses to kernel virtual mappings.
- `imx_rproc_addr_init()` maps ATT-owned regions and optional reserved-memory regions, including a dedicated `rsc-table` pointer.
- `imx_rproc_prepare()` adds reserved-memory carveouts except `vdev0buffer` and `rsc-table`, and records coredump segments.
- `imx_rproc_xtr_mbox_init()`, `imx_rproc_kick()`, `imx_rproc_rx_callback()`, and `imx_rproc_vq_work()` implement mailbox transport for virtqueue notifications.
- Detect-mode helpers decide whether the core is offline, detached/already running, or only attachable because Linux does not own it.

## Control flow

Probe allocates an `imx-rproc`, selects the SoC data, creates a workqueue, initializes optional mailboxes early, maps memories, detects control mode, optionally enables clocks, sets `auto_boot` if the core is not detached, installs system-off handlers when required, enables runtime PM, and registers the remoteproc.

For normal boot, remoteproc prepare scans DT reserved-memory entries and adds carveouts/coredump segments. Start requests mailboxes if needed, then invokes the selected backend: MMIO clears wait or updates SRC bits; SMC calls the i.MX SIP service; SCU starts the resource at `entry`; System Manager CPU or LMM protocols set reset vectors and boot the CPU/logical machine. Kicks send `vqid << 16` through the mailbox. RX callbacks queue work, and the work iterates all remoteproc notify IDs and calls `rproc_vq_interrupt()` for each.

Stop calls the backend, then frees mailbox channels on success. MMIO stop sets GPR wait and SRC stop bits; SMC stop can report a forced stop if the core was not in WFI; SCU/SM stop calls the relevant firmware protocol. Attach initializes mailboxes. Detach is supported only for the SCU API path and only when Linux does not own the resource.

Detect mode is a major branch. MMIO mode reads SRC/GPR bits and may stop a cold-boot wait-state core before loading firmware. SMC mode asks firmware whether the core has started. SCU mode checks resource ownership: if Linux owns it, it requires an entry address and attaches PM domains; if another partition owns it, it marks the rproc detached, enables recovery-on-attach, and registers a SCU reboot notifier. System Manager mode checks CPU started state, discovers the current Linux LMM, chooses CPU protocol if the remote is in the same LMM and LMM protocol otherwise, then tests whether Linux can power/control that LMM.

## State and persistence behavior

In-memory state includes mailbox handles, mapped memory slots, resource-table pointer, SCU partition/resource ids, workqueue state, and `RPROC_DETACHED`/runtime remoteproc state. Persistent hardware state is in SRC/GPR reset/wait bits, SCU/SM firmware-owned CPU state, power domains, TCM/OCRAM/DDR contents, and mailbox FIFOs. If a reserved memory region named `rsc-table` is mapped, the driver exposes it as the loaded resource table for attach paths. Power-domain state can cause probe to mark the remote detached when all attached domains are already on.

System-off handling frees blocking mailboxes and reinitializes them non-blocking during power-off/restart prepare, avoiding atomic notifier problems later in shutdown.

## Dependencies and integration points

The driver integrates with the remoteproc core, mailbox framework, i.MX SCU firmware, i.MX System Manager SCMI protocol, ARM SMCCC, syscon/regmap, reserved memory, PM domains, runtime PM, reset/power-off notifiers, and DT compatibles. It shares its config ABI with `imx_rproc.h`, and the DSP driver reuses the same address/config structures.

DT integration includes compatible-specific data, `syscon`, optional `fsl,iomuxc-gpr`, optional `mbox-names` with `tx`/`rx`, reserved-memory regions, `fsl,resource-id`, `fsl,entry-address`, `fsl,auto-boot`, and PM domains.

## Risks and edge cases

- Several address boundary checks use strict `<` rather than `<=`, so an access exactly ending at the end of a mapped range can fail translation.
- `imx_rproc_prepare()` assumes i.MX reserved-memory physical addresses can be used directly as device addresses; this is valid for documented layouts but fragile if a future SoC needs translation.
- `IMX_RPROC_MEM_MAX` silently limits mapped regions; if too many ATT/reserved entries exist, later entries are skipped.
- Mailbox channels are requested in probe and again on start/attach after stop/detach. Correct NULL/error cleanup is important for repeated lifecycle tests.
- System Manager LMM mode can be attach-only when Linux lacks control, so start/stop must fail with `-EACCES` rather than corrupt another logical machine.
- SCU-notifier crash reporting depends on correct partition id lookup and IRQ group enable/disable.
- The resource-table mapping returns a fixed `SZ_1K` size, which assumes the mapped table is at least that large and sufficient for consumers.

## Test signals

Compile all supported i.MX variants. Boot tests should cover MMIO, SMC, SCU, and System Manager paths; offline boot and already-running attach; dual-core i.MX8QM core-index filtering; reserved-memory carveouts; loaded resource table mapping; mailbox kicks; SCU reboot notification; and system-off handler behavior. Static tests should check each ATT range for overlaps, valid end-boundary translations, and correct `ATT_CORE()` filters. Runtime tests should verify SRC/GPR bits, SM/SCU calls, PM domain attach detection, vdev/rsc-table reserved-memory exclusions, coredump segments, and repeated start/stop/attach/detach cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/imx_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/imx_rproc.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/imx_rproc.h

## Purpose

`imx_rproc.h` is the shared private configuration header for NXP i.MX remoteproc drivers. It defines the address translation table entry format, device-configuration flags, platform operation callbacks, and SoC configuration descriptor used by `imx_rproc.c` and reused by `imx_dsp_rproc.c`.

## Important APIs, types, and data

- `struct imx_rproc_att` maps a remote device address (`da`) to a system bus address (`sa`) and size, with driver-specific flags.
- `IMX_RPROC_NEED_SYSTEM_OFF` marks configurations needing reboot/power-off mailbox handling.
- `IMX_RPROC_NEED_CLKS` marks configurations where Linux should enable a clock when the remote core is under Linux control.
- `struct imx_rproc_plat_ops` contains optional `start`, `stop`, `detach`, `detect_mode`, and `prepare` hooks.
- `struct imx_rproc_dcfg` combines reset/source register fields, GPR wait fields, ATT table pointer and size, flags, platform ops, and System Manager `cpuid`/`lmid`.

## Control flow

The header has no executable flow. Runtime behavior is driven by consumers that choose an `imx_rproc_dcfg` from an OF match entry, call `detect_mode`, map ATT entries, and call `start`/`stop`/`prepare` through `imx_rproc_plat_ops`.

## State and persistence behavior

The types are static configuration contracts and hold no state by themselves. The fields describe persistent hardware state locations such as SRC/GPR reset registers and remote memory address windows. In consumers, `cpuid` and `lmid` are treated as firmware protocol identifiers rather than mutable state.

## Dependencies and integration points

The header assumes Linux integer types and `BIT()` are available from including C files. It is local to the remoteproc drivers and should stay synchronized with both generic M-core and DSP driver expectations. The ATT flags are interpreted differently by each C file, so new flag bits must not collide across users without auditing both consumers.

## Risks and edge cases

- `lmid` is commented as "Logcial Machine", a spelling issue only, but the field is a critical System Manager identifier.
- The header does not define ATT flag bits; each user defines its own high-bit meanings. This reduces coupling but makes shared-table reuse risky if flags are moved into the header later.
- Address and size fields are 32-bit. This matches current i.MX remote views but constrains future address maps above 4 GiB.

## Test signals

Header validation is mostly compile-time: every C file using it should build with all configured SoC tables, callbacks, and flag definitions. Adding fields should trigger review of both `imx_rproc.c` and `imx_dsp_rproc.c`, plus DT-compatible data initialization for all i.MX variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/imx_rproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ingenic_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/ingenic_rproc.c

## Purpose

`ingenic_rproc.c` is a compact remoteproc driver for the Ingenic JZ4770 VPU auxiliary processor. It maps VPU TCSM/SRAM memories, controls VPU/AUX clocks, starts and resets the AUX interface, and uses AUX message registers for virtqueue kicks and interrupts.

## Important APIs, types, and functions

- `auto_boot` is a module parameter that controls `rproc->auto_boot`.
- `struct vpu_mem_map` defines remote device base addresses for `tcsm0`, `tcsm1`, and `sram`.
- `struct vpu_mem_info` stores each mapped resource's table entry, length, and `ioremap` base.
- `struct vpu` stores IRQ, two clocks (`vpu`, `aux`), AUX register base, memory mappings, and device pointer.
- `ingenic_rproc_prepare()` enables clocks before firmware load; `ingenic_rproc_unprepare()` disables them.
- `ingenic_rproc_start()` enables the IRQ and writes AUX reset/NMI/message IRQ bits. `ingenic_rproc_stop()` disables the IRQ and holds AUX in software reset.
- `ingenic_rproc_kick()` writes the virtqueue id to `REG_CORE_MSG`.
- `ingenic_rproc_da_to_va()` maps remote addresses into the three memory regions.
- `vpu_interrupt()` reads `REG_AUX_MSG`, acknowledges with `REG_AUX_MSG_ACK`, and calls `rproc_vq_interrupt()`.

## Control flow

Probe allocates the rproc, stores `auto_boot`, maps the `aux` register bank, maps `tcsm0`, `tcsm1`, and `sram`, gets `vpu`/`aux` clocks, requests an initially disabled IRQ, and registers remoteproc. Prepare enables clocks so the loader can access TCSM. Start enables the IRQ and releases AUX with NMI reset semantics and message IRQs enabled. Kicks write to the core message register. Interrupts read the remote-provided vring id and pass it to remoteproc. Stop disables the IRQ and puts AUX back into reset.

## State and persistence behavior

Software state is limited to mapped memory descriptors and clock/IRQ handles. Hardware state persists in AUX control/message registers and memory contents while clocks and reset state allow access. Stop leaves AUX held in reset; unprepare turns clocks off after remoteproc no longer needs memory access.

## Dependencies and integration points

The driver uses platform resources named `aux`, `tcsm0`, `tcsm1`, and `sram`, two clocks named `vpu` and `aux`, a single IRQ, and the compatible `ingenic,jz4770-vpu-rproc`. It depends on remoteproc core, IRQ, clock, IO mapping, and `remoteproc_internal.h`.

## Risks and edge cases

- The address check uses `(da + len) < end`, so a buffer ending exactly at the region end is rejected.
- `platform_get_resource_byname()` is not checked before `devm_ioremap_resource()`, so missing named resources depend on that helper's error behavior.
- The IRQ payload is trusted as the vring id; unexpected values rely on `rproc_vq_interrupt()` handling.
- There is no custom firmware sanity/load path, so firmware must match the generic remoteproc expectations and the fixed memory map.

## Test signals

Build with Ingenic remoteproc enabled. DT tests should verify all resources/clocks/IRQ names. Runtime tests should cover `auto_boot`, firmware load into each mapped region, exact-end address translation, virtqueue kick/interrupt exchange, clock enable/disable around prepare/unprepare, and repeated start/stop leaving AUX reset asserted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ingenic_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/keystone_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/keystone_remoteproc.c

## Purpose

`keystone_remoteproc.c` controls TI Keystone C66x DSP remote processors. It maps internal L2/L1 memories, programs a boot address through a device-control syscon, manages DSP reset, handles vring and exception interrupts, uses a GPIO-backed kick mechanism, and registers the DSP with the remoteproc core.

## Important APIs, types, and functions

- `struct keystone_rproc_mem` describes internal DSP memory with CPU mapping, bus address, DSP device address, and size.
- `struct keystone_rproc` stores device/rproc pointers, memory table, syscon/reg offset, reset control, IRQs, kick GPIO, and work item.
- `keystone_rproc_dsp_boot()` validates 1 KiB boot-address alignment, writes the boot register, and deasserts reset.
- `keystone_rproc_exception_interrupt()` reports `RPROC_FATAL_ERROR`.
- `handle_event()` services vqid 0 and 1 because the vring interrupt has no payload.
- `keystone_rproc_start()` initializes work, enables vring/exception IRQs, and boots from `rproc->bootaddr`.
- `keystone_rproc_stop()` asserts reset, disables IRQs, and flushes pending vring work.
- `keystone_rproc_kick()` toggles the optional `kick` GPIO.
- `keystone_rproc_da_to_va()` translates both DSP-local addresses and SoC bus addresses for internal memories.
- Probe helpers parse `ti,syscon-dev` and map named memories `l2sram`, `l1pram`, and `l1dram`.

## Control flow

Probe requires DT and an alias id `rprocN`, builds a default firmware name `keystone-dspN-fw`, allocates the rproc, disables IOMMU use, locates the syscon boot register, gets reset, enables runtime PM so memories can be accessed, maps and zeroes internal memories, requests disabled `vring` and `exception` IRQs, obtains the `kick` GPIO, initializes reserved memory if present, forces the DSP into reset if needed, and registers remoteproc.

Start enables IRQs and writes the boot address before reset deassertion. If boot fails, pending work is flushed. Vring interrupts schedule work that services both virtqueues. Exception interrupts immediately report a fatal crash. Stop asserts reset, disables both IRQs, and flushes work. Address translation first treats addresses below `KEYSTONE_RPROC_LOCAL_ADDRESS_MASK` as DSP-view addresses and otherwise compares against SoC bus addresses.

## State and persistence behavior

Driver state includes mapped internal memories, reset state, boot register offset, and IRQ/work state. Internal memories are zeroed at probe and persist while the DSP power domain/runtime PM keeps access enabled. The boot address persists in the syscon register until overwritten. Stop leaves the DSP in reset but does not clear memory.

## Dependencies and integration points

The driver integrates with DT compatibles `ti,k2hk-dsp`, `ti,k2l-dsp`, `ti,k2e-dsp`, and `ti,k2g-dsp`; OF aliases; syscon/regmap; reset controller; runtime PM; reserved memory/CMA; named memory resources; IRQs named `vring` and `exception`; and a `kick` GPIO. Remoteproc and rpmsg clients rely on the fixed two-vring interrupt assumption.

## Risks and edge cases

- The work handler assumes exactly two vrings and no interrupt payload. More vrings would require protocol changes.
- Missing OF alias fails probe because it is used for default firmware naming.
- `gpiod_set_value(kick_gpio, 1)` does not explicitly clear the GPIO; correct operation depends on the GPIO provider/IP block modeling a pulse or interrupt generation on set.
- `keystone_rproc_da_to_va()` uses `da < KEYSTONE_RPROC_LOCAL_ADDRESS_MASK`; the mask boundary itself falls into the bus-address path.
- The driver zeroes internal memories at probe, which is useful for clean boot but may destroy diagnostics if probing an already-running or crashed DSP were ever attempted.

## Test signals

Build with Keystone remoteproc and reset/syscon/GPIO support. DT tests should validate alias ids, syscon argument parsing, memory names, IRQ names, kick GPIO, and reserved memory. Runtime tests should check boot address alignment rejection, reset assert/deassert, vring interrupt scheduling, fatal exception recovery, local and bus address translation, memory zeroing, and repeated start/stop with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/keystone_remoteproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/meson_mx_ao_arc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/meson_mx_ao_arc.c

## Purpose

`meson_mx_ao_arc.c` is the Amlogic Meson8/Meson8b AO ARC remoteproc driver. It allocates the always-on SRAM from a gen_pool, configures AO remap and secure bus registers so the ARC core sees SRAM at address zero, controls ARC reset and clock, and loads generic ELF firmware through remoteproc.

## Important APIs, types, and functions

- `struct meson_mx_ao_arc_rproc_priv` stores remap and CPU register bases, SRAM virtual/physical address and size, gen_pool pointer, reset control, clock, and SECBUS2 regmap.
- `meson_mx_ao_arc_rproc_start()` enables the peripheral clock, programs ARM/media SRAM remap fields, updates `AO_SECURE_REG0`, resets the ARC, translates the SRAM physical address by subtracting `MESON_AO_RPROC_MEMORY_OFFSET`, and writes `AO_CPU_CNTL_RUN`.
- `meson_mx_ao_arc_rproc_stop()` writes `AO_CPU_CNTL_HALT` and disables the clock.
- `meson_mx_ao_arc_rproc_da_to_va()` maps ARC device addresses directly into the allocated SRAM because the core sees SRAM starting at 0.
- `meson_mx_ao_arc_rproc_ops` uses generic ELF boot address, load, and sanity-check helpers.

## Control flow

Probe optionally reads `firmware-name`, allocates the rproc, gets the `sram` gen_pool, allocates all available SRAM, validates that the physical address uses only allowed remap bits, obtains the `amlogic,secbus2` syscon, maps resources named `remap` and `cpu`, gets reset and clock, stores drvdata, and calls `rproc_add()`. Remove unregisters remoteproc and frees the SRAM allocation.

Start configures remap registers before releasing the ARC, then sets run control after a short reset delay. Stop halts the CPU and disables the clock. Address translation rejects any firmware address range beyond the SRAM size.

## State and persistence behavior

The driver owns a single gen_pool allocation for the remote firmware memory across the rproc lifetime. Register state persists in AO remap, AO CPU control, and secure bus registers until reset or reconfiguration. Stop halts the core and gates the clock but does not clear SRAM. Remove frees SRAM back to the pool.

## Dependencies and integration points

It depends on genalloc SRAM pools, syscon/regmap, reset, clock, platform resources, and remoteproc generic ELF helpers. DT must provide compatible `amlogic,meson8-ao-arc` or `amlogic,meson8b-ao-arc`, an `sram` pool, `amlogic,secbus2`, and `remap`/`cpu` memory resources.

## Risks and edge cases

- `priv->sram_size = gen_pool_avail()` then allocating that full amount can starve other users of the SRAM pool.
- The code contains hardware behavior learned by trial and error, including an `AO_CPU_CNTL_UNKNONWN` bit and a physical-address translation by subtracting `0x10000000`.
- `da + len` is not overflow-checked before comparing with `sram_size`.
- The driver allocates with `devm_rproc_alloc()` but calls non-devm `rproc_add()` and explicitly `rproc_del()` in remove; probe error cleanup must keep this pairing correct.

## Test signals

Build and boot on Meson8/Meson8b DTs with valid SRAM pool/remap resources. Tests should verify SRAM usable-bit validation, full-pool allocation and release, remap register values, reset/clock sequencing, firmware load at device address 0, rejection of out-of-range ELF segments, halt on stop, and repeated probe/remove or start/stop cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/meson_mx_ao_arc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_common.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_common.h

## Purpose

`mtk_common.h` is the private shared header for the MediaTek SCP remoteproc driver and its IPI helper. It defines SoC register offsets and bit masks for MT8183, MT8186, MT8188, MT8192, and MT8195 SCP cores, plus the data structures that connect the core remoteproc driver, rpmsg/IPI layer, multi-core cluster state, and SoC-specific operation tables.

## Important APIs, types, and data

- Register macros cover reset, host/SCP IPC, watchdog, SRAM power-down, cache control, L2TCM/L1TCM power, dual-core IPC, system status, SRAM offset, and secure control registers.
- `SCP_FW_VER_LEN` fixes firmware version string storage at 32 bytes.
- `struct scp_run` carries firmware-ready signal, firmware version, video decode/encode capabilities, and the waitqueue used by boot.
- `struct scp_ipi_desc` protects each IPI handler/private pointer with a mutex.
- `struct mtk_scp_sizes_data` defines firmware DRAM reservation size and IPI buffer size.
- `struct mtk_scp_of_data` is the SoC/core operation table: clock get, pre-load setup, IRQ handler, reset assert/deassert, stop, address translation, IPC register/bit, IPI buffer offset, and sizes.
- `struct mtk_scp_of_cluster` stores shared register mappings, optional L1TCM, a list of SCP cores, cluster lock, and shared L2TCM refcount.
- `struct mtk_scp` is the per-core state used by both `mtk_scp.c` and `mtk_scp_ipi.c`.
- `struct mtk_share_obj` describes the shared SRAM IPI object layout.
- Exported helper prototypes are `scp_memcpy_aligned()`, `scp_ipi_lock()`, and `scp_ipi_unlock()`.

## Control flow

The header has no executable flow. Consumers fill `struct mtk_scp_of_data` per compatible, allocate `struct mtk_scp` per core, and use the register macros in start/load/stop/IRQ/IPI paths. The IPI file uses `struct mtk_share_obj`, `struct scp_ipi_desc`, and locks from this header to register and send messages.

## State and persistence behavior

The structures model persistent SCP hardware state but do not manage it directly. `struct mtk_scp_of_cluster` coordinates shared L2TCM power state through `l2tcm_refcnt`; `struct mtk_scp` stores live mailbox/IPI buffers, DMA memory, and rpmsg subdevice pointers; `scp_run` persists the last firmware-reported version and capability values until overwritten by the next boot.

## Dependencies and integration points

This header includes Linux interrupt, kernel, platform, remoteproc, and public MediaTek SCP API headers. It is tightly coupled to `mtk_scp.c`, `mtk_scp_ipi.c`, `linux/remoteproc/mtk_scp.h`, and the MediaTek rpmsg bridge.

## Risks and edge cases

- A macro typo `MT8186_SCP_L1_SRAM_PD_p2` uses lowercase `p`, which is harmless to C but inconsistent.
- Register offsets are shared across several SoCs with subtle differences; incorrect reuse in an `mtk_scp_of_data` table can reset or power-gate the wrong core.
- `struct mtk_share_obj` declares `u8 *share_buf`, but the code treats the field as an in-SRAM flexible payload location. This ABI is layout-sensitive and should not be changed casually.
- Cluster-level refcounting assumes all L2TCM users hold the same `cluster_lock` discipline.

## Test signals

Compile all MediaTek SCP compatibles and both single-core and dual-core data tables. Static checks should verify every `mtk_scp_of_data` fills all required callbacks and size pointers. Runtime tests should validate register offsets against datasheets for each SoC, especially dual-core IPC/reset/watchdog and L2TCM offset registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp.c

## Purpose

`mtk_scp.c` is the MediaTek System Control Processor remoteproc driver. It supports multiple MediaTek SoCs, single-core and dual-core SCP clusters, firmware loading into SRAM/TCM/optional DRAM, IPI buffer setup, rpmsg subdevice creation, watchdog reporting, video capability publication, default firmware-name generation, and system sleep clock handling.

## Important APIs, types, and functions

- Public exports include `scp_get()`, `scp_put()`, `scp_get_device()`, `scp_get_rproc()`, `scp_get_vdec_hw_capa()`, `scp_get_venc_hw_capa()`, and `scp_mapping_dm_addr()`.
- `scp_ipi_handler()` dispatches shared-buffer messages to registered handlers and wakes ack waiters.
- SoC-specific reset/IRQ/pre-load/stop helpers implement MT8183, MT8186, MT8188, MT8192, and MT8195 differences.
- `scp_sram_power_on/off()` sequence SRAM power registers one bit at a time while honoring reserved masks.
- `scp_elf_load_segments()` is a 32-bit ELF loader that uses `scp_memcpy_aligned()` for SRAM writes.
- `scp_elf_read_ipi_buf_addr()` discovers a `.ipi_buffer` ELF section; `scp_ipi_init()` falls back to a SoC default offset and initializes receive/send objects.
- `scp_start()` deasserts reset and waits up to 2 seconds for the `SCP_IPI_INIT` handler to set `run.signaled`.
- Address translators `mt8183_scp_da_to_va()` and `mt8192_scp_da_to_va()` cover SRAM, optional L1TCM, and optional coherent DRAM.
- `scp_rproc_init()`, `scp_add_single_core()`, and `scp_add_multi_core()` build per-core remoteproc instances and cluster lists.

## Control flow

Probe maps the cluster `cfg` region and optional `l1tcm`, initializes the cluster list and lock, populates child `mediatek,scp-core` devices, and then chooses single-core or multi-core setup. Per core, `scp_rproc_init()` parses or generates firmware path, allocates a remoteproc, maps the `sram` resource, gets clocks, initializes optional reserved/coherent memory, initializes IPI locks and waitqueues, registers `SCP_IPI_INIT`, allocates the shared receive buffer, creates an rpmsg subdevice, and requests the IRQ.

Remoteproc prepare prepares the clock. Load enables the clock, asserts reset, runs the SoC pre-load hook to power SRAM/TCM and configure MPU/cache/offset registers, then copies firmware segments. Parse firmware enables the clock and initializes the IPI buffers from `.ipi_buffer` or default offset. Start enables the clock, clears the init signal, deasserts reset, waits for firmware init IPI, disables the clock, and reports the firmware version. Stop enables the clock, asserts reset, runs SoC-specific SRAM/watchdog shutdown, and disables the clock.

Interrupt handling enables the clock, calls the SoC-specific handler, and disables the clock. IPC interrupts dispatch IPI handlers; watchdog conditions report crashes for every core in the cluster. Dual-core MT8188/MT8195 paths refcount shared L2TCM and program core1 address offset registers before booting core1.

## State and persistence behavior

Per-core state includes SRAM mappings, optional coherent DRAM, IPI descriptors, firmware-reported capabilities, current IPI buffers, rpmsg subdevice, and rproc state. Cluster state includes shared register base, optional L1TCM mapping, core list, lock, and L2TCM refcount. Hardware state persists in SCP reset, SRAM power, watchdog, cache, MPU, IPC, and offset registers. The last firmware version and capabilities remain in `scp->run` after boot and are exported to clients.

## Dependencies and integration points

The driver depends on remoteproc, MediaTek SCP public API, MediaTek rpmsg (`mtk_rpmsg_create_rproc_subdev()`), coherent DMA/reserved memory, OF child population, clocks, IRQs, and the shared `mtk_common.h`/`mtk_scp_ipi.c` layer. DT must provide cluster compatible strings, `cfg`, per-core `sram`, optional `l1tcm`, optional `firmware-name`, optional reserved memory, and optional child core nodes for dual-core systems.

## Risks and edge cases

- `scp_get()` returns platform drvdata but does not take an explicit device reference on the SCP device, while `scp_put()` calls `put_device(scp->dev)`. That pairing relies on an external reference path and should be audited with users.
- `scp_mapping_dm_addr()` requests length 0; the address translators accept zero-length ranges and can return base pointers, which is useful but different from several other remoteproc drivers.
- `scp_elf_read_ipi_buf_addr()` parses ELF section tables without the same truncation checks used by some other loaders.
- `scp_ipi_handler()` treats missing handlers as errors and does not clear the hardware IPC bit itself; SoC IRQ handlers must always clear/ack correctly after dispatch.
- Multi-core setup stores parent `pdev` drvdata as the last created core solely to find the cluster on remove. This is documented but fragile if later code assumes parent drvdata is core0.
- Coherent memory allocation is attempted even when `max_dram_size` can be zero; this path depends on DMA API behavior and later unmap skips only by size.
- Shared L2TCM refcounts must remain balanced across load/stop failures for dual-core SoCs.

## Test signals

Build all MediaTek SCP compatibles. Boot tests should cover MT8183/MT8186/MT8188/MT8192/MT8195, single and dual core, default firmware-name generation, `.ipi_buffer` and default IPI offsets, IPI init timeout, rpmsg namespace service, watchdog crash broadcast, coherent DRAM mapping, L1TCM mapping, L2TCM refcounting on failures, and suspend/resume clock prepare handling. Static validation should compare register tables against SoC data and check all per-compatible callbacks are non-NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp_ipi.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp_ipi.c

## Purpose

`mtk_scp_ipi.c` provides the exported Inter-Processor Interrupt API used by MediaTek SCP client drivers and the MediaTek rpmsg bridge. It registers per-IPI handlers, copies data into the shared SCP SRAM object with alignment-safe writes, sends host-to-SCP interrupts, and optionally waits for firmware acknowledgements.

## Important APIs, types, and functions

- `scp_ipi_register()` installs a handler and private pointer for an IPI id.
- `scp_ipi_unregister()` clears the handler and private pointer.
- `scp_memcpy_aligned()` writes to SCP SRAM using 32-bit writes and read-modify-write at unaligned edges because byte writes are not supported.
- `scp_ipi_lock()` and `scp_ipi_unlock()` expose per-IPI mutexes for the SCP core driver.
- `scp_ipi_send()` validates id/length/buffer, enables the SCP clock, serializes sends with `send_lock`, waits for the previous host-to-SCP register to clear, writes payload/id/len to `send_buf`, triggers the configured IPC bit, optionally waits for `ipi_id_ack[id]`, and disables the clock.

## Control flow

Clients register handlers after obtaining an `mtk_scp`. Sending an IPI first validates that the id is not reserved (`SCP_IPI_INIT`, `SCP_IPI_NS_SERVICE`, or out of range), that the buffer fits the SoC's `ipi_share_buffer_size`, and that a buffer exists. It enables the SCP clock, waits up to `SCP_TIMEOUT_US` for the host IPC register to be idle, copies payload into shared SRAM, writes length and id, clears the ack flag, triggers the host-to-SCP bit, and optionally waits for the core interrupt path to set the ack flag.

Inbound dispatch itself lives in `mtk_scp.c`; this file supplies the locking and send-side API it uses.

## State and persistence behavior

Handler state persists in `scp->ipi_desc[id]` until unregistered. Send-side serialization is per SCP instance through `send_lock`. Ack state is stored in `ipi_id_ack[]` and `ack_wq`. Hardware-visible state is the shared SRAM `send_buf` object and host-to-SCP IPC register bit; both are overwritten on each send.

## Dependencies and integration points

The file depends on `mtk_common.h`, the public `linux/remoteproc/mtk_scp.h` IPI ids and handler types, clocks, IO accessors, atomic polling, and waitqueues. It exports all APIs with GPL symbols for MediaTek media/rpmsg clients.

## Risks and edge cases

- `scp_ipi_send()` assumes `scp`, `scp->data`, `scp->send_buf`, and `scp->clk` are valid; unlike register/unregister it does not guard against NULL `scp`.
- The wait parameter is in milliseconds; a zero wait sends fire-and-forget and does not prove firmware accepted the command.
- `scp_memcpy_aligned()` may write extra bytes at the beginning and end of the destination word, intentionally preserving existing bytes by reading first. Concurrent writers to overlapping words would be unsafe.
- Timeout while waiting for the host IPC register leaves the previous SCP command state unresolved and returns without sending the new message.
- Ack flags are indexed by IPI id, so clients must avoid sharing an id concurrently beyond the provided `send_lock` serialization.

## Test signals

Unit-style tests should cover invalid ids, NULL handlers, oversize messages, unaligned destination copies, timeout when host IPC never clears, fire-and-forget sends, waited sends with ack, unregister during no active dispatch, and clock enable failures. Integration tests should verify IPI namespace service, rpmsg channel creation, and client media capability exchanges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp_ipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/omap_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/omap_remoteproc.c

## Purpose

`omap_remoteproc.c` is the TI OMAP/DRA7 IPU and DSP remoteproc driver. It supports OMAP4/OMAP5/DRA7 DSP and IPU cores, using reset controls, mailbox messages, optional boot-address syscon programming, internal memory mappings, timer/watchdog management, IOMMU integration, runtime autosuspend, and system suspend/resume.

## Important APIs, types, and functions

- `struct omap_rproc` holds mailbox, boot data, internal memories, timer arrays, autosuspend state, rproc pointer, reset control, PM completion, functional clock, and suspend-ack flag.
- `struct omap_rproc_boot_data` describes the syscon boot register and shift for DSP boot address programming.
- `struct omap_rproc_timer` wraps OMAP DMTimer handles, ops, and watchdog IRQs.
- Timer helpers request/start/stop/release timers and acknowledge watchdog interrupts.
- `omap_rproc_mbox_callback()` handles crash, echo, suspend ACK/CANCEL, reserved mailbox messages, and vring ids.
- `omap_rproc_start()` sets the boot address, requests mailbox, sends an echo, enables timers, deasserts reset, and enables runtime PM autosuspend.
- `omap_rproc_stop()` wakes the device, asserts reset, disables timers, frees mailbox, and disables runtime PM.
- `_omap_rproc_suspend()` and `_omap_rproc_resume()` implement both system and runtime suspend flows.
- `omap_rproc_da_to_va()` translates internal memory device addresses for IPU/DRA7 DSP memories.

## Control flow

Probe requires DT, gets the reset array, parses `firmware-name`, sets a 32-bit coherent DMA mask, allocates the rproc, marks it as IOMMU-backed, optionally detaches old ARM DMA-IOMMU mappings, maps internal memories based on compatible data, parses optional boot register, counts timers and watchdog timers, initializes completion/autosuspend delay, gets the functional clock, initializes reserved memory if provided, stores drvdata, and registers remoteproc.

Start optionally programs a 1 KiB-aligned boot address into the syscon, requests a mailbox channel, sends `RP_MBOX_ECHO_REQUEST`, configures and starts timers/watchdog timers, deasserts reset, and enables autosuspend runtime PM. Kicks take a runtime PM reference to wake an autosuspended remote, send the vqid over mailbox, then drop the reference with autosuspend.

Mailbox callbacks report firmware crashes, complete suspend handshakes, ignore known non-vring protocol messages, reject unknown ids beyond `max_notifyid`, and dispatch valid ids to `rproc_vq_interrupt()`. Stop resumes the device if needed, asserts reset, releases timers and mailbox, disables runtime PM, and marks the device suspended.

Suspend sends either `RP_MBOX_SUSPEND_AUTO` or `RP_MBOX_SUSPEND_SYSTEM`, waits for ACK/CANCEL, then polls the functional clock standby state before asserting reset and stopping timers. Runtime suspend additionally deactivates the OMAP IOMMU domain. Resume reverses the sequence: activate IOMMU for runtime resume, restore boot address, restart timers, and deassert reset.

## State and persistence behavior

Runtime state includes mailbox handle, timer handles and IRQs, suspend completion state, `need_resume`, runtime PM usage/autosuspend state, and remoteproc state transitions to `RPROC_SUSPENDED`. Hardware state persists in reset lines, boot syscon bits, DMTimer state, mailbox queues, internal memory contents, and IOMMU domain activation. `need_resume` records whether system resume should wake a processor that was running before suspend.

## Dependencies and integration points

The driver integrates with OMAP mailbox, OMAP DMTimer platform ops, reset controller arrays, syscon/regmap, OMAP IOMMU, reserved memory/CMA, runtime PM, clock standby introspection (`ti_clk_is_in_standby()`), and remoteproc core. DT properties include `firmware-name`, optional `ti,bootreg`, `ti,timers`, `ti,watchdog-timers`, `ti,autosuspend-delay-ms`, memory resources named for SoC internals, and compatibles for OMAP4/5/DRA7 DSP/IPU.

## Risks and edge cases

- Suspend relies on remote firmware sending ACK before entering WFI and then on clock standby polling to prove context save completed. Firmware bugs can cause `-EBUSY` or `-ETIME`.
- Timer setup error paths are complex and combine normal timers and watchdog timers; off-by-one cleanup errors would leak IRQs or timer handles.
- Runtime suspend is refused if the remote is not already in standby, so busy firmware prevents autosuspend.
- The mailbox callback casts `void *data` directly to `u32`; this follows the OMAP mailbox convention but is not portable to payload-pointer mailboxes.
- The probe warning allows missing reserved memory, but the comments strongly imply CMA should usually be present.
- Internal-memory mapping count is derived from `reg` property element count while the loop is driven by the compatible's `mems` array; mismatches can over-allocate or leave entries unused.

## Test signals

Build with OMAP remoteproc, mailbox, IOMMU, DMTimer, watchdog optional config, and PM enabled. Hardware tests should cover each compatible, boot register alignment failure, mailbox echo, rpmsg vring ids, crash message recovery, timer/watchdog IRQ reporting, runtime autosuspend/resume with IOMMU deactivate/activate, system suspend/resume with `need_resume`, missing/invalid timers, internal-memory translation, and reserved-memory/CMA setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/omap_remoteproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/omap_remoteproc.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/omap_remoteproc.h

## Purpose

`omap_remoteproc.h` defines the mailbox protocol constants shared by OMAP remoteproc firmware and the Linux OMAP remoteproc driver. It is a small protocol header rather than a driver implementation.

## Important APIs, types, and data

- `enum omap_rp_mbox_messages` reserves high mailbox values beginning at `0xFFFFFF00` so protocol messages do not collide with low virtqueue ids.
- Defined messages include remote ready, pending message, crash, echo request/reply, abort request, system and auto suspend requests, suspend ACK, suspend cancel, and `RP_MBOX_END_MSG`.

## Control flow

The header has no control flow. `omap_remoteproc.c` sends echo and suspend messages and interprets incoming crash, echo, suspend ACK/CANCEL, and reserved message ranges using this enum. Firmware must send the same values for Linux to classify messages correctly.

## State and persistence behavior

No software state is stored here. The enum values define persistent ABI between Linux and remote firmware images; changing values would break deployed firmware.

## Dependencies and integration points

The header is included by `omap_remoteproc.c` and should remain synchronized with TI SYS/BIOS or other OMAP remote firmware mailbox implementations. The BSD-3-Clause license header reflects shared firmware-facing ABI usage.

## Risks and edge cases

- `RP_MBOX_END_MSG` must remain last and bounds the range of known control messages in the driver.
- New messages must stay far from valid vring ids. The current high-value convention is the main collision guard.
- Firmware that sends `RP_MBOX_PENDING_MSG` rather than explicit vqid is currently ignored as a known control message; the rest of the IPC stack must match that behavior.

## Test signals

Protocol tests should inject each mailbox value into `omap_rproc_mbox_callback()` and verify crash reporting, echo logging, suspend completion flags, ignored reserved messages, and normal vqid dispatch for values below the reserved range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/omap_remoteproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.c

## Purpose

`pru_rproc.c` is the TI PRU-ICSS/ICSSG remoteproc driver for PRU, RTU, and Tx_PRU cores. It exposes PRU cores as remoteproc instances, maps PRU instruction/control/debug regions, provides client ownership APIs, configures PRUSS GP mux and constant tables, parses PRU-specific firmware sections, sets up PRUSS interrupt mappings, implements PRU-specific firmware loading quirks, and provides debugfs register/single-step controls.

## Important APIs, types, and functions

- `struct pru_rproc` stores PRU id, parent PRUSS pointer, rproc pointer, memory regions, owning client node, firmware name, interrupt map data, register RMW lock, debug single-step state, event mappings, and saved GPMUX value.
- Exported APIs are `pru_rproc_get()`, `pru_rproc_put()`, and `pru_rproc_set_ctable()`.
- `pru_control_*()` helpers read/write/update control registers under spinlock for RMW operations.
- `pru_rproc_get()` enforces single-client ownership through `client_np`, sets sysfs read-only while a kernel client owns the PRU, saves/restores GPMUX, optionally applies `ti,pruss-gp-mux-sel`, and optionally selects per-client firmware.
- `pru_handle_intrmap()` consumes `.pru_irq_map` data and creates IRQ mappings in the sibling PRUSS interrupt controller.
- `pru_rproc_start()` configures interrupt mappings and writes the start PC plus enable bit to `PRU_CTRL_CTRL`; `pru_rproc_stop()` clears enable and disposes mappings.
- `pru_d_da_to_va()` and `pru_i_da_to_va()` translate data and instruction address spaces. `pru_rproc_da_to_va()` exposes only data RAMs to remoteproc clients.
- `pru_rproc_load_elf_segments()` handles PRU program/data segment copying and K3 4-byte copy restrictions.
- `pru_rproc_parse_fw()` loads optional resource tables and finds `.pru_irq_map`.
- Debugfs `regs` and `single_step` expose control/debug registers and single-step execution.

## Control flow

Probe matches PRU/RTU/Tx_PRU data, parses firmware name, allocates a remoteproc, overrides `.load` and `.parse_fw`, disables recovery and auto-boot, stores PRUSS parent state, maps `iram`, `control`, and `debug` resources, derives PRU id from IRAM physical offset, registers remoteproc, and creates debugfs entries.

Kernel clients call `pru_rproc_get()` through their DT `ti,prus` phandle. The function validates that the phandle is a PRU rproc, ensures exclusive ownership, saves and optionally changes GPMUX, optionally changes firmware, and returns the rproc. `pru_rproc_put()` restores GPMUX and firmware, clears ownership, re-enables sysfs writes, and drops the rproc reference.

Firmware parse loads a standard resource table if present and locates `.pru_irq_map` without loading it into PRU memory. Start validates and maps the interrupt map into the PRUSS INTC, then writes enable and boot PC. Firmware load distinguishes executable PT_LOAD segments as IRAM and others as data RAM. K3 cores use a custom 4-byte copy routine because unaligned/8-byte writes to IRAM corrupt or fault.

## State and persistence behavior

Ownership state persists in `client_np` and `rproc->sysfs_read_only` while a client holds the PRU. GPMUX and selected firmware are saved/restored around that ownership. Interrupt mappings are firmware-specific and exist only while the rproc is running. Debug single-step state stores the previous continuous control register value for restoration. Hardware state persists in PRU control registers, constant table registers, PRUSS INTC mappings, local IRAM, data RAMs, and GPMUX configuration.

## Dependencies and integration points

The driver depends on the PRUSS core driver, PRUSS memory regions, PRUSS config helpers, IRQ domains, OF phandles, remoteproc ELF helpers, debugfs, and public PRUSS/PRU headers. DT must provide memory resources named `iram`, `control`, and `debug`, firmware names, compatible strings for SoC/core type, and optional client properties `ti,prus`, `ti,pruss-gp-mux-sel`, and per-index `firmware-name`.

## Risks and edge cases

- PRU has separate instruction and data address spaces with overlapping local addresses. Generic clients get only data-space translation; loader code must correctly classify executable segments.
- K3 firmware load rejects unaligned destination or size in `pru_rproc_memcpy()`, so firmware linkers must align IRAM segments to 4 bytes.
- `.pru_irq_map` points into the firmware buffer and is cleared after start; delayed use after `rproc_start()` would be invalid.
- `pru_d_da_to_va()` does not explicitly check `da >= PRU_PDRAM_DA` for primary DRAM because that base is zero; this is fine today but depends on constants.
- Debug register reads are blocked while running, but single-step writes can change control state and should remain a debug-only facility.
- Client ownership changes sysfs mutability and firmware selection; error paths must always call `pru_rproc_put()` to restore GPMUX and references.

## Test signals

Build all PRU/RTU/Tx_PRU compatibles. Tests should cover client get/put exclusivity, GPMUX save/restore, per-client firmware selection, constant table programming, debugfs `regs` and `single_step`, ELF data/IRAM loading, K3 aligned-copy failures, `.resource_table` optional handling, `.pru_irq_map` validation and IRQ mapping cleanup, PRU0/PRU1 DRAM swap behavior, shared RAM translation, and start/stop register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.h

## Purpose

`pru_rproc.h` defines PRU firmware interrupt-map data structures consumed by `pru_rproc.c`. It documents the compact `.pru_irq_map` section format used by PRU firmware to describe PRUSS system-event, channel, and host interrupt routing.

## Important APIs, types, and data

- `struct pruss_int_map` maps one PRU system event to one PRUSS interrupt channel and one host interrupt.
- `struct pru_irq_rsc` is a packed variable-length section header containing a resource type, event count, and flexible array of `struct pruss_int_map`.

## Control flow

The header has no executable flow. `pru_rproc_parse_fw()` locates `.pru_irq_map`, saves a pointer and size, and `pru_handle_intrmap()` validates `type`, `num_evts`, and total size before creating IRQ mappings from the flexible array.

## State and persistence behavior

No state lives in the header. The structures define firmware ABI. During runtime, `pru_rproc.c` holds a temporary pointer into the firmware image until start consumes it; created IRQ mappings persist until stop or start failure cleanup.

## Dependencies and integration points

This header is shared between PRU firmware layout expectations and Linux PRU remoteproc parsing. It uses fixed-width integer types and `__packed` for ABI layout. It integrates with PRUSS INTC routing through `irq_create_fwspec_mapping()`.

## Risks and edge cases

- The flexible array has no inherent bounds; consumers must validate `num_evts` and total section size, which `pru_handle_intrmap()` does.
- `type` currently supports only zero. Future types require coordinated parser changes.
- Because the structures are packed firmware ABI, padding or type changes would break existing firmware blobs.

## Test signals

Firmware parser tests should cover no section, header-only/truncated section, invalid type, `num_evts` above `MAX_PRU_SYS_EVENTS`, size mismatch, valid single mapping, many-to-one channel/host mappings, and cleanup when one mapping fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.c

## Purpose

`qcom_common.c` implements shared Qualcomm remoteproc helpers used by multiple Qualcomm peripheral loader drivers. It provides minidump coredump segment collection, GLINK and SMD rpmsg subdevice lifecycle glue, ELF dump-segment registration, subsystem restart (SSR) notifier registration and remoteproc subdev notifications, and a Protection Domain Mapper auxiliary device subdev.

## Important APIs, types, and functions

- Minidump structures mirror Qualcomm SMEM table-of-contents layouts: `minidump_region`, `minidump_subsystem`, and `minidump_global_toc`.
- `qcom_minidump()` locates the global minidump ToC in SMEM item 602, validates subsystem state/encryption, replaces normal coredump segments with SMEM-provided regions, runs coredump by sections, and cleans up.
- `qcom_register_dump_segments()` adds coredump segments for ELF PT_LOAD entries while skipping Qualcomm MDT hash segments and zero-sized segments.
- `qcom_add_glink_subdev()` / `qcom_remove_glink_subdev()` manage `glink-edge` child nodes and GLINK SMEM registration.
- `qcom_add_smd_subdev()` / `qcom_remove_smd_subdev()` manage `smd-edge` child nodes and SMD edge registration.
- `qcom_register_ssr_notifier()` and `qcom_unregister_ssr_notifier()` manage SRCU notifier chains by subsystem name.
- `qcom_add_ssr_subdev()` wires remoteproc prepare/start/stop/unprepare to SSR before/after powerup and shutdown notifications.
- `qcom_add_pdm_subdev()` / `qcom_remove_pdm_subdev()` create and remove an auxiliary `pd-mapper` device during remoteproc prepare/unprepare.

## Control flow

For minidumps, a crashing driver calls `qcom_minidump()` with a minidump id and dump callback. The function fetches the SMEM global ToC, checks id bounds and subsystem validity, falls back to normal `rproc_coredump()` when the subsystem ToC is not ready/enabled, skips when encryption is not done, clears existing coredump segments, maps the region table, adds valid regions as custom segments, emits a section-based coredump, and then frees the temporary segment list.

GLINK and SMD helpers are called by concrete remoteproc drivers during probe. They look for child nodes under the parent DT node, configure `rproc_subdev` callbacks, and add subdevices. During remoteproc start/stop, those callbacks register or unregister GLINK/SMD transport edges.

SSR helpers maintain a global list of named subsystems protected by a mutex. Remoteproc subdev callbacks emit SRCU notifications at before powerup, after powerup, before shutdown, and after shutdown. PDM helpers create an auxiliary bus device named `pd-mapper` at prepare and remove it at unprepare.

## State and persistence behavior

Global SSR subsystem state persists in `qcom_ssr_subsystem_list` for the module lifetime; entries are not removed when remoteprocs unregister. Minidump state is transient, using SMEM as authoritative persistent storage and the rproc dump segment list as temporary state. GLINK/SMD edge pointers and PDM auxiliary device pointers live in per-remoteproc helper structs and are nulled during stop/unprepare. Device-tree node references are held until remove helpers run.

## Dependencies and integration points

The file depends on remoteproc internals, Qualcomm SMEM, MDT loader flags, GLINK SMEM, SMD, QMI SSR data types, auxiliary bus, notifier/SRCU, firmware ELF headers, and DT child nodes. It exports helper symbols for Qualcomm platform remoteproc drivers and also exports SSR notifier registration for other kernel clients.

## Risks and edge cases

- `qcom_add_minidump_segments()` can return early on `kstrndup()` allocation failure without unmapping the mapped region table in that branch.
- `qcom_ssr_get_subsys()` allocates global subsystem entries but does not free them later; acceptable for long-lived subsystem names, but not for dynamic unbounded names.
- Minidump cleanup replaces the remoteproc dump segment list temporarily; errors must always clean up to avoid dangling custom segment names.
- `qcom_add_glink_subdev()` returns if no `glink-edge` node, but if `kstrdup_const()` fails after `of_get_child_by_name()`, the node reference is not released in that path.
- PDM auxiliary device creation happens in prepare; failure there can abort remoteproc boot and must be tested with auxiliary bus errors.
- SSR notifications use SRCU chains, so callbacks may sleep but ordering and crash-state values must match clients' expectations.

## Test signals

Build Qualcomm remoteproc helpers with GLINK, SMD, SMEM, auxiliary bus, and optional sysmon users. Tests should cover minidump SMEM absent, invalid id, disabled subsystem fallback, encryption-not-ready skip, valid region custom dumps, ELF dump segment filtering, GLINK/SMD DT node absence and lifecycle, SSR notifier ordering and unregister, PDM auxiliary add/delete failures, and memory-leak checks on probe/remove error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.h

## Purpose

`qcom_common.h` declares shared helper structures and functions for Qualcomm remoteproc platform drivers. It is the local interface for GLINK/SMD transport subdevices, SSR notifier subdevices, PDM auxiliary subdevices, minidump setup, ELF dump segment registration, and optional sysmon integration.

## Important APIs, types, and data

- `struct qcom_rproc_glink` stores a remoteproc subdev, SSR name, device/node references, and a GLINK SMEM edge pointer.
- `struct qcom_rproc_subdev` stores a remoteproc subdev, device/node references, and an SMD edge pointer.
- `struct qcom_rproc_ssr` stores a subdev and private SSR subsystem info pointer.
- `struct qcom_rproc_pdm` stores a subdev, parent device, remoteproc index, and auxiliary device pointer.
- Declared helpers include `qcom_minidump()`, GLINK add/remove, `qcom_register_dump_segments()`, SMD add/remove, SSR add/remove, PDM add/remove, and sysmon add/remove/shutdown-acked helpers.
- When `CONFIG_QCOM_SYSMON` is disabled, sysmon helpers compile to safe stubs.

## Control flow

The header itself has no control flow. Concrete Qualcomm remoteproc drivers embed these structs, call add helpers during probe before `rproc_add()`, and call remove helpers during remove. The remoteproc core later invokes the embedded `rproc_subdev` callbacks installed by `qcom_common.c`.

## State and persistence behavior

The structs are per-rproc lifecycle state holders. They store DT node references, transport edge handles, subsystem info pointers, and auxiliary devices that are valid only between add/remove or prepare/unprepare phases. Sysmon stubs return NULL or false and perform no state changes when the feature is disabled.

## Dependencies and integration points

The header depends on remoteproc core/internal definitions and Qualcomm QMI types. It forward declares GLINK and sysmon types to avoid heavier includes. It is intended for Qualcomm remoteproc drivers that also interact with DT child nodes and the remoteproc subdevice lifecycle.

## Risks and edge cases

- Drivers must keep the embedded helper structs alive for the whole remoteproc lifetime because subdev callbacks reference them by container.
- Remove helpers must match add helpers even when optional DT nodes were absent; the C implementation handles NULL/absent cases, but callers should preserve ordering.
- Sysmon behavior changes at compile time. Callers must tolerate NULL sysmon handles and `false` shutdown-ack results.

## Test signals

Compile with and without `CONFIG_QCOM_SYSMON`. Driver integration tests should ensure each embedded struct is initialized once, add/remove helpers are balanced, optional GLINK/SMD nodes are handled, and sysmon stubs do not break shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.c

## Purpose

`qcom_pil_info.c` records Qualcomm Peripheral Image Loader relocation information in a reserved IMEM region described by the `qcom,pil-reloc-info` DT node. Remoteproc/PIL drivers call it to publish loaded firmware image name, base address, and size for post-mortem crash analysis.

## Important APIs, types, and functions

- `PIL_RELOC_NAME_LEN` is 8 bytes; each entry stores an 8-byte name, 64-bit little-endian base, and 32-bit little-endian size.
- `struct pil_reloc` stores the mapped IMEM base and number of entries.
- `_reloc` is a module-global, read-mostly relocation table descriptor protected by `pil_reloc_lock`.
- `qcom_pil_info_init()` lazily finds the `qcom,pil-reloc-info` node, maps its first resource, clears the region, and computes the number of fixed-size entries.
- `qcom_pil_info_store()` finds an existing matching image slot or the first empty packed slot, writes the name if new, then writes base low/high and size using 32-bit writes.
- `pil_reloc_exit()` unmaps the region at module unload.

## Control flow

The first store call locks the mutex and initializes the IMEM mapping if needed. Initialization is skipped on later calls if `_reloc.base` is already set. Store scans entries in order; an empty first byte terminates the packed list and becomes the new slot, while a matching first 8 bytes updates an existing slot. If all entries are occupied, it warns and returns `-ENOMEM`. Base is written with two `writel()` operations because odd entries may only be 4-byte aligned for the 64-bit field.

## State and persistence behavior

The IMEM table is persistent hardware/shared-memory state used outside this driver for crash analysis. The driver clears the entire region on first initialization, so previous bootloader or earlier-kernel records are discarded. `_reloc.base` and `_reloc.num_entries` persist until module exit; individual entries persist until overwritten or the IMEM region is cleared on the next initialization/reset.

## Dependencies and integration points

The file depends on DT address translation, IO mapping/accessors, mutexes, and the local `qcom_pil_info.h` declaration. Qualcomm remoteproc/PIL loaders are expected to call `qcom_pil_info_store()` after placing firmware images.

## Risks and edge cases

- Image names are truncated to 8 bytes and compared over exactly 8 bytes, so names sharing the same prefix collide intentionally or accidentally.
- If no `qcom,pil-reloc-info` node exists, store returns `-ENOENT`; callers must treat this as optional on platforms without the feature.
- `pil_reloc_exit()` calls `iounmap(_reloc.base)` without checking for NULL; this is generally tolerated but depends on architecture implementation.
- The table is cleared at first init even if some firmware had already populated entries before Linux.
- Entry count truncates resource size to a whole number of entries; trailing bytes are ignored.

## Test signals

Tests should cover missing DT node, invalid resource, ioremap failure, first store clearing and writing, update of an existing 8-byte name, name truncation collisions, full table exhaustion, odd-entry base alignment, concurrent stores under the mutex, and module exit after no successful init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.h

## Purpose

`qcom_pil_info.h` is the small public-local declaration for Qualcomm PIL relocation info storage. It exposes the function used by Qualcomm image loader drivers to publish firmware relocation metadata.

## Important APIs, types, and data

- `qcom_pil_info_store(const char *image, phys_addr_t base, size_t size)` stores or updates one PIL relocation record containing image identifier, physical base, and size.

## Control flow

The header has no control flow. Callers include it and call `qcom_pil_info_store()` after loading a firmware image. The implementation performs lazy IMEM mapping and table update.

## State and persistence behavior

No state lives in the header. The function it declares updates persistent IMEM state managed by `qcom_pil_info.c`.

## Dependencies and integration points

The header includes `linux/types.h` for `phys_addr_t` and `size_t`. It is intended for in-kernel Qualcomm PIL/remoteproc users rather than a generic subsystem ABI.

## Risks and edge cases

- The declaration does not document the 8-byte image-name truncation or optional `-ENOENT` behavior; callers need to know implementation constraints.
- The function returns negative errno values and callers should not treat failures as fatal unless their platform requires post-mortem relocation info.

## Test signals

Compile tests should verify every caller includes this header rather than open-coding the prototype. Integration tests should pair calls through this declaration with the IMEM table behavior in `qcom_pil_info.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.h -->
