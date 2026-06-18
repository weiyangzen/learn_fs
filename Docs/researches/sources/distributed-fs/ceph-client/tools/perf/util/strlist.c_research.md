# sources/distributed-fs/ceph-client/tools/perf/util/strlist.c

## Purpose

`strlist.c` implements an ordered unique string set on top of perf's `rblist`. It can parse comma-separated lists, load entries from files, and optionally treat list entries as filenames relative to a directory.

## Important APIs, Types, and Functions

Public functions are `strlist__new()`, `strlist__delete()`, `strlist__add()`, `strlist__load()`, `strlist__remove()`, `strlist__find()`, and `strlist__entry()`. Private callbacks implement node allocation, deletion, and string comparison. Parsing helpers include `strlist__parse_list_entry()` and `strlist__parse_list()`.

## Control Flow and Data Flow

`strlist__new()` initializes an `rblist`, installs callbacks, sets `file_only`, and parses the optional comma-separated list. Each entry may be substituted with `dirname/entry`; if accessible, it is loaded as a file of newline-separated entries. If not accessible and `file_only` is set, parsing fails with `-ENOENT`; otherwise the entry string is inserted. `strlist__load()` reads each line, strips the final newline byte, and inserts it into the tree. Lookup and indexed access delegate to `rblist`.

## State and Persistence Behavior

The strlist owns duplicated node strings and rbtree nodes. It stores entries sorted by `strcmp()` and does not preserve input order. `strlist__delete()` deletes rblist contents but does not free the `struct strlist` wrapper in this implementation, so caller conventions must be checked. Removed nodes are deleted through rblist callbacks.

## Dependencies and Integration Points

It depends on `rblist`, Linux zalloc, stdio, errno, string, stdlib, and `access()`. It is used by filter lists such as symbols, DSOs, comms, and sort elision logic.

## Risks and Edge Cases

`strlist__load()` strips `entry[len - 1]` even if the last line has no newline, removing the final character. `strlist__parse_list()` returns early on error without freeing the duplicated list string, causing a leak. `strlist__new()` frees only the wrapper on parse error and may rely on rblist cleanup elsewhere. Sorted uniqueness means duplicate inputs collapse and input order is lost.

## Test Signals

Tests should cover duplicate insertion, sorted lookup, indexed access, removal, list parsing, file loading with and without trailing newline, `file_only` behavior, dirname substitution, and parse-error cleanup.
