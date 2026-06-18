# File Research: sources/block-storage/parted/parted/strlist.c

## Purpose

`strlist.c` implements Parted’s linked-list string utility used for command aliases, completions, prompts, help text, wrapped output, translated option matching, and table row construction. It stores strings internally as `wchar_t` when NLS is enabled and as `char` otherwise.

## Main Responsibilities

- Allocate, append, insert, join, duplicate, and destroy `StrList` nodes.
- Convert between gettext/catalog strings and internal wide-character strings.
- Convert list nodes or whole lists back to multibyte strings.
- Print lists directly or wrapped to a target line width.
- Match input tokens against valid possibilities with full or prefix matching.
- Support case-insensitive command/option matching, including translated aliases.

## Important Functions

- `gettext_to_wchar()` converts multibyte gettext strings to internal wide strings under NLS; without NLS it duplicates bytes directly.
- `wchar_to_str()` converts internal strings back to multibyte strings, optionally truncating by character count.
- `str_list_create()` and `str_list_create_unique()` build varargs lists terminated by `NULL`.
- `str_list_append()` appends a translated string.
- `str_list_append_unique()` appends only if no case-insensitive equivalent exists.
- `str_list_insert()` prepends by creating a single-node list and joining it to the old list.
- `str_list_join()` links two lists without copying.
- `str_list_duplicate()` and `str_list_duplicate_node()` deep-copy nodes and strings.
- `str_list_convert()` concatenates every non-null node into a newly allocated `char *`.
- `str_list_print()` prints each node in sequence.
- `str_list_print_wrap()` wraps text at break points based on screen width, offset, and indent.
- `str_list_match_node()` returns full/partial/no match for one node.
- `str_list_match_any()` returns the best match status across a list.
- `str_list_match()` returns an exact match immediately, a single partial match if unambiguous, or `NULL` for no/ambiguous match.
- `str_list_length()` counts nodes.

## Data Model

Each `StrList` node owns its `str` allocation and its `next` link. Destruction is recursive for whole lists. Several APIs transfer or share list ownership directly: `str_list_join()` reuses existing list nodes rather than copying.

## NLS Behavior

With `ENABLE_NLS`, list strings are wide characters and matching uses `wcscasecmp()` / `wcsncasecmp()`. Printing converts back through `wcrtomb()`. Without NLS, `wchar_t` is macro-mapped to `char`, and wrappers use normal byte-string functions.

## Wrapping Behavior

`str_list_print_wrap()` treats spaces as removable whitespace and explicit `\n` as forced breaks. It searches backward for break points using `is_break_point()`, which is locale-aware under NLS. The comments explicitly discuss Japanese text where word spaces may not exist.

## Dependencies and Interactions

- Used by `command.c` for command names, summaries, help text, and matching.
- Used by `ui.c` for command-line token lists, completion possibilities, prompts, and exception choices.
- Used by `parted.c` to construct generated help strings and human output table rows.
- Used by `table.c` through direct access to `StrList->str`.

## Notable Edge Cases

- `str_list_create(NULL, ...)` creates a single node with a null string because it calls `str_list_append(NULL, first)` before checking `first`.
- `str_list_match()` treats multiple partial matches as ambiguous and returns `NULL`.
- Conversion errors in NLS paths print an error and terminate the process with `exit(EXIT_FAILURE)`.
- `str_list_destroy()` is recursive, so extremely long lists could consume call stack, though normal Parted lists are small.
- `str_list_convert()` uses `realloc()` directly instead of `xrealloc()` and does not explicitly check for allocation failure.
