# sources/distributed-fs/beegfs-go/common/beegfs/entry.go

## Purpose
`entry.go` defines BeeGFS file-entry and file-state constants used by protocol, CLI, and storage workflows.

## APIs and Control Flow
`EntryType` models directory, regular file, symlink, device, FIFO, and socket entries; `IsFile` treats all non-directory concrete entry types as files. `StripePatternType` formats RAID and buddy mirror patterns. `EntryFeatureFlags` exposes bit checks and setters for inlined and buddy-mirrored entries. `FileState` packs lower five-bit `AccessFlags` and upper three-bit `DataState`, with helpers to construct, inspect, stringify, and return modified copies with new data or access states.

## State, Dependencies, and Integration
All values are small integer/bitfield types with no external persistence beyond protocol or metadata use. The file references C++ BeeGFS definitions in comments, making cross-language numeric compatibility important.

## Risks and Test Signals
`WithoutAccessState` appears to preserve the data-state bits and clear all access bits with `&^ AccessFlagMask`, ignoring the `flags` argument; if intended to clear only specified flags, this is a behavioral bug. Tests cover `EntryType.IsFile` and feature flag setters, but not `FileState` packing or access-state mutation.
