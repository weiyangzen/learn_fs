# sources/distributed-fs/ceph/src/mon/NVMeofGwMon.h

## Purpose
`NVMeofGwMon.h` declares the NVMe-oF gateway monitor Paxos service. It defines the service state, lifecycle hooks, command/beacon dispatch, subscription handling, timeout tracking, and helper APIs that connect monitor Paxos to `NVMeofGwMap`.

## Important APIs, Types, and Members
`LastBeacon` identifies a gateway/group pair for timeout tracking and defines ordering/equality for `std::map`. `NVMeofGwMon` derives from `PaxosService` and `md_config_obs_t`. It owns committed `map`, `pending_map`, `last_beacon`, and `last_beacon_check`. It also exposes `gws_deleting_time` for health timing.

Overrides include config observer stubs, `create_initial()`, `create_pending()`, `encode_pending()`, `init()`, `on_shutdown()`, `on_restart()`, `update_from_paxos()`, `get_trim_to()`, `preprocess_query()`, `prepare_update()`, empty `encode_full()`, `tick()`, and `print_summary()`. Public service helpers include command/beacon preprocess/prepare methods, subscription checks, and `get_map()`.

Private helpers cover last-beacon synchronization, gateway-down processing, gateway lookup by connection address, ACK epoch selection, gateway epoch recreation, pending-map restoration/cleanup, listener formatting, beacon application, ACK sending, and timeout checks.

## Control Flow Contract
The service is leader-driven for periodic work and Paxos-driven for mutations. Gateway beacons always flow to the prepare path because they may mutate pending state. Commands can be answered in preprocessing if read-only or prepared as Paxos updates if mutating. Subscriptions are checked after map loads and ticks to deliver full or filtered maps.

## State and Persistence
`map` is the committed Paxos state, while `pending_map` is rebuilt from `map` for each proposal. `last_beacon`, `last_beacon_check`, and `gws_deleting_time` are monitor-local runtime state. The constructor sets `map.mon = &mn`; `pending_map.mon` is not set in the header, so implementation paths rely on copy/assignment or external initialization to preserve monitor access.

## Dependencies and Integration Points
The class includes `PaxosService` and `NVMeofGwMap`. It is instantiated by `Monitor` as the `PAXOS_NVMEGW` service and interacts with monitor sessions, gateway beacon/map messages, OSDMonitor, and monitor health. `md_config_obs_t` is present but currently observes no keys.

## Risks
The class stores maps by value, so copies must preserve embedded `Monitor *` where implementation methods need it. Config observer stubs mean changes to relevant NVMe-oF config are read dynamically through `g_conf()` rather than cached here. `LastBeacon` ordering must remain stable with `NvmeGroupKey` ordering for timeout erasure and lookup correctness.

## Test Signals
Tests should instantiate the service with monitor fixtures, verify lifecycle and map pointer initialization, exercise LastBeacon ordering, check runtime state reset on restart, and cover public preprocess/prepare dispatch with beacon and command messages.
