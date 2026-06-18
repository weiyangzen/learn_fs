# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsDir.h

**Purpose:** Provides the small public interface for BeeGFS dentry operations and dentry-to-path buffer resolution. It lets other filesystem components attach BeeGFS revalidation/delete behavior to dentries and resolve raw paths using the mount's no-allocation buffer store.

**Important APIs/types/functions:** Exports `fhgfs_dentry_ops`, a `struct dentry_operations` defined in `FhgfsOpsDir.c`, and `__FhgfsOps_pathResolveToStoreBuf(NoAllocBufferStore*, struct dentry*, char**)`, which returns either a path pointer inside the acquired store buffer or an `ERR_PTR` while setting `*outStoreBuf` to NULL on failure.

**Control flow:** Callers include this header when they need to set `d_op` on dentries obtained from lookup/NFS export paths or when they need a temporary path string without dynamic allocation. The path helper's contract requires callers to return the buffer to `NoAllocBufferStore` after successful use.

**State and persistence behavior:** The header owns no state. It exposes operations that manipulate Linux dcache state and borrow buffers from `NoAllocBufferStore`.

**Dependencies and integration points:** Depends on Linux `dcache.h` and BeeGFS `NoAllocBufferStore`. Included by export and other filesystem operation files that need `fhgfs_dentry_ops`.

**Risks:** The path helper uses a borrowed fixed-size buffer and can return `-ENAMETOOLONG`. Its implementation warns against taking two buffers in the same thread because the store can deadlock under pressure.

**Test signals:** Compile users across kernel versions, verify dentries receive BeeGFS ops when needed, and test path helper success, long-path failure, and buffer-return discipline.
