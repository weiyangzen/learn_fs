# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.c

Purpose: simple streaming JSON writer used by `ynltool` for machine-readable output. It handles separators, nesting depth, optional pretty indentation, string escaping, and primitive values.

Important APIs/functions: `jsonw_new()` allocates state with output file, depth, pretty flag, and separator. `jsonw_destroy()` asserts all collections are closed, writes a newline, flushes, frees, and nulls the caller pointer. `jsonw_begin()`/`jsonw_end()` back arrays/objects. `jsonw_name()` writes object property names. Primitive emitters include string, bool, null, float, uint, unsigned short, unsigned long long, and int variants; field helpers combine name and value.

Control flow/state: state is per-writer and tracks only current depth and whether a comma is due. Pretty mode controls newlines/indentation. Strings escape common JSON control characters, backslash, and quote.

Dependencies/integration: used through global `json_wtr` in `ynltool/main.c`, `page-pool.c`, and `qstats.c`.

Risks/test signals: callers must balance start/end calls or assertions fire. `jsonw_printf()` can emit raw invalid JSON if callers pass non-JSON text. String escaping does not handle all control characters or UTF-8 validation. Signals are valid JSON output from all `--json` subcommands and assertion-free shutdown.
