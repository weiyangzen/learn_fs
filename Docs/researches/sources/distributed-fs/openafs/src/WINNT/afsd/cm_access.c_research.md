# sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.c

## Purpose
`cm_access.c` decides whether cached access-right information is sufficient for a user/scache request and forces status/callback fetches when it is not. It bridges public directory rights, per-user ACL cache entries from `cm_aclent.c`, Unix mode bits, DFS/per-file access policy, and callback validity.

## Important APIs And State
The exported functions are `cm_HaveAccessRights` and `cm_GetAccessRights`. Globals are `cm_deleteReadOnly`, which controls whether SMB delete is removed for read-only mode bits, and `cm_accessPerFileCheck`, which forces rights checks on the file itself instead of parent directory ACLs. Rights come from `scp->anyAccess`, per-user `cm_FindACLCache`, Unix mode bits, creator identity, and AFS PRSFS bits.

## Control Flow
`cm_HaveAccessRights` is called with the target scache write-locked and must not block on expensive fetches. It chooses the ACL scache: directories, per-file-check mode, DFS volumes, and missing volumes use the file itself; normal files use the parent directory. If the parent scache is not available or lacks a callback, it returns false so callers can stabilize and fetch. Once it has an ACL scache, it grants immediately when requested rights are covered by public `anyAccess`; otherwise it checks the per-user ACL cache. It then masks READ/WRITE/DELETE based on Unix mode bits, grants READ/WRITE when the creator has INSERT, implies LOCK from WRITE, and returns whether the answer is authoritative.

`cm_GetAccessRights` performs the blocking side. For directories/per-file/DFS cases it forces callback and status on the target. For normal files it releases the target lock, obtains the parent scache, forces callback/status on the parent, releases it, and reacquires the target lock.

## Dependencies And Integration
This file depends on scache, volume, ACL cache, callbacks, sync operations, request flags, logging, and AFS rights constants. It is called from scache/status and ioctl paths before deciding whether server RPCs are needed.

## Risks And Test Signals
The main risks are lock ordering around parent scache acquisition, stale callback use, races noted by comments, and subtle rights masking that can over- or under-grant local operations before server validation. Test signals include directory versus file checks, parent scache unavailable, callback revoked during checks, DFS volume behavior, `cm_accessPerFileCheck`, read-only delete policy for SMB, creator-with-insert behavior, write implying lock, and retry loops around `cm_GetAccessRights`.
