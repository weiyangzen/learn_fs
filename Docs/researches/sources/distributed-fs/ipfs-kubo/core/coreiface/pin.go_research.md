# sources/distributed-fs/ipfs-kubo/core/coreiface/pin.go

## Purpose
Defines CoreAPI pinning interfaces and pin verification result contracts.

## Important APIs, Types, and Functions
Declares `Pin`, `PinStatus`, `BadPinNode`, and `PinAPI` methods `Add`, `Ls`, `IsPinned`, `Rm`, `Update`, and `Verify`.

## Control Flow and State
No implementation flow is present. The contract represents recursive, direct, and indirect pin state, optional pin names, update semantics, and streamed verification results.

## Dependencies and Integration Points
Depends on context, Boxo path, CIDs, and pin options. Implementations wrap the node pinner and are exercised by pin conformance tests.

## Risks and Test Signals
Risks include channel close/error ordering in `Ls`/`Verify`, pin type precedence, indirect reason reporting, and name preservation. Tests cover simple/recursive/direct/indirect pins, list consistency, is-pinned reasons, verification, and named pins.
