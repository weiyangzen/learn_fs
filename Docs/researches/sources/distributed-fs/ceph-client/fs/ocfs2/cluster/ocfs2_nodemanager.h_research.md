# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_nodemanager.h

## Purpose
`ocfs2_nodemanager.h` defines userspace-visible O2CB nodemanager constants and limits.

## Important APIs, types, and functions
It defines `O2NM_API_VERSION` as 5, `O2NM_MAX_NODES` and `O2NM_INVALID_NODE_NUM` as 255, `O2NM_MAX_NAME_LEN` as 64, and `O2NM_MAX_REGIONS` as 32.

## Control flow
The constants constrain configfs validation, heartbeat bitmaps/slot counts, sysfs interface revision reporting, and global heartbeat region allocation.

## State and persistence behavior
The header has no state. Changing these values affects runtime ABI and, for max regions, DLM compatibility.

## Dependencies and integration points
It is included by nodemanager and heartbeat headers and by sysfs revision code. Userspace cluster tools depend on the API version and limits.

## Risks and test signals
Risks are ABI breakage from changing constants, off-by-one treatment of node 255 as invalid, and exceeding DLM-compatible region limits. Test signals include configfs boundary values for node numbers, node names, and region count; sysfs `interface_revision`; and bitmap sizing builds.
