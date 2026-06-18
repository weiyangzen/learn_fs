# sources/distributed-fs/ceph-client/tools/include/linux/ctype.h

## Purpose

This header provides kernel-style character classification and case conversion helpers for tools code.

## APIs, State, and Dependencies

It defines classification bit masks, declares external `_ctype[]`, and maps `isalnum`, `isalpha`, `iscntrl`, `isgraph`, `islower`, `isprint`, `ispunct`, `isspace`, `isupper`, `isxdigit`, `isascii`, `toascii`, `isdigit`, `tolower`, `toupper`, `_tolower`, and `isodigit`. `isdigit` uses a compiler builtin when available. State is limited to the external classification table.

## Risks and Test Signals

The macros index `_ctype` by unsigned char cast, which avoids negative-char indexing. Locale is not considered; behavior is kernel ASCII-style. Tests should link `_ctype`, cover all ASCII classes, and check case conversion boundaries.
