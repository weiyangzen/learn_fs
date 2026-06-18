# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.c

Purpose: top-level CLI dispatcher and global output/error handling for `ynltool`.

Important APIs/functions: globals track `bin_name`, last command context for `usage()`, JSON writer, and output flags. `clean_and_exit()` closes JSON output before exiting. `do_help()` and `do_version()` support root commands. `cmd_select()` dispatches by prefix across `struct cmd` tables. `is_prefix()` and `detect_common_prefix()` implement abbreviated command matching and ambiguity reporting. `p_err()` and `p_info()` route errors/info to JSON or stderr.

Control flow: `main()` parses `--json`, `--pretty`, `--help`, and `--version` via `getopt_long`, initializes JSON output lazily, adjusts argc/argv, then calls `do_version()` or `cmd_select()` over root commands (`help`, `page-pool`, `qstats`, `version`). JSON writer is destroyed before return.

State/dependencies: global JSON mode affects all subcommands. Last-command globals let `usage()` call the current subcommand help. Depends on `json_writer`, `page-pool`, and `qstats` modules.

Risks/test signals: prefix matching can select the first matching command unless subcommands call ambiguity checks. `p_err()` can emit multiple JSON objects if multiple errors occur. Signals are `ynltool help`, `version`, JSON/pretty output, invalid option handling, and subcommand dispatch.
