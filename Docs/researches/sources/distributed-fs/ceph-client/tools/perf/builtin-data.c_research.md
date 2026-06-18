# sources/distributed-fs/ceph-client/tools/perf/builtin-data.c

Purpose: implements `perf data convert`, dispatching conversion of perf.data into JSON or CTF formats depending on build support.

Important APIs, types, and functions: `data_cmd_fn_t` and `struct data_cmd` define subcommand dispatch. `data_cmds[]` currently contains only `convert`. `data_options[]` defines shared and convert options: verbosity, input, `--to-json`, optional `--to-ctf`, `--tod`, force, all events, and time range. `opts` is a `struct perf_data_convert_opts` passed to converters. `cmd_data_convert()` validates conversion options and calls `bt_convert__perf2json()` or `bt_convert__perf2ctf()`. `cmd_data()` parses the subcommand and dispatches.

Control flow: `cmd_data()` uses `parse_options_subcommand()` with `convert` as the only recognized subcommand. `cmd_data_convert()` re-parses convert options, rejects positional leftovers, rejects both JSON and CTF at once, requires an available output format, and invokes the selected converter. If CTF support or traceevent support is missing, it reports a build-support error.

State and persistence: input defaults through global `input_name`; output paths come from `--to-json` or `--to-ctf`. The command writes converted output through converter helpers. Option state is held in file-static globals, so repeated in-process calls can retain values unless reinitialized by process startup.

Dependencies and integration points: depends on `data-convert.h` converter APIs, parse-options subcommand support, global `verbose` and `input_name`, and optional `HAVE_LIBBABELTRACE_SUPPORT` plus `HAVE_LIBTRACEEVENT`.

Risks: shared `data_options` are parsed at both top-level and subcommand levels, so option placement needs coverage. The non-babeltrace error block has unusual indentation, increasing maintenance risk. JSON and CTF converter behavior is external to this file. Static globals make in-process repeated invocations potentially surprising.

Test signals: convert small perf.data to JSON, reject both `--to-json` and `--to-ctf`, reject no output format, test CTF builds with and without required libraries, validate `--all`, `--time`, `--force`, `--tod`, top-level option placement, unknown subcommands, and positional leftovers.
