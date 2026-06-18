# File Research: sources/cow-pools/bcachefs-tools/c_src/tools-util.c

- Common userspace utility implementation.
- Provides fatal `die`, formatted allocation helpers, fd stat wrapper, file string/u64 readers, interactive yes/no prompt, and fatal signal handlers that print unified bcachefs backtraces before re-raising.
- Uses libblkid to detect existing filesystems before formatting and optionally wipe detected metadata; enforces libblkid >= 2.40.1 unless forced.
- Implements CRC32C with a table fallback and x86 SSE4.2 fast path selected lazily.
