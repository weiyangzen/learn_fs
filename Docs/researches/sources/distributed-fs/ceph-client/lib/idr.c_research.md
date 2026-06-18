# sources/distributed-fs/ceph-client/lib/idr.c

## Purpose
`idr.c` implements two ID allocation facilities. IDR maps integer IDs to pointers using radix-tree/XArray machinery. IDA allocates integer IDs only, storing compact bitmaps or value entries in an XArray and handling its own locking.

## Important APIs, Types, and Functions
IDR exports `idr_alloc_u32()`, `idr_alloc()`, `idr_alloc_cyclic()`, `idr_remove()`, `idr_find()`, `idr_for_each()`, `idr_get_next_ul()`, `idr_get_next()`, and `idr_replace()`. IDA exports `ida_alloc_range()`, `ida_find_first_range()`, `ida_free()`, and `ida_destroy()`. IDA internals use `struct ida_bitmap`, `IDA_BITMAP_BITS`, value entries for low sparse IDs, and `XA_FREE_MARK` to find non-full chunks.

## Control Flow, State, and Persistence
IDR allocation normalizes by `idr_base`, asks `idr_get_free()` for a free radix-tree slot up to an inclusive max, stores the ID in `*nextid` before publishing the pointer, replaces the slot, and clears `IDR_FREE`. Cyclic allocation starts from `idr_next` and wraps once. Lookups and iteration use radix-tree traversal and RCU dereference rules; writers require caller synchronization. IDA allocation locks the XArray, finds a marked free chunk, sets a free bit in either a value entry or allocated bitmap, converts value entries to bitmaps when needed, clears the free mark when full, and retries through XArray allocation handling. `ida_free()` validates the bit, clears it, restores the free mark, and deletes empty entries.

## Dependencies and Integration Points
The file depends on radix tree, XArray, bitmap, spinlock/irqsave locking, slab allocation, RCU access patterns, and IDR/IDA public headers. These allocators are widely integrated with driver core, device numbering, minor numbers, handles, and kernel object indexes.

## Risks and Test Signals
Risks include IDR caller-side locking mistakes, base/end inclusive-versus-exclusive confusion, cyclic wrap behavior, pointer validity constraints for XArray entries, IDA warnings on freeing unallocated IDs, memory allocation retries under lock drop/retry paths, and signed `INT_MAX` limits. Tests should cover boundary ranges, `idr_base`, allocation failure, cyclic wrap, replace/remove/find races under documented locking, IDA value-to-bitmap conversion, full chunk marking, first-used search, freeing invalid IDs, and destroy cleanup.
