# File Research: sources/block-storage/kvdo/vdo/super-block.c

This file wraps the super-block codec with asynchronous metadata I/O. `struct vdo_super_block` stores a parent completion, metadata VIO, codec, and `unwriteable` flag.

Lifecycle:
- `allocate_super_block()` allocates the object, initializes the codec, and creates a metadata VIO using the codec's encoded block buffer.
- `vdo_free_super_block()` frees the VIO, codec resources, and object.

Save/load behavior:
- `vdo_save_super_block()` rejects writes if marked unwriteable or busy, encodes the super block, stores the parent, then submits metadata write with `REQ_PREFLUSH | REQ_FUA`.
- Save errors record metadata I/O errors, log failure, mark the super block unwriteable, and finish the parent to prevent later successful writes from obscuring failed growth/readonly transitions.
- `vdo_load_super_block()` allocates the wrapper and submits a metadata read; completion decodes the super block and finishes the parent.
- Read errors are recorded but still flow through decode completion, letting decode surface the final result.

`vdo_get_super_block_codec()` exposes the codec so component-state code can read/write component data.
