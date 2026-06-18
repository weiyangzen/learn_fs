# sources/distributed-fs/ceph-client/drivers/tty/vt/conmakehash.c

Purpose: `conmakehash.c` is a host-build utility that parses a console Unicode font mapping file such as `cp437.uni` and emits C arrays used by the kernel to initialize the default font-to-Unicode map.

Important APIs and data: it defines `MAX_FONTLEN` as 256, `typedef unsigned short unicode`, global `unitable[MAX_FONTLEN][255]`, and `unicount[MAX_FONTLEN]`. Helpers are `usage()`, `getunicode()`, `addpair()`, and `main()`.

Control flow: `main()` opens the input file or stdin, assumes a 256-glyph font, clears per-glyph counts, then parses each nonblank, noncomment line. Accepted syntax maps one glyph to a list of `U+hhhh` values, a glyph range to `idem`, or a glyph range to an equal-length Unicode range. `getunicode()` recognizes exactly four hex digits after `U+`. `addpair()` ignores values above `0xfffe`, deduplicates per glyph, enforces at most 255 Unicode values per glyph, and records the mapping. After EOF, it counts total Unicode entries and prints a generated C file containing `u8 dfont_unicount[256]` and packed `u16 dfont_unitable[n]`.

State and persistence: all state is process-local global arrays. Output is written to stdout and redirected by Kbuild to `consolemap_deftbl.c`; no files are modified directly by the program.

Dependencies and integration points: built as a Kbuild host program by `drivers/tty/vt/Makefile`. Its generated arrays are referenced by `consolemap.c` as `dfont_unicount[]` and `dfont_unitable[]`, then loaded by `con_set_default_unimap()`.

Risks: the parser only accepts four-digit Unicode values, so supplementary-plane mappings are ignored or rejected. Fixed 256-font assumptions must match console font expectations. A malformed range or too many mappings exits with sysexits codes, breaking the build. Duplicate filtering is per glyph only. Lines longer than 64 KiB are truncated with a warning, which could silently produce incomplete generated data.

Test signals: parse single glyph mappings, duplicate entries, `idem` ranges, Unicode ranges with matching and mismatched lengths, glyph range bounds, values above `0xfffe`, trailing junk warnings, stdin input, too many mappings for one glyph, and regenerated output matching shipped `consolemap_deftbl.c`.
