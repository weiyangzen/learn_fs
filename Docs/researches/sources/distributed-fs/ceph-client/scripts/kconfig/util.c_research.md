# sources/distributed-fs/ceph-client/scripts/kconfig/util.c

## Purpose
`util.c` provides two shared Kconfig utility areas: tracking parsed Kconfig files to reject repeated includes, and implementing the `struct gstr` growable string helper used for generated dependency text and diagnostics.

## Important APIs, Types, and Functions
`file_hashtable` stores every parsed Kconfig file. `struct file` records a file name plus the parent file and line number of the first inclusion. `die_duplicated_include()` emits a repeated-include diagnostic and exits. `file_lookup()` canonicalizes/stores file names, recursively records parent names, rejects a second include with parent context, and appends the file to `autoconf_cmd`.

The growable string API is `str_new()`, `str_free()`, `str_append()`, `str_printf()`, and `str_get()`. `str_new()` starts with a 64 byte buffer, `str_append()` reallocates to exact required size when needed, and `str_printf()` formats through a 10000 byte stack buffer before appending.

## Control Flow
During scanning, each source file is passed to `file_lookup()`. First inclusion allocates and hashes a `struct file`; repeated inclusion through a parent path triggers `die_duplicated_include()`. Gstr helpers are leaf routines: callers allocate with `str_new()`, append strings/formatted text, read `gs.s` with `str_get()`, and release with `str_free()`.

## State and Persistence
Parsed file state persists in the process-global `file_hashtable` for the duration of the Kconfig parse. Each file entry stores heap memory for the flexible-array name. `str_printf(&autoconf_cmd, ...)` also persists include dependency lines in the global autoconf command string. Each `struct gstr` owns heap memory that callers must free.

## Dependencies and Integration Points
The file depends on `hash.h`, `hashtable.h`, `xalloc.h`, and `lkc.h`. It integrates with scanner include handling and with `parser.y`/`preprocess.c` through the shared `autoconf_cmd` and `struct gstr` API.

## Risks and Edge Cases
Repeated include handling exits immediately, so diagnostics must be precise enough for users to fix include loops or duplicate sources. `str_printf()` truncates any single formatted append over 9999 bytes before appending. `str_append()` grows to exactly the requested length, which is simple but may reallocate frequently for many small appends. There is no reset API for `file_hashtable`, so repeated parses in one process would retain file entries.

## Test Signals
The `err_repeated_inc` fixture directly tests repeated include diagnostics. Parser and preprocessor tests indirectly exercise `struct gstr` through `autoconf_cmd`, environment dependencies, warnings, and help/config output.
