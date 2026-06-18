# sources/distributed-fs/ceph-client/include/linux/drbd_genl.h

## Purpose
This header is macro input for DRBD's generic-netlink schema generator. It defines nested top-level attributes, configuration structures, notifications, and admin operations for DRBD control and status reporting.

## Important APIs, types, and functions
The file uses generator macros such as `GENL_struct`, `GENL_mc_group`, `GENL_notification`, `GENL_op`, `GENL_tla_expected`, `GENL_op_init`, and `GENL_doit`. Structures include config reply/context, disk config, resource options, net config, role/resize/new-current-UUID/timeout/disconnect/detach parameters, state info, resource/device/connection/peer-device info, statistics blocks, notification header, and helper info.

Admin operations include status query, new/delete minor, new/delete resource, resource opts, connect, change net opts, disconnect, attach, change disk opts, resize, primary/secondary role changes, new current UUID, online verify, detach, invalidate, pause/resume sync, suspend/resume I/O, outdate, timeout query, down, dump resources/devices/connections/peer devices, initial-state dump, and helper notifications. The `events` multicast group carries state and helper notifications.

## Control flow, state, and persistence
Control flow is declarative: generator includes turn these macro records into enums, policies, conversion functions, operation tables, and multicast helpers. State carried over netlink includes persistent DRBD configuration, runtime connection/disk/role state, counters, UUIDs, bitmaps, pending request counts, and helper execution status. Required, invariant, optional, and sensitive flags affect validation and output handling.

## Dependencies and integration points
It depends on `drbd.h`, `drbd_limits.h` defaults, and the `genl_magic_*` generator headers included by `drbd_genl_api.h`. It is tightly coupled to kernel handlers named in `GENL_doit()` and dump callbacks. User-space DRBD admin tools must match the generated command numbers and attribute schema.

## Risks and test signals
Risks include duplicate field names across generated structs, changing command numbers, failing to mark required/invariant fields, exposing sensitive fields such as `shared_secret`, and schema drift between kernel and user tools. Tests should validate generated nla policies, required-attribute rejection, dumpit pagination/done callbacks, event multicast payloads, handler command numbers, and backward compatibility for optional fields.
