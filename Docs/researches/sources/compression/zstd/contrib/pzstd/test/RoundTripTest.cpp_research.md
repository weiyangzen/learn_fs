<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/RoundTripTest.cpp -->
# sources/compression/zstd/contrib/pzstd/test/RoundTripTest.cpp

## Purpose
This standalone randomized round-trip test exercises pzstd with generated inputs and option combinations.

## Important APIs, Types, And Functions
It defines generator helpers for input files and options, then `main` runs repeated round trips.

## Control Flow
The test generates input content, constructs pzstd options with varied compression settings/thread counts, calls the shared round-trip helper, and exits nonzero on failure.

## State And Persistence
Temporary input, compressed, and decompressed files are created during runs. Persistent state is limited to test artifacts if cleanup fails.

## Dependencies And Integration Points
It depends on `RoundTrip.h`, pzstd engine code, and standard random/file utilities. It complements deterministic GoogleTest cases.

## Risks
Randomized coverage can be nondeterministic if seed behavior changes. It may miss edge cases unless configured for enough iterations and sizes.

## Test Signals
Successful runs provide broad losslessness evidence across generated file contents.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/RoundTripTest.cpp -->
