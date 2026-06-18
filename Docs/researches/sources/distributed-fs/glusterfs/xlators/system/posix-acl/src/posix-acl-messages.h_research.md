# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-messages.h

Purpose: stable Gluster message-ID declarations for POSIX ACL log events.

Important APIs, types, and functions: uses `GLFS_MSGID(POSIX_ACL, POSIX_ACL_MSG_EACCES)` to allocate the component message ID used when permission checks fail.

Control flow: `posix-acl.c` includes this header and logs denied access through `gf_msg(..., POSIX_ACL_MSG_EACCES, ...)`.

State and persistence: no runtime state. Message IDs are a persistence contract for log analysis and must not be removed or reused.

Dependencies and integration points: depends on `glusterfs/glfs-message-id.h` and the global component registry. Integrates POSIX ACL logs with Gluster's structured logging system.

Risks and test signals: changing IDs or component names can break log parsers and documented diagnostics. Test signals are build-time message ID generation and runtime EACCES logs that include the expected POSIX ACL message identifier.
