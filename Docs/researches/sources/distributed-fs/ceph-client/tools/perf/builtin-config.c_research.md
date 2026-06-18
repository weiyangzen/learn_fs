# sources/distributed-fs/ceph-client/tools/perf/builtin-config.c

Purpose: implements `perf config`, listing, reading, and setting perf configuration variables in the user or system config file.

Important APIs, types, and functions: `use_system_config`, `use_user_config`, and `actions` capture option state. `set_config()` rewrites a config file from a `perf_config_set`. `show_spec_config()` prints one `section.name=value`. `show_config()` prints all collected values. `parse_config_arg()` validates and splits `section.name[=value]`. `perf_config__set_variable()` is an exported helper for setting one variable. `cmd_config()` is the command entry point.

Control flow: command options choose list, system config, or user config. The command rejects simultaneous system and user selection, determines `config_exclusive_filename`, creates a config set, and then either lists all values, shows selected variables, or collects updates and writes the config file once if anything changed. With no action and no args it falls through to list behavior.

State and persistence: this command rewrites the selected config file, defaulting to `$HOME/.perfconfig` unless `--system` or `--user` overrides. `set_config()` writes an auto-generated first line and serializes sections/items while optionally skipping system-origin entries when not writing system config.

Dependencies and integration points: uses perf config set collection and iteration APIs, cache path helpers, parse-options, and global `config_exclusive_filename`. Other perf code can call `perf_config__set_variable()`.

Risks: writes are not atomic and can clobber formatting/comments beyond the auto-generated line. `mkpath(... getenv("HOME"))` assumes `HOME` is set. `parse_config_arg()` uses `strchr(arg, '.')`, despite the variable name `last_dot`, so section parsing splits at the first dot. Empty value validation uses `strcmp(*value, "=")`, which is unusual pointer/string logic but detects a bare equals. The config set is not explicitly collected before `show_config()`, relying on constructor behavior.

Test signals: list empty and populated configs, get one variable, set one or multiple variables, use `--user`, `--system`, both options together, malformed names, missing values, unset `HOME`, and verify rewritten file contents.
