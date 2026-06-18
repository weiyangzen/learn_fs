# sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs_test.go

## Purpose
Tests validation of UnixFS HAMT fanout option values.

## Important APIs, Types, and Functions
Defines `TestMaxHAMTFanoutValidation`.

## Control Flow and State
The test calls `UnixfsAddOptions(Unixfs.MaxHAMTFanout(v))` for valid powers of two from 8 through 1024 and for invalid negative, small, non-power-of-two, and oversized values. Invalid cases must include the expected error text.

## Dependencies and Integration Points
Depends on testify `require` and the UnixFS options builder.

## Risks and Test Signals
This is a narrow validation signal for sharding settings. It does not test downstream MFS/HAMT construction, but catches regressions in the option-level guardrail.
