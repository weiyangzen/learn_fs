# File Research: sources/cow-pools/bcachefs-tools/linux/seq_buf.c

## Purpose
Minimal Linux `seq_buf` formatter implementation.

## Key Responsibilities
- Appends formatted strings with `seq_buf_vprintf()` and `seq_buf_printf()`.
- Appends strings, characters, and raw memory with `seq_buf_puts()`, `seq_buf_putc()`, and `seq_buf_putmem()`.
- Marks overflow via `seq_buf_set_overflow()`.

## Behavior
- Functions return `0` on success and `-1` on overflow.
- `seq_buf_puts()` preserves a trailing NUL in storage but does not count it in `s->len`.
- Warns if used with a zero-sized buffer.

## Dependencies
Uses `linux/seq_buf.h`, libc `stdio.h`, and standard string/memory routines.
