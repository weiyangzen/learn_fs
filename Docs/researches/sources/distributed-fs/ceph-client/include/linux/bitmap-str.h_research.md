# sources/distributed-fs/ceph-client/include/linux/bitmap-str.h

## Purpose
Declares bitmap string parsing and formatting helpers for kernel and userspace buffers, supporting both hexadecimal bitmask and list forms.

## Important APIs, types, and functions
- `bitmap_parse_user()` parses a user buffer into a bitmap.
- `bitmap_print_to_pagebuf()` formats into a page buffer in list or mask mode.
- `bitmap_print_bitmask_to_buf()` and `bitmap_print_list_to_buf()` support offset/count streaming for sysfs/procfs-style reads.
- `bitmap_parse()` parses kernel memory buffers.
- `bitmap_parselist()` and `bitmap_parselist_user()` parse list syntax from kernel or user buffers.

## Control flow and state
Callers provide destination bitmaps and bit counts for parsing or source bitmaps and output buffers for printing. User-buffer functions handle `__user` pointers and lengths; streaming print helpers honor `loff_t off` and `count`.

## State and persistence behavior
No internal state. Parsed bitmaps become caller-owned runtime state, often cpumasks, nodemasks, or device resource masks exposed through sysfs/procfs.

## Dependencies and integration points
Depends on kernel types and user pointer annotations. Integrated by sysfs/procfs attributes, CPU/node masks, device affinity, and kernel parameter parsing.

## Risks
Callers must pass the correct `nbits`/`nmaskbits` to avoid accepting out-of-range bits or truncating output. User-buffer parsers can fail on invalid syntax or access errors. Streaming output must correctly handle offsets to avoid duplicate or missing text.

## Test signals
Test mask and list parsing, user and kernel buffers, invalid ranges, high bits beyond `nbits`, empty input, large masks, page-buffer output, and offset/count streaming reads.
