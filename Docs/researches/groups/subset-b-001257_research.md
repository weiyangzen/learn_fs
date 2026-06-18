# subset-b-001257 research

This grouped report covers Intel IOAT DMAEngine support plus HiSilicon K3, Intel LGM, Loongson APB/CMC, and LPC DMA router drivers. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/dma.c

Purpose: implements the runtime engine for Intel I/OAT QuickData DMA channels after PCI probe has enumerated them. It owns interrupt handling, descriptor-ring allocation, submission, completion cleanup, timeout recovery, channel reset, and DMAEngine status reporting for memcpy, interrupt, XOR, and PQ descriptors prepared elsewhere.

Important APIs and control flow: `ioat_dma_do_interrupt()` handles shared INTx/MSI by checking `IOAT_INTRCTRL`, reading channel attention bits, and scheduling per-channel cleanup tasklets; `ioat_dma_do_interrupt_msix()` schedules one channel directly. `ioat_issue_pending()` and `__ioat_issue_pending()` publish pending descriptors by advancing `issued`/`dmacount` and writing `IOAT_CHAN_DMACOUNT_OFFSET`. `ioat_alloc_ring()` allocates coherent descriptor chunks, wraps them in `ioat_ring_ent` objects, links hardware `next` pointers into a circular chain, and enables descriptor prefetching for DPS-capable hardware. `ioat_check_space_lock()` reserves ring entries under `prep_lock`; descriptor submit callbacks leave that lock held until `ioat_tx_submit_unlock()` assigns a cookie, advances `head`, and optionally pushes descriptors. Cleanup flows through `ioat_cleanup_event()`, `ioat_cleanup()`, and `__ioat_cleanup()`, which read the completion writeback, complete cookies, unmap descriptors, invoke callbacks, skip extension descriptors, free super-extended descriptors, and advance `tail`. Recovery paths include `ioat_timer_event()`, `ioat_eh()`, `ioat_restart_channel()`, `ioat_reboot_chan()`, and `ioat_reset_hw()`.

State and persistence behavior: channel state is split between hardware MMIO registers, a DMA-coherent completion word, a coherent hardware descriptor ring, and software ring cursors `head`, `tail`, `issued`, and `dmacount`. `prep_lock` serializes producers; `cleanup_lock` serializes tasklet/timer cleanup and error handling. Timers persist while work is active, first using `completion_timeout` and later `idle_timeout`. Module parameters tune completion timeout, idle timeout, and pending-descriptor batching indirectly through `ioat_pending_level` from `init.c`. Reset clears channel errors and, for BWD/BDX-DE MSI-X errata, saves/restores MSI-X table/PBA shadow state.

Dependencies and integration points: depends on `dma.h`, `registers.h`, `hw.h`, DMAEngine cookie/callback helpers, PCI config space, coherent DMA allocation, tasklets, timers, and IOAT-specific descriptor layouts. It is called by `init.c` through DMAEngine operation pointers and by `prep.c` through shared ring helpers and submit callbacks.

Risks and test signals: risks include fatal `BUG()` on unexpected channel errors, subtle ordering requirements around `wmb()`/`smp_mb()`, ring-full handling that depends on timer-driven cleanup, descriptor extension accounting mistakes, completion-writeback races after restart, and hardware-specific reset errata. Test signals include successful memcpy self-test, MSI-X/MSI/INTx cleanup interrupts, timer recovery after missed interrupts, no leaked coherent chunks on allocation failure, valid callbacks for abort/read/write errors, sysfs ring counters changing with activity, and successful reset/restart after injected channel halt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/dma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/dma.h

Purpose: provides the private IOAT DMA driver contract shared by PCI init, descriptor preparation, runtime cleanup, and sysfs support. It defines device/channel/ring state, common conversions, ring math, MMIO helpers, operation prototypes, and exported globals.

Important APIs and control flow: `struct ioatdma_device` wraps the PCI device, MMIO base, completion and super-extended descriptor pools, embedded `dma_device`, capability/version data, channel index table, DCA provider, IRQ mode, and MSI-X errata shadows. `struct ioatdma_chan` embeds `dma_chan`, per-channel MMIO base, completion writeback buffer, tasklet/timer, kobject, ring cursors, locks, descriptor chunks, and interrupt coalescing state. `struct ioat_ring_ent` overlays all IOAT hardware descriptor formats with DMAEngine descriptor metadata, callback length/result storage, debug ID, and optional SED pointer. Inline helpers convert DMAEngine objects to IOAT containers, read channel status/errors, issue suspend/reset commands, classify status bits, compute ring active/pending/space counts, map transfer length to descriptor count, fetch ring entries, and program chain address registers.

