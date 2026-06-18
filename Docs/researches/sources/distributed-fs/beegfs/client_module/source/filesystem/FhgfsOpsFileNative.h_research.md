# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFileNative.h

**Purpose:** Declares the native BeeGFS file and address-space operation tables and lifecycle functions. This is the public hook used by filesystem setup code to enable the native cache implementation from `FhgfsOpsFileNative.c`.

**Important APIs/types/functions:** Exports `fhgfs_file_native_ops`, `fhgfs_addrspace_native_ops`, `beegfs_native_init(void)`, and `beegfs_native_release(void)`. The operation tables provide VFS and page-cache callbacks; the lifecycle functions allocate/free native writeback/read-ahead resources and the remoting workqueue.

**Control flow:** Initialization code calls `beegfs_native_init` before using the native operation tables and calls `beegfs_native_release` on module teardown. Inodes configured for native cache mode can point their file/address-space operations at the exported tables.

**State and persistence behavior:** The header owns no state. It exposes global operation tables and lifecycle hooks for state managed inside the `.c` file: mempool, workqueue, and cached page-private metadata.

**Dependencies and integration points:** Depends only on Linux `fs.h` for operation-table types. Included by native implementation and cache-mode selection code.

**Risks:** Callers must respect lifecycle ordering; using native ops before successful init or after release would dereference uninitialized global infrastructure. The include guard uses a generated mixed-case identifier rather than the project’s usual filename style, but it is unique.

**Test signals:** Build native-cache configurations, verify init failure unwinds resources, verify release destroys resources once, and mount/open files with native ops enabled after initialization.
