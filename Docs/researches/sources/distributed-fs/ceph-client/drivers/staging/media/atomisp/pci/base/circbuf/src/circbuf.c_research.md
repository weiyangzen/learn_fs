# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/src/circbuf.c

Purpose: implements non-inline CSS circular-buffer operations: create/destroy, pop, arbitrary extraction, peeking, and size growth.

Important APIs/types/functions: public functions are `ia_css_circbuf_create()`, `ia_css_circbuf_destroy()`, `ia_css_circbuf_pop()`, `ia_css_circbuf_extract()`, `ia_css_circbuf_peek()`, `ia_css_circbuf_peek_from_start()`, and `ia_css_circbuf_increase_size()`. Internal helpers are `ia_css_circbuf_read()`, `ia_css_circbuf_shift_chunk()`, and `ia_css_circbuf_elem_get_val()`.

Control flow: create resets descriptor positions and clears all elements. Pop asserts non-empty, reads and clears `start`, then advances it. Extract pops offset zero, returns zero for offsets beyond current occupancy, otherwise reads a target element and shifts older elements toward the hole before adjusting `start`. Growth validates `u8` size addition, optionally appends new elements, and fixes wrapped `end`/`start` placement.

State and persistence: mutates only caller-owned descriptor and element array. Destroy nulls pointers but does not free storage.

Dependencies and integration: built on the inline descriptor/ring API and CSS assertion support. It serves CSS firmware-side queue logic such as taggers.

Risks and test signals: no locking is provided. `extract()` does not explicitly reject negative offsets, so modular offset behavior can expose unexpected positions. Growth assumes preallocated storage and has a FIXME-like comment about maximum size. Unit tests should cover invalid offsets, wrapped extraction, growth when `end < start`, element clearing, and caller-managed storage lifetime.
