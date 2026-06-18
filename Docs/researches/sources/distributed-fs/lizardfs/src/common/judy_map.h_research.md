<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map.h -->
# sources/distributed-fs/lizardfs/src/common/judy_map.h

## Purpose
Provides a `std::map`-like wrapper around JudyL arrays for compact ordered maps with key and value types no larger than `Word_t`. The source was read completely for this report.

## Important APIs, Types, And Functions
Important types include `judy_map`, `detail::judy_pair`, `detail::judy_iterator`, iterators, `insert`, `erase`, `find`, `find_nth`, `lower_bound`, `upper_bound`, `operator[]`, `at`, `clear`, and comparison operators.

## Control Flow
Keys are converted to raw `Word_t` indices, JudyL stores mapped values, and iterators reconstruct a pair-like object with local key storage plus a reference to Judy memory. Insert uses placement construction; erase/destruction manually calls key/value destructors and deletes Judy nodes.

## State And Persistence Behavior
Owns a `Pvoid_t data_` Judy array. State is heap memory managed by Judy; no persistence. Erase partially invalidates iterators until `reload` is called.

## Dependencies And Integration Points
Requires Judy (`<Judy.h>`) and is compiled/tests guarded by `LIZARDFS_HAVE_JUDY`. Used where dense ordered integer maps benefit from Judy performance.

## Risks And Edge Cases
Raw reinterpretation means key ordering follows binary representation, not necessarily semantic ordering for signed or non-integral small types. Manual lifetime management and exception paths are high risk.

## Test Signals
`judy_map_unittest.cc` covers constructors, swap, iterators, insert/erase, equality, `at`, and `find_nth` when Judy support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/judy_map.h -->
