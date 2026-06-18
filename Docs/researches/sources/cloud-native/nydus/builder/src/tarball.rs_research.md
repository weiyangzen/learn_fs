# sources/cloud-native/nydus/builder/src/tarball.rs

## Purpose
This Rust module implements the tarball-backed `Builder` for Nydus RAFS generation. It converts tar, gzip tar, eStargz-style gzip tar, reference tar, and tarfs inputs into a RAFS tree, optional data blob, and bootstrap metadata. The design is explicitly stream-aware: tar entries are processed once, nodes are created from headers, file data is optionally written to blob artifacts, and the resulting `Tree` is serialized by shared builder/bootstrap code.

## Important APIs, Types, and Functions
`TarballBuilder` is the exported builder implementing `Builder::build`. `TarballTreeBuilder` owns the conversion state for one layer: conversion type, `BuildContext`, `BlobManager`, blob artifact writer, chunk buffer, and `TarBuilder`. `TarReader` abstracts readable tar input variants and implements `Read` plus limited `Seek`; seek support is only available for direct files and `BufReaderInfoSeekable`. `CompressionType` is a small gzip/no-compression detector result. Core functions are `build_tree`, `parse_entry`, `detect_compression_algo`, `set_v5_dir_size`, `get_uid_gid`, `get_mode`, and `get_file_name`.

## Control Flow
`Builder::build` creates bootstrap context and a blob writer, builds the tree, builds bootstrap metadata, dumps blob data and blob metadata, then finalizes blob/bootstrap in inline-meta-dependent order. `build_tree` opens the source, detects compression and conversion type, chooses a `TarReader`, configures `tar::Archive`, creates an initial root node, iterates entries using seek-aware entries when possible, skips stargz special files, and delegates each entry to `parse_entry`. `parse_entry` rejects unsupported tar extensions, derives metadata, resolves special devices, symlinks, hardlinks, PAX xattrs, creates a RAFS V5 or V6 inode, dumps node data from the entry for non-hardlinks, fixes V5 blocks, and inserts the node into the tree.

## State, Persistence, and Dependencies
State persists through `BuildContext` fields such as `blob_zran_generator`, `blob_tar_reader`, and `blob_features`, plus blob artifacts written via `ArtifactWriter` or `NoopArtifactWriter`. The module depends on `tar`, `anyhow`, Nydus RAFS metadata/layout types, storage blob features and ZRAN helpers, digest/compression utilities, and shared builder tree/node/blob/bootstrap code.

## Integration Points
It integrates with `ConversionType` to support RAFS, reference, and tarfs outputs; `BlobManager` and `Blob::dump` for data persistence; `BootstrapManager` for bootstrap serialization; `TarBuilder` for path/tree handling; and RAFS V5/V6 inode formats. Reference conversions set up ZRAN or raw tar readers for later access rather than always copying data into a blob.

## Risks and Test Signals
Risks include unsafe assumptions around hardlink target ordering, rejected tar extensions that may appear in real archives, `unwrap` in compression rewind, device major/minor requirements for FIFO handling, and very large files exceeding `RAFS_MAX_CHUNKS_PER_BLOB`. Seekability changes behavior for hash calculation and tarfs. Tests cover basic and encrypted `TarToTarfs` builds against texture archives, but visible tests do not cover gzip, ZRAN, hardlink error cases, unsupported tar headers, xattrs, or reference conversions.
