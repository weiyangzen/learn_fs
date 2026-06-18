# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-compilation.c

## Purpose

This file generates OSTree static deltas. A static delta packages the objects needed to recreate a target commit from an optional source commit, using compressed parts, rollsum copy operations, bsdiff patches, plain object payloads, and optional HTTP fallback entries. It can write deltas into the repository layout or to a caller-provided filename, and can wrap the superblock in a signature container.

## Important APIs, Types, and Functions

- `OstreeStaticDeltaPartBuilder` accumulates one part: object list, payload bytes, operation stream, mode and xattr dictionaries, temp file, header, and sizes.
- `OstreeStaticDeltaBuilder` owns all parts and fallback objects plus thresholds and counters.
- `finish_part()` builds the part payload variant, compresses it with LZMA, writes it to a linkable tmpfile, computes its checksum, and creates the meta-entry header.
- `allocate_part()` finalizes the previous part and starts a new one.
- `process_one_object()` encodes a full metadata, regular-file, or symlink object using `OPEN_SPLICE_AND_CLOSE`.
- `try_content_rollsum()`, `process_one_rollsum()`, `try_content_bsdiff()`, and `process_one_bsdiff()` implement optimized content deltas against existing source objects.
- `generate_delta_lowlatency()` is the main object-selection and part-building algorithm.
- `get_fallback_headers()` serializes objects that should be fetched separately.
- `ostree_repo_static_delta_generate()` is the public generation API.

## Control Flow

Generation starts by reading parameters such as fallback threshold, bsdiff limit, chunk size, endianness, inline-parts, output filename, verbosity, and signing settings. It loads the target commit and opens the output directory. `generate_delta_lowlatency()` then reads source and target commits, traverses reachable objects, subtracts objects already reachable from the source, and partitions new objects into metadata, regular content, and symlink content.

For regular content, it calls `_ostree_delta_compute_similar_objects()` to find possible source objects. Each candidate must be world-readable before the compiler attempts rollsum, because clients may apply deltas using different privileges or parent repositories. Rollsum is preferred when at least half the target chunks can be copied from the source. If rollsum fails and bsdiff is enabled and below the size threshold, bsdiff is selected. Large remaining regular files may be placed in fallback entries. Metadata is packed first, followed by rollsum objects, bsdiff objects, plain regular content, and symlinks. Parts are split when payload size crosses the configured chunk size.

After part generation, `ostree_repo_static_delta_generate()` creates the superblock with metadata, timestamp, from/to checksums, the target commit object, an empty recursion array, part headers, and fallback headers. Parts are either linked as files named `0`, `1`, etc. or embedded in metadata when inline-parts is enabled. Detached commit metadata is included if present. If signing parameters are supplied, the superblock bytes are signed by each configured key and written in `OSTREE_STATIC_DELTA_SIGNED_FORMAT`; otherwise the raw superblock is linked atomically.

## State and Persistence Behavior

Persistent outputs are stored under the repository static delta path, normally below `deltas/`, or under the directory of a supplied filename. Part files and the superblock are first written as linkable tmpfiles, chmodded to `0644`, and atomically linked into place. The compiler does not alter refs. It reads repository object content, file metadata, xattrs, detached commit metadata, and object storage sizes. It records fallback object metadata in the superblock rather than copying those object bytes.

## Dependencies and Integration Points

The file integrates with traversal, static delta private wire-format definitions, LZMA compression, rollsum matching, bsdiff generation, OSTree raw file conversion, object storage-size queries, detached metadata, and the `OstreeSign` abstraction. Generated operations are consumed by `ostree-repo-static-delta-processing.c`, and generated superblocks are read by `ostree-repo-static-delta-core.c`.

## Risks and Edge Cases

The generator has multiple size and endianness boundaries. Wrong byte swapping would make deltas unreadable on opposite-endian systems. Rollsum and bsdiff are deliberately limited by readability and size checks; relaxing those checks can create deltas clients cannot apply. Fallback entries make deltas unsuitable for offline execution. Inline parts skip external part checksums during offline execution because they are covered by the metadata blob. Signature generation only runs when both a sign name and key IDs are provided.

## Test Signals

Useful tests include from-scratch and from-parent delta generation, chunk splitting, inline versus external parts, fallback threshold behavior, bsdiff disabled mode, world-readable gating for optimized source objects, symlink encoding, metadata/detached metadata inclusion, big- and little-endian output, signed superblock generation, and applying generated deltas through the offline executor.
