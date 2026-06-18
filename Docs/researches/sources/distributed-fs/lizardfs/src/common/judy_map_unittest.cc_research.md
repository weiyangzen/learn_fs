<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/judy_map_unittest.cc

## Purpose
Tests the Judy-backed map facade when Judy support is enabled. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `judy_map<int,int>` and gtest across constructors, range construction, move/copy, swap, iteration, insert/erase, equality, and nth lookup.

## Control Flow
Tests fill maps, mutate entries through `operator[]`, erase by key/iterator, and compare iteration order to expected integer order.

## State And Persistence Behavior
No persistent state; tests allocate Judy arrays and rely on destructors/clear.

## Dependencies And Integration Points
Compiled only under `LIZARDFS_HAVE_JUDY`, depending on the Judy library.

## Risks And Edge Cases
Does not test custom small POD keys, exception safety, iterator `reload`, or signed negative key ordering.

## Test Signals
Passing tests signal the basic map facade works on the configured platform/Judy build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map_unittest.cc -->
