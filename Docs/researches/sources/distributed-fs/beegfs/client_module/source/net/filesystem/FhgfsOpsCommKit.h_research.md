# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.h

## Purpose
Defines the generic communication-kit public interface and shared per-operation state structures for storage reads, writes, fsync, and stat-storage requests.

## Important APIs and Types
Public APIs initialize/release emergency pools, run generic communication, invoke read/write/fsync/stat-storage communication, and initialize file/fsync/stat-storage state. `CommKitState` enumerates state-machine phases. `CommKitTargetInfo` is the base state for each target. `FileOpState`, `FsyncContext`, `FsyncState`, and `StatStorageState` extend it with operation-specific fields.

## Control Flow
Callers allocate operation states, initialize them, link them into lists, and pass them to the operation-specific communicate wrapper. The driver in `FhgfsOpsCommKit.c` mutates `state`, `nodeResult`, socket/node/header fields, and operation-specific counters.

## State and Persistence
All structs are per I/O request except the emergency pools declared by API. `FileOpState` owns data iterators, offsets, transfer counters, session-check flags, expected result, and optional RDMA mapping pointer. `FsyncContext` stores flags that decide whether a remote fsync message is needed.

## Dependencies and Integration Points
Includes `PathInfo`, optional `RdmaInfo`, iov iterator compatibility, and common comm-kit context definitions. Used by remoting and storage I/O code to communicate with chunk targets.

## Risks
The base struct must remain first in derived states used with `container_of`. Callers must keep state lists alive until communication completes. `nodeResult` uses negative BeeGFS error conventions, which differ from Linux errno.

## Test Signals
Compile call sites, initialize states for single and multi-target operations, verify list linkage, result interpretation, RDMA-enabled builds, and session-check flag propagation.
