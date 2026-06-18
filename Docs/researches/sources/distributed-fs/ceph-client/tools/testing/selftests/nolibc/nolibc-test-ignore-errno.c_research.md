# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-ignore-errno.c

Purpose: Tiny compile-only source that defines `NOLIBC_IGNORE_ERRNO` and includes nolibc via `<stdlib.h>` to ensure nolibc headers compile when errno support is intentionally ignored.

Important APIs/functions: no functions are defined. The important API is the preprocessor contract: `#define NOLIBC_IGNORE_ERRNO` before including nolibc headers.

Control flow: none at runtime; the file participates in compilation/linkage through the nolibc test source list.

State and persistence: no state.

Dependencies and integration: depends on include paths arranged by the nolibc Makefile. It validates header-level conditional compilation in nolibc.

Risks: because it is compile-only, it catches symbol/header failures but not runtime errno semantics.

Test signals: successful compilation is the signal; any conflict with `NOLIBC_IGNORE_ERRNO` should surface as a build error.
