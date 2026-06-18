# sources/distributed-fs/ceph-client/net/bridge/br_stp_timer.c

## Purpose
`br_stp_timer.c` owns bridge and port STP timers. It periodically sends hello BPDUs, expires received root information, progresses forward-delay state transitions, retransmits TCNs, clears topology-change state, handles config BPDU hold-down, and exposes timer values for user APIs.

## Important APIs, types, and functions
- `br_stp_timer_init()` initializes bridge timers: hello, TCN, and topology-change.
- `br_stp_port_timer_init()` initializes per-port message-age, forward-delay, and hold timers.
- `br_timer_value()` returns pending time in `USER_HZ` clock ticks for netlink/sysfs.
- Timer callbacks include `br_hello_timer_expired()`, `br_message_age_timer_expired()`, `br_forward_delay_timer_expired()`, `br_tcn_timer_expired()`, `br_topology_change_timer_expired()`, and `br_hold_timer_expired()`.

## Control flow
The hello timer emits config BPDUs while the bridge is up and reschedules only for kernel STP. The message-age timer means a neighbor's superior BPDU information expired; the port becomes designated, configuration is recomputed, and the bridge may become root. The forward-delay timer moves listening to learning, then learning to forwarding, optionally triggering topology-change detection and carrier on. The TCN timer retransmits TCNs while non-root and up. The topology-change timer clears topology-change flags and restores ageing time through `__br_set_topology_change()`. The hold timer sends a pending config BPDU after the hold interval.

## State and persistence
Timer state is in `struct timer_list` fields on `struct net_bridge` and `struct net_bridge_port`. Timers mutate in-memory STP fields under `br->lock` and emit rtnetlink notifications.

## Dependencies and integration points
The callbacks call STP state-machine functions from `br_stp.c`, notification functions from `br_netlink.c`, netdevice carrier helpers, and bridge logging. They rely on bridge/port lifetime management to cancel timers before freeing objects.

## Risks and edge cases
Callbacks use plain `spin_lock()` because they run in timer context. Message-age and forward-delay callbacks recheck disabled state after locking. `br_ifinfo_notify()` is called with an RCU read-side section in the forward-delay path. Failure to delete timers during port/bridge teardown would risk use-after-free.

## Test signals
Use timer-driven STP simulations for hello reschedule, neighbor loss, listening-to-learning-to-forwarding, TCN retransmission, topology-change expiry, hold-timer pending config, and teardown while timers are active.
