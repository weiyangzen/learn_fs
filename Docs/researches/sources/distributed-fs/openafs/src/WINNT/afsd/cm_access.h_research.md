# sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.h

## Purpose
`cm_access.h` declares the cache-manager access-right API used by scache and request handling code. It exposes the nonblocking cached-rights check, the blocking fetch path, and the per-file access-check configuration flag.

## APIs And Integration
`cm_HaveAccessRights(struct cm_scache *scp, struct cm_user *up, struct cm_req *reqp, afs_uint32 rights, afs_uint32 *outRights)` reports whether local cache state can answer a rights question and returns the rights found. `cm_GetAccessRights(struct cm_scache *scp, struct cm_user *up, struct cm_req *reqp)` forces the status/callback work needed to populate rights. `cm_accessPerFileCheck` is externally configured, read by `cm_access.c`, and also consulted by other cache-manager modules.

## State, Risks, And Test Signals
The header depends on `cm_user.h` for user/request type visibility and forward-visible scache declarations. Risks are mostly contract-related: callers must hold the scache lock as required by the implementation and loop around races where cached rights cannot be stabilized. Test signals are compile coverage, callers respecting lock preconditions, and runtime behavior with `cm_accessPerFileCheck` toggled.
