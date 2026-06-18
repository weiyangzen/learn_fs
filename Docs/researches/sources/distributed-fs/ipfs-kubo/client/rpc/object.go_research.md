# sources/distributed-fs/ipfs-kubo/client/rpc/object.go

## Purpose
This file implements legacy object patch and diff operations over HTTP RPC.

## Important APIs, Types, And Functions
`ObjectAPI` exposes `AddLink`, `RmLink`, and `Diff`. `objectOut` carries returned hashes, and `change` maps JSON diff entries to `iface.ObjectChange`.

## Control Flow
Patch methods call `object/patch/add-link` or `object/patch/rm-link`, pass UnixFS validation options, parse returned hashes, and return immutable paths. `Diff` calls `object/diff`, then maps before/after CIDs to immutable paths when defined.

## State And Persistence Behavior
Patch methods create new DAG objects in the remote repo. Diff is read-only.

## Dependencies And Integration Points
It integrates legacy object commands, coreiface object options, CIDs, and path wrappers.

## Risks And Test Signals
Risks include legacy object API drift, UnixFS validation option mismatch, and undefined CID handling in diffs. Signals are object link add/remove/diff CoreAPI tests.
