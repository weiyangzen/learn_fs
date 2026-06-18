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
