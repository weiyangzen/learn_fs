# sources/distributed-fs/ceph-client/net/lapb/lapb_iface.c

## Purpose
`lapb_iface.c` is the public interface and lifetime manager for the LAPB protocol. It lets network devices register callbacks, controls LAPB parameters, handles connect/disconnect/data requests, dispatches inbound data to the state machine, and reacts to netdevice carrier/up/down events.

## Important APIs, Types, and Functions
Exported APIs include `lapb_register()`, `lapb_unregister()`, `lapb_getparms()`, `lapb_setparms()`, `lapb_connect_request()`, `lapb_disconnect_request()`, `lapb_data_request()`, and `lapb_data_received()`. Callback dispatch helpers include `lapb_connect_confirmation()`, `lapb_connect_indication()`, `lapb_disconnect_confirmation()`, `lapb_disconnect_indication()`, `lapb_data_indication()`, and `lapb_data_transmit()`. The file owns the global `lapb_list` protected by `lapb_list_lock`.

## Control Flow
Registration creates and initializes a `struct lapb_cb`, inserts it into `lapb_list`, starts T1, and associates it with a net device and callback table. Public operations find the control block by device, take its spinlock, then either mutate state or call cross-file helpers. Connect from state 0 starts link establishment and moves to state 1. Disconnect clears queues and sends DISC when connected. Data requests enqueue skb data to `write_queue` and call `lapb_kick()`. Received data is passed to `lapb_data_input()`. Netdevice notifier events start establishment on carrier-up for DTE mode, start T1 for DCE mode, disconnect before going down, and clear state/timers on down or carrier loss.

## State and Persistence
State is held in `struct lapb_cb`: device pointer, callbacks, T1/T2 timers, mode, window, state, sequence variables, queues, conditions, and refcount. The global list keeps one LAPB control block per device. There is no persistent storage beyond in-kernel protocol state.

## Dependencies and Integration Points
This file integrates with `net/lapb.h`, skbuff queues, kernel timers, netdevice notifier infrastructure, and device callbacks supplied by LAPB consumers. It only handles devices in `init_net` with `ARPHRD_X25` in its notifier path.

## Risks and Edge Cases
Unregister waits for references to drain while holding the list write lock, then synchronously deletes timers, so lifetime ordering matters. Parameter changes to mode/window are only allowed in state 0; timer values can change while active. Callback implementations own transmitted or indicated skb handling, making ownership semantics important. Device events are ignored outside `init_net`.

## Test Signals
Tests should register/unregister repeatedly under traffic, verify duplicate registration returns `LAPB_BADTOKEN`, exercise state transitions from connect/disconnect APIs and carrier changes, validate parameter bounds for normal and extended windows, and run with lockdep/KASAN to catch timer/refcount races.
