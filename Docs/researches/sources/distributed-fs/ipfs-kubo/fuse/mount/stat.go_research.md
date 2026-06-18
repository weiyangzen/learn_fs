<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/stat.go

## Purpose

This file provides stat-related constants and helpers shared by FUSE filesystems. It anchors Kubo's visible `st_blocks` and `st_blksize` behavior.

## Important APIs, Types, and Functions

`StatBlockSize` is 512 bytes, matching POSIX `st_blocks`. `DefaultBlksize` is 1 MiB. `SizeToStatBlocks` rounds byte sizes up to 512-byte units. `BlksizeFromChunker` extracts sizes from `size-<bytes>` chunker strings, falls back for variable/malformed chunkers, and clamps values to `fuse.MAX_KERNEL_WRITE`.

## Control Flow, State, and Integration

Readonly and writable attr fillers use these helpers for files, directories, and symlinks. MFS/IPNS mount setup derives writable block size from import config.

## Dependencies, Risks, and Test Signals

Dependencies are string parsing and go-fuse's kernel write limit. Risks include breaking `du`/`ls -s` semantics, advertising oversized buffers, or drifting from CID-deterministic defaults. `stat_test.go`, readonly tests, and MFS tests cover rounding, fallback, clamping, and per-entry stat fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat.go -->
