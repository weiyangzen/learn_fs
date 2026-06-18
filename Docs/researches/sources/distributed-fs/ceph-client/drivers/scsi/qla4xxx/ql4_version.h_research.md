# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_version.h

## Purpose
`ql4_version.h` is a small version header for the QLogic iSCSI HBA driver family. It defines the kernel driver version string consumed by the qla4xxx driver sources and build metadata.

## Important APIs, Types, And Functions
The only exported definition is `QLA4XXX_DRIVER_VERSION`, currently `"5.04.00-k6"`. There are no functions, types, storage objects, or control paths.

## Control Flow
This file participates through C preprocessing. Any qla4xxx source including it embeds the version literal into module information, diagnostics, or adapter reporting paths.

## State And Persistence
There is no runtime state. The version macro is compile-time state baked into the built module and persists only as part of the resulting binary.

## Dependencies And Integration Points
The header depends only on include ordering by qla4xxx sources. Its integration point is the qla4xxx driver build and any module/version display logic that refers to `QLA4XXX_DRIVER_VERSION`.

## Risks And Edge Cases
The main risk is metadata drift: updating the driver without updating this macro can mislead support tooling, logs, and user reports. Because it lacks an include guard, repeated inclusion is harmless for a macro with the same value but would warn or fail if a caller defines the macro differently first.

## Test Signals
Builds of the qla4xxx module should compile without macro redefinition warnings. Runtime checks are version-string visibility in module metadata, dmesg banner paths, or qla4xxx diagnostic output that reports `"5.04.00-k6"`.
