
# sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.h

Purpose: declares the small sublevel-option parser interface.

Important APIs/types/functions: `struct sublevel_option` maps an option `name` to an integer pointer. `perf_parse_sublevel_options` applies a comma-separated user string to an array terminated by `name == NULL`.

Control flow: none; caller provides the terminator and storage.

State and persistence: state is caller-owned integers only.

Dependencies: none beyond C declarations.

Integration points: perf CLI sub-option parsing.

Risks: missing terminator causes out-of-bounds scanning. Test signals are parser unit tests and option-table validation.
