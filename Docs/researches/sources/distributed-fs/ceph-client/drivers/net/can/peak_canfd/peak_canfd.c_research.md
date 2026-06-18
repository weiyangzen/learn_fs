# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd.c

## Purpose
`peak_canfd.c` is the common PEAK-System uCAN CAN FD netdev layer. It provides command construction, bit timing commands, mode changes, RX message parsing, status/error handling, TX skb formatting, echo management, hardware timestamp reporting, and allocation of PEAK CAN FD netdevs. Bus-specific drivers supply command and TX transport callbacks.

## Important APIs, Types, And Functions
- `peak_canfd_nominal_const` and `peak_canfd_data_const` define bit timing ranges from uCAN field widths.
- `pucan_init_cmd()`, `pucan_add_cmd()`, and `pucan_write_cmd()` build and submit uCAN commands through bus callbacks.
- Command helpers include reset/normal/listen-only modes, slow/fast timing, standard filters, TX abort, error counter clear, option set/clear, and RX barrier.
- RX handlers include `pucan_handle_can_rx()`, `pucan_handle_error()`, `pucan_handle_status()`, and `pucan_handle_cache_critical()`.
- Public message APIs are `peak_canfd_handle_msg()` and `peak_canfd_handle_msgs_list()`.
- Netdev operations are `peak_canfd_open()`, `peak_canfd_close()`, and `peak_canfd_start_xmit()`.
- `alloc_peak_canfd_dev()` allocates and initializes a SocketCAN netdev with PEAK-specific callbacks and capabilities.

## Control Flow
Open calls `open_candev()`, commands reset mode, configures CAN FD ISO/non-ISO option when FD is enabled, enables error counter reporting, programs all standard filter rows to accept all standard IDs, starts the controller in normal or listen-only mode, then sends an RX barrier. The bus-specific driver treats the barrier status as the point where the TX path can be safely enabled and the netdev queue woken.

TX asks the bus-specific `alloc_tx_msg()` for room, formats a `pucan_tx_msg` with CAN ID, DLC, CAN FD flags, RTR, loopback, and optional self-receive, stores an echo skb under `echo_lock`, advances `echo_idx`, stops the queue when echo slots or transport room are exhausted, and calls `write_tx_msg()`.

RX message lists are parsed by size/type. CAN RX messages may first reclaim echo skbs when marked looped back, then optionally deliver self-received frames to RX. Status messages update CAN state, emit CAN error frames, call `can_bus_off()` on bus-off, and process RX barrier confirmation. Error messages update cached BEC counters. Cache-critical messages report RX overflow.

## State And Persistence
State lives in `struct peak_canfd_priv`: CAN core state, netdev pointer, channel index, cached error counters, echo ring index/lock, command buffer state, and bus callback pointers. Hardware timestamps are converted from uCAN microsecond counters to skb hardware timestamps. No persistent storage exists.

## Dependencies And Integration Points
The file depends on SocketCAN, PEAK uCAN protocol structures from `<linux/can/dev/peak_canfd.h>`, and bus-specific callbacks supplied through `peak_canfd_user.h`. The PCIe FD implementation is one such bus-specific backend.

## Risks And Edge Cases
- `pucan_add_cmd()` returns NULL on command-buffer overflow, but several command helpers dereference the returned pointer without checking because current command buffers are sized for one command.
- Queue wake relies on loopback echo messages; lost loopback notifications can leave echo slots occupied.
- RX barrier sequencing is required before TX path enablement; a missing barrier status would keep the queue stopped.
- The common code accepts all standard filters but does not show extended filter programming in this file.
- `pucan_handle_status()` calls `dev_kfree_skb(skb)` even if `alloc_can_err_skb()` returned NULL in the no-state-change path; `dev_kfree_skb(NULL)` is safe but worth noting.

## Test Signals
Test open configuration, CAN FD ISO/non-ISO option switching, listen-only, loopback and self-receive, echo reclaim, queue stop/wake on echo ring exhaustion, RX barrier handling, bus-off and restart, error counter reporting, RX overflow error frames, and hardware timestamp visibility through ethtool/SO_TIMESTAMPING.
