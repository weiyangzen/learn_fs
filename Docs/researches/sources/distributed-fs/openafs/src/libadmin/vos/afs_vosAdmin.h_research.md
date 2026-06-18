# sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.h

## Purpose

`afs_vosAdmin.h` is the public C API for OpenAFS VOS administration through libadmin. It defines public constants, enums, structs, callback types, and function prototypes used by test clients and other callers to manipulate volumes, partitions, fileserver address records, and VLDB entries.

## Important APIs, Types, and Functions

Important constants define maximum public sizes: partition names, volume names, volume types, replica sites, and server addresses. Public enums cover force/exclude options, volume status/type, volume read/write and time-stat buckets, VLDB entry status bits, replica-site flags, transaction attach/active/status states, restore type, online type, and message callback type.

Core structs are `vos_fileServerEntry_t`, `vos_volumeEntry_t`, `vos_partitionEntry_t`, `vos_vldbEntry_t`, and `vos_serverTransactionStatus_t`. `vos_MessageCallBack_t` lets APIs report debug/error/verbose messages, although the implementation uses it only in limited paths.

The prototype surface covers backup, partition, server, fileserver address, transaction status, VLDB, volume lifecycle, partition conversion, quota, raw volume info, and update-counter APIs.

## Control Flow

The header has no executable flow, but it defines the begin/next/done iterator contract for partitions, fileservers, transaction statuses, VLDB entries, and volumes. Callers open server handles with `vos_ServerOpen`, pass those handles to server-scoped APIs, and close them with `vos_ServerClose`.

## State and Persistence Behavior

The API surface includes many persistent mutators: volume create/delete/rename/move/release/zap/restore/quota/update-counter, VLDB entry remove/lock/unlock/site changes/sync, server sync, and fileserver address changes. Structs returned by read calls are caller-owned output values, while iterator handles are opaque heap-backed state owned by the library until done.

## Dependencies and Integration Points

The header depends on OpenAFS base/admin types, `volint.h`, system sockets, and Windows winsock when needed. It is installed as `afs/afs_vosAdmin.h` and is built into `libvosadmin.a`.

## Risks and Test Signals

Because the header is the ABI contract, risks include enum value drift, struct layout changes, and prototype/implementation mismatch. `vos_VolumeGet2` exposes raw `volintInfo`, making callers more coupled to volserver internals than the normalized `vos_volumeEntry_t` path. Compatibility tests should compile a client that calls every prototype and verify struct sizes/field expectations across supported platforms.
