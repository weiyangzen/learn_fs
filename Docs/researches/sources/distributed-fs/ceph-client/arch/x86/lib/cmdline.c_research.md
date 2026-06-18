# sources/distributed-fs/ceph-client/arch/x86/lib/cmdline.c

Purpose: supplies small x86 command-line parsing helpers for early and normal boot code.

Important APIs/functions: exports `cmdline_find_option_bool` and `cmdline_find_option`. Internal state-machine helpers `__cmdline_find_option_bool` and `__cmdline_find_option` parse bounded command-line buffers. `myisspace()` treats any byte `<= ' '` as whitespace.

Control flow: boolean lookup scans words up to `COMMAND_LINE_SIZE`, matching an entire option word and returning its 1-based position or zero; null `cmdline` returns `-1`. Value lookup scans for `option=argument`, returns the full argument length, copies a truncated NUL-terminated value into the supplied buffer if present, and intentionally returns the last occurrence. Public wrappers first search the supplied command line and, if enabled and not already added, fall back to `builtin_cmdline`.

State and persistence behavior: no local mutable state. Reads `builtin_cmdline` and `builtin_cmdline_added` from setup code. Writes only the caller-provided output buffer.

Dependencies/integration points: used by x86 setup and early option consumers. Depends on `CONFIG_CMDLINE_BOOL`, `COMMAND_LINE_SIZE`, and builtin command-line setup state.

Risks: callers must interpret zero, positive positions, positive lengths, and `-1` correctly. `cmdline_find_option` returns only if `ret > 0`, so empty arguments do not suppress fallback. The parser is whitespace-only and does not handle quoting.

Test signals: unit-style parser tests for whole-word matching, repeated options, truncation, null command lines, empty values, builtin fallback, and maximum-size non-NUL-terminated buffers.
