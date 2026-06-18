# sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.h

Purpose: Defines libsubcmd option-parser data structures, flags, constructor macros, return codes, and public parser/usage APIs.

Important APIs/types/functions: `enum parse_opt_type`, `enum parse_opt_flags`, `enum parse_opt_option_flags`, `struct option`, `parse_opt_cb`, and `struct parse_opt_ctx_t` define the parser contract. Macros such as `OPT_BOOLEAN`, `OPT_STRING`, `OPT_INTEGER`, `OPT_U64`, `OPT_CALLBACK`, `OPT_GROUP`, and `OPT_END` build option arrays with type checking via `check_vtype`.

Control flow: Header-only setup; callers declare an option array terminated by `OPT_END()` or `OPT_PARENT()`, then pass it to `parse_options()`/`parse_options_subcommand()`.

State and persistence: Parser writes to caller-provided storage pointed to by `struct option.value` and optional `set`. No persistent state in the header.

Dependencies/integration: Includes `<linux/kernel.h>`, `<stdbool.h>`, `<stdint.h>`, and depends on compiler support for GNU `typeof`/`__builtin_types_compatible_p`.

Risks: The macro `OPT_CALLBACK_DEFAULT_NOOPT` initializes `.arg`, but `struct option` has `.argh`; if used, this is a compile-time bug. Type-checking macros are GCC/Clang-specific. Callers must ensure help strings are non-NULL except for end markers and that option arrays are terminated.

Test signals: Compile representative option arrays using every macro, especially callback/default variants, under GCC and Clang with warnings as errors. Runtime tests belong with `parse-options.c`.
