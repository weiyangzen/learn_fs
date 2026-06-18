# sources/distributed-fs/lizardfs/src/tools/tools_commands.cc

Purpose: Command registry and usage printer for the unified `lizardfs` tool executable and interactive shell.

Important APIs/types/functions: `printUsage`; `printTools`; `getCommand`; `printArgs`; static built-ins `cd_func`, `ls_func`, `exit_func`; map `lizard_commands`.

Control flow: `printUsage` prints general usage or dispatches a named command with a single `help` argument. `getCommand` looks up command names in an unordered map. Built-ins implement shell-like `cd`, `ls`, and process exit.

State and persistence: The command map is static process state. `cd_func` changes current working directory; `exit_func` terminates the process.

Dependencies and integration: Exposes all `*_run` tool entry points declared in `tools_commands.h`. Used by `main.cc` and installed wrapper names.

Risks and test signals: `ls_func` builds a shell command by concatenating arguments, which is command-injection-prone in interactive use. `printUsage` calls target functions with `argc=1`, relying on each command to show usage. No direct tests in this subset.
