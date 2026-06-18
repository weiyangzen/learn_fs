<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-core.h -->
# sources/compression/xz/lib/getopt-core.h

Purpose: public declarations for basic portable `getopt` state and function.

Important APIs/types/functions: declares globals `optarg`, `optind`, `opterr`, `optopt`, and `getopt(int, char *const *, const char *)`.

Control flow: header-only declarations documenting short-option parsing behavior, optional arguments, `--`, permutation, `+`, `-`, and `POSIXLY_CORRECT`.

State and persistence: exposes process-global parser state through standard getopt globals.

Dependencies and integration: included through generated `getopt.h`; used by xz argument parsing when system getopt is missing/replaced.

Risks: prototypes use standards-compatible `char *const *` even though permutation requires a writable argv array. Global state is not thread-safe.

Test signals: run short-option parsing tests including missing arguments, non-option ordering, and reset via `optind`.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-core.h -->
