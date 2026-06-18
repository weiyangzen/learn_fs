# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads-messages.h

## Purpose
Defines structured log message IDs and reusable strings for the io-threads translator.

## Important APIs, types, and functions
`GLFS_MSGID(IO_THREADS, ...)` assigns IDs for init failure, child misconfiguration, memory/accounting failures, pthread setup failures, and worker initialization failures. `_STR` macros provide common messages.

## Control flow
No logic is implemented. `io-threads.c` includes this header for `gf_smsg()` calls during init, memory accounting, and thread setup.

## State and persistence behavior
The message IDs form part of Gluster's stable logging interface and should be appended rather than reordered or removed.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the global `IO_THREADS` component ID. It integrates with log analysis and support tooling.

## Risks and test signals
Risks are ID reuse, component mismatch, and stale messages after code changes. Compile tests and log-path assertions for init failure and worker setup failure cover the header.
