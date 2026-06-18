<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/internal/fusemount/context.go -->
# sources/distributed-fs/ipfs-kubo/internal/fusemount/context.go

## Purpose

This internal package provides a context marker that allows the IPNS FUSE mount's own republishing path to bypass manual-publish guards in the Name API.

## Important APIs, Types, and Functions

`publishKey` is an unexported context key. `ContextWithPublish` returns a context carrying the marker. `IsPublish` checks whether the marker is present.

## Control Flow, State, and Integration

The marker is process-local context state only; it is not persisted. `fuse/ipns` uses it inside the MFS publish function before calling `Name().Publish`, while core API guard code can distinguish mount-internal publishes from user-initiated publishes.

## Dependencies, Risks, and Test Signals

Dependency is the standard `context` package. Risks include over-broad bypass if misused and a documented unresolved conflict: external `ipfs name publish` for a mounted local key can be overwritten on next mount flush. IPNS persistence tests exercise the intended bypass path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/internal/fusemount/context.go -->
