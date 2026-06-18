# File Research: sources/cow-pools/nilfs-utils/lib/vector.c

## Scope

Implements a small generic resizable array used by NILFS utilities.

## APIs And Behavior

- `nilfs_vector_create()` allocates the vector object and an initial data array for a nonzero element size.
- `nilfs_vector_destroy()` releases the backing array and wrapper.
- `nilfs_vector_get_new_element()` appends one uninitialized element, enlarging capacity when needed.
- `nilfs_vector_delete_elements()` removes a contiguous range and compacts later elements with `memmove`.
- `nilfs_vector_clear()` resets the logical size and opportunistically shrinks capacity back to the initial size without clobbering `errno` on shrink failure.
- `nilfs_vector_insert_elements()` inserts a gap of uninitialized elements at an index, enlarging and shifting existing elements as required.

## State And Dependencies

The vector stores raw `void *` data with element size, capacity, and length fields declared in `vector.h`. It relies on `malloc`, `realloc`, `memmove`, `SIZE_MAX`, and local `likely`/`unlikely` helpers.

## Risks And Invariants

Capacity growth checks multiplication overflow before reallocating. Deletion with `nelems == 0` would underflow `index + nelems - 1`; callers are expected to pass a positive count. Returned element pointers are invalidated after later reallocations.
