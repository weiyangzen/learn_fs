# sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.h

## Purpose
Declares constants and the initialization entry point for the NFS ACLv3 RPC program.

## APIs, Types, and Functions
Defines procedure numbers `ACL3_NULL`, `ACL3_GETACL`, `ACL3_SETACL`, and `ACL3_PROC_COUNT`; listener port `GF_ACL3_PORT`; logging domain `GF_ACL`; ACL mask bits `NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`; NFS default ACL tag bit `NFS_ACL_DEFAULT`; and maximum ACL entry count `NFS_ACL_MAX_ENTRIES`. It declares `rpcsvc_program_t *acl3svc_init(xlator_t *nfsx)`.

## Control Flow, State, and Persistence
The header has no runtime flow. Its constants control ACL RPC dispatch sizing, valid mask validation, ACL translation bounds, and listener configuration in `acl3.c`.

## Dependencies and Integration
Depends on `<glusterfs/glusterfs-acl.h>` for POSIX ACL definitions and on types visible through included NFS/RPC headers in consumers. It integrates with `acl3.c` and the NFS server build.

## Risks and Test Signals
Risks include mismatch between `ACL3_PROC_COUNT` and the actor table, changing `GF_ACL3_PORT` breaking clients or firewall rules, and `NFS_ACL_MAX_ENTRIES` diverging from allocated call-state buffers. Test signals are compile-time actor table builds, ACL GET/SET calls using the defined masks, and interoperability with NFS ACL clients.
