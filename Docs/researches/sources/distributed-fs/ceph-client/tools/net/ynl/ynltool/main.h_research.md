# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.h

Purpose: shared header for `ynltool` modules. It defines command parsing macros, shared globals, diagnostics, and subcommand entry points.

Important APIs/macros: `NEXT_ARG`, `NEXT_ARGP`, `GET_ARG`, `BAD_ARG`, and `REQ_ARGS` mutate argc/argv and call `usage()` or `p_err()` on bad input. `HELP_SPEC_OPTIONS` documents JSON flags. `struct cmd` is the dispatch table shape used by `cmd_select()`. It declares `p_err`, `p_info`, `is_prefix`, `detect_common_prefix`, `usage`, `do_page_pool`, and `do_qstats`.

State/dependencies: exposes global `bin_name`, `json_wtr`, `json_output`, and `pretty_output` for subcommands. Includes `json_writer.h` and standard headers, and defines `_GNU_SOURCE` if absent.

Integration: included by `main.c`, `page-pool.c`, and `qstats.c`.

Risks/test signals: argument macros have side effects and assume local variables named `argc`/`argv`; misuse can skip arguments or call global usage. Build warnings and command parsing tests are the main signals.
