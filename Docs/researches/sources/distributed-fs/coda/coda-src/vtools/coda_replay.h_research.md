# sources/distributed-fs/coda/coda-src/vtools/coda_replay.h

## Purpose

`coda_replay.h` defines the tar-compatible block layout and Coda-specific operation codes consumed by `coda_replay.cc`.

## Important APIs, Types, and Functions

It defines `TBLOCK`, `NBLOCK`, `NAMSIZ`, and union `hblock`, whose `header` view contains tar fields `name`, `mode`, `uid`, `gid`, `size`, `mtime`, `chksum`, `linkflag`, and `linkname`. It maps `linkflag` values to operations: `STOREDATA`, `LINK`, `SYMLINK`, `STORESTATUS`, `REMOVE`, `RENAME`, `MKDIR`, and `RMDIR`.

## Control Flow

This header has no execution flow. Consumers interpret each 512-byte `hblock` as either a tar header, data block, or trailer block.

## State and Persistence Behavior

No state is stored here. Persistence semantics are determined by consumers that replay the encoded operations.

## Dependencies and Integration Points

The structure mirrors historical tar headers while extending `linkflag` beyond standard tar values. It is an ABI contract between closure producers and replay consumers.

## Risks and Test Signals

The layout assumes 512-byte packing and 100-byte path/link fields. Long names, large sizes, and nonstandard tar variants require producer-side handling. Tests should assert `sizeof(hblock) == TBLOCK`, operation constants, checksum compatibility, and compatibility with the replay parser.
