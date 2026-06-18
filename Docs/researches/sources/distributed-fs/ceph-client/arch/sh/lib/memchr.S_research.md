# sources/distributed-fs/ceph-client/arch/sh/lib/memchr.S

Purpose: implements the standard `memchr` byte-search primitive.

Important symbol: `ENTRY(memchr)`.

Control flow: scans a memory range for the target byte and returns a pointer to the first match or null when length is exhausted.

State and persistence: read-only over the input buffer; no persistent state.

Dependencies and integration: linked into the kernel library and used by generic string/memory callers.

Risks: incorrect length handling can read past buffers; incorrect return convention breaks callers doing parser/buffer scans.

Test signals: string/memory selftests with zero length, first/last byte matches, no match, and unaligned inputs.
