<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSCommon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSCommon.h

## Purpose
`AFSCommon.h` is the central kernel-mode public header for the OpenAFS Windows redirector library. It defines the common include set, imports Windows kernel and OpenAFS user/service protocol headers, exposes compatibility declarations, and declares the library's cross-module APIs for create, read, write, extent, volume, object, name, security, cleanup, service communication, worker, and utility code.

## Important APIs, Types, And Functions
The header includes `ntifs.h`, `wdmsec.h`, `ntintsafe.h`, `AFSDefines.h`, user ioctl/structure headers, redirector common headers, `AFSStructs.h`, provider definitions, and usually `AFSExtern.h`. It declares compatibility APIs such as `ZwQueryInformationProcess` and `RtlAbsoluteToSelfRelativeSD` and defines `AFS_KERNEL_MODE`.

Major API families include B-tree/name lookup helpers; driver and library lifecycle (`DriverEntry`, `AFSUnload`, `AFSInitializeLibrary`, `AFSCloseLibrary`, library device creation/removal); service communication (`AFSEnumerateDirectory`, `AFSNotifyFileCreate`, `AFSUpdateFileInformation`, pipe operations, volume/file status operations); create/open paths; extent management; cache-file I/O fanout; read/write dispatch; file information and EA operations; flush, volume, directory-control, FS/device/internal-control, shutdown, lock, cleanup, security, system-control, quota, and generic helpers; object/name invalidation and validation; name-array utilities; worker pool/queue APIs; and optional MD5 generation.

## Control Flow And Integration
`AFSCommon.h` has no executable control flow, but it establishes the call graph contract for the redirector library. A typical file operation enters through dispatch prototypes (`AFSCreate`, `AFSRead`, `AFSWrite`, `AFSSetFileInfo`, etc.), uses FCB/CCB/object structures from `AFSStructs.h`, calls service-facing request helpers for server/cache-manager state, coordinates local cache extents and cache-file I/O, and may queue asynchronous worker operations. The header's ordering matters: core defines and user protocol types are included before structures/prototypes that reference them, and `AFSExtern.h` is included unless `NO_EXTERN` is set to let defining translation units avoid duplicate extern declarations.

## State And Persistence
The header itself stores no state. It exposes APIs that operate on persistent or semi-persistent surfaces: Windows cache manager state, redirector cache-file state, OpenAFS service metadata, volume/object/dir-entry trees, FCB/CCB lifetimes, extent dirty/clean state, auth groups, network-provider connection data, and security descriptors. It also declares `AFSReferenceCacheFileObject`/`AFSReleaseCacheFileObject`, signaling shared ownership of the persistent cache file object.

## Dependencies And Integration Points
The file is Windows-kernel-specific and depends on WDK headers, OpenAFS redirector user/kernel protocol headers, C++ `extern "C"` linkage around C-style kernel functions, and all major library source files. It is the integration point between files such as `AFSWrite.cpp`, `AFSWorker.cpp`, `AFSRead.cpp`, `AFSGeneric.cpp`, `AFSNameSupport.cpp`, `AFSExtentsSupport.cpp`, `AFSIoSupport.cpp`, `AFSVolume.cpp`, and service communication modules.

## Risks And Edge Cases
Because this header is broad, prototype drift can break many translation units at once. Duplicated declarations exist, including `AFSShutdownVolumeWorker` appearing twice, and `AFSQueuePurgeObject` is declared even though no definition appears in the reviewed `AFSWorker.cpp`. Changes to include order can expose missing type dependencies. The `extern "C"` block is important for linkage stability in a C++ kernel library. Pointer ownership and locking preconditions are mostly implicit in prototypes, so callers must follow implementation-specific contracts that are not enforced by the type system.

## Test Signals
Primary signals are full Windows driver/library compilation, link coverage for every declared non-inline function, static analysis for SAL/IRQL/locking assumptions, include-order tests with and without `NO_EXTERN`, and runtime coverage of all dispatch families. Targeted compile checks should catch duplicate/stale prototypes, missing definitions such as declared worker helpers, and ABI mismatches against service/user protocol structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSCommon.h -->