State and persistence behavior: the header fixes in-memory layout rather than owning state directly. Runtime state persists in channel objects allocated by `init.c`, coherent descriptor chunks allocated by `dma.c`, and DMA pools referenced by device fields. Bit definitions in `ioatdma_chan.state` gate shutdown, active cleanup, pending reset, kobject lifetime, and normal run state. Ring counters are 16-bit and masked against a power-of-two ring size.

Dependencies and integration points: depends on Linux DMAEngine, dmapool, PCI IDs, interrupt definitions, circular-buffer helpers, and local `registers.h`/`hw.h`. It is the shared include for `dma.c`, `init.c`, `prep.c`, and `sysfs.c`; exported prototypes become the internal link points between those translation units.

Risks and test signals: risks include layout coupling between unioned descriptor pointers and raw hardware formats, ring arithmetic relying on power-of-two sizes, channel-number derivation assuming 0x80-byte channel windows, source-count conversion macros requiring caller-side bounds, and `ioat_set_chainaddr()` always using v2 offsets despite compatibility macros existing. Test signals include clean compile with DEBUG and non-DEBUG descriptor IDs, correct channel lookup for all enumerated channels, ring counter wraparound under high transfer counts, successful RAID source-count encoding, and status helpers matching observed `CHANSTS` hardware states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/hw.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/hw.h

Purpose: declares IOAT hardware-facing constants and descriptor structures: supported Intel PCI device IDs, IOAT version values, fixed descriptor size, operation opcodes, and packed descriptor layouts for copy, XOR, PQ, PQ update, raw, and super-extended descriptors.

Important APIs and control flow: the main structures are `ioat_dma_descriptor`, `ioat_xor_descriptor`, `ioat_xor_ext_descriptor`, `ioat_pq_descriptor`, `ioat_pq_ext_descriptor`, `ioat_pq_update_descriptor`, and `ioat_sed_raw_descriptor`. Bitfield unions expose control bits such as interrupt enable, snoop controls, completion write, fence, null descriptor, source count, PQ disable flags, writeback-error status, and the operation opcode. PQ16 helper structures define the two 64-byte SED halves used for 9-16 source RAID operations.

State and persistence behavior: hardware descriptor state persists in DMA-coherent memory allocated by the runtime driver and consumed by the IOAT engine. The file itself has no mutable software state, but its layout is a binary ABI with hardware and must remain 64-byte aligned/compatible with `IOAT_DESC_SZ` and `SED_SIZE`.

Dependencies and integration points: included by all IOAT source files and paired with `registers.h` for MMIO access. `prep.c` fills these descriptors, `dma.c` interprets `op`, extension requirements, and writeback error status during cleanup, and `init.c` uses PCI IDs and versions to select capabilities and quirks.

Risks and test signals: risks include implementation-defined C bitfield layout assumptions, endian sensitivity of descriptor control fields, stale or missing PCI IDs preventing probe, operation-code mismatches, and descriptor-size regressions corrupting ring linking. Test signals include `sizeof`/alignment sanity for descriptor formats, successful memcpy/XOR/PQ/PQ16 self-tests on capable hardware, correct interpretation of DWBES validation bits, and no hardware descriptor errors from alignment or next-pointer encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/init.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/init.c

Purpose: owns IOAT PCI-driver lifecycle. It matches supported Intel devices, maps MMIO, allocates the `ioatdma_device`, configures DMAEngine capabilities, enumerates channels, sets up interrupts, runs hardware self-tests, registers DMA/DCA/sysfs services, handles shutdown/AER recovery, and tears down module caches.

Important APIs and control flow: `ioat_pci_probe()` enables the PCI device, maps BAR0, rejects pre-v3.0 hardware, sets a 64-bit DMA mask, applies version quirks, and calls `ioat3_dma_probe()`. `ioat3_dma_probe()` installs DMAEngine callbacks from `prep.c`/`dma.c`, reads `IOAT_DMA_CAP_OFFSET`, masks RAID capabilities for selected platforms or DCA conflicts, creates SED pools for RAID16SS, calls `ioat_probe()`, registers DMAEngine, adds IOAT kobjects, optionally initializes DCA, disables PCIe relaxed ordering, and sets DPS prefetch limits. `ioat_probe()` creates the completion pool, calls `ioat_enumerate_channels()`, configures interrupts, and runs `ioat3_dma_self_test()`. Channel setup is split across `ioat_enumerate_channels()`, `ioat_init_channel()`, `ioat_alloc_chan_resources()`, and `ioat_free_chan_resources()`. Self-tests exercise memcpy plus XOR/XOR_VAL when supported.

State and persistence behavior: module state includes `ioat_cache`, `ioat_sed_cache`, and module parameters `ioat_dca_enabled`, `ioat_pending_level`, and `ioat_interrupt_style`. Device state persists in the allocated `ioatdma_device`, DMA pools, registered DMAEngine channels, sysfs kobjects, optional DCA provider, interrupt mode, and channel objects. Shutdown marks channels down, deletes timers, resets hardware, and disables interrupts; PCIe AER callbacks reuse shutdown/resume logic to quiesce and re-enable channels after slot reset.

