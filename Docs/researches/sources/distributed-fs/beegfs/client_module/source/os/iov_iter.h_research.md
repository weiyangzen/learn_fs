## sources/distributed-fs/beegfs/client_module/source/os/iov_iter.h

**Purpose:** Provides kernel-version shims and BeeGFS convenience helpers for `iov_iter` use, plus the `BeeGFS_ReadSink` structure declaration.

**Important APIs/types/functions:** Defines iterator feature requirements, shims for `iter_iov_addr`, `iter_iov_len`, `iov_iter_type`, `iov_iter_is_pipe`, wrappers `BEEGFS_IOV_ITER_KVEC` and `BEEGFS_IOV_ITER_BVEC`, stack allocation macros `STACK_ALLOC_BEEGFS_ITER_IOV`/`KVEC`, and internal initializer helpers.

**Control flow:** Callers create one-segment user or kernel iterators through stack macros, inspect iterator type/count/segments through wrappers, and use `BeeGFS_ReadSink` for pipe-safe reads. The direction/type flag handling adapts kernels that include or exclude iterator type flags in the direction parameter.

**State and persistence behavior:** The header defines transient iterator construction only. `BeeGFS_ReadSink` contains temporary page/bvec arrays and a sanitized iterator, managed by functions in `iov_iter.c`.

**Dependencies and integration points:** Required by remoting read/write wrappers and storage commkit code. It depends on kernel uio/uaccess/bvec APIs and BeeGFS feature macros.

**Risks:** The stack macros return pointers to compound literals and must be used only within the full expression/scope where those literals live. Compile-time `#error` guards intentionally reject kernels lacking required iterator features. Direction/type flag compatibility is subtle across kernel releases.

**Test signals:** Build on supported kernels before and after iterator API changes, run stack-macro read/write wrapper tests, pipe read tests, and static analysis for escaping stack iterator pointers.
