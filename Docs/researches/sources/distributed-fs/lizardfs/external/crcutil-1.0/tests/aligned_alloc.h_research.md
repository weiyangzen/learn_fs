<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/aligned_alloc.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/aligned_alloc.h

## Purpose
Header-only aligned memory helper for crcutil tests. It gives tests a portable way to allocate a block whose returned pointer, optionally adjusted by a field offset, satisfies a power-of-two alignment requirement.

## Important APIs, Types, and Functions
Defines `crcutil::AlignedAlloc(size_t size, size_t field_offset, size_t align, const void **allocated_mem)` and `crcutil::AlignedFree(void *aligned_memory)`. `AlignedAlloc` stores the original `new char[]` pointer immediately before the aligned pointer and optionally returns that original allocation through `allocated_mem`.

## Control Flow, State, and Persistence
Invalid alignment values are coerced to pointer-size alignment. Allocation over-allocates by `align - 1 + sizeof(*allocated_mem)`, advances past the hidden storage pointer, adjusts for `field_offset`, stores the raw pointer at index `-1`, and returns the aligned address. State is only heap memory and the hidden back-pointer; `AlignedFree` retrieves it and deletes the raw array.

## Dependencies and Integration Points
Depends on crcutil `std_headers.h` for size types and is used by crcutil unit/performance tests that need 16/128/256-byte placement for SSE and table-aligned objects.

## Risks and Test Signals
Risks include callers freeing with `delete[]` instead of `AlignedFree`, field-offset alignment misunderstandings, assumptions that `sizeof(char *)` equals the desired minimum pointer storage alignment, and overflow if enormous `size` plus padding wraps. Test signals are alignment checks for several powers of two and offsets, invalid alignment fallback, null-safe `AlignedFree`, and valgrind/ASan leak checks across repeated allocate/free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/aligned_alloc.h -->
