# sources/distributed-fs/ceph-client/net/ceph/auth_none.h

## Purpose
Declares private types and initializer for the auth-none backend.

## Important APIs, Types, and Functions
`struct ceph_none_authorizer` wraps `struct ceph_authorizer`, a 128-byte encoded buffer, and its length. `struct ceph_auth_none_info` stores the backend `starting` flag. `ceph_auth_none_init()` is the initializer consumed by `auth.c`.

## Control Flow
The header has no executable flow. It defines the data layout used by `auth_none.c` to create authorizers and track monitor-auth progress.

## State and Persistence
No standalone state. The declared structs are allocated by `auth_none.c` for each auth client and authorizer.

## Dependencies and Integration Points
Includes Ceph generic auth declarations and slab helpers. It is private to the libceph auth implementation, not a UAPI header.

## Risks
Changing the fixed buffer size or struct layout requires checking `ceph_auth_none_build_authorizer()` bounds and all authorizer users. The header comment accurately states this is null security mode, so callers must not infer confidentiality or integrity from it.

## Test Signals
Compile coverage with `auth_none.c`, authorizer buffer-size tests, and backend init/destroy tests that verify `ac->private` lifetime.
