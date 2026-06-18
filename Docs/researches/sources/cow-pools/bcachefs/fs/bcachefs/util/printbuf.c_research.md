# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.c

This file implements `printbuf`, bcachefs’s reusable diagnostic string builder with best-effort allocation, indentation, tabstop alignment, and unit formatting.

Buffer growth:
- `bch2_printbuf_make_room_gfp()` ensures capacity including NUL.
- Fixed external buffers set overflow on insufficient room.
- Heap buffers grow to the next power of two.
- Allocation respects `atomic` mode and optional `may_vmalloc`.
- Allocation failures set flags rather than forcing callers to unwind.
- `bch2_printbuf_make_room()` uses `GFP_KERNEL`.

Printing:
- `bch2_prt_vprintf()` and `bch2_prt_printf()` retry after growth when formatted output does not fit.
- `bch2_printbuf_str()` returns `""` for empty/unallocated buffers.
- `bch2_printbuf_exit()` frees owned memory and poisons the pointer.

Indent/tabstops:
- Tracks current line, last field, indent, and tabstop index.
- `bch2_printbuf_tabstop_push/pop/reset()` manage preset tabstops.
- `bch2_printbuf_indent_add*()` and `bch2_printbuf_indent_sub()` manage indentation.
- `bch2_prt_newline()` emits newline plus current indentation.
- `bch2_prt_tab()` left-aligns to next tabstop.
- `bch2_prt_tab_rjust()` right-aligns previous field to next tabstop.
- `bch2_prt_bytes_indented()` post-processes embedded `\n`, `\t`, and `\r`.
- `bch2_printbuf_tabstop_align()` performs a two-pass elastic alignment over raw tab characters.

Formatting helpers:
- Human-readable unsigned/signed integers.
- Raw or human-readable units based on printbuf flags.
- String option list with selected item bracketed.
- Bitflag formatting from string tables.
- Bitflag vector formatting.

Important invariants:
- `printbuf_remaining()` reserves one byte for NUL.
- Printbuf functions favor partial output over hard errors.
- Atomic mode avoids sleeping allocations.
- Alignment post-processing may replace the owned buffer.

Research notes:
- Most files in this group use `printbuf` for fsck, status, and debug rendering.
- The design intentionally supports both kernel-space and userspace portability.
