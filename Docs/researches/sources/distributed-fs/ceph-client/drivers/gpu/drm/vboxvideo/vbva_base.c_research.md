# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbva_base.c

## Purpose

`vbva_base.c` implements the guest-side VBVA ring-buffer writer used to send graphics update records to the VirtualBox host.

## Important APIs, Types, and Functions

- `vbva_buffer_available`: computes free ring space from host `data_offset` and guest `free_offset`.
- `vbva_buffer_place_data_at`: copies data into the ring, handling wraparound.
- `vbva_buffer_flush`: submits `VBVA_FLUSH` to make the host process records.
- `vbva_write`: writes arbitrary-length record payloads, flushing and respecting partial-write threshold when space is low.
- `vbva_enable`, `vbva_disable`, and `vbva_inform_host`: initialize/reset the ring and send `VBVA_ENABLE`/disable commands.
- `vbva_buffer_begin_update` and `vbva_buffer_end_update`: reserve a record slot, mark it partial, and later mark it complete.
- `vbva_setup_buffer_context`: records each screen's ring offset and length.

## Control Flow

Hardware init sets up each buffer context and calls `vbva_enable`. During a plane damage update, KMS code calls begin, writes a `vbva_cmd_hdr`, and ends the update. Writes flush the host when record slots or data space are low, and set overflow state if progress is impossible.

## State and Persistence Behavior

Persistent shared state lives in `struct vbva_buffer`: ring offsets, record queue indices, host flags, data length, and record flags. The guest owns `free_offset` and record allocation; the host owns `data_offset` and processes completed records. `vbva_buf_ctx` tracks active record and overflow state.

## Dependencies and Integration Points

It depends on HGSMI buffer submission, VBVA channel constants, and protocol structures. `vbox_main.c` enables/disables buffers, and `vbox_mode.c` writes dirty rectangles through this API under `hw_mutex`.

## Risks and Edge Cases

- Pointer arithmetic on `const void *p` relies on compiler extensions; kernel builds allow it but changes should keep types explicit.
- Ring overflow sets `buffer_overflow` and prevents further writes until end/disable.
- Begin/end pairing is required; missing end leaves a partial record for the host.
- Space calculations assume the host updates `data_offset` coherently after flush.

## Test Signals

Unit or VM tests for ring wraparound, full record queue flushing, large writes near `partial_write_tresh`, overflow recovery, enable/disable result handling, and dirty rectangle delivery to the host.
