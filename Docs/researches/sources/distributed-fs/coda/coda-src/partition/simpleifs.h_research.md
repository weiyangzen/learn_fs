# sources/distributed-fs/coda/coda-src/partition/simpleifs.h

Purpose: constants and private state for the simple inode backend.

State/constants: defines filename/link limits, `FILEDATA`, `VICEMAGIC`, and `struct part_simple_opts` with the next-inode hint.

Dependencies/risks: included through `partition.h` and backend code. Constants are part of the sidecar header validation story; changing `VICEMAGIC` breaks existing partitions. `FNAMESIZE` is small relative to `MAXPATHLEN`, so long partition paths can overflow callers that format into this size.
