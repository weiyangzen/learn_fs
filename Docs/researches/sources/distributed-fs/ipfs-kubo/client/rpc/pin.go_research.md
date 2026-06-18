# sources/distributed-fs/ipfs-kubo/client/rpc/pin.go

## Purpose
This file implements local pin operations over the HTTP API.

## Important APIs, Types, And Functions
`PinAPI` exposes `Add`, `Ls`, `IsPinned`, `Rm`, `Update`, and `Verify`. `pin` implements `iface.Pin`; `pinVerifyRes` and `badNode` implement pin verification status interfaces.

## Control Flow
Add/remove/update map options to `pin/*` commands. `Ls` streams JSON pin entries and sends converted pins to a caller-provided channel. `IsPinned` queries `pin/ls` with a target arg and treats "is not pinned" text as a negative result. `Verify` streams verbose verification responses in a goroutine.

## State And Persistence Behavior
Add, remove, and update mutate the daemon pinset. List/is/verify read pin state and may traverse pinned DAGs.

## Dependencies And Integration Points
It integrates Kubo pin commands, coreiface pin options, streaming JSON, CID parsing, and path wrappers.

## Risks And Test Signals
Risks include brittle string matching for not-pinned errors, channel close ownership, and decode errors represented as status messages. Signals are CoreAPI pin lifecycle/list/is/verify tests.
