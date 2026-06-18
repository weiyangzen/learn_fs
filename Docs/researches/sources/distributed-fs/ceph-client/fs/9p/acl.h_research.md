<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.h -->
# sources/distributed-fs/ceph-client/fs/9p/acl.h

## Purpose
`acl.h` provides the conditional ACL interface used by 9p inode and superblock code.

## Important APIs, types, and functions
When `CONFIG_9P_FS_POSIX_ACL` is enabled it declares ACL get/set/chmod/create helpers. Otherwise it supplies NULL operation pointers and no-op inline helpers.

## Control flow
No runtime control flow except inline no-op paths in non-ACL builds.

## State and persistence
No state is owned here. It controls whether ACL state is handled by compiled code.

## Dependencies and integration points
It integrates optional `acl.c` support with inode operation tables and creation/setattr code.

## Risks and test signals
Risks include build breakage from missing stub coverage and behavior differences when ACL support is disabled. Test signals are ACL-enabled/disabled builds and inode operation table initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.h -->
