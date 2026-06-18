<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/reed_solomon_unittest.cc

## Purpose
Tests Reed-Solomon encoding/recovery correctness, zero-input optimization, performance benchmarks, and matrix invertibility. The source was read completely for this report.

## Important APIs, Types, And Functions
Helpers generate deterministic pseudo-random data, encode parity, recover erased parts, benchmark throughput, and test matrix invertibility through `gf_invert_matrix`.

## Control Flow
Correctness tests erase data and parity combinations and compare recovered buffers to originals. Benchmark tests run small and large encodes. Matrix tests enumerate erasure combinations for m=1..4 within supported ranges.

## State And Persistence Behavior
No persistence; tests allocate large in-memory buffers, including 64 MiB benchmark data.

## Dependencies And Integration Points
Depends on gtest, `reed_solomon.h`, `slice_traits.h`, and `time_utils.h`.

## Risks And Edge Cases
Benchmark tests can be heavy for regular unit runs. Matrix tests skip m=4 for k>20 in the RS matrix branch.

## Test Signals
Passing tests are strong signals for normal EC recovery and generator-matrix invertibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon_unittest.cc -->
