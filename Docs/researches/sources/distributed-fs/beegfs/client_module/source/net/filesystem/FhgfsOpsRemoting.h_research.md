## sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsRemoting.h

**Purpose:** Declares the BeeGFS client remoting API used by filesystem/VFS code to perform metadata RPCs and storage IO. It also provides small inline wrappers that adapt raw user or kernel buffers into `iov_iter` objects.

**Important APIs/types/functions:** Defines `enum Fhgfs_RWType`, `struct FileOpVecState`, `union RWFileVecState`, lifecycle functions for message-buffer caches, metadata operations, open/close/locking APIs, vector/page IO APIs, xattr APIs, lookup-intent/hardlink/refresh/version/file-state APIs, and the internal lock helper `__FhgfsOpsRemoting_flockGenericEx`. Inline helpers include `FhgfsOpsRemoting_writefile`, `writefile_kernel`, `readfile_user`, `readfile_kernel`, and `statDirect`.

**Control flow:** Callers include this header, initialize a `RemotingIOInfo`, and then call public remoting functions. The inline read/write wrappers allocate stack-local `iov_iter`/`iovec` or `kvec` compound literals through `STACK_ALLOC_BEEGFS_ITER_*`, then delegate to `readfileVec`/`writefileVec`.

**State and persistence behavior:** The header itself owns no state. It exposes state-bearing structures from `RemotingIOInfo`, `FileOpState`, and page-vector helpers. Persistent filesystem effects occur in the `.c` implementation through remote RPCs.

**Dependencies and integration points:** Includes BeeGFS filesystem info types, storage definitions/errors, `MetadataTk`, `FileEvent`, commkit declarations, `RemotingIOInfo`, `os/iov_iter.h`, and page-vector wrappers. It is a central interface between VFS operation files and network/storage layers.

**Risks:** The header contains both a `static inline` declaration and an `extern` declaration for `FhgfsOpsRemoting_statDirect`, which is unusual but used to publish the inline definition. Stack iterator wrappers rely on compound-literal lifetime staying within the call expression. The internal `__FhgfsOpsRemoting_flockGenericEx` is exposed to allow specialized callers but is easy to misuse because ack IDs and initialized message types must match.

**Test signals:** Compile all remoting callers across supported kernel versions, validate user/kernel buffer wrappers for read/write paths, and check that every declared RPC has exactly one compatible implementation and expected response type.
