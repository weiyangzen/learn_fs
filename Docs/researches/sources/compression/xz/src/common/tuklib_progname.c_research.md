# sources/compression/xz/src/common/tuklib_progname.c

Purpose: initializes a global program-name pointer used in diagnostics, with DOS-like cleanup of `argv[0]`.

Important APIs/types/functions: defines `char *progname` when `HAVE_PROGRAM_INVOCATION_NAME` is unavailable and exports `tuklib_progname_init(char **argv)`. Uses `<string.h>` helpers `strlen` and `strrchr`.

Control flow: on `TUKLIB_DOSLIKE`, the initializer mutates `argv[0]` presentation by stripping path components, truncating a dot suffix such as `.exe`, and lowercasing ASCII uppercase letters. It then assigns global `progname = argv[0]`. On non-DOS-like systems, it simply stores the original `argv[0]`, unless the header maps `progname` to libc `program_invocation_name`.

State and persistence: persistent process-global pointer only. It borrows storage from the application's argument vector and, on DOS-like builds, mutates that storage in place.

Dependencies/integration: paired with `tuklib_progname.h`; used by command-line tools and common message code that want a stable program-name variable independent of libc availability.

Risks: assumes `argv` and `argv[0]` are non-NULL and writable on DOS-like systems. The suffix stripping removes any final extension, not only `.exe`, because it truncates at the last dot. Borrowed pointer lifetime is process lifetime for normal `argv`, but not guaranteed if embedded callers pass temporary storage.

Test signals: no direct test found in this subset. Diagnostics tests or command-line output comparisons would expose regressions in displayed program names.
