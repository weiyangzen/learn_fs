# sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/src/lib.rs

## Purpose
This library implements the splitfdstream wire format: a sequential binary stream where chunks are either inline bytes or references to external file descriptors. It is useful for passing mostly inline metadata plus large externally supplied payloads over fd-passing transports.

## Important APIs, Types, and Functions
`MAX_INLINE_CHUNK_SIZE` caps inline chunk reads at 256 MiB. `Chunk<'a>` is `Inline(&'a [u8])` or `External(u32)`. `SplitfdstreamWriter<W>` provides `new()`, `write_inline()`, `write_external()`, and `finish()`. `SplitfdstreamReader<R>` provides `new()`, `into_inner()`, and `next_chunk()`. Test-only helpers include `ReadAtReader`, `SplitfdstreamAsRead`, and `reconstruct()`.

## Control Flow
Writers encode each inline chunk as a negative signed 64-bit little-endian prefix followed by that many bytes. Empty inline chunks are skipped. External chunks encode the fd index as a non-negative signed 64-bit little-endian prefix and carry no inline payload. Readers attempt to read an 8-byte prefix; any `UnexpectedEof` while reading the prefix is treated as clean stream end. Negative prefixes allocate/read an inline buffer after enforcing the 256 MiB maximum. Non-negative prefixes yield `Chunk::External(prefix as u32)`. Test reconstruction reads inline data directly and external data from the selected file, using `pread` wrappers so repeated references to the same fd start at offset zero each time.

## State and Persistence
Runtime state is limited to the wrapped reader/writer and the reader's reusable inline buffer. The stream format has no header, footer, checksum, or embedded external length, so external chunk size is defined by the referenced fd content as interpreted by the receiver.

## Dependencies and Integration Points
The production implementation uses only `std::io`. Test-only code uses `rustix::io::pread`, file descriptors, `tempfile`, and `proptest`. Higher layers are expected to pass the stream fd and external fds out of band; this crate only serializes references.

## Risks
Partial prefix reads return `Ok(None)`, so truncated streams shorter than 8 trailing bytes are accepted as EOF. External indexes are encoded from `u32`, but reader casts any non-negative `i64` to `u32`, so malformed prefixes above `u32::MAX` would wrap rather than error. Because external chunks contain no length, reconstruction reads whole files; callers needing subranges need a higher-level protocol. Inline chunks allocate a buffer of the declared size, bounded by 256 MiB.

## Test Signals
Tests cover empty streams, inline-only, external-only, mixed/interleaved chunks, boundary sizes, fd index zero and max u32, skipped empty inline chunks, many small chunks, alternating patterns, truncated prefix/data handling, inline limit enforcement, reconstruction with external fds, out-of-bounds external refs, large external files, repeated fd references, `into_inner()`, and property tests for arbitrary chunk sequences and read-adapter equivalence.
