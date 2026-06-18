# sources/distributed-fs/ceph-client/tools/lib/subcmd/help.c

Purpose: Discovers executable subcommands in configured directories and prints column-formatted command lists for help output.

Important APIs/types/functions: `add_cmdname()`, `clean_cmdnames()`, `cmdname_compare()`, `uniq()`, `exclude_cmds()`, `load_command_list()`, `list_commands()`, and `is_in_cmdlist()`. Internal helpers determine terminal dimensions, executable status, filename extensions, and directory scanning.

Control flow: `load_command_list()` scans the preferred exec path into `main_cmds`, scans each PATH entry into `other_cmds`, sorts/deduplicates both lists, and excludes main commands from other commands. `list_commands()` computes the longest command name and prints separate sections for preferred and other commands using terminal-width-aware columns.

State and persistence: `struct cmdnames` arrays are caller-owned and dynamically grown; `clean_cmdnames()` frees entries and resets counters. No persistent files.

Dependencies/integration: Uses `exec-cmd.c` for `get_argv_exec_path()`, `subcmd-util.h` allocation helpers, Linux `strstarts`, POSIX directory/stat APIs, and terminal dimension APIs.

Risks: `list_commands_in_dir()` appends each directory entry to `buf` without resetting it to the directory prefix, so repeated entries can build an invalid path unless `astrcat()` behavior is externally countered; this is a notable path-construction risk. `is_executable()` only checks user execute bit (`S_IXUSR`), not group/other or access rights. `exclude_cmds()` assumes sorted input. Memory allocation failure in `add_cmdname()` silently skips that command.

Test signals: Use temporary directories with executable/non-executable files, `.exe` suffixes, duplicate commands, PATH exclusions, terminal width variations, and empty command sets.
