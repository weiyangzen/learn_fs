# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyList.h

## Purpose
Defines a linked list of copied `int64_t` values for architectures where storing 64-bit integers directly in pointer slots is unsafe.

## Important APIs and control flow
`Int64CpyList_init` wraps `PointerList_init`. `append` allocates an `int64_t`, stores the value, and appends the pointer. `uninit` and `clear` free every value copy before clearing list nodes. `length` delegates to `PointerList_length`.

## State, dependencies, integration
State is a `PointerList` whose node values own heap-allocated `int64_t` copies. Serialization helpers use this list for int64 list wire formats.

## Risks and test signals
Allocation results are not checked before dereference. Tests should cover append/clear/uninit ownership and behavior on simulated allocation failure.