Dependencies and integration points: depends on PCI core, DMAEngine, DCA, DMA pools, IOAT runtime/prep/sysfs files, and hardware/register definitions. Integration is primarily through `pci_driver`, `dma_async_device_register()`, `of`-independent PCI matching, DCA provider registration, and DMAEngine clients such as async_tx/RAID helpers.

Risks and test signals: risks include interrupt fallback complexity, partial resource cleanup differences before and after DMAEngine registration, self-test failures disabling otherwise visible hardware, DCA versus RAID capability conflicts, `ioat_dca_enabled` being globally mutated for v3.4+, and device-ID quirk drift. Test signals include module load/unload without leaks, correct MSI-X/MSI/INTx fallback based on `ioat_interrupt_style`, self-test pass/fail diagnostics, DMA capability masks matching hardware/quirks, sysfs `quickdata` nodes per channel, DCA provider registration only when enabled, and AER recovery restoring usable channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/prep.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/prep.c

Purpose: prepares IOAT hardware descriptor chains for DMAEngine operations. It translates memcpy, interrupt, XOR, XOR validation, PQ generation, PQ validation, PQ-backed XOR, and PQ16 RAID operations into IOAT ring entries while holding producer ordering locks until descriptor submission.

Important APIs and control flow: `ioat_dma_prep_memcpy_lock()` splits large copies by channel transfer cap, fills copy descriptors, marks the final descriptor for interrupt/fence/completion, and returns its DMAEngine descriptor. `__ioat_prep_xor_lock()` maps source indices into base or extension descriptors, adds a legacy null completion descriptor to order RAID completions, and supports validation result storage. `__ioat_prep_pq_lock()` fills P/Q descriptors, handles DMA_PREP_CONTINUE variants, optionally enables DWBES writeback status, and adds a null completion descriptor on older CB3.2 hardware. `__ioat_prep_pq16_lock()` allocates super-extended descriptors for 9-16 source PQ/PQ_VAL operations. Public wrappers validate channel-down state, clear validation result bits, normalize disabled P/Q destinations, and select PQ8 versus PQ16 paths. `ioat_prep_interrupt_lock()` emits a null interrupt descriptor.

State and persistence behavior: descriptor state is written into the coherent ring allocated by `dma.c`; SED state is allocated from device DMA pools and later freed by cleanup. The channel `produce` count and `prep_lock` are managed by `ioat_check_space_lock()` and the submit callback, so callers receive a descriptor while the channel remains locked for in-order submission. Validation results persist through caller-provided `enum sum_check_flags` pointers until cleanup/error handling updates them.

Dependencies and integration points: depends on `dma.c` ring helpers, hardware descriptor layouts from `hw.h`, DMAEngine flags and continuation helpers, scatter/generic mapping already performed by clients, and capability setup in `init.c`. Cleanup in `dma.c` must understand descriptor opcodes, extension descriptors, SED pointers, and DWBES result fields prepared here.

Risks and test signals: risks include `BUG_ON()` for invalid source counts, leaked SED allocations if PQ16 preparation fails after reserving ring space, reliance on source-index lookup tables, CB3.2/CB3.3 completion-order workarounds, flag combinations that mutate destination arrays in place, and `MAX_SCF` limiting PQ-backed XOR wrappers. Test signals include memcpy transfer-size splitting, XOR with 2-8 sources, PQ with disabled P/Q and continuation, PQ16 with 9-16 sources, XOR_VAL/PQ_VAL result bits, interrupt descriptors invoking callbacks, and lockdep coverage for submit-unlock paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/prep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/registers.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/registers.h

Purpose: defines IOAT PCI configuration offsets, global MMIO offsets, per-channel MMIO offsets, capability bits, status masks, error masks, DCA register offsets, version-dependent register selectors, descriptor prefetch controls, and latency-tolerance registers.

Important APIs and control flow: key macros include global registers such as `IOAT_CHANCNT_OFFSET`, `IOAT_XFERCAP_OFFSET`, `IOAT_INTRCTRL_OFFSET`, `IOAT_ATTNSTATUS_OFFSET`, `IOAT_VER_OFFSET`, `IOAT_DMA_CAP_OFFSET`, and `IOAT_PREFETCH_LIMIT_OFFSET`; channel registers such as `IOAT_CHANCTRL_OFFSET`, `IOAT_CHANSTS_OFFSET`, `IOAT_CHAN_DMACOUNT_OFFSET`, `IOAT_CHANCMD_OFFSET(ver)`, `IOAT_CHANCMP_OFFSET_*`, `IOAT_CHANERR_OFFSET`, and DRS/LTR registers; and capability bits for DCA, XOR, PQ, DWBES, RAID16SS, and DPS. `IOAT_CHANCTRL_RUN` packages the interrupt/error bits normally written by cleanup/resource allocation.

