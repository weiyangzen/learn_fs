<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-help.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-help.c

## Purpose
Implements `perf help`, including common command listing, all-command listing, and dispatch to man, info, or HTML/web documentation viewers.

## Important APIs, Types, and Functions
The entry point is `cmd_help()`. `enum help_format` tracks selected output (`man`, `info`, `web/html`, or none). Viewer configuration is stored in linked lists `man_viewer_list` and `man_viewer_info_list`. Important helpers are `parse_help_format()`, `perf_help_config()`, `add_man_viewer()`, `add_man_viewer_info()`, `add_man_viewer_path()`, `add_man_viewer_cmd()`, `exec_viewer()`, `show_man_page()`, `show_info_page()`, `show_html_page()`, `get_html_page_path()`, `setup_man_path()`, `cmd_to_page()`, and `list_common_cmds_help()`.

Viewer-specific launchers include `exec_man_man()`, `exec_woman_emacs()`, `exec_man_konqueror()`, `exec_man_cmd()`, and platform-overridable `open_html()`. `check_emacsclient_version()` probes `emacsclient --version` before using Emacs woman mode.

## Control Flow
`cmd_help()` loads the command list with `load_command_list("perf-", ...)`, applies config through `perf_config(perf_help_config, &help_format)`, parses subcommands and help format options, and then either prints all commands, prints usage plus common commands, or opens documentation for the requested command. `show_man_page()` builds the man page name (`perf` or `perf-<cmd>`), prepends perf's man path to `MANPATH`, tries configured viewers in order, tries `PERF_MAN_VIEWER`, and finally tries `man`. `show_info_page()` sets `INFOPATH` and execs `info perfman <page>`. `show_html_page()` validates `PERF_HTML_PATH`, constructs `<page>.html`, and delegates to `open_html()`.

## State and Persistence Behavior
State is process-local: viewer linked lists are populated from config, command lists are loaded for listing, and environment variables `MANPATH` or `INFOPATH` are set before exec. Successful viewer paths replace the process with `execlp()`/`execl()`; failures return and try the next viewer. The command does not persist data or modify repository files.

## Dependencies and Integration Points
Depends on perf config/cache/system-path helpers, subcmd command discovery and parse-options, run-command, strbuf, debug/util helpers, and platform `open_html` overrides. It integrates with installed perf documentation directories (`PERF_MAN_PATH`, `PERF_INFO_PATH`, `PERF_HTML_PATH`), external programs (`man`, `info`, `emacsclient`, `kfmclient`, custom viewer commands, `web--browse`), and config keys `help.format`, `man.viewer`, `man.<tool>.path`, and `man.<tool>.cmd`.

## Risks and Edge Cases
This snapshot contains a duplicated `if (!strcmp(subkey, ".path")) {` in `add_man_viewer_info()`, a compile-time risk signal. Viewer command execution is intentionally shell-based for custom commands (`/bin/sh -c`), so config values are trusted. `cmd_to_page()` allocates with `asprintf()` for non-`perf` commands and callers intentionally leak when they exec; non-exec failure paths may also leak small strings. `exec_man_konqueror()` may duplicate and modify a path string without freeing before exec/fallback. `add_man_viewer()` and `do_add_man_viewer_info()` do not check allocation failures before `strcpy()`/`strncpy()`.

Behavior depends heavily on documentation installation paths and external viewer availability. The built-in common command list is manually maintained and conditioned by compile-time features, so it can drift from actual commands.

## Test Signals
Test `perf help`, `perf help --all`, `perf help <cmd>`, `--man`, `--info`, `--web`, config-driven `help.format`, multiple `man.viewer` entries, `PERF_MAN_VIEWER`, supported and unsupported `man.<viewer>.path/cmd` settings, missing HTML documentation, absent `DISPLAY` for konqueror, old or missing `emacsclient`, and command-list feature guards (`HAVE_LIBELF_SUPPORT`, `HAVE_LIBTRACEEVENT`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-help.c -->
