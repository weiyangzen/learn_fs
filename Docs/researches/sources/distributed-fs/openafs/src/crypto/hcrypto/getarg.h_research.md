# sources/distributed-fs/openafs/src/crypto/hcrypto/getarg.h

This header disables Heimdal getarg functionality while preserving enough API shape for code to compile. It defines `struct getargs` with long/short names, option type enum, value pointer, help, and arg-help fields, then provides inline no-op `getarg`, `arg_printusage`, and `rk_print_version`.

Control flow is trivial: `getarg` always returns 0 and the usage/version functions return immediately. There is no persistent state. Integration is with Heimdal test or utility code that includes getarg but is not expected to parse command-line options in OpenAFS builds.

The main risk is behavioral surprise if a program built in this tree expects actual option parsing; options will be silently accepted but ignored. Test signals are compile coverage and ensuring no installed/user-facing OpenAFS tool relies on these stubs for argument handling.
