# sources/distributed-fs/openafs/src/tests/write3.c

Purpose: tests ordinary small-file write, truncate, read, close, and unlink behavior, including in-fd size observation before close.

Important APIs and functions: `check_size` verifies `stat` size unless the `paranoia` flag is set. `check_size_read` saves current offset, seeks to start, allocates a buffer of expected size, reads exactly that many bytes, then seeks to end and expects the offset to equal the expected size. `main` writes `"kaka"` to `foobar`, verifies after close, reopens with `O_TRUNC`, writes again, verifies via read and seek, closes, then unlinks.

State: creates `foobar` in the current directory and removes it at the end. Dependencies are POSIX file APIs and `err`.

Risks/test signals: it incorrectly declares `read`/`lseek` results as `size_t`, so negative errors are poorly represented, and the second `open` uses decimal `644` instead of octal `0644`. Still, it provides useful read-after-write and file-length signals.
