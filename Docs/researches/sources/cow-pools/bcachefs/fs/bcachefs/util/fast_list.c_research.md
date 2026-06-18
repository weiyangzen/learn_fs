# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.c

This file implements fast unordered lists backed by a generic radix tree, an ID allocator, and per-CPU slot buffers.

Design:
- Items live in a `genradix` indexed by allocated integer slots.
- Slot numbers are allocated by `ida`.
- Per-CPU buffers cache free slot IDs to reduce contention.
- Adding/removing/iterating is mostly lockless except when refilling or draining per-CPU slot buffers.

Main functions:
- `fast_list_get_idx()` reserves a slot:
  - consumes a per-CPU cached slot if available
  - otherwise allocates a batch of slots with `ida`
  - preallocates the radix-tree pointer slot
- `fast_list_add()` reserves a slot and stores the item pointer.
- `fast_list_put_idx()` returns a reserved but unused slot to per-CPU cache or `ida`.
- `fast_list_remove()` clears the radix-tree item and frees the slot.
- `fast_list_exit()` frees per-CPU cached slots, warns if objects remain, destroys `ida`, and frees radix tree.
- `fast_list_init()` initializes storage and allocates per-CPU buffers.

Important invariants:
- Slot index 0 is treated as invalid/no slot.
- `fast_list_remove()` must be passed the index returned by add/get.
- Exit warns if allocated slots remain live.
- Per-CPU buffer manipulation disables local IRQs.

Research notes:
- This structure optimizes unordered membership/iteration where stable slot IDs are enough and ordering is irrelevant.
