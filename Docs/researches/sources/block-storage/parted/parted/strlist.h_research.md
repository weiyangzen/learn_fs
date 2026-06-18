# File Research: sources/block-storage/parted/parted/strlist.h

## Purpose

`strlist.h` declares Parted’s `StrList` linked-list string abstraction and its construction, conversion, printing, matching, and length APIs.

## Contents

- Includes `<wchar.h>`.
- If NLS is disabled:
  - defines `L_(str)` as `str`,
  - undefines and remaps `wchar_t` to `char`.
- Defines `typedef struct _StrList StrList`.
- Defines `struct _StrList` with:
  - `StrList *next`
  - `const wchar_t *str`
- Declares external charset/language variables:
  - `language`
  - `gettext_charset`
  - `term_charset`

## Declared API

- Creation:
  - `str_list_create()`
  - `str_list_create_unique()`
- Destruction:
  - `str_list_destroy()`
  - `str_list_destroy_node()`
- Copying and composition:
  - `str_list_duplicate()`
  - `str_list_duplicate_node()`
  - `str_list_insert()`
  - `str_list_append()`
  - `str_list_append_unique()`
  - `str_list_join()`
- Conversion:
  - `str_list_convert()`
  - `str_list_convert_node()`
- Output:
  - `str_list_print()`
  - `str_list_print_wrap()`
- Matching:
  - `str_list_match_any()`
  - `str_list_match_node()`
  - `str_list_match()`
- Introspection:
  - `str_list_length()`

## Dependencies and Role

This header is a shared utility contract for `parted.c`, `ui.c`, `command.c`, and `table.c`. It intentionally exposes the node layout, allowing `table.c` to read `list->str` directly.

## Notable Details

The NLS-disabled `wchar_t` remapping is invasive but lets the same implementation and table renderer compile against byte strings. Callers must treat returned `char *` conversions as owned allocations.
