# sources/distributed-fs/ceph-client/include/soc/tegra/ivc.h

## Purpose

`ivc.h` declares the Tegra Inter-VM Communication shared-memory queue API used to exchange fixed-size frames with firmware or peer devices.

## Important APIs, Types, and Functions

`struct tegra_ivc` stores peer device, RX/TX iosys maps, queue positions, DMA physical addresses, notification callback data, frame count, and frame size. The API uses two-step access: `tegra_ivc_read_get_next_frame()` plus `tegra_ivc_read_advance()`, and `tegra_ivc_write_get_next_frame()` plus `tegra_ivc_write_advance()`. `tegra_ivc_notified()` handles remote notifications and reset progress; `tegra_ivc_reset()` initializes shared state. `tegra_ivc_align()`, `tegra_ivc_total_queue_size()`, `tegra_ivc_init()`, and `tegra_ivc_cleanup()` handle layout and lifetime.

## Control Flow

Users initialize or reset the channel, process notifications until ready, get a frame map, read or write data, and then advance the queue to consume or publish the frame.

## State and Persistence

Local RX/TX positions live in `struct tegra_ivc`; shared queue headers and frames live in mapped DMA/shared memory. Notification state is owned by the peer protocol.

## Dependencies and Integration Points

It depends on Linux device, DMA mapping, iosys-map, and types. BPMP channels can embed IVC objects, and other firmware transports can share the abstraction.

## Risks

Risks include misaligned frame sizes, queue desynchronization after reset, stale maps, missed notifications, and concurrent queue advancement errors.

## Test Signals

Test alignment and total queue sizing, reset handshakes, full/empty queues, read/write sequencing, notification handling, and BPMP IVC integration.
