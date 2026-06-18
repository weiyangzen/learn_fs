# sources/distributed-fs/openafs/src/aklog/linked_list.h

## Purpose
`linked_list.h` declares the simple list data structures and operations used by `aklog`.

## Important APIs, types, and functions
It defines `LL_SUCCESS`, `LL_FAILURE`, `ll_node`, `linked_list`, `ll_end` (`ll_head`, `ll_tail`), and `ll_s_action` (`ll_s_add`, `ll_s_check`). The `ll_add_data(n, d)` macro casts and assigns node data. Prototypes cover `ll_init`, `ll_add_node`, `ll_delete_node`, and `ll_string`, with K&R fallbacks for non-ANSI C.

## Control flow
There is no runtime control flow beyond macro expansion.

## State and persistence
The header defines the in-memory shape: a list keeps first/last pointers and element count; each node keeps prev/next/data.

## Dependencies and integration points
Included by `aklog.h`, `aklog.c`, and `linked_list.c`. The data pointer is typed as `char *`, matching the string-heavy use in `aklog`.

## Risks
The macro does not validate node pointers or ownership and erases data type information. The API does not encode whether data should be freed by the list. Compatibility K&R prototypes obscure type checking on very old compiler paths.

## Test signals
Compile consumers with strict warnings and exercise all list operations through `linked_list.c`.
