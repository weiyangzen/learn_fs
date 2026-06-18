# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.c

## Purpose
Owns cleanup helpers for per-frame cloudsync state and remote-read xattr metadata.

## Important APIs, types, and functions
`cs_xattrinfo_wipe()` frees `cs_loc_xattr_t` fields attached under `local->xattrinfo.lxattr`. `cs_local_wipe()` releases copied `loc_t`, referenced `fd_t`, pending call stub, request/response dictionaries, anonymous download fd, remote path string, xattr info, and finally returns `cs_local_t` to the local mem pool.

## Control flow
Cloudsync unwind macros detach `frame->local`, unwind/destroy the stack, and call these cleanup routines. Error paths in stat checking and postprocess also depend on them to dispose partially initialized state.

## State and persistence behavior
No durable state. It manages transient ownership of refs and heap allocations stored in `cs_local_t`.

## Dependencies and integration points
Depends on GlusterFS loc/fd/dict/call-stub APIs and the cloudsync mem pool created by `cs_init`. Used by both the translator and plugin builds because plugin Makefiles compile `cloudsync-common.c` into plugin modules.

## Risks and test signals
Risks are double unrefs when callbacks reuse `dlfd`, stale `frame->local`, and leaks on partially initialized `xattrinfo`. Tests should cover unwind after failed stub creation, failed xattr extraction, remote read callback, and download failure.
