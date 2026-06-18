# File Research: sources/cow-pools/bcachefs-tools/include/linux/seq_buf.h

Defines `struct seq_buf` and inline buffer-state helpers: init, clear, overflow detection, remaining capacity, used length, null termination, get-buffer, and commit. It declares printf/puts/putc/user-copy/human-readable helpers implemented in `linux/seq_buf.c`.

Overflow is represented by `len > size`, so callers must use `seq_buf_has_overflowed()` rather than only checking `len`.
