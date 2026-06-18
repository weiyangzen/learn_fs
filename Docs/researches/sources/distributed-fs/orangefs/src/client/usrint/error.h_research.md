# sources/distributed-fs/orangefs/src/client/usrint/error.h
## sources/distributed-fs/orangefs/src/client/usrint/error.h

**Purpose:** Local declaration of glibc-compatible `error()` APIs used by OrangeFS user-interface code.

**APIs and control flow:** Declares `error(status, errnum, format, ...)`, `error_at_line(status, errnum, fname, lineno, format, ...)`, the optional `error_print_progname` hook, `error_message_count`, and `error_one_per_line`. Uses `__BEGIN_DECLS`/`__END_DECLS` and printf-format attributes. Optionally includes `<bits/error.h>` for inline variants.

**State and dependencies:** Depends on glibc `<features.h>` conventions and C linkage macros. It mirrors a subset of glibc's public error API for local builds.

**Risks and tests:** Portability is tied to glibc-specific macros and `bits/error.h`. The implementation must provide the declared globals or link against compatible libc definitions. Tests should include compilation under target libc versions, C++ inclusion, format-attribute warnings, and linkage with `error.c`.
