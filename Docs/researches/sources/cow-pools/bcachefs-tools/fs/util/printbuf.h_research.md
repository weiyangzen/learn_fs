# File Research: sources/cow-pools/bcachefs-tools/fs/util/printbuf.h

Purpose: Public interface and inline helpers for print buffers.

Key APIs and behavior:
- `struct printbuf` tracks buffer pointer, size, position, indentation, tabstops, allocation mode, and output flags.
- Provides `PRINTBUF` for heap-backed buffers and `PRINTBUF_EXTERN` for caller-owned buffers.
- Inline append helpers cover chars, repeated chars, bytes, strings, and hex bytes.
- State save/restore, reset, atomic allocation guards, and indent guards are provided.

Integration:
- Depends on Linux kernel string/hex helpers.
- Function implementations live in `printbuf.c`.
- The RAII-style `DEFINE_CLASS` and `DEFINE_GUARD` helpers support scoped cleanup/indent/atomic state.

Risks and invariants:
- `printbuf_remaining_size()` clamps invalid positions with `WARN_ON`.
- External buffers cannot grow and use overflow signaling.
- `prt_bytes()` calls `printbuf_nul_terminate()` after copying, which may allocate.
