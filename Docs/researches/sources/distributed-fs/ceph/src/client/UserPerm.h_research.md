# sources/distributed-fs/ceph/src/client/UserPerm.h

## Purpose
`UserPerm.h` packages the effective uid, gid, and supplementary groups used by client permission checks and FUSE request forwarding.

## Important APIs, Types, and Functions
`UserPerm` stores `m_uid`, `m_gid`, `gid_count`, `gids`, and `alloced_gids`. It offers default/effective identity construction, explicit identity construction, deep-copy copy constructor/assignment, move construction, destructor, `uid()`, `gid()`, `gid_in_groups()`, `get_gids()`, `init_gids()`, `shallow_copy()`, and `print()`.

## Control Flow
Default uid/gid values of `(uid_t)-1` and `(gid_t)-1` defer to `geteuid()` and `getegid()`. `init_gids()` takes ownership of an allocated group array. Copy assignment deep-copies owned or borrowed group lists; `shallow_copy()` intentionally borrows without ownership.

## State and Persistence Behavior
All state is process-local and request-scoped. The destructor releases only arrays marked as allocated by this object.

## Dependencies and Integration Points
FUSE code builds `UserPerm` from `fuse_req_ctx()` and optionally fills groups with `fuse_req_getgroups()`. ACL code calls `gid_in_groups()` to evaluate group entries.

## Risks
Ownership is subtle: constructing with a non-owned `gidlist`, then calling `init_gids()` without first releasing an owned list could leak if misused. Move assignment is absent. `print()` omits supplementary groups.

## Test Signals
Unit coverage should exercise default identity fallback, deep copy isolation, move destruction, borrowed vs owned group arrays, and group matching.
