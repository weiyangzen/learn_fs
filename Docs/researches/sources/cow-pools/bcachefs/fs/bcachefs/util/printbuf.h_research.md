# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.h

This header defines the `printbuf` structure, initialization macros, inline primitive append helpers, and public formatting API.

Core structure:
- Buffer pointer, size, write position.
- Line/field/indent tracking.
- Atomic allocation nesting count.
- Flags:
  - allocation failure
  - heap allocated
  - overflow
  - suppressed
  - SI unit mode
  - human-readable units
  - has indent/tabstops
  - may vmalloc
- Inline tabstop array of 8 entries.

Initialization:
- `PRINTBUF` creates heap-allocated printbuf state.
- `PRINTBUF_EXTERN(buf, size)` uses caller-provided storage.
- `bch2_printbuf_init()` returns `PRINTBUF`.
- `DEFINE_CLASS(printbuf, ...)` adds cleanup support.

State helpers:
- Save/restore printbuf position, line, field, indent, tabstop.
- Reset with or without keeping tabstops.
- Remaining capacity and NUL termination helpers.

Primitive append helpers:
- reserved and checked char append
- repeated chars
- raw bytes
- strings
- lowercase/uppercase hex bytes

Guards:
- `printbuf_atomic` increments/decrements atomic allocation mode.
- `printbuf_indent`
- `printbuf_indent_nextline`

Public declarations:
- buffer growth
- printf/vprintf
- tabstop/indent management
- newline/tab/rjust tab
- tabstop alignment
- bytes with indentation
- unit/human-readable formatting
- options and bitflags

Important behavior:
- Callers can check `allocation_failure` if they need to return `-ENOMEM`.
- Otherwise, printbuf is designed for best-effort diagnostics.
- External buffers do not allocate and can overflow.

Research notes:
- This header is used broadly enough that its inline functions are effectively part of bcachefs’s diagnostic ABI.
