# sources/distributed-fs/openafs/src/afs/UKERNEL/sysincludes.h

## Purpose

`sysincludes.h` is the central UKERNEL compatibility header. It includes user-space system headers, renames kernel structure names to `usr_*`, defines kernel constants and macros, and declares user-space replacements for vnode, VFS, uio, credential, network-interface, and directory types.

## Important APIs, Types, and Functions

Key macro groups include kernel-to-user renames (`vnode` to `usr_vnode`, `vfs` to `usr_vfs`, `vattr` to `usr_vattr`, `uio` to `usr_uio`, `crget` to `usr_crget`), vnode/file constants (`VREG`, `VDIR`, `VLNK`, `FREAD`, `FWRITE`, `FTRUNC`, `LOCK_*`, `UIO_*`, buffer flags), copy helpers (`copyin`, `copyout`, `copyinstr`, `copyoutstr`), thread helpers (`usr_thread_create`, `usr_thread_sleep`), assertion/panic helpers, and vnode reference macros `VN_HOLD` and `VN_RELE`.

Important structs are `usr_statfs`, `usr_vattr`, `usr_vnode`, `usr_inode`, `usr_fileops`, `usr_file`, `usr_flock`, `usr_proc`, `usr_uio`, `usr_buf`, `usr_vnodeops`, `usr_fs`, `usr_mount`, `usr_vfsops`, `usr_vfs`, network-interface structs, `min_direct`, `usr_ucred`, `usr_user`, `usr_dirent`, and `usr_DIR`.

## Control Flow

Most content is compile-time adaptation. Runtime behavior appears in inline/macros: `panic` prints and asserts; `usr_thread_create` initializes pthread attributes, sets a fixed stack size, starts a thread, and destroys attributes; `usr_thread_sleep` calculates an absolute timeout and waits on a shared condition; `VN_RELE` asserts the AFS global lock, decrements the vnode count, and calls `afs_inactive` at zero.

## State and Persistence Behavior

The header declares global sleep primitives, network-interface lists, `usr_rx_port`, credential/user accessors, and file helpers. It stores no persistent data itself. `usr_user` and `usr_ucred` define the in-memory identity state that drives request creation and PAG/token behavior.

## Dependencies and Integration Points

This file must be included before OpenAFS internals that expect kernel types. It integrates with `afs_usrops.c` implementations of credentials, per-thread user state, sleep, and file operations, plus `osi_machdep.h` current-credential macros.

## Risks and Edge Cases

- Heavy macro renaming can cause surprising symbol substitutions and include-order sensitivity.
- `pid_t` is redefined to `int`, and `getpid()` is mapped to a pthread-derived value, which changes process identity semantics.
- `VN_RELE` requires the AFS global lock and calls into inactive cleanup from a macro.
- `usr_thread_create` uses a fixed stack size, which may be insufficient for deep call paths or excessive for many worker threads.
- Several kernel constants are simplified and may not match every host platform's values.

## Test Signals

The most valuable tests are cross-platform UKERNEL builds, compile checks for struct layout assumptions, thread creation/sleep tests, vnode refcount/inactive tests, credential copy/free tests, and integration tests that include system and OpenAFS headers in the same order as production.
