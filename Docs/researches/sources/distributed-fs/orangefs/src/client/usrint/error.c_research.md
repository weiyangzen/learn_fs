# sources/distributed-fs/orangefs/src/client/usrint/error.c
## sources/distributed-fs/orangefs/src/client/usrint/error.c

**Purpose:** Provides a simplified OrangeFS-local implementation of glibc-style `error()` and `error_at_line()` for noninteractive user-interface utilities.

**APIs and control flow:** `error()` flushes stdout, prints program name through `error_print_progname` or `program_invocation_name`, formats the message, appends `strerror(errnum)` if nonzero, increments `error_message_count`, flushes stderr, and exits if `status` is nonzero. `error_at_line()` optionally suppresses duplicate file/line reports when `error_one_per_line` is set, prints file and line context, then delegates to `error_tail()`.

**State and dependencies:** Uses global variables declared by glibc-compatible `error.h`: `error_print_progname`, `error_message_count`, and `error_one_per_line`, plus `program_invocation_name`. Depends on varargs, stdio, strerror, and exit through `usrint.h`.

**Risks and tests:** Both callers call `va_end(args)` after `error_tail()` already calls `va_end(args)`, which is undefined behavior. Duplicate suppression static state is not thread-safe. `fprintf` format for absent file name still receives unused arguments. Tests should cover errnum/no-errnum, exit status through subprocess tests, one-per-line suppression, custom program-name printer, and sanitizer detection of varargs misuse.
