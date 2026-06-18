# sources/distributed-fs/ceph-client/fs/btrfs/lzo.c

## Purpose
`lzo.c` implements Btrfs' LZO compression backend. It allocates per-worker LZO workspaces, compresses file data into Btrfs' segmented LZO on-disk format, and decompresses both regular compressed bios and inline compressed extents. The source was read as a complete 583-line file.

## Important APIs, Types, and Functions
Public functions are `lzo_alloc_workspace()`, `lzo_free_workspace()`, `lzo_compress_bio()`, `lzo_decompress_bio()`, `lzo_decompress()`, and the `btrfs_lzo_compress` level descriptor. `struct workspace` owns LZO working memory, an uncompressed buffer, a compressed buffer, and list linkage. Internal helpers include workspace size helpers, `write_and_queue_folio()`, `copy_compressed_data_to_bio()`, `get_current_folio()`, and `copy_compressed_segment()`.

## Control Flow
Compression allocates an output folio, reserves the first 4-byte total-length header, walks input file folios sector by sector, compresses each sector with `lzo1x_1_compress()`, writes a 4-byte segment length plus payload, pads with zeros when needed so the next segment header never crosses a sector boundary, and finally patches the total compressed length into the first header. It aborts with `-E2BIG` if compression grows too much, especially after the first two sectors.

Bio decompression reads the total LZO length from the first folio, validates it against the compressed bio size and maximum compressed extent size, then iterates segment headers and payloads. Each segment payload is copied into the workspace compressed buffer, decompressed with `lzo1x_decompress_safe()`, and copied into destination inode pages through the generic Btrfs decompression helper. Inline decompression validates the two headers expected for a single segment, decompresses into the workspace buffer, copies to the destination folio, zero-fills short output, and returns an error on early end.

## State and Persistence Behavior
Workspace allocations are runtime-only. Persistent format state is the bytes written into compressed extents: a little-endian total length followed by per-segment little-endian payload lengths, payloads, and at most three bytes of sector padding before the next segment header. The compression level descriptor advertises only level 1.

## Dependencies and Integration Points
The file integrates with Linux LZO, bio/folio APIs, Btrfs compression infrastructure, compressed bio lifecycle, inode/root metadata for error logging, and filesystem sector/minimum-folio sizing. It is selected through Btrfs compression type dispatch.

## Risks and Edge Cases
The on-disk segment layout is strict: segment headers must fit in one sector, total length must not exceed the actual compressed bio, and padding must be skipped correctly. Corrupt headers can cause `-EUCLEAN` or `-EIO`; diagnostics include root, inode, and offset. Large folio and subpage behavior depends on offset calculations and `bio_get_size()`. `write_and_queue_folio()` assumes bio vector merging behaves as expected and returns `-E2BIG` on bvec-limit pressure. Inline decompression treats short decompressed output as an error after zero-filling.

## Test Signals
Signals include compression/decompression round trips with multiple sectors, sector-boundary header padding, incompressible data returning `-E2BIG`, inline LZO extents, corrupt total length, oversized segment length, decompressor failure injection, large folio/min-folio configurations, non-4K sectors, and mount/read tests that verify logged root/inode/offset diagnostics on corrupted compressed extents.
