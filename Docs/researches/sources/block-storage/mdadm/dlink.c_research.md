# File Research: sources/block-storage/mdadm/dlink.c

## Purpose
`dlink.c` implements a small intrusive-style doubly linked list allocation helper used by mdadm parsers.

## Behavior
`dl_alloc()` allocates hidden prev/next header space before the returned payload. `dl_head()` creates a circular sentinel. `dl_init()` initializes a payload as a circular list node. `dl_insert()` inserts after the head; `dl_add()` appends before the head; `dl_del()` unlinks a node and nulls its links. `dl_free()` frees the hidden allocation, and `dl_free_all()` frees a whole list. `dl_strdup()` and `dl_strndup()` allocate string payload nodes.

## Integration Notes
The config parser uses these lists to represent logical lines and words. Allocation uses mdadm's `xcalloc()`.

## Risks
The API relies on callers passing pointers returned by `dl_alloc`/`dl_strdup`, because metadata lives immediately before the payload pointer. Passing ordinary memory corrupts/free-invalid memory.
