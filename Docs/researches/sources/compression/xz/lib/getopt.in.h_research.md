<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt.in.h -->
# sources/compression/xz/lib/getopt.in.h

Purpose: template for generated `getopt.h`.

Important APIs/types/functions: defines `_GETOPT_H`, optional prefix pre-includes, `_GL_ARG_NONNULL`, and includes `getopt-cdefs.h`, `getopt-pfx-core.h`, and `getopt-pfx-ext.h`.

Control flow: preprocessor-only; `lib/Makefile.am` prepends a generated-file comment.

State and persistence: compile-time declarations only; generated `getopt.h` persists in build output.

Dependencies and integration: central public header for bundled getopt replacement.

Risks: assumes included fragment headers are discoverable via include path. Prefix pre-includes are intended to prevent later system declarations from conflicting.

Test signals: generated header should compile both prefixed and unprefixed consumers with nonnull attributes where supported.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt.in.h -->
