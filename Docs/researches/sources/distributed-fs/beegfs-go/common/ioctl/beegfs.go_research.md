<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/beegfs.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/beegfs.go

Purpose: Go translation of BeeGFS UAPI ioctl constants, command numbers, command encodings, and ABI argument structures.

Important APIs/types/functions: constants for buffer sizes and ioctl numbers, `beegfsIOCTypeID`, command variables `iocGetCfgFile`, `iocCreateFileV3`, `iocMkFileStripeHints`, `iocGetEntryInfo`, `iocPingNode`, `iocSetFileState`, `iocGetEntryInfoV2`, and unexported ABI structs such as `getCfgFileArg`, `mkFileV3Arg`, `makeFileStripeHintsArg`, `getEntryInfoArg`, `pingNodeArg`, `setFileStateArg`, and `getEntryInfoV2Arg`.

Control flow: no runtime flow beyond command variable initialization using `_ior`, `_iow`, and `_iowr` with `unsafe.Sizeof`.

State and persistence: no state, but struct layout defines the memory state exchanged with the kernel BeeGFS client.

Dependencies and integration points: depends on `structs.HostLayout` and `unsafe`; consumed by `api.go` and `createfile.go`. Must match BeeGFS client headers exactly.

Risks: any field order/type/size change can corrupt ioctl calls. Comments note architecture-sensitive ioctl bit sizes and pointer-to-uintptr concerns. `mkFileV3Arg.PrefTargetsLen` expects raw byte length; callers must provide exactly what the kernel expects.

Test signals: build-tagged ioctl integration tests exercise selected structs indirectly; no compile-time size assertions are present in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/beegfs.go -->
