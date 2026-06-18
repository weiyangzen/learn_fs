# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/scripts.c

## Purpose

`scripts.c` implements the TUI script picker used from histogram browsing. It offers built-in `perf script` views, user-configured report scripts, custom command arguments, and discovered scripts from perf's script directories.

## Important APIs, Types, and Functions

`attr_to_script` augments script fields based on sample type, including trace, raw, addr, and data source. `scripts_config` handles `scripts.*` config entries. `check_ev_match` filters scripts against event requirements embedded in script comments. `find_scripts` scans language subdirectories under `perf exec-path/scripts`, skipping `top.*` scripts. `list_scripts` builds the popup menu. Public functions are `run_script` and `script_browse`.

## Control Flow and State

`script_browse` asks `list_scripts` for a command, then wraps it with event filters, optional `-i input_name`, stderr redirection, and `less`. `run_script` leaves SLang raw mode, executes the shell command, resets the terminal with escape sequences, reinitializes SLang, and refreshes the screen. Configured script entries allocate name/path strings and are freed after menu use.

## Dependencies and Integration Points

This file depends on perf config, sessions, evlist/hists, symbol metadata, script directories under perf's exec path, SLang, and global `input_name`. It is called from `browsers/hists.c` and `res_sample.c`.

## Risks and Test Signals

Shell command construction and user-configured scripts are the main risk. Directory entries with unknown `d_type`, event-name matching, missing scripts, and terminal restore after failures need coverage. Test signals include built-in sample modes, custom command entry, configured scripts, discovered scripts with and without event match comments, and returning cleanly to the TUI after `system()`.
