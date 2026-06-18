<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap-str.c -->
# sources/distributed-fs/ceph-client/lib/bitmap-str.c

## Purpose
Implements string and user-buffer conversion helpers for kernel bitmaps, including hex bitmask parsing, decimal list/range parsing, and sysfs-friendly printing.

## APIs, Types, and Functions
Exports `bitmap_parse_user()`, `bitmap_print_to_pagebuf()`, `bitmap_print_bitmask_to_buf()`, `bitmap_print_list_to_buf()`, `bitmap_parselist()`, `bitmap_parselist_user()`, and `bitmap_parse()`. Internal `struct region` represents list ranges with optional used/group pattern syntax. Helpers include region find/parse/check/set routines, number parsing with `N` as the last-bit token, reverse hex chunk parsing, and buffered printing through `kasprintf()` plus `memory_read_from_buffer()`.

## Control Flow, State, and Persistence
User parsers copy user buffers with `memdup_user_nul()` before delegating. `bitmap_parselist()` clears the output mask, repeatedly finds comma/whitespace-separated regions, parses single bits, ranges, `all`, `N`, and `start-end:used/group` patterns, validates bounds, then sets selected bits. `bitmap_parse()` walks a hex bitmask string from right to left in comma-separated 32-bit chunks, writing host-order u32 chunks into the bitmap and clearing/validating tail bits beyond `nmaskbits`. Print helpers format either `%*pb` hex masks or `%*pbl` lists; bin-attribute variants support offset/count at the cost of allocating the full string each call. No persistent state is owned.

## Dependencies and Integration
Depends on bitmap core helpers, ctype, errno, user-copy helpers, hex conversion, page offsets, `kstrtox` internals, and printk `%*pb/%*pbl` formatting. Used heavily by sysfs/procfs cpumask and nodemask interfaces.

## Risks and Test Signals
Risks include confusing byte/character offsets with bit offsets in bin-attribute printers, partial list output being non-parseable, integer overflow in list parameters, dynamic `N` values changing with bitmap width, big-endian 64-bit u32 chunk ordering, and accepting empty comma groups in hex parser. Test signals include list forms `all`, `N`, ranges, patterns such as `0-1023:2/256`, overflow and out-of-range values, whitespace/comma edge cases, big-endian parse/print fixtures, user-copy fault injection, and sysfs bin-attribute partial reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap-str.c -->
