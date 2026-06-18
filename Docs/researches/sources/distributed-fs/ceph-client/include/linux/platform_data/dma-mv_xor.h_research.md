
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-mv_xor.h

## Purpose
This header defines platform data for Marvell XOR DMA engines. It supplies per-channel DMA capability masks to the `mv_xor` driver.

## Important APIs And Types
`MV_XOR_NAME` is the platform device name. `struct mv_xor_channel_data` contains a DMA capability mask, and `struct mv_xor_platform_data` points to an array of channel descriptors.

## Control Flow, State, And Persistence
There is no code flow. Platform code provides channel capability descriptions, which the driver exposes through DMAengine. State is static platform data.

## Dependencies And Integration Points
It depends on DMAengine capabilities and `linux/mbus.h`. Integration points include Marvell platform devices, DMAengine clients, and XOR/offload users such as RAID or memory operations.

## Risks And Test Signals
Incorrect capability masks can expose unsupported operations or hide usable acceleration. Test signals include DMAengine capability enumeration, XOR/memcpy offload tests, channel probe for each configured entry, and fallback behavior when no XOR channel is suitable.
