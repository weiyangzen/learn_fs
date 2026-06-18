# sources/distributed-fs/ceph-client/drivers/misc/cb710/sgbuf2.c

Purpose: exports scatterlist mapping iterator helpers that read and write 32-bit words across possibly unaligned or segment-split SG buffers for CB710 child drivers.

Important APIs, types, and functions: `cb710_sg_dwiter_read_next_block()` returns the next 32-bit word, zero-padding past the end of the buffer. `cb710_sg_dwiter_write_next_block()` writes the next 32-bit word, silently discarding bytes beyond the end. Internal helpers advance `struct sg_mapping_iter`, handle end detection, and choose fast direct access versus slow byte-copy for unaligned or cross-segment words.

Control flow: read/write first tries `sg_dwiter_get_next_block()`; if at least four aligned bytes are available in the current segment, it directly dereferences the word and advances. Otherwise, slow paths copy byte fragments across SG segments using `sg_miter_next()`, update `miter->consumed`, and pad/discard incomplete tails.

State and persistence: state is entirely in the caller-provided `sg_mapping_iter`, especially `addr`, `length`, and `consumed`. No driver-global state exists.

Dependencies and integration points: depends on Linux scatterlist mapping iterators and `linux/cb710.h` exported prototypes. Child drivers can use these helpers to stream FIFO words to/from card-reader hardware while respecting SG layout.

Risks: `sg_dwiter_write_slow()` copies to `miter->addr` rather than `miter->addr + miter->consumed`, which is notable and should be checked against intended kernel version behavior. Direct word dereferences depend on CPU unaligned access support and pointer alignment. Callers must start/stop the SG mapping iterator correctly and obey its context constraints.

Test signals: unit-style SG tests with aligned, unaligned, one-byte, split-at-every-byte, and partial-tail buffers; data round-trip through CB710 child transfers; KASAN/KMSAN for SG boundary issues.
