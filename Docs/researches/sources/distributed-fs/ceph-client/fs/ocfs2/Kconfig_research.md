# sources/distributed-fs/ceph-client/fs/ocfs2/Kconfig

## Purpose
`fs/ocfs2/Kconfig` exposes OCFS2 filesystem build options and dependencies for the shared-disk cluster filesystem, clustering backends, statistics, mask logging, and expensive debug checks.

## Important Options
`OCFS2_FS` is the main tristate and depends on `INET`, `SYSFS`, and `CONFIGFS_FS`; it selects buffer heads, JBD2, CRC32, quotas, POSIX ACLs, and legacy direct I/O. `OCFS2_FS_O2CB` enables kernelspace O2CB clustering. `OCFS2_FS_USERSPACE_CLUSTER` enables userspace clustering with DLM. `OCFS2_FS_STATS` depends on DEBUG_FS. `OCFS2_DEBUG_MASKLOG` enables logging controls. `OCFS2_DEBUG_FS` enables expensive consistency checks.

## Control Flow and Integration
These symbols drive `fs/ocfs2/Makefile` object inclusion. Main OCFS2 and stack glue build with `OCFS2_FS`; stack modules and DLM subdirectories are conditional. Selected ACL and quota infrastructure supports files such as `acl.c`.

## State and Persistence Behavior
Kconfig has no runtime state, but it changes compiled filesystem behavior. ACL and quota selections affect persistent inode xattrs and quota metadata. Debug options add logging or consistency-check behavior.

## Dependencies and Integration Points
The dependency graph connects OCFS2 to networking, sysfs, configfs, buffer heads, journaling, CRC32, quotas, ACLs, direct I/O compatibility, debugfs, and DLM.

## Risks
Misconfigured dependencies can produce partial cluster-stack builds or missing runtime tooling expectations. Debug mask logging increases kernel size; expensive checks are correctly default-off for performance.

## Test Signals
Validate allmodconfig and modular builds for main OCFS2, O2CB, userspace cluster, stats, masklog, and debug combinations. Confirm Makefile selection matches Kconfig symbols.
