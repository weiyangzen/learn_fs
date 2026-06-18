## sources/distributed-fs/orangefs/src/client/usrint/recursive-remove.h

Purpose: Declares the recursive removal API and debug/error macros for the OrangeFS recursive delete helper.

Important APIs, types, and functions: Public functions are `recursive_delete_dir` and `remove_files_in_dir`. Macros `RR_PFI`, `RR_PRINT`, `RR_ERROR`, and `RR_PERROR` compile to `printf`/`fprintf`/`perror` diagnostics depending on `ENABLE_RR_*` defines; errors and perror reporting are enabled by default.

Control flow: Header-only macros either emit diagnostics or compile away. `RR_PERROR` reports only when `errno != 0`, including line and `__PRETTY_FUNCTION__`.

State and persistence: No durable state. The active macro configuration affects process stderr/stdout during recursive deletion.

Dependencies and integration points: Includes `<dirent.h>`, `<stdio.h>`, and `<errno.h>`. Used directly by `recursive-remove.c`.

Risks and test signals: Default stderr logging can surprise library callers. `__PRETTY_FUNCTION__` is compiler-specific. `RR_PERROR` can suppress useful messages if a caller returns an error without setting `errno`, and stale `errno` can mislead. Test builds with each debug define toggled and errors from APIs that do and do not set `errno`.
