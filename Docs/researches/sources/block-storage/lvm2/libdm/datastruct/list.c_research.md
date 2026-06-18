# File Research: sources/block-storage/lvm2/libdm/datastruct/list.c

## Purpose
Implements libdm’s intrusive circular doubly linked list primitive.

## Main Responsibilities
- Initialize list heads as self-referential sentinels.
- Add elements at tail or head.
- Delete and move elements.
- Query list boundaries and emptiness.
- Return first/last/previous/next elements.
- Count list size by walking.
- Splice one list into another.

## Key Functions
- `dm_list_init()` sets `head->n` and `head->p` to `head`.
- `dm_list_add()` inserts before the head, effectively appending.
- `dm_list_add_h()` inserts after the head, effectively prepending.
- `dm_list_del()` unlinks an element without clearing its own pointers.
- `dm_list_move()` deletes then appends an element elsewhere.
- `dm_list_splice()` appends all elements from `head1` to `head` and reinitializes `head1`.

## Edge Cases and Invariants
- Operations assert initialized list heads where needed.
- Empty lists are represented by `head->n == head`.
- `dm_list_first()` and `dm_list_last()` return `NULL` for empty lists.
- `dm_list_splice()` is a no-op for an empty source list.
