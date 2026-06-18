# Research: sources/compression/xz/src/xz/args.h
## sources/compression/xz/src/xz/args.h

Purpose: Declares the argument parsing contract for the xz front end.

Important APIs and types: `args_info` carries `arg_names`, `arg_count`, optional `files_name`, `files_file`, and `files_delim`. The header exports process-wide flags set by `args.c`: `opt_stdout`, `opt_force`, `opt_keep_original`, `opt_synchronous`, `opt_robot`, and `opt_ignore_check`. It also exports `stdin_filename`, `args_parse()`, and debug-only `args_free()`.

Control flow and integration: `main.c` creates an `args_info`, passes it to `args_parse()`, then uses the resulting arrays and optional `files_file` stream to drive `coder_run()` or `list_file()`. Other modules test the exported booleans directly: `file_io.c` uses force/stdout/keep/sync semantics, `message.c` uses robot mode, `coder.c` uses ignore-check, and `list.c` mutates stdout/force for listing.

State and persistence: The struct references existing `argv` storage except for duplicated `--files` names from environment parsing. The `stdin_filename` sentinel is a stable global pointer used for identity checks, not just string comparison.

Risks: The API is heavily global and order-dependent; callers must run `hardware_init()` before `args_parse()` and must not treat `stdin_filename` as mutable. `files_file` ownership is split: `args.c` opens it, while `main.c` closes non-stdin streams.

Test signals: Header-level tests are integration tests: verify implicit stdin, `--files` stream handling, and that exported flags cause expected I/O and coder behavior.
