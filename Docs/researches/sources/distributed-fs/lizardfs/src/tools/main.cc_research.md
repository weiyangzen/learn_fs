# sources/distributed-fs/lizardfs/src/tools/main.cc

Purpose: Main entry point and interactive shell for the `lizardfs` tools executable.

Important APIs/types/functions: `main`; `split`; `print_prefix`; `getCommand`; `set_humode`; `force_master_conn_close`.

Control flow: With command-line arguments, it dispatches `argv[1]` to the command registry. With no arguments, it enters a simple prompt loop, tokenizes input on whitespace, dispatches commands, closes any cached master connection after each command, resets human-readable mode from the environment, and prints a new prompt.

State and persistence: Maintains process status, static path buffer, and command-line parsing state (`optind` reset in interactive mode). No persistent state.

Dependencies and integration: Depends on `tools_commands` registry and common formatting setup. The interactive shell also supports built-in `cd`, `ls`, `exit`, and `quit` via the registry.

Risks and test signals: The tokenizer does not handle quotes or escapes; interactive command arguments split only on whitespace. `isspace` is used on `char` values. No direct tests in this subset.
