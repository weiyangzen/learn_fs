# File Research: sources/block-storage/stratisd/src/bin/udev-lib/stratis-str-cmp.rs

Tiny udev helper for string comparison.

Key behavior:
- Requires two string arguments.
- Prints `0` if equal, `1` otherwise.
- Returns errors only for missing arguments.

The stdout convention is suitable for udev rule condition pipelines.
