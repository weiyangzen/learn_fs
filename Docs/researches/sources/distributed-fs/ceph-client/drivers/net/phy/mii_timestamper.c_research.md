# sources/distributed-fs/ceph-client/drivers/net/phy/mii_timestamper.c

## Purpose
Provides a generic registry that lets MII timestamp controller devices expose per-port `struct mii_timestamper` instances to PHY consumers through device-tree node and port lookup.

## Important APIs, Types, And Functions
`struct mii_timestamping_desc` stores list node, controller callbacks, and backing device. `register_mii_tstamp_controller()` and `unregister_mii_tstamp_controller()` manage the global controller list. `register_mii_timestamper()` finds a controller by OF node and calls `probe_channel()`. `unregister_mii_timestamper()` releases the channel and device reference.

## Control Flow
Controllers register into a global list protected by `tstamping_devices_lock`. Consumers request a timestamper by device node and port; lookup returns `-EPROBE_DEFER` if no controller is present. Static PHY-owned timestampers without `mii_ts->device` are ignored during unregister.

## State And Persistence
State is kernel memory only: the global list and descriptors. Active timestampers hold device references with `get_device()` and `put_device()`.

## Dependencies And Integration Points
Depends on `linux/mii_timestamper.h`, list/mutex/device APIs, and controller `probe_channel`/`release_channel` callbacks.

## Risks
The `list_add_tail()` argument order appears reversed relative to the standard Linux API and should be verified. Device-node matching assumes unique controller nodes. Lifetime safety depends on unregister ordering and controller release behavior.

## Test Signals
Build timestamping users, register multiple controllers, request/release ports, validate `-EPROBE_DEFER`, and run list-debug/KASAN coverage around register/unregister.
