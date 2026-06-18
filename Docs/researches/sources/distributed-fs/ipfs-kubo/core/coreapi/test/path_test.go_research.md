# sources/distributed-fs/ipfs-kubo/core/coreapi/test/path_test.go

Purpose: regression test for resolving partially missing UnixFS HAMT-sharded directories.

Important APIs/types/functions: `TestPathUnixFSHAMTPartial`.

Control flow: creates one online full-identity API node, temporarily forces HAMT sharding size to 1, builds a directory large enough for multiple HAMT levels, adds it without pinning, fetches the root DAG-PB node, removes one shard block, then attempts to resolve every child path with a one-second timeout. Errors are accepted only when the timeout context expired.

State and persistence behavior: writes test DAG blocks, removes one block through `Block().Rm`, and leaves all state in the test repo/mocknet. Restores global `uio.HAMTShardingSize` afterward.

Dependencies and integration points: exercises UnixFS add, DAG get, block remove, and CoreAPI path resolution over HAMT directories with missing blocks.

Risks: mutates a package global (`uio.HAMTShardingSize`) and must restore it; parallel execution would be unsafe, but the test is not parallel. Expected timeout behavior means it tolerates network lookup delays rather than checking a specific error type.

Test signals: protects against incorrect partial HAMT path resolution returning wrong nodes or non-timeout errors when shard blocks are missing.
