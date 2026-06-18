# sources/distributed-fs/ipfs-kubo/core/commands/pin/pin.go

## Purpose

`pin/pin.go` implements local pin management: adding, removing, listing, updating, and verifying pins. It protects local DAGs from garbage collection and integrates with Kubo's fast-provide behavior so newly pinned content can be announced.

## Important APIs, Types, and Functions

`PinCmd` registers `add`, `rm`, `ls`, `verify`, `update`, and `remote`. Output types include `PinOutput`, `AddPinOutput`, `PinLsOutputWrapper`, `PinLsList`, `PinLsType`, `PinLsObject`, `PinVerifyRes`, `PinStatus`, and `BadNode`. Helpers include `pinAddMany`, `resolveFastProvideFlags`, `fastProvideAfterPin`, `pinLsKeys`, `pinLsAll`, `pinVerify`, and `PinVerifyRes.Format`.

## Control Flow

`pin add` validates optional pin name, resolves each path to an immutable root, and calls `api.Pin().Add` as recursive or direct. With `--progress`, it wraps the context in a DAG progress tracker, runs pinning in a goroutine, and emits periodic progress before final pins. After success it may fast-provide the root or whole DAG using config defaults and explicit flags. `pin rm` resolves inputs and removes pins. `pin ls` validates pin type/name filters, then either checks specific arguments through the pinner or streams all pins through CoreAPI; non-stream mode accumulates a legacy map. `pin update` resolves old and new paths, calls `api.Pin().Update`, optionally unpins the old root, and fast-provides the new root. `pin verify` walks recursive pin DAGs with a validating blockstore, detecting missing/corrupt blocks and optionally outputting OK pins.

## State and Persistence Behavior

Pin add/rm/update mutate the local pinning service and therefore GC reachability. Verify is normally read-only. Fast-provide affects provider queues/network advertisement but not pin state. Listing is read-only and may be expensive with names or indirect pins.

## Dependencies and Integration Points

Dependencies include CoreAPI pin/path/DAG APIs, Boxo pinner, blockstore, offline blockservice, merkledag, CID validation, config fast-provide settings, cmdenv provider helpers, and command utilities. `remotePinCmd` is wired in from `remotepin.go`.

## Risks and Test Signals

Risks include progress goroutine cancellation, name validation, pin list memory growth in non-stream mode, pin verify duplicate implementation drift from CoreAPI, and fast-provide errors being best-effort/log-only. Tests should cover recursive/direct add/rm/update, named pins, stream/non-stream listing, type and name filters, indirect pin reporting, progress output, invalid names/types, fast-provide flag resolution, verify broken/OK DAGs, and quiet/verbose formatting.
