# sources/distributed-fs/lizardfs/src/metadump/mfsmetadump.cc

## Purpose

`mfsmetadump.cc` implements a standalone utility that reads binary LizardFS/MooseFS metadata files and prints a textual dump of headers, nodes, edges, free inode lists, chunks, and unknown sections. The file was read as a complete 540-line implementation.

## Important APIs, Types, and Functions

Important functions are `dispchar`, `chunk_load`, `print_name`, `fs_loadedge`, `fs_loadnode`, `fs_loadnodes`, `fs_loadedges`, `fs_loadfree`, `hexdump`, `fs_load`, `fs_load_2x`, `fs_load_20`, `fs_load_29`, `fs_loadall`, and `main`. It uses metadata signatures and type constants from `MFSCommunication.h` and binary decoding helpers from `datapack.h`.

## Control Flow

`main` requires exactly one metadata filename and calls `fs_loadall`. The loader reads the 8-byte signature, selects legacy 1.5/1.6 layout or sectioned 2.0/2.9 layout, and prints formatted records. Legacy files read global metadata header, nodes, edges, free list, and chunk table. Sectioned files iterate 16-byte section headers until EOF marker, dispatching known sections (`NODE 1.0`, `EDGE 1.0`, `FREE 1.0`, `CHNK 1.0`) or hex-dumping unknown sections. Node parsing branches by type and prints type-specific fields, file chunks, and session IDs.

## State and Persistence Behavior

The utility is read-only: it opens a metadata file and writes formatted text to stdout/stderr. It does not modify metadata. Parsing state is local buffers and file offsets.

## Dependencies and Integration Points

It depends on C stdio, metadata protocol constants, `datapack` endian decoders, and build installation as `mfsmetadump`. It is an operational/debugging tool for inspecting metadata images.

## Risks and Edge Cases

Large stack buffer `unodebuff` reserves space for maximum chunk/session batches. The parser trusts many length fields and reports errors when reads or section offsets do not match. Output replaces non-printable names with dots, so dumps are not lossless for arbitrary byte names. Unknown sections are hex-dumped rather than semantically parsed. `fopen` uses text mode `"r"`, which is safe on POSIX but not portable to newline-transforming platforms.

## Test Signals

Tests should run the tool against fixture metadata signatures 1.5, 1.6, 2.0, and 2.9; corrupt/truncated files; unknown sections; nodes with long chunk lists; symlink/device/trash/reserved entries; and lock-id versus no-lock-id chunk records.
