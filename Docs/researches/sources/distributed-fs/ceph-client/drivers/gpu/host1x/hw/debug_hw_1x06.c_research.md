<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x06.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x06.c

## Purpose

`debug_hw_1x06.c` implements register-specific debug output for HW6+ host1x generations with VM/hypervisor register layouts and wider DMA addresses.

## Important APIs, Types, And Functions

- `host1x_debug_show_channel_cdma()`: reads 64-bit-capable DMA start/end registers, DMAPUT/DMAGET/DMACTRL, command processor offset/class, channel status, and queued gathers.
- `host1x_debug_show_channel_fifo()`: reads command FIFO status/data and, on HW6/HW7, uses hypervisor peek registers with SLCG override to dump FIFO contents.
- `host1x_debug_show_mlocks()`: currently a TODO for newer hardware.

## Control Flow

CDMA debug returns inactive when DMASTOP is set or no pushbuffer exists; otherwise it prints whether the channel is waiting in host1x class or active in another class. FIFO debug prints direct FIFO status/data and conditionally performs hypervisor FIFO peeking for generations where those registers exist.

## State And Persistence Behavior

The file observes channel and hypervisor registers. During FIFO peeking on HW6/HW7 it temporarily forces clock-gating override and then clears both peek control and override.

## Dependencies And Integration Points

It depends on VM/hypervisor register macros, `HOST1X_HW`, the shared decoder in `debug_hw.c`, and debugfs dump flow from `debug.c`.

## Risks And Test Signals

The TODO MLOCK dump means newer timeout diagnostics lack MLOCK ownership detail. Hypervisor peek register availability changes on HW8, so conditional code must match silicon. Test debugfs on Tegra186/194/234, including 64-bit DMA addresses and FIFO non-empty cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x06.c -->
