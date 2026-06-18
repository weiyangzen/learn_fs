# File Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8n.h

## Purpose
Private declarations for the UTF-8 normalization implementation.

## Contents
- Declares `utf8version_is_supported()`, `utf8nlen()`, `utf8ncursor()`, and `utf8byte()`.
- Defines `UTF8HANGULLEAF`.
- Defines `struct utf8cursor`.
- Defines `struct utf8data` and `struct utf8data_table`.
- Declares external `utf8_data_table`.

## Integration Notes
This header connects high-level Unicode helpers in `utf8-core.c` with trie/cursor internals in `utf8-norm.c` and generated normalization data.
