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
