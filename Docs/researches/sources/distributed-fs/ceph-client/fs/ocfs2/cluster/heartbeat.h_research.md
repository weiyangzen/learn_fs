# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.h

## Purpose
`heartbeat.h` defines the in-kernel O2CB heartbeat interface, constants, callback contract, and public region/node query APIs.

## Important APIs, types, and functions
Constants define heartbeat timing (`O2HB_REGION_TIMEOUT_MS`, `O2HB_DEFAULT_DEAD_THRESHOLD`, `O2HB_MAX_WRITE_TIMEOUT_MS`), live/dead thresholds, region name length, and callback magic. `enum o2hb_callback_type` defines node-down and node-up callbacks. `struct o2hb_callback_func` stores callback function, data, priority, type, list node, and magic. Declarations cover callback setup/register/unregister, node-map fills, heartbeat init/exit, region stop/listing, node heartbeat checks, and global heartbeat mode query.

## Control flow
Subsystems initialize a callback with `o2hb_setup_callback`, register it optionally against a region UUID, receive serialized node up/down calls from heartbeat threads, then unregister before teardown. Region configfs groups are allocated by nodemanager through `o2hb_alloc_hb_set`.

## State and persistence behavior
The header exposes `o2hb_dead_threshold`, whose value influences on-disk `hb_dead_ms` and write-timeout fencing. It has no direct storage beyond declarations but defines the callback ABI used to pin heartbeat regions while dependent users exist.

## Dependencies and integration points
It includes `ocfs2_heartbeat.h` for on-disk slot layout and forward-declares nodemanager nodes/configfs groups. It is consumed by nodemanager, quorum, TCP networking, DLM, and filesystem code that checks cluster membership.

## Risks and test signals
Risks include callback users registering with wrong priority/type, stale region UUID assumptions in local heartbeat mode, and timeout macros changing as `o2hb_dead_threshold` changes. Test signals include callback registration order, unregister during active callbacks, local versus global region UUID behavior, and builds across configfs users.
