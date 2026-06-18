# sources/distributed-fs/ceph-client/tools/perf/util/data-convert.h

## Purpose

`data-convert.h` declares the shared option structure and converter entry points used by perf data conversion commands.

## Important APIs, Types, and Functions

`struct perf_data_convert_opts` contains `force`, `all`, `tod`, and optional `time_str`. `bt_convert__perf2ctf()` is declared only when Babeltrace support is compiled in. `bt_convert__perf2json()` is always declared.

## Control Flow

The header has no control flow. It lets command code select a converter and pass the same option bundle to either CTF or JSON conversion. Conditional compilation hides the CTF entry when the dependency is unavailable.

## State and Persistence Behavior

The header stores no state. Its option fields influence persistent outputs: overwrite behavior, whether non-sample events are exported, wall-clock timestamp conversion for CTF, and time-range filtering.

## Dependencies and Integration Points

It depends only on `<stdbool.h>` and integrates command-line parsing with `data-convert-bt.c` and `data-convert-json.c`.

## Risks and Edge Cases

Callers must honor compile-time availability of `bt_convert__perf2ctf()`. Not every option is supported by every backend; JSON rejects `all` and `tod`, while CTF supports both subject to metadata availability.

## Test Signals

Build tests should cover configurations with and without `HAVE_LIBBABELTRACE_SUPPORT`. CLI tests should confirm option forwarding, JSON unsupported-option errors, CTF TOD clock metadata validation, and force overwrite behavior.
