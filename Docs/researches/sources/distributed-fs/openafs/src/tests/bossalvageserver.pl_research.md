<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvageserver.pl -->
# sources/distributed-fs/openafs/src/tests/bossalvageserver.pl

## Purpose
Smoke-tests salvaging all partitions on localhost through BOS.

## Important APIs, Types, And Functions
Calls `AFS_bos_salvage("localhost", undef, undef, undef, 1, ...)` with the `all` flag.

## Control Flow
Initializes AFStools, invokes all-partition salvage, and exits on wrapper success.

## State And Persistence
May inspect/repair every server partition and write salvage logs.

## Dependencies And Integration Points
Exercises the `-all` path in `OpenAFS::bos::AFS_bos_salvage`.

## Risks And Test Signals
Potentially expensive and disruptive. Test signal is normal BOS completion output parsed by the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvageserver.pl -->
