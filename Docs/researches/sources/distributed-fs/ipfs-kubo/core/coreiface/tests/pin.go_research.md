# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pin.go

## Purpose
Conformance tests for pin add/list/remove/update/verify/is-pinned behavior and pin-name handling.

## Important APIs, Types, and Functions
Defines many `TestPin*` tests, helpers `getThreeChainedNodes`, `assertPinTypes`, `assertPinCids`, `assertPinLsAllConsistency`, `assertIsPinned`, `assertNotPinned`, and `accPins`.

## Control Flow and State
Tests add UnixFS/IPLD objects, create recursive and direct pins, inspect all/direct/recursive/indirect listings, verify precedence rules, check is-pinned reasons, stream verification results, add/list/update/re-pin named pins, and ensure nondetailed lists omit names.

## Dependencies and Integration Points
Depends on Unixfs, Dag, PinAPI, pin options, CIDs, dag-cbor, and path helpers.

## Risks and Test Signals
Strong signals cover pin state precedence, indirect listing even with direct parents, duplicate handling, detailed name exposure, update name preservation, and direct pin naming. Missing-block verify failure is left as TODO because it requires lower-level node access.
