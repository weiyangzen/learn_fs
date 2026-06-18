# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/dim2.c

## Purpose
Implements the MOST HDM for DIM2/MediaLB hardware: platform probe, MOST interface registration, channel configuration, DMA buffer enqueue/completion, interrupt handling, network-info delivery, sysfs lock state, and platform-specific clock/PHY enablement.

## Important APIs, Types, And Functions
`struct hdm_channel` tracks per-channel MOST/HAL state, pending and started MBO lists, direction, type, and reset DBR pointer. `struct dim2_hdm` owns 31 DMA channels, MOST interface/capabilities, MMIO base, clocks, netinfo thread/waitqueue, MAC/link state, async-TX index, and platform hooks. `configure_channel()` normalizes buffer sizes and initializes HAL channels by MOST data type. `enqueue()` adds MBOs to pending and tries transfer. `poison_channel()` destroys HAL channel and completes pending/started MBOs with close status. IRQ paths call `dim_service_mlb_int_irq()`, `dim_service_ahb_int_irq()`, `dim_service_channel()`, `service_done_flag()`, and `try_start_dim_transfer()`. Probe parses `microchip,clock-speed`, maps MMIO, starts HAL, requests interrupts, starts netinfo thread, fills capabilities, and registers MOST interface.

## Control Flow
Userspace/MOST core configures a channel, then enqueues MBOs. Pending MBOs move to started when HAL reports ready and DBR space exists. AHB IRQ top half services HAL interrupt state and wakes threaded handler; threaded handler services each channel, detaches completed buffers, completes MBOs, and starts more transfers. Async RX network-info packets are parsed and recycled; a thread calls the MOST netinfo callback.

## State And Persistence
State is runtime-only. The driver keeps MBO queues under `dim_lock`, active HAL channel state, DBR sizing, async-TX index, link/MAC info, and platform clock handles. Sysfs `state` exposes MediaLB lock status.

## Dependencies And Integration Points
Depends on Linux platform/OF/IRQ/clock/DMA/kthread APIs, MOST core (`struct most_interface`, MBO callbacks), and the local HAL. Platform data supports i.MX6, Renesas Gen2/Gen3, and Xilinx compatibles.

## Risks And Test Signals
Global `dim_lock` serializes HAL and list state; completion callbacks are invoked after dropping it, which is important. Busy `while (!try_start_dim_transfer())` loops can spin if progress is rapid. Probe returns directly from `most_register_interface()` after creating a release-managed device, so failure behavior should be checked. Test signals include channel configure/enqueue/poison for all data types/directions, DBR exhaustion, netinfo packet parsing, IRQ storm/empty-list hard error paths, sysfs lock state, and platform clock enable/disable on remove.
