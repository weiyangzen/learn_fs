# sources/compression/xz/src/liblzma/simple/simple_coder.c

## Purpose
Implements the common wrapper for BCJ/simple filters, handling filter-chain integration, buffering of unfiltered tails, start offsets, finish behavior, and memory ownership.

## Important APIs, Types, And Functions
- `copy_or_code()` either copies input directly or calls the next filter to provide data.
- `call_filter()` invokes the architecture-specific filter and advances `now_pos`.
- `simple_code()` is the main filter-chain callback.
- `simple_coder_end()` frees next coder, filter-specific state, and wrapper.
- `simple_coder_update()` forwards unsupported updates to the next filter.
- `lzma_simple_coder_init()` allocates/configures the wrapper and initializes the next filter.

## Control Flow
`simple_code()` rejects `LZMA_SYNC_FLUSH`. It first flushes already filtered bytes from the internal buffer. If output has enough room, it copies any buffered tail to output, gets more data from input or the next coder, filters the new output range in place, and copies any unfiltered tail back into the internal buffer. If buffered data remains, it compacts/fills the internal buffer, filters as much as possible, treats all remaining data as filtered at end-of-stream, and flushes to output. It returns `LZMA_STREAM_END` only after the next/end condition is reached and all buffered data is emitted.

## State And Persistence
Persistent wrapper state includes next coder, `end_was_reached`, direction flag, filter callback, optional filter-specific state, `now_pos`, allocated buffer size, buffer flush position, filtered boundary, current buffer size, and flexible buffer contents. Tail bytes that cannot yet be filtered are persisted across calls.

## Dependencies And Integration Points
Includes `simple_private.h`. Called by every architecture-specific simple filter init with its callback, private-state size, maximum unfiltered tail, required alignment, and direction.

## Risks
Buffer pointer arithmetic must avoid undefined behavior when `out == NULL`; the code includes explicit checks. `unfiltered <= allocated/2` depends on filter callbacks returning conservative filtered sizes. No sync flush support may surprise filter-chain users. Allocation of `simple` after wrapper allocation can leak wrapper if not cleaned by caller on error unless higher-level init handles it. Alignment validation uses start offsets from options.

## Test Signals
Streaming tests with tiny input/output buffers, no next coder, next coder returning `STREAM_END`, finish behavior, unsupported sync flush, nonzero start offsets, invalid alignment, and filters with unfiltered tails. Leak tests around allocation failures are useful.
