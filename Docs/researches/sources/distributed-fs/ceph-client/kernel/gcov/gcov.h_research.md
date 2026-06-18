# sources/distributed-fs/ceph-client/kernel/gcov/gcov.h

## Purpose
`gcov.h` defines the shared internal contract between compiler-specific gcov backends, registration code, and the debugfs exporter. It hides compiler-private `struct gcov_info` layouts while exposing uniform operations to enumerate, serialize, copy, reset, and combine coverage data.

## Important APIs, types, and functions
The header defines gcda constants `GCOV_DATA_MAGIC`, `GCOV_TAG_FUNCTION`, `GCOV_TAG_COUNTER_BASE`, and `GCOV_TAG_FOR_COUNTER()`, plus `gcov_type` sized by native word width. It forward-declares `struct gcov_info`, declares all `gcov_info_*()` operations, `convert_to_gcda()`, `gcov_event()`, `gcov_enable_events()`, `store_gcov_u32()`, `store_gcov_u64()`, and the `struct gcov_link` array used for companion file symlinks.

## Control flow
There is no runtime control flow in the header, but it defines the call graph contract: compiler constructors register `gcov_info`; generic code enumerates with `gcov_info_next()`, builds debugfs nodes through `gcov_event()`, converts objects through `convert_to_gcda()`, and duplicates/adds/resets through the compiler backend functions.

## State and persistence
The header declares shared global state `gcov_events_enabled` and `gcov_lock`, while actual state lives in backend lists and debugfs nodes. `struct gcov_link` instances identify build-tree/source-tree link targets but do not persist data.

## Dependencies and integration points
`gcov.h` includes module and type definitions and is included by GCC, Clang, base registration, and filesystem exporter code. Its opaque layout boundary is the key integration point that allows GCC and Clang to provide different in-memory metadata while sharing the same debugfs frontend.

## Risks and test signals
Risks include stale prototypes when backend APIs change, incorrect gcov constants breaking userspace parsing, and ABI drift where generic code accidentally assumes a concrete `gcov_info` layout. Test signals include building both GCC and Clang coverage configurations, sparse/compiler warnings on prototypes, and userspace gcov successfully reading generated `.gcda` files.
