# sources/distributed-fs/openafs/src/external/heimdal/roken/getopt.c

Purpose: BSD-derived fallback implementation of `getopt()`.

Important APIs/types/functions: global variables `opterr`, `optind`, `optopt`, `optreset`, and `optarg`; public `getopt(int nargc, char * const *nargv, const char *ostr)`.

Control flow: maintains static scanning pointer `place`, starts a new argv element when needed, stops at non-option or `--`, validates option characters against `ostr`, handles options with required arguments, returns `?` or `:` according to leading-colon rules, and prints diagnostics when `opterr` permits.

State and persistence behavior: uses global and static parser state across calls; `optreset` resets scanning.

Dependencies and integration points: command-line portability layer for tools that cannot rely on libc `getopt`.

Risks: global state is not thread-safe. Only short options are supported. Error messages go to stderr and derive program name from argv[0]. Behavior should match BSD enough for callers but may differ from GNU extensions.

Test signals: grouped short options, options with adjacent and separate arguments, missing arguments with/without leading colon, illegal options, `--`, `optreset`, and non-option termination.
