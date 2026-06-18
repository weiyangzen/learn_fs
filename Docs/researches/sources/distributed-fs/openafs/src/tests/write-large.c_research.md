# sources/distributed-fs/openafs/src/tests/write-large.c

Purpose: validates writing an AFS file up to the 2 GiB minus 1 byte boundary. It is aimed at large-file handling and cache/file-server write path limits.

Important APIs and functions: `check_size` optionally `stat`s the fixed file `foobar` and compares `st_size`. `main` opens `foobar` with `O_LARGEFILE` when available, writes 2,097,151 chunks of 1024 bytes, then expects the next 1024-byte write to return exactly 1023 bytes, producing size `2147483647`.

Control flow/state: a single file named `foobar` is created/truncated in the working directory and left behind. The loop makes the file nearly 2 GiB, then intentionally tests the boundary short-write. Dependencies are POSIX `open`, `write`, `close`, `stat`, large-file macros, and BSD `err` APIs.

Risks: this test consumes about 2 GiB of quota and time, uses an uninitialized stack buffer for content, and assumes the expected AFS/file-size limit is exactly `INT32_MAX`; on modern large-file-capable storage a full final 1024-byte write would make the test fail. Test signal is strict exit status plus final size verification.
