# sources/distributed-fs/ipfs-kubo/core/coreiface/object.go

## Purpose
Defines dag-pb object mutation and diff contracts for CoreAPI.

## Important APIs, Types, and Functions
Defines `ChangeType` constants `DiffAdd`, `DiffRemove`, and `DiffMod`; `ObjectChange`; and `ObjectAPI` methods `New`, `Put`, `Get`, `Data`, `Links`, `Stat`, `AddLink`, `RmLink`, `AppendData`, `SetData`, and `Diff`.

## Control Flow and State
No implementation flow is present. The interface describes DAG object state transformations that create new immutable paths rather than mutating existing CIDs.

## Dependencies and Integration Points
Depends on Boxo path, IPLD links, context, readers, and object options. It is tied to dag-pb and UnixFS validation behavior in implementations.

## Risks and Test Signals
Risks include corrupting UnixFS file or HAMT shard nodes through low-level link mutation, link ordering, and diff correctness. Tests cover add/rm link validation, explicit non-UnixFS bypass, create-parent behavior, and modification diffs.
