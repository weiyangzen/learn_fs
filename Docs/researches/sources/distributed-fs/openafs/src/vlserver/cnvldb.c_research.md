# sources/distributed-fs/openafs/src/vlserver/cnvldb.c

## Purpose

`cnvldb.c` is the VLDB on-disk conversion utility. It reads a Ubik VLDB file, detects or validates its VLDB version, optionally prints version/entries, converts headers and entries between supported versions 1 through 4, repairs some multihome extent block pointers, writes a temporary database, fsyncs it, and renames it over the original path.

## Important APIs, Types, And Functions

- `handleit` is the command dispatcher for `-to`, `-from`, `-path`, `-showversion`, and `-dumpvldb`.
- `readheader`, `readentry`, and `printentry` consume existing VLDB bytes after the 64-byte Ubik header.
- `read_mhentries` reads and validates v4 multihomed extent blocks into `base[]`.
- `convert_mhentries` repairs multihome pointers and converts multihome address references back to single addresses for v4-to-v3.
- `convert_header` rewrites header versions, sizes, EOF/free pointers, hash table pointers, and server address arrays.
- `Conv4to3` adjusts record offsets when v4 multihome blocks are removed.
- `convert_vlentry` rewrites per-volume entries between old/new struct layouts and handles multihome info blocks.
- `rewrite_header` seeks back after entry conversion to write final header state.

## Control Flow

The converter opens the database read-only, reads the version at offset 64, reads the 64-byte Ubik header, decodes the VL header, and, for v3/v4-style headers, reads multihome extent blocks before resuming sequential entry processing. In display mode it prints version or entries and exits. In conversion mode it verifies requested versions and multihome downgrade constraints, changes to the database parent directory, writes `XXnewvldb`, copies the Ubik header, converts the VL header and each entry sequentially, performs multihome fixups, rewrites the final header, fsyncs, closes, and renames the temp file to the requested path.

## State And Persistence Behavior

This utility mutates the persistent VLDB file by replacement. It preserves the Ubik header verbatim and rewrites VLDB content in network byte order. Header conversions adjust offsets by header-size differences. Version 4 multihome continuation blocks are preserved only when converting to version 4 or higher; downgrading to version 3 removes them, rewrites hash/list offsets, clears `SIT`, and chooses the first IP address from a multihomed set.

## Dependencies And Integration Points

It depends on `vlserver.h` for current VLDB constants and `cnvldb.h` for legacy on-disk layouts. It is built by `vlserver/Makefile.in` and installed as `vldb_convert`. It complements `vldb_check` and the VL server's Ubik database format.

## Risks And Edge Cases

- It replaces the original database after `fsync(new)` but does not fsync the parent directory after rename.
- Several error paths call `exit`, so library-style recovery is impossible.
- Some read/write checks use `int` for byte counts and offsets; large/corrupt databases can stress assumptions.
- A likely bug in `convert_header` for v2/3/4 to v1 writes `sizeof(struct vlheader_1)` but compares against `sizeof(struct vlheader_2)`.
- Downgrading multihomed entries loses all but one IP address.

## Test Signals

Use golden VLDB fixtures for versions 1, 2, 3, and 4; round-trip conversions where lossless; v4-to-v3 tests with multihomed extent blocks; corrupted SIT/extent pointer repair tests; `-showversion` and `-dumpvldb` smoke tests; and failure-injection tests for short reads/writes, fsync, and rename.
