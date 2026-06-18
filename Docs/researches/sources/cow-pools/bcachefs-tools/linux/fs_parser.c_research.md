# File Research: sources/cow-pools/bcachefs-tools/linux/fs_parser.c

Provides filesystem parser constant lookup. It defines `bool_names` for common boolean strings and `lookup_constant()` to search a `constant_table`, returning a caller-supplied fallback if absent.
