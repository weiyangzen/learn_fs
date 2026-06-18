# sources/distributed-fs/ipfs-kubo/client/rpc/errors_test.go

## Purpose
This test file validates RPC not-found error reconstruction and compatibility with `ipld.IsNotFound`.

## Important APIs, Types, And Functions
`doParseIpldNotFoundTest` compares original and rebuilt messages and `ipld.IsNotFound` behavior. `TestParseIPLDNotFound` builds valid and invalid IPLD not-found variants. `TestBlockstoreNotFoundMatchingIPLDErrNotFound` checks blockstore text compatibility.

## Control Flow
Tests iterate multiple wrapping formats, CID break characters, CIDv0/CIDv1/base encodings, undefined CIDs, invalid CIDs, and unrelated errors.

## State And Persistence Behavior
No persistent state; all tests are pure functions.

## Dependencies And Integration Points
It integrates Go error wrapping, CID/multibase/multihash libraries, and the RPC error parser.

## Risks And Test Signals
Risks are that tests mirror current parser assumptions and may miss future API error variants. Signals are exact message preservation and matching `ipld.IsNotFound` results.
