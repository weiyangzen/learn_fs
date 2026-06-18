# File Research: sources/block-storage/mdadm/lib.c

## Purpose
`lib.c` contains shared mdadm utility functions for device-name mapping, config tokenization, quoted output, string/name validation, environment checks, numeric parsing, and small math/hostname helpers.

## Key Behavior
- `is_string_lq()` validates non-empty strings shorter than a limit including NUL space.
- Device helpers map `dev_t`, `stat`, or fd values to kernel names and md dev names through `/sys/dev/block`, with md major fallbacks.
- `/dev` scanning via `nftw()` builds a major/minor map; `map_dev_preferred()` chooses preferred, shortest, `/dev/md/`, or caller-preferred paths, and can fall back to `major:minor`.
- `conf_word()` tokenizes config/mdstat-style words with comments, quotes, indentation rules, and compatibility fixes for old `(auto-read-only)` mdstat output.
- `conf_line()` builds a dlink word list for one logical config line; `free_line()` releases it.
- `print_quoted()` emits strings with quotes only when needed.
- `is_name_posix_compatible()` enforces POSIX portable filename characters and forbids leading `-`.
- `parse_num()` safely parses non-negative `int` values.
- `s_gethostname()` wraps `gethostname()` and forces NUL termination.

## Integration Notes
This file is foundational for config parsing, mdstat parsing, metadata display, and device discovery. It uses `dlink`, `xmalloc`, sysfs paths, `/proc/devices`, and POSIX file tree walking.

## Risks
`map_dev_preferred()` caches `/dev` scans globally and refreshes only on miss. Several helpers return static buffers, so callers must copy results if they need stable storage across calls.
