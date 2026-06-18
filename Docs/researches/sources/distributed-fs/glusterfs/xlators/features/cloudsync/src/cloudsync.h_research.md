# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.h

## Purpose
Public internal header for the cloudsync translator, defining state objects and prototypes shared by manual and generated fops.

## Important APIs, types, and functions
Defines `ALIGN_SIZE`, `CS_LOCK_DOMAIN`, `cs_dlstore`, `cs_inode_ctx_t`, and plugin descriptor `cs_plugin`. Declares core helpers for local initialization, locate/execute, resume paths, inodelk unlock, write callback, common callback, object-state checks, xattr callbacks, reading auth info, inode context update/get/reset, read/truncate resume functions, remote-read postprocess, and `cs_serve_readv`.

## Control flow
Generated C includes this header to call shared helpers, while `cloudsync.c` uses it to expose manual fops and plugin-related routines.

## State and persistence behavior
`cs_inode_ctx_t` caches object state per inode and includes loc/xattr metadata. Other declared state is transient.

## Dependencies and integration points
Includes `cloudsync-common.h` and generated `cloudsync-autogen-fops.h`, binding generated and manual sources together.

## Risks and test signals
Header cycles are possible because the generated header includes `cloudsync.h` in its template. Tests should compile from a clean generated state and verify all declared helpers have definitions or are intentionally external/generated.
