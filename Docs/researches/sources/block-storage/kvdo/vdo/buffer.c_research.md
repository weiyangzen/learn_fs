# File Research: sources/block-storage/kvdo/vdo/buffer.c

## Purpose

Implements a rolling byte buffer used for marshalling data to and from storage formats.

## Main Responsibilities

- Wraps existing byte arrays or allocates owned buffers.
- Tracks processed content with `start` and `end` indices.
- Compacts consumed data when more write space is needed.
- Supports skip, rewind, clear, end reset, and content comparison.
- Gets/puts raw bytes and typed little-endian integers.
- Copies content between buffers.
- Zero-fills buffer ranges.
- Encodes/decodes booleans.

## Important Functions

- `wrap_buffer()` creates a buffer over caller-provided bytes.
- `make_buffer()` allocates owned data and wraps it.
- `free_buffer()` frees owned data if not wrapped.
- `content_length()`, `available_space()`, `uncompacted_amount()`, `buffer_used()` expose buffer state.
- `ensure_available_space()` compacts if needed.
- `compact_buffer()` moves unread data to offset 0.
- `get_bytes_from_buffer()` and `put_bytes()` are raw copy primitives.
- `get_uint*_le_from_buffer()` and `put_uint*_le_into_buffer()` handle little-endian numeric fields.

## Behavior Details

Consumed data is not physically removed until compaction. This lets callers rewind within already-consumed content when needed.

## Notable Edge Cases

- `clear_buffer()` sets `end` to full buffer length, making the entire buffer content region available for reads; it does not zero memory.
- `wrap_buffer()` asserts `content_length <= length` but proceeds to allocate the wrapper object.
- `copy_bytes()` allocates before consuming bytes and frees on read failure.
