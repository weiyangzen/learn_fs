# sources/distributed-fs/ceph-client/fs/nfsd/export.h

## Purpose
`export.h` defines the public data structures and helper APIs used by NFSD export lookup, export-cache management, and NFSv4 export metadata handling.

## Important APIs, types, and functions
Important types are `struct nfsd4_fs_location`, `struct nfsd4_fs_locations`, `struct exp_flavor_info`, `struct export_stats`, `struct svc_export`, and `struct svc_expkey`. It defines limits such as `MAX_FS_LOCATIONS`, `MAX_SECINFO_LIST`, and `EX_UUID_LEN`, export convenience macros `EX_ISSYNC()`, `EX_NOHIDE()`, and `EX_WGATHER()`, and declarations for `check_xprtsec_policy()`, `check_security_flavor()`, `check_nfsd_access()`, export init/shutdown/flush helpers, request lookup helpers, `exp_rootfh()`, and `exp_pseudoroot()`. Inline `exp_put()` and `exp_get()` wrap SUNRPC cache reference management.

## Control flow
The header has no control flow of its own, but it establishes the contract used by filehandle verification, NFSv3/NFSv4 request handlers, pNFS code, and export-cache code. Callers acquire `svc_export` references through lookup helpers and release them with `exp_put()`.

## State and persistence
`svc_export` is the persistent runtime representation of an exported path: client identity, flags, fsid, anonymous uid/gid, path, UUID, NFSv4 fs_locations, secinfo flavors, pNFS layout/device map, transport security modes, export stats, and cache/workqueue fields. `svc_expkey` is the runtime mapping from client and fsid bytes to a path. Neither structure represents durable storage; userspace reconstructs cache content as needed.

## Dependencies and integration points
The header depends on SUNRPC cache headers, percpu counters, workqueues, NFS export UAPI flags, and NFSv4 definitions. It is consumed by `export.c`, filehandle verification code, NFSv4 state/layout code, and request procedure implementations.

## Risks and test signals
Risk comes from structure ownership rules: `ex_path`, `ex_client`, `ex_uuid`, `ex_fslocs`, `ex_stats`, and `ek_path` must be reference-managed consistently by cache callbacks. API test signals include balanced `exp_get()`/`exp_put()` around every lookup, stable behavior with secinfo arrays at `MAX_SECINFO_LIST`, fs_locations at `MAX_FS_LOCATIONS`, and correct counter initialization/destruction.
