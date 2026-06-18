# sources/distributed-fs/openafs/src/tests/write-rand.c

Purpose: creates or overwrites a file with pseudo-random bytes of a requested size. It is a simple workload generator for write tests rather than a verifier.

Important APIs and functions: `write_random_file` allocates up to a 2048-byte buffer, fills it with `rand()` bytes, and repeatedly writes chunks until the requested `size_t` length reaches zero. `main` parses `file size`, seeds with `time(NULL)`, opens the file `O_RDWR | O_CREAT` mode `0755`, seeks to offset zero, writes, and closes.

Control flow/state: state is only the target file contents. The file is not truncated, so if the new requested size is smaller than the old file size, stale trailing data may remain. Dependencies are POSIX file APIs and libc random/time functions.

Risks: `atoi` silently accepts bad or negative sizes before conversion to `size_t`; `write_random_file` returns `char *` but returns `0`; partial writes are treated as errors instead of retrying. Test signal is weak: success means writes returned the requested chunk lengths, not that the resulting file size or data was verified.
