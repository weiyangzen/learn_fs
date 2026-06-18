## sources/distributed-fs/beegfs/client_module/source/os/OsTypeConversion.h

**Purpose:** Provides inline conversions between Linux/VFS types and BeeGFS protocol/internal types for open flags, directory entry types, and file lock types.

**Important APIs/types/functions:** Defines `OsTypeConv_openFlagsOsToFhgfs`, `OsTypeConv_dirEntryTypeToOS`, and `OsTypeConv_flockTypeToFhgfs`.

**Control flow:** Open flags map `O_RDWR`, `O_WRONLY`, default read, append, truncation, direct, sync, and nonblocking to `OPENFILE_ACCESS_*` flags. Paged write-only opens are upgraded to read-write to support read-modify-write page updates. Directory entry types map BeeGFS file kinds to `DT_*`. Lock conversion maps `F_RDLCK`/`F_WRLCK`/other to shared/exclusive/unlock and sets `ENTRYLOCKTYPE_NOWAIT` when `FL_SLEEP` is absent.

**State and persistence behavior:** No state is stored; these conversions affect subsequent remote open/lock RPC semantics.

**Dependencies and integration points:** Depends on BeeGFS storage definitions, time/common helpers, Linux fs/filelock headers, and `FhgfsCommon_getFileLockType/Flags`. Used by VFS open, readdir, and lock paths before calling remoting.

**Risks:** Incorrect flag mapping changes server-side handle permissions or lock blocking behavior. The paged-mode write-only upgrade is necessary for page-cache correctness but may surprise tests expecting strict write-only handles. Unknown directory entry types intentionally return `DT_UNKNOWN`.

**Test signals:** Test all open flag combinations including paged write-only, nonblocking, direct/sync, all BeeGFS dir entry kinds, and POSIX lock conversions with/without `FL_SLEEP`.
