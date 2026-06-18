# sources/distributed-fs/ceph-client/drivers/remoteproc/stm32_rproc.c

## Purpose
Platform driver for STM32MP1 M4 remote processor control. It supports remoteproc-managed boot, attach/detach to bootloader-started firmware, hold-boot control through SCMI reset, SMC, or syscon, mailbox virtqueue and lifecycle signaling, watchdog crash reporting, reserved-memory carveouts, resource-table discovery, and wake IRQ handling.

## Important APIs, Types, And Functions
Private types include `struct stm32_syscon`, `struct stm32_rproc_mem`, `struct stm32_rproc_mem_ranges`, `struct stm32_mbox`, and `struct stm32_rproc`. `st_rproc_ops` supplies prepare/start/stop/attach/detach/kick, ELF callbacks, and `get_loaded_rsc_table`. Key helpers include memory translation, reserved-memory prepare, mailbox setup, hold-boot control, coredump trace addition, resource-table mapping, and DT parsing.

## Control Flow
Probe sets a 32-bit DMA mask, reads firmware name, allocates rproc, sets ELF coredump info, parses watchdog IRQ, resets, hold-boot controls, optional PDDS, auto-boot, M4 state, and resource-table syscon, reads parent `dma-ranges`, detects already-running M4 as `RPROC_DETACHED`, creates a workqueue, requests mailboxes, and registers the rproc.

Prepare translates reserved memory from PA to DA, registers normal regions as ioremap-backed carveouts and coredump segments, and registers `vdev0buffer` for DMA allocation. Firmware parsing tolerates a missing resource table with a warning. Start clears deep sleep, releases hold boot, then reasserts hold boot for the next cycle. Attach adds coredump trace segments and holds boot. Detach sends a detach mailbox message and releases hold boot. Stop optionally sends shutdown, holds boot, asserts reset, sets deep sleep, and updates M4 state.

Mailbox callbacks queue work for vq interrupts under `rproc->lock`; `kick()` sends "kick" on the matching channel. `get_loaded_rsc_table()` reads a DA from syscon, translates to PA, maps a fixed 1 KiB window, and returns it for attach mode.

## State And Persistence Behavior
Private state tracks mapped reserved memories, mailboxes, syscon descriptors, watchdog IRQ, workqueue, and mapped resource-table window. Carveouts and coredump segments are registered during prepare and cleaned by core. Mailbox channels and workqueue persist from probe to remove. Wake IRQ state is enabled for `wakeup-source`.

## Dependencies And Integration Points
Depends on STM32 DT bindings for reset/syscon/mailbox/reserved-memory/dma-ranges properties, optional `st,auto-boot`, watchdog IRQ, ARM SMCCC when configured, regmap/syscon, reset, mailbox, PM wake IRQ, remoteproc coredump, and virtio/rpmsg.

## Risks
The fixed 1024-byte resource-table mapping assumes firmware reserves enough space and detach overwrites that whole window. Missing resource tables are allowed, so vdev/trace resources may be absent. Mailboxes are optional except deferral, so firmware protocols must tolerate missing shutdown/detach channels. Hold-boot has three control paths and is sensitive to DT correctness. Remove explicitly calls shutdown before `rproc_del()`, relying on core idempotency.

## Test Signals
Test remoteproc boot and bootloader attach, all hold-boot mechanisms, no-resource-table firmware, mailbox vq/kick/shutdown/detach paths, watchdog crash IRQ recovery, coredump segment and trace inclusion, suspend/resume wake IRQ, `dma-ranges` translation failures, and missing optional syscon properties.
