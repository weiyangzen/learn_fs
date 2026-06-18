# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.c

## Purpose
`ctcm_main.c` is the primary Linux network driver implementation for s390 CTC and CTCMPC channel devices. It registers the ccw and ccwgroup drivers, creates two-channel group devices, initializes netdevs, handles ccw interrupts, formats and transmits packets, unpacks classic CTC receive blocks, and tears resources down.

## Important APIs, Types, And Functions
- Module lifecycle: `ctcm_init()` registers debug views, a root device, the ccw driver, and the ccwgroup driver; `ctcm_exit()` unregisters them.
- Device discovery and grouping: `ctcm_ids`, `ctcm_ccw_driver`, `ctcm_group_driver`, `group_store()`, `ctcm_probe_device()`, `ctcm_new_device()`, `ctcm_shutdown_device()`, and `ctcm_remove_device()`.
- Channel management: global `channels`, `add_channel()`, `channel_get()`, `channel_free()`, `channel_remove()`, and `ctcm_ch_alloc_buffer()`.
- Netdev operations: `ctcm_open()`, `ctcm_close()`, `ctcm_tx()`, `ctcmpc_tx()`, `ctcm_change_mtu()`, and `ctcm_stats()` via `ctcm_netdev_ops` and `ctcm_mpc_netdev_ops`.
- Packet paths: `ctcm_transmit_skb()` for classic CTC, `ctcmpc_transmit_skb()` for MPC, `ctcm_unpack_skb()` for classic receive blocks, and `ctcmpc_send_sweep_req()` for MPC sequence maintenance.
- Interrupt path: `ctcm_irq_handler()` maps ccw status into channel FSM events.

## Control Flow
Module initialization starts with `ctcm_init()`, which sets `channels = NULL`, creates the `ctcm` root device, registers a ccw driver for 3088 channel variants, and registers a ccwgroup driver with a writable `group` driver attribute. Writing a group spec calls `ccwgroup_create_dev()`, then `ctcm_probe_device()` allocates `struct ctcm_priv`, assigns both ccw interrupt handlers, and attaches sysfs groups.

When a group is set online, `ctcm_new_device()` adds both channel devices to the global list, sets both ccw devices online, allocates and initializes a netdev, reserves one channel for read and one for write, attaches the netdev to the ccwgroup device, and registers it. Non-MPC netdev open/close directly sends device FSM start/stop events. MPC open/close is mediated by exported MPC APIs in `ctcm_mpc.c`.

`ctcm_irq_handler()` validates the IRB, identifies whether the interrupt belongs to the read or write channel, copies the IRB to `ch->irb`, and emits FSM events based on subchannel checks, unit checks, busy/attention bits, final status, or normal IRQ status. Unit-check sense bytes are decoded by `ccw_unit_check()` into remote reset, remote system reset, hardware failure, parity, timeout, zero, or unknown events.

Classic transmit begins at `ctcm_tx()`. It validates skb headroom, ensures the device FSM is running, marks the netdev busy, and calls `ctcm_transmit_skb()`. That function prepends the link-level header and block length, handles high-address DMA/IDAL limitations by copying when needed, prepares either direct skb ccws or reusable `trans_skb` ccws, starts the write ccw, and relies on FSM completion actions for stats and queue draining. MPC transmit follows the same high-level shape but prepends PDU and TH headers, observes MPC group state and sweep state, and can aggregate PDUs.

Classic receive blocks are unpacked by `ctcm_unpack_skb()`: it parses a leading length and repeated `struct ll_header` entries, validates protocol and lengths, clones each packet into a fresh skb, sets protocol/checksum metadata, updates stats, and delivers via `netif_rx()`.

## State And Persistence Behavior
The file owns the global in-memory channel list and root device pointer. Per-device state is held in `struct ctcm_priv` and attached to ccwgroup and netdev objects. Per-channel state includes ccw arrays, IRB storage, skbs, skb queues, timers, FSMs, flags, retry counters, and profiling counters. Sysfs can persistently influence runtime defaults while the device exists (`protocol`, `buffer_size`), but there is no storage across module unload or reboot.

## Dependencies And Integration Points
This code integrates with the s390 ccw and ccwgroup subsystems, Linux netdev APIs, skbuff APIs, IDAL/CDA helpers, root devices, sysfs driver attributes, and local FSM/MPC/debug modules. It depends on `ctcm_fsms.c` for state tables and actions, `ctcm_sysfs.c` for device attributes, and `ctcm_mpc.c` for MPC group initialization and callbacks.

## Risks
- The global `channels` list is manipulated without an obvious global list lock in the visible code, so lifetime assumptions depend on ccwgroup serialization.
- Error paths in `ctcm_new_device()` call `channel_get()` during rollback; because `channel_get()` marks channels in use and mutates direction flags, rollback ordering is subtle.
- DMA and IDAL fallback handling is complex. Incorrect normalized CDA cleanup or skb refcounting can leak DMA mappings, leak skbs, or free buffers still referenced by ccws.
- `ctcm_tx()` returns `NETDEV_TX_BUSY` after `ctcm_transmit_skb()` failure even after some error paths have already cleared busy state, so queue behavior should be tested under start failures.
- `ctcm_unpack_skb()` returns on the first malformed packet in a block; malformed trailing data can drop remaining packets.

## Test Signals
- Module load/unload and ccwgroup creation should leave no dangling root devices, ccw handlers, netdevs, channels, tasklets, or timers.
- Online/offline tests should cover both success and rollback after each failure point in `ctcm_new_device()`.
- Packet tests should cover classic S390/OS390/Linux protocols, MTU changes, illegal packet type/length, multi-packet receive blocks, direct and fallback transmit, and MPC TH/PDU formatting.
- IRQ tests should inject unit-check, busy, attention, final-status, subchannel-check, and IRB error cases and verify the emitted FSM events.
