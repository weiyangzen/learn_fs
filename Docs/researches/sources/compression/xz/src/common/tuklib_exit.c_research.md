<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.c -->
# sources/compression/xz/src/common/tuklib_exit.c

Purpose: exits a program after flushing/closing stdout and stderr, converting close errors into a caller-specified error status.

Important APIs/types/functions: `tuklib_exit(int status, int err_status, int show_error)`, `ferror`, `fclose`, `progname`, `_`, and `strerror(errno)`.

Control flow: if current status is not already error status, close stdout and optionally print a localized diagnostic on failure; then close stderr and adjust status if needed; call `exit`.

State and persistence: consumes stdio stream state; process terminates.

Dependencies and integration: requires tuklib gettext and progname modules; used by command-line tools to catch delayed write errors.

Risks: once stdout fails, diagnostic depends on stderr still being usable. `errno` use after `fclose` is meaningful only for close failures, handled separately from `ferror`.

Test signals: pipe xz output to a command that closes early and verify error status/message handling.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.c -->