State and persistence behavior: the file has no runtime state, but it defines how persistent hardware register state is read and mutated by the IOAT driver. Version-dependent macros select v1 versus v2 command/chain-address offsets, while newer DPS and LTR macros enable performance and power-management features.

Dependencies and integration points: included by IOAT runtime, init, prep, and sysfs files. It is the binding layer between symbolic driver logic and IOAT silicon, PCI config access, DCA support, interrupt routing, reset, channel error clearing, and sysfs interrupt coalescing.

Risks and test signals: risks include incorrect offsets causing silent MMIO corruption, masks that do not match newer device revisions, typo-prone capability semantics such as `IOAT_INTRDELAY_COALESE_SUPPORT`, DCA register assumptions on unsupported systems, and version macros unused or bypassed by some code paths. Test signals include channel count/xfercap reads matching hardware, interrupts acknowledged correctly, error bits logged/cleared accurately, DRS/LTR writes accepted on v3.4+, reset command polling clearing, and capability-dependent feature exposure matching `IOAT_DMA_CAP_OFFSET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/sysfs.c

Purpose: exposes per-channel IOAT diagnostics and tuning through a `quickdata` kobject under each DMA channel device. It reports advertised capabilities, hardware version, ring size/activity, and a writable interrupt-coalescing factor.

Important APIs and control flow: `struct ioat_sysfs_entry` binds sysfs attributes to DMA-channel show/store callbacks. `cap_show()` prints the active DMAEngine capability set, `version_show()` formats the IOAT version nibble pair, `ring_size_show()` and `ring_active_show()` report ring allocation/activity, and `intr_coalesce_show()`/`intr_coalesce_store()` expose `ioat_chan->intr_coalesce`. `ioat_kobject_add()` initializes `quickdata` kobjects for all channels after DMAEngine registration, and `ioat_kobject_del()` removes them if initialization succeeded. `ioat_ktype` wires custom sysfs ops and default attribute groups.

State and persistence behavior: per-channel kobject lifetime is tracked in `ioat_chan->state` with `IOAT_KOBJ_INIT_FAIL`. `intr_coalesce` persists in the channel object; `dma.c` later writes the global interrupt-delay register when the value changes during cleanup. Ring counters are sampled without precision guarantees.

Dependencies and integration points: depends on DMAEngine channel devices already existing, IOAT channel/device containers from `dma.h`, and capability masks set by `init.c`. It integrates with sysfs through raw kobject APIs rather than a device attribute helper.

Risks and test signals: risks include `sscanf(page, "%du", ...)` accepting odd input patterns, ring-size display masking off one descriptor while allocation keeps the full power-of-two count, imprecise unlocked `ring_active`, kobject parent assumptions, and global interrupt-delay hardware being tuned from per-channel state. Test signals include `quickdata` nodes present for every channel, capability output matching DMAEngine caps, version output matching MMIO version, writable `intr_coalesce` rejecting out-of-range values, and removal/unload not leaking kobjects after partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/k3dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/k3dma.c

Purpose: implements a HiSilicon K3 platform DMAEngine controller with physical channels multiplexed across virtual request channels. It supports memcpy, slave scatter-gather, cyclic DMA, runtime pause/resume/terminate, residue reporting, OF DMA translation, and suspend/resume.

Important APIs and control flow: `k3_dma_probe()` maps MMIO, reads `dma-channels`, `dma-requests`, and optional `dma-channel-mask`, gets the clock unless a SoC flag disables it, requests the shared IRQ, creates an LLI DMA pool, initializes physical and virtual channels, registers DMAEngine, and registers an OF DMA controller. `k3_dma_issue_pending()` moves virtual descriptors to the issued queue and adds channels to `chan_pending`; `k3_dma_tasklet()` assigns free physical channels and starts queued work with `k3_dma_start_txd()`. `k3_dma_int_handler()` processes TC1 completion, TC2 cyclic period callbacks, error bits, acknowledges raw interrupt registers, and schedules the tasklet. Preparation functions build hardware LLI chains for memcpy, slave SG, and cyclic transfers. `k3_dma_tx_status()` computes residue from queued descriptors or current hardware LLI/count registers.

State and persistence behavior: `struct k3_dma_dev` stores global MMIO, tasklet, lock, pending virtual-channel list, physical channel array, virtual channel array, clock, LLI pool, and masks. Each virtual channel stores configuration, physical assignment, status, cyclic flag, and slave config. Each physical channel tracks current and completed descriptors. Descriptor state persists in DMA-pool-allocated LLI blocks until virt-dma frees them.

Dependencies and integration points: depends on `virt-dma`, DMAEngine, OF DMA, platform IRQ/resources, clocks, DMA pools, and DT compatibles `hisilicon,k3-dma-1.0` and `hisilicon,hisi-pcm-asp-dma-1.0`. Clients acquire channels by request ID through `k3_of_dma_simple_xlate()`.

Risks and test signals: risks include `clk_prepare_enable()` on an optional/NOCLK clock pointer, channel-mask width assumptions, residue math based on current LLI address, status not always transitioned for paused/completed cases, cyclic chain size limits, and shared tasklet scheduling races between physical and virtual channel locks. Test signals include OF channel lookup by request, memcpy splitting at `DMA_MAX_SIZE`, SG and cyclic audio transfers, TC1/TC2 interrupt behavior, pause/resume removing and requeueing channels, suspend rejection while hardware is active, and no LLI pool leaks after terminate/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/k3dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/lgm/Kconfig

Purpose: declares the build-time option for Intel Lightning Mountain centralized DMA controllers.

Important APIs and control flow: `config INTEL_LDMA` is a boolean option labeled "Lightning Mountain centralized DMA controllers". It depends on `X86 || COMPILE_TEST` and selects `DMA_ENGINE` plus `DMA_VIRTUAL_CHANNELS`. Its help text describes DMA support for on-chip devices including HSNAND and GSWIP.

State and persistence behavior: no runtime state is present. The option controls whether `lgm-dma.o` is built into the kernel because it is `bool`, matching the driver’s `builtin_platform_driver()` registration.

Dependencies and integration points: integrates with the parent DMA Kconfig hierarchy and the local Makefile. Selecting DMAEngine and virt-dma guarantees the symbols used by `lgm-dma.c` are available.

Risks and test signals: risks include lack of module build coverage due to `bool`, architecture gating hiding compile errors outside X86 unless `COMPILE_TEST` is enabled, and missing dependencies for reset/clk/OF APIs if parent menus change. Test signals are successful `CONFIG_INTEL_LDMA=y` builds, visible platform driver registration, and compile-test coverage with OF/reset/clk stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/lgm/Makefile

Purpose: maps the Lightning Mountain DMA Kconfig symbol to the driver object.

Important APIs and control flow: `obj-$(CONFIG_INTEL_LDMA) += lgm-dma.o` adds the LGM DMA implementation when the boolean Kconfig option is enabled.

State and persistence behavior: no runtime state exists; this file controls link-time inclusion.

Dependencies and integration points: depends on `CONFIG_INTEL_LDMA` from the same directory’s Kconfig and the parent kernel build system descending into `drivers/dma/lgm`.

Risks and test signals: risks are limited to symbol/name drift between Kconfig, Makefile, and source file. Test signals include `lgm-dma.o` appearing in built objects for enabled configs and absent for disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/lgm-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/lgm/lgm-dma.c

Purpose: implements Intel Lightning Mountain centralized DMA controllers for multiple instance types and hardware revisions. It exposes slave DMA channels through DMAEngine/OF, configures controller, port, and channel registers, supports v2.2 software descriptors and v3.x hardware/client-provided descriptors, and handles interrupts through virt-dma completions.

Important APIs and control flow: `intel_ldma_probe()` obtains instance match data, maps registers, enables optional clock/reset, reads `DMA_ID` for revision/channel/port/address/data-width capabilities, sets DMA mask, initializes v2.2 IRQ/workqueue where needed, reads `dma-channel-mask`, allocates ports/channels, parses DT feature flags, initializes hardware with `ldma_dev_init()`, registers DMAEngine, and registers `ldma_xlate()`. Controller config helpers set packet arbitration, global polling, DRB, byte enable, flow control, descriptor fetch-on-demand, SRAM descriptors, outstanding reads, and descriptor timeouts. Channel helpers select channels through `DMA_CS`, configure control/class/IRQ/endian/header/byte-offset/ABC/non-posted writes, program descriptor base/count, turn channels on/off, and reset channels. DMAEngine callbacks include `ldma_alloc_chan_resources()`, `ldma_free_chan_resources()`, `ldma_prep_slave_sg()`, `ldma_issue_pending()`, `ldma_terminate_all()`, pause/resume, status, and synchronize. v2.2 uses `dw2_desc` pools, channel IRQs, and ordered workqueue callbacks; newer revisions can accept descriptor base/count directly from SG input.

State and persistence behavior: `struct ldma_dev` stores MMIO base, reset/clock, DMAEngine object, revision, IRQ, ports, channels, feature flags, polling count, instance data, and optional workqueue. `struct ldma_chan` stores virt-channel state, port back pointer, flags, descriptor base/count, channel config knobs, descriptor pool, current descriptor, and work item. Register state persists in controller, port, and selected-channel register windows. Device-managed actions disable the clock and assert reset on teardown.

Dependencies and integration points: depends on platform/OF resources, `virt-dma`, DMAEngine, reset and clock frameworks, bitfield helpers, readl polling, and OF DMA routing. Compatible strings identify CDMA, TX/RX, memory-copy, and TOE DMA instances with different feature defaults.

Risks and test signals: risks include complex revision-dependent behavior, `DMA_CS` selected-register races requiring `dev_lock`, 36-bit addressing only when 64-bit config is enabled, v3.x `ldma_prep_slave_sg()` treating SG DMA address as externally allocated descriptors, incomplete remove path because the driver is built-in, workqueue cleanup around `c->ds`, interrupt masking/ack ordering, and `ldma_dev_df_tout_cfg()` mask omission for the enable bit. Test signals include probe logs showing revision/ports/channels, OF xlate with one-arg and extended client configs, v2.2 SG completion callbacks, v3.x hardware descriptor programming, channel reset/off polling success, interrupt ack/re-enable behavior, port burst/endian configuration, and DMA mask selection for 32/36-bit hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/lgm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/Kconfig

Purpose: groups Loongson DMA controller options and exposes three DMAEngine drivers for Loongson1 APB, Loongson2 APB, and Loongson2 chain multi-channel DMA hardware.

Important APIs and control flow: the menu is active under `MACH_LOONGSON32 || MACH_LOONGSON64 || COMPILE_TEST`. `LOONGSON1_APB_DMA` is tristate, depends on `MACH_LOONGSON32 || COMPILE_TEST`, and selects DMAEngine plus virt-dma. `LOONGSON2_APB_DMA` and `LOONGSON2_APB_CMC_DMA` are tristate, depend on `MACH_LOONGSON64 || COMPILE_TEST`, and select the same DMAEngine infrastructure.

State and persistence behavior: no runtime state exists; symbols control whether the matching platform drivers are compiled as built-ins or modules.

Dependencies and integration points: integrates with the local Makefile and architecture configuration. The help text describes Loongson1 NAND/audio, Loongson2 single-channel APB peripherals, and Loongson-2K0300/2K3000 multi-channel bidirectional controllers.

Risks and test signals: risks include architecture dependency drift, help text not matching actual compatible coverage, and missing compile-test dependencies if APIs evolve. Test signals include all three symbols building under native Loongson configs and `COMPILE_TEST`, and module aliases being generated from OF/ACPI tables in the C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/Makefile

Purpose: ties Loongson DMA Kconfig symbols to their implementation objects.

Important APIs and control flow: `LOONGSON1_APB_DMA` builds `loongson1-apb-dma.o`, `LOONGSON2_APB_DMA` builds `loongson2-apb-dma.o`, and `LOONGSON2_APB_CMC_DMA` builds `loongson2-apb-cmc-dma.o`.

State and persistence behavior: no runtime state exists; the Makefile affects build inclusion only.

Dependencies and integration points: depends on the local Kconfig symbols and the parent DMA Makefile descending into the Loongson subdirectory.

Risks and test signals: risks are object-name or symbol drift. Test signals are successful built-in/module object generation for each selected option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson1-apb-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson1-apb-dma.c

Purpose: implements the Loongson-1 APB DMAEngine driver for up to three APB DMA channels used by peripherals such as NAND and audio. It supports slave scatter-gather, cyclic transfers, pause/resume, termination, residue reporting, and OF channel translation by channel ID.

Important APIs and control flow: `ls1x_dma_probe()` counts IRQs to determine channels, allocates the controller with a flexible channel array, fills DMAEngine capabilities, initializes each channel in `ls1x_dma_chan_probe()`, registers DMAEngine, and registers `of_dma_xlate_by_chan_id`. `ls1x_dma_alloc_chan_resources()` requests a per-channel IRQ, creates an LLI DMA pool, and allocates a coherent query descriptor. `ls1x_dma_prep_lli()` builds hardware LLI lists from scatterlists, chooses RAM-to-device or device-to-RAM command bits, checks copy alignment, links entries, and loops the list for cyclic transfers. `ls1x_dma_issue_pending()` starts the first issued LLI; `ls1x_dma_irq_handler()` completes or cyclic-callbacks the active virt-dma descriptor. Pause/resume query the current LLI, stop hardware, then restart from the saved physical address. `ls1x_dma_tx_status()` queries current LLI state and sums remaining descriptor lengths for residue.

State and persistence behavior: each channel owns an IRQ, register base, LLI pool, coherent current-LLI query buffer, source/destination slave config, bus width, cyclic flag, and current LLI pointer. Descriptors own lists of DMA-pool LLIs freed by virt-dma cleanup. Hardware state is driven through a shared control register with channel ID bits.

Dependencies and integration points: depends on platform resources, per-channel named IRQs `ch0`.., DMAEngine/virt-dma, OF DMA, DMA pools, and the compatible `loongson,ls1b-apbdma`. Clients pass peripheral addresses and bus widths through `dma_slave_config`.

Risks and test signals: risks include `ls1x_dma_prep_dma_cyclic()` leaking `desc` if scatterlist allocation fails, freeing `curr_lli` without checking allocation state, `is_cyclic` not obviously cleared for non-cyclic descriptors, 32-bit address truncation in LLI fields, residue list search assumptions, and shared control register operations across channels. Test signals include per-channel IRQ acquisition, SG and cyclic audio/NAND transfers, pause/resume from queried LLI, correct residue after partial transfer, rejection of unaligned buffers and unsupported directions, and clean removal/freeing of LLI pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson1-apb-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson2-apb-cmc-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson2-apb-cmc-dma.c

Purpose: implements the Loongson-2 chain multi-channel DMA controller for LS2K0300/LS2K3000-class hardware. It exposes multiple private DMAEngine slave/cyclic channels, supports both OF and ACPI DMA translation, and programs per-channel register snapshots for SG or cyclic periods.

Important APIs and control flow: `loongson2_cmc_dma_probe()` obtains SoC config from OF/ACPI match data, reads `dma-channels` with a max fallback, maps registers, enables an optional clock, initializes all virt-dma channels, registers DMAEngine, requests one IRQ per channel, then registers ACPI and OF DMA controllers. `loongson2_cmc_dma_of_xlate()` validates channel/config arguments, obtains a slave channel, and stores masked CCR stream config; `loongson2_cmc_dma_acpi_filter()` does the same from ACPI `chan_id`. Preparation functions build an array of `sg_req` register snapshots: `loongson2_cmc_dma_prep_slave_sg()` for SG and `loongson2_cmc_dma_prep_dma_cyclic()` for cyclic periods. `loongson2_cmc_dma_start_transfer()` stops/clears the channel, loads CCR/CNDTR/CPAR/CMAR for the next SG, and enables the channel. Interrupt handling clears per-channel status bits, handles transfer complete, ignores half-transfer after ack, reports transfer errors, and schedules the next SG or cyclic callback.

State and persistence behavior: device state includes MMIO base, clock, channel count, channel register stride, and flexible channel array. Each channel stores its DMA slave config, active descriptor, ID, IRQ, next SG index, and base CCR/CPAR/CMAR/CNDTR template. Descriptors are software-only register snapshots plus cyclic and count metadata; no hardware descriptor pool is used.

Dependencies and integration points: depends on platform resources, optional clocks, DMAEngine/virt-dma, OF DMA, ACPI DMA, bitfield helpers, and compatibles `loongson,ls2k0300-dma`, `loongson,ls2k3000-dma`, plus ACPI ID `LOON0014`. Consumers supply channel ID and CCR stream bits through firmware DMA specifiers.

Risks and test signals: risks include returning `ERR_PTR()` from prep callbacks that usually return NULL on failure, leaking `desc` on some error paths after allocation, CCR state carrying `CIRC` between preparations if not reset by xlate, residue calculation using the active descriptor for queued cyclic special cases, OF cleanup called even for ACPI-only registration, and per-channel IRQ setup occurring after DMAEngine registration. Test signals include OF and ACPI channel acquisition, correct max-channel fallback, per-channel IRQ callbacks, SG chaining across multiple requests, cyclic one-period hardware circular mode and multi-period software CMAR updates, transfer-error logs, and residue matching CNDTR plus pending SG lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson2-apb-cmc-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson2-apb-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson2-apb-dma.c

Purpose: implements the single-channel Loongson-2 APB DMA controller as a DMAEngine slave/cyclic driver. It builds linked hardware descriptors in a DMA pool, starts transfers by writing a global command register, and supports pause/resume/terminate around the active descriptor chain.

Important APIs and control flow: `ls2x_dma_probe()` maps the command register block, enables the clock, initializes the sole virt-dma channel/IRQ in `ls2x_dma_chan_init()`, fills DMAEngine callbacks/capabilities, registers DMAEngine, and registers OF translation by channel ID. `ls2x_dma_alloc_chan_resources()` creates a descriptor pool; `ls2x_dma_prep_slave_sg()` and `ls2x_dma_prep_dma_cyclic()` allocate flexible software descriptors and one hardware descriptor per SG/period, fill memory/APB addresses, word counts, step fields, direction/interrupt command bits, and next pointers. `ls2x_dma_start_transfer()` dequeues the next virt descriptor and starts hardware at the first descriptor. ISR completion either invokes cyclic callbacks or completes the descriptor and starts the next queued transfer. Pause/resume write STOP/START command bits if the active descriptor is paused or in progress.

State and persistence behavior: `struct ls2x_dma_priv` stores the embedded `dma_device`, clock, MMIO registers, and single channel. The channel stores the active descriptor, descriptor pool, IRQ, and last slave config. Descriptor state includes cyclic flag, burst size, direction, status, and per-SG hardware descriptor metadata. Hardware state is controlled through `LDMA_ORDER_ERG` and descriptor fields containing 64-bit memory/next addresses split high/low.

Dependencies and integration points: depends on `virt-dma`, DMAEngine, platform IRQ/resources, OF DMA, clocks, non-atomic lo/hi 64-bit IO helpers, and compatible `loongson,ls2k1000-apbdma`. Clients configure peripheral address, width, maxburst, and direction before preparing transfers.

Risks and test signals: risks include suspicious bus-width validation in `ls2x_dmac_detect_burst()` rejecting configurations where both src and dst widths match supported masks, no custom residue reporting despite cyclic/SG operation, command-register sharing in a single-channel model, descriptor-pool allocation per channel use, and relying on DMAEngine callbacks to treat `ERR_PTR`-free NULL failures. Test signals include SG and cyclic peripheral transfers, IRQ completion starting queued descriptors, pause/resume command behavior, 64-bit DMA address programming, descriptor-chain termination bit on final descriptor, and OF channel registration under `loongson,ls2k1000-apbdma`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson2-apb-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc18xx-dmamux.c -->
# sources/distributed-fs/ceph-client/drivers/dma/lpc18xx-dmamux.c

Purpose: implements an OF DMA router for the LPC18xx/43xx DMA mux. It maps client DMA specifiers onto a single DMA master while programming CREG mux bits and reserving each mux line until the DMA route is released.

Important APIs and control flow: `lpc18xx_dmamux_probe()` allocates router state, looks up the `nxp,lpc1850-creg` syscon regmap, reads local and master `dma-requests`, allocates one mux state per master request, initializes the spinlock and `dma_router`, then registers `of_dma_router_register()`. `lpc18xx_dmamux_reserve()` expects three DMA args: mux number, mux value, and downstream request. It validates the mux and mux value, substitutes `dma_spec->np` with the first `dma-masters` phandle, marks the mux busy under lock, updates `LPC18XX_CREG_DMAMUX`, rewrites args to the downstream two-argument format, and returns the mux state as route data. `lpc18xx_dmamux_free()` clears the busy flag.

State and persistence behavior: each `lpc18xx_dmamux` entry stores the selected mux value and busy flag. The hardware mux selection persists in the CREG syscon register; freeing a route only clears software busy state and does not reset the hardware bits. Locking protects busy/value changes and register updates.

Dependencies and integration points: depends on OF DMA router APIs, OF platform device lookup, syscon/regmap, spinlocks, a parent/peer DMA master referenced by `dma-masters`, and compatible `nxp,lpc1850-dmamux`. Downstream DMA clients see the rewritten specifier and acquire channels from the real master.

Risks and test signals: risks include no hardware reset on route free, reliance on `of_find_device_by_node()` succeeding for the router node, lack of `regmap_update_bits()` error checking, using master request count for mux array sizing while also reading local `dma-requests`, and route conflicts returning `-EBUSY`. Test signals include invalid arg/mux/value rejection, successful route reservation rewriting to master args, busy detection for duplicate mux claims, correct CREG bitfield writes, and DMA client operation through the selected downstream request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc18xx-dmamux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc32xx-dmamux.c -->
# sources/distributed-fs/ceph-client/drivers/dma/lpc32xx-dmamux.c

Purpose: implements an OF DMA router for the LPC32xx DMA mux signals whose routing is controlled through SSP and I2S clock-control syscon bits. It maps a small fixed table of ambiguous DMA request signals to selected peripheral functions.

Important APIs and control flow: `lpc32xx_dmamux_probe()` allocates router state, gets the parent syscon regmap, initializes the spinlock and `dma_router`, and registers `of_dma_router_register()`. `lpc32xx_dmamux_reserve()` expects three args, finds a fixed `lpc32xx_muxes[]` entry by request signal, validates a binary mux select value, obtains the first `dma-masters` phandle, marks the entry busy under lock, writes the target bit with `regmap_update_bits()`, rewrites the specifier to two args for the downstream master, and returns the mux entry as route data. `lpc32xx_dmamux_release()` clears the busy flag.

State and persistence behavior: fixed mux entries store signal number, names for select values, mux register/bit, current mux value, and busy flag. Hardware routing persists in the syscon bit after release; software only prevents concurrent conflicting use while a route is reserved.

Dependencies and integration points: depends on OF DMA router support, syscon/regmap from the parent node, OF platform lookup, spinlocks/guard helpers, and compatible `nxp,lpc3220-dmamux`. The fixed table covers signal 3, 10, 11, 14, and 15 routing between SPI/SSP/UART/I2S/none functions.

Risks and test signals: risks include debug messages using `name_sel1` in both select cases, error text printing the wrong argument for invalid mux value, no regmap error checking, no hardware reset on release, and only table-listed signals being routable. Test signals include successful reservation for each fixed signal, `-EBUSY` on duplicate active route, correct SSP/I2S syscon bit updates, downstream DMA specifier rewrite, and client transfers through both select-0 and select-1 routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc32xx-dmamux.c -->
