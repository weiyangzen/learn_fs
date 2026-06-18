# sources/distributed-fs/ceph-client/scripts/include/array_size.h

## Purpose
Provides a small host-tool copy of the common `ARRAY_SIZE()` macro.

## APIs, Control Flow, and State
The header defines `ARRAY_SIZE(arr)` as `sizeof(arr) / sizeof((arr)[0])` under an include guard. It has no functions, state, or runtime behavior.

## Dependencies and Integration
It is used by host tools and helper headers such as `hashtable.h` where the full kernel header stack is not available or appropriate.

## Risks and Test Signals
The macro does not reject pointers, so misuse can silently compute pointer-size ratios. Test signals are host-tool compilation and review of callers that pass actual arrays.
