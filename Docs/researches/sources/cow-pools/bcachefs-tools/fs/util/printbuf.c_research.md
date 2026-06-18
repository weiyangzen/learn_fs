# File Research: sources/cow-pools/bcachefs-tools/fs/util/printbuf.c

Purpose: Implements growable best-effort string buffers for structured textual output.

Key APIs and behavior:
- `bch2_printbuf_make_room_gfp()` grows heap buffers with `krealloc` or `kvrealloc`; external buffers set overflow instead.
- `bch2_prt_printf()` and `bch2_prt_vprintf()` append formatted text and post-process indentation/tab controls.
- Newline, tab, right-justified tab, indent, and tabstop helpers maintain layout state.
- Human-readable unit printers, string-option printer, bitflag printers, and elastic tab alignment are implemented.

Integration:
- Implements `printbuf.h`; re-exported through aliases in `util.h`.
- Uses `darray` for elastic tab alignment column-width storage.
- Used broadly by diagnostics, sysfs/debug output, and error messages.

Risks and invariants:
- Allocation failures are sticky state, not direct hard errors for most printers.
- `bch2_printbuf_tabstop_align()` replaces heap storage and must preserve ownership flags correctly.
- Mixed raw `\n`, `\t`, and `\r` should go through printbuf helpers for correct indentation/alignment.
