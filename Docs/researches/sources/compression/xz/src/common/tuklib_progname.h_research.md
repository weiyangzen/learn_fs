# sources/compression/xz/src/common/tuklib_progname.h

Purpose: declares the program-name global and initializer used by xz common diagnostic code.

Important APIs/types/functions: includes `tuklib_common.h` and `<errno.h>`, maps `progname` to `program_invocation_name` when available, otherwise declares prefixed `extern char *progname`; maps and declares `tuklib_progname_init(char **argv)`.

Control flow: no runtime flow. Preprocessor selection decides whether the project uses libc's invocation name or its own global variable.

State and persistence: exposes a process-global string pointer, either provided by libc or by `tuklib_progname.c`. The header itself does not own storage.

Dependencies/integration: used by command-line programs before emitting errors or warnings. `TUKLIB_SYMBOL` avoids name collisions when tuklib helpers are embedded into libraries or tools.

Risks: exposing `progname` as a macro/global can collide with application symbols if prefixing is misconfigured. Callers must initialize it early unless relying on libc `program_invocation_name`.

Test signals: diagnostics output and startup paths are the meaningful checks; there is no isolated unit test in this item.
