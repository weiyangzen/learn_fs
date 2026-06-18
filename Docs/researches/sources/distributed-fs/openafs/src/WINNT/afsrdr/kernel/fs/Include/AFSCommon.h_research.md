# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSCommon.h

## Purpose
`AFSCommon.h` is the central public header for the fs-layer compilation unit. It brings Windows kernel headers and OpenAFS shared user/redirector headers into an `extern "C"` block, includes local defines/structs/externs, and declares the cross-file API surface used by all fs modules.

## Important APIs, Control Flow, And State
The header declares driver entry/unload, auth-group APIs, B-tree helpers, communication request APIs, every major IRP dispatch handler, generic resource/completion/registry/device helpers, Fast I/O callbacks, library lifecycle APIs, RDR device APIs, trace/dump APIs, and process tracking APIs. It also declares `ZwQueryInformationProcess`, sets `AFS_KERNEL_MODE`, pulls in `ntifs.h`, `wdmsec.h`, `initguid.h`, `ntstrsafe.h`, and conditionally includes `AFSExtern.h` unless `NO_EXTERN` is defined.

## Dependencies And Integration Points
This header is the glue between the fs shim, the loadable library, shared redirector structures, user IOCTL contracts, provider contracts, and generic utility modules. It exposes the same dispatch handlers installed by `DriverEntry` and resubmitted by `AFSSubmitLibraryRequest`.

## Risks And Test Signals
Because it is broad, prototype drift between this header and implementations can break many files. Duplicate `AFSSetVolumeInfo` declaration is benign but untidy. Include order matters because `AFSDefines.h` defines GUIDs under `initguid.h`. Build tests should compile all fs modules with and without `NO_EXTERN`, verify C linkage, and catch signature mismatches across dispatch, library callback, and Fast I/O APIs.
