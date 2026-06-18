# sources/distributed-fs/ceph-client/include/linux/assoc_array_priv.h

## Purpose
Defines private node, shortcut, edit, and pointer-tagging internals for the generic associative-array implementation.

## Important APIs, Types, And Functions
Constants define a 16-way fanout, fan masks, level step, and key chunk masks. `struct assoc_array_node` stores back pointer, parent slot, 16 tagged slots, and branch leaf count. `struct assoc_array_shortcut` compresses shared key prefixes. `struct assoc_array_edit` carries preallocated metadata, excised subtrees, count adjustments, parent-slot updates, and pointer assignments. Tagged-pointer helpers distinguish leaf/meta, node/shortcut, strip tags, and create tagged leaf/node/shortcut pointers.

## Control Flow, State, And Persistence
The implementation navigates an N-way tree by key segments. Metadata pointers use low bits as tags, so nodes and shortcuts can be identified without dereferencing. Edits stage multiple structural mutations and count adjustments before committing to the persistent tree.

## Dependencies And Integration Points
Depends on `linux/assoc_array.h` and `CONFIG_ASSOCIATIVE_ARRAY`. Integrated only by the associative-array implementation; public consumers should not rely on these internals.

## Risks And Test Signals
Pointer tagging assumes alignment leaves low bits free. Incorrect tag stripping or shortcut level math can corrupt the tree. Tests should stress shared-prefix keys, branch splits, shortcut insertion/removal, RCU freeing, GC excision, and sanitizer coverage for misaligned or stale pointers.
