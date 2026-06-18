# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsExport.h

**Purpose:** Declares BeeGFS NFS export support and the packed handle formats used by `FhgfsOpsExport.c`. The header is compiled only for kernels new enough to support exportfs operations.

**Important APIs/types/functions:** Exports `fhgfs_export_ops`, `FhgfsOpsExport_encodeNfsFileHandle` with kernel-version-dependent signature, `FhgfsOpsExport_nfsFileHandleToDentry`, `FhgfsOpsExport_nfsFileHandleToParent`, `FhgfsOpsExport_getName`, `FhgfsOpsExport_getParentDentry`, and internal helpers for handle lookup and entry-ID parse/rebuild. It defines packed `FhgfsNfsFileHandleV1`, `FhgfsNfsFileHandleV2`, and `FhgfsNfsFileHandleV3`. V1 stores parent/entry ID components, owner node, and entry type. V2 adds parent owner node. V3 changes owner fields to `NumNodeID` and adds `isBuddyMirrored`.

**Control flow:** NFS/exportfs callers receive function pointers through `fhgfs_export_ops`; encode/decode paths exchange one of the packed handle structures through Linux `fid` buffers. The V3 structure is the current full-fidelity format; V1/V2 remain decode-compatible.

**State and persistence behavior:** These packed structures are persistent file-handle ABI for NFS clients. Field layout and handle type values must remain backward-compatible. The header does not own runtime state, but its structs determine what identity survives across NFS handle encode/decode cycles.

**Dependencies and integration points:** Depends on `common/Common.h` for kernel version macros and `linux/exportfs.h`. It is included by export implementation and any code needing export operation declarations.

**Risks:** Packed ABI changes can invalidate existing NFS file handles. V1/V2 contain 16-bit owner/node fields while V3 uses `NumNodeID`; conversion must preserve legacy semantics. The header exposes internal helper declarations, so accidental external use could couple code to handle internals.

**Test signals:** Compile with kernels before/after `KERNEL_HAS_ENCODE_FH_INODE`, verify struct sizes and packed layout expectations, and run NFS export handle compatibility tests for V1, V2, and V3 buffers.
