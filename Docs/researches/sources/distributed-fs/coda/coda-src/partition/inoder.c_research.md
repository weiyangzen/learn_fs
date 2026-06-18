# sources/distributed-fs/coda/coda-src/partition/inoder.c

Purpose: command-line utility for manual partition inode operations: create inode, read header, increment/decrement link count, and overwrite header metadata.

Flow: initializes partitions from a supplied vicetab and host name, finds a partition by directory, then dispatches based on command string. `icreate` takes volume/vnode/unique/version; `header` prints `i_header`; `iinc`/`idec` adjust link counts; `setheader` writes a new header using the backend magic.

Dependencies/risks: depends on `DP_Init`, `DP_Get`, legacy inode wrappers, and backend `magic`. It is operator-facing and can corrupt metadata if pointed at production partitions. Test signal is successful command-line operations on test vicetab/simple/ftree directories.
