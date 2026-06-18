# sources/distributed-fs/ceph-client/net/ceph/ceph_strings.c

## Purpose
Maps Ceph numeric protocol constants to readable names for logging, debugging, and option/error messages.

## Important APIs, Types, and Functions
Functions are `ceph_entity_type_name()`, `ceph_auth_proto_name()`, `ceph_con_mode_name()`, `ceph_osd_op_name()`, `ceph_osd_watch_op_name()`, and `ceph_osd_state_name()`. Only `ceph_entity_type_name()` is exported from this file, while the others are used within libceph.

## Control Flow
Each function is a switch statement over Ceph constants. `ceph_osd_op_name()` expands `__CEPH_FORALL_OSD_OPS()` to stay aligned with the central OSD op list.

## State and Persistence
No state. Returned string literals have static lifetime.

## Dependencies and Integration Points
Depends on `linux/ceph/types.h` for constants and module export support. Used by auth, OSD, and debug/logging paths.

## Risks
New protocol constants can print as `???` or `unknown` until the mapping is updated. These helpers are diagnostic only and should not be used for protocol decisions.

## Test Signals
Compile-time coverage when constants are added, unit checks for known names, and log-path tests that confirm unknown values remain safe printable strings.
