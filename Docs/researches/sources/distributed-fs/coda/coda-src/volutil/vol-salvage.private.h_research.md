# sources/distributed-fs/coda/coda-src/volutil/vol-salvage.private.h

## Purpose

`vol-salvage.private.h` defines the private data structures and internal prototypes shared within the salvage implementation. The complete 117-line header was read. It documents the salvager's core summaries for partition inodes, volumes, vnode essence, vnode-class state, and directory traversal.

## Important APIs, Types, and Functions

Important declarations include `readOnly(vsp)`, `InodeSummary`, `VolumeSummary`, `VnodeEssence`, `VnodeInfo`, and `DirSummary`. It prototypes all internal salvage phases: summary construction, volume-group salvage, quick checks, vnode/inode checks, directory completeness, free-list sanity, inode cleanup, callback/offline helpers, skip-list logic, and global reset.

## Control Flow

The header has no executable flow, but it encodes the staged salvager pipeline: build inode and volume summaries, run checks, apply corrections, coordinate with fileserver state, and release locks/reset globals.

## State and Persistence Behavior

The structs carry transient mirrors of persistent state. `InodeSummary` records offsets into the temporary inode file. `VolumeSummary` connects RVM volume headers to inode summaries and optional resolution logs/bitmaps. `VnodeEssence` and `VnodeInfo` are in-memory distilled views used to validate directory references and volume accounting.

## Dependencies and Integration Points

It depends on `rec_dlist.h`, `bitmap.h`, and `recov_vollog.h`, and assumes types from volume/vnode/directory headers are already visible. It is included by `vol-salvage.cc`.

## Risks and Test Signals

Risks include macro-based read-only classification, static prototypes in a private header, signed link-count assumptions in `VnodeEssence::count`, and tight coupling to salvage globals. Test coverage comes indirectly from salvage tests that exercise summaries, log bitmaps, directory traversal, and skip-list helper behavior.
