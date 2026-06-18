# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.h

## Purpose
`sys.h` declares the O2CB sysfs lifecycle functions.

## Important APIs, types, and functions
It declares `o2cb_sys_init` and `o2cb_sys_shutdown`.

## Control flow
Nodemanager module initialization calls `o2cb_sys_init` after configfs registration; module exit calls `o2cb_sys_shutdown` before lower-level heartbeat/network teardown.

## State and persistence behavior
The header has no state. The implementation owns runtime sysfs kset state only.

## Dependencies and integration points
It is included by nodemanager and implemented by `sys.c`, binding module lifecycle to O2CB sysfs presence.

## Risks and test signals
Risks are limited to missing lifecycle calls or wrong init/exit ordering. Test signals include load/unload cycles and failure unwind coverage.
