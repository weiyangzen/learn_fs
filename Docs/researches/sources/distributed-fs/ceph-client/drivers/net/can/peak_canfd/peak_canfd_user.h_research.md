# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd_user.h

## Purpose
`peak_canfd_user.h` defines the private interface between PEAK's common uCAN CAN FD logic and bus-specific drivers.

## Important APIs, Types, And Functions
- `PCANFD_ECHO_SKB_DEF` tells the allocator to use the common default echo skb count.
- `struct peak_canfd_priv` embeds `can_priv`, netdev pointer, channel index, BEC cache, echo ring state, command buffer state, and callback hooks.
- Callback hooks cover command pre-processing, command write, command post-processing, TX path enablement, TX message allocation, and TX message submission.
- Public prototypes expose `alloc_peak_canfd_dev()`, `peak_canfd_handle_msg()`, and `peak_canfd_handle_msgs_list()`.

## Control Flow
Bus drivers allocate a netdev with `alloc_peak_canfd_dev()`, then fill callbacks and command buffer fields. The common code calls those callbacks during open, mode changes, and TX. Bus drivers call `peak_canfd_handle_msgs_list()` when transport-specific RX/IRQ code obtains uCAN messages.

## State And Persistence
The struct defines per-channel runtime state. It has no persistent storage and no global state.

## Dependencies And Integration Points
It includes `<linux/can/dev/peak_canfd.h>` for uCAN message and command protocol definitions. It is shared by `peak_canfd.c` and `peak_pciefd_main.c`.

## Risks And Edge Cases
- `struct can_priv` must remain first for SocketCAN private-data assumptions.
- The callback contract is not type-specialized by transport, so bus drivers must ensure command buffer size, DMA/message allocation, and callback sequencing match common expectations.
- Echo locking is shared between common TX and backend IRQ wake paths.

## Test Signals
Compile common plus PCIe backend, validate callback initialization before registration, and run TX/RX paths that exercise every callback.
