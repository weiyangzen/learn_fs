# Research: sources/compression/xz/src/xz/main.c
## sources/compression/xz/src/xz/main.c

Purpose: Provides the `main()` entry point, process initialization, file iteration, `--files`/`--files0` handling, exit-status policy, and high-level dispatch between coding and listing.

Important APIs and functions: `set_exit_status()` upgrades global exit status to warning or error, preserving errors over warnings and using a Windows critical section when needed. `set_exit_no_warn()` suppresses warning exit status. `read_name()` reads one delimited filename from a `--files` stream into a growing static buffer. `main()` wires together all modules.

Control flow: Startup initializes Windows synchronization, program name, stdio/file I/O, early sandbox, gettext, messages, hardware defaults, and arguments. It rejects unsupported `--robot` compression/decompression, tells `message.c` the file count, prevents compressed binary output to a terminal, installs signal handlers for non-list modes, optionally tightens sandbox for read-only/stdout-only operation, picks `coder_run()` or `list_file()`, processes command-line filenames with special `"-"` handling, then processes names from `--files`/`--files0`. After list mode it prints totals, runs debug cleanup, honors pending signals through `signals_exit()`, applies `--no-warn`, and exits via `tuklib_exit()`.

State and persistence: Maintains process exit status and `no_warn`. `read_name()` keeps a static reusable filename buffer until exit. Persistent work is delegated to coder/list/file I/O; `main.c` decides iteration and when streams close.

Dependencies and integration points: It is the central orchestrator for `io`, `sandbox`, `gettext`, `message`, `hardware`, `args`, `signals`, `coder`, and `list`. It enforces sequencing that other modules rely on, especially hardware before argument parsing and signal setup before actual I/O.

Risks: `read_name()` can read arbitrarily large filename lists into memory one name at a time with no configured cap. Handling stdin both as data and as filename list is explicitly rejected. Terminal checks must prevent compressed output to TTY and compressed input from TTY in decode/test paths. Sandbox decisions depend on the complete argument set and must stay aligned with file-open behavior.

Test signals: Cover no arguments, `"-"` inputs, stdout terminal refusal, stdin terminal refusal for decompression/test, `--files` from stdin conflict, long filename entries, embedded NUL in `--files`, `--files0` consecutive delimiters, list-mode totals, `--robot` rejection outside list/info/version, warning suppression, and signal exit behavior.
