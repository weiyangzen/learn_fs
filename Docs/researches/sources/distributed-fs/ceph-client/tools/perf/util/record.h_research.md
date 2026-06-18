# sources/distributed-fs/ceph-client/tools/perf/util/record.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/record.h` defines shared recording options and declarations used by perf record-like commands and Python record configuration.

## Important APIs, Types, and Functions

`struct record_opts` contains target selection, inheritance, sampling toggles, address/page-size/weight/data-source flags, auxtrace settings, namespace/cgroup/switch/data mmap options, callchain/user/kernel flags, overwrite/build-id/kcore/text-poke toggles, sampling frequency/period fields, register masks, branch stack mask, clockid settings, control fds, synthesis/threading settings, compression, affinity, and off-CPU threshold. It declares `record_usage`, `record_options`, `record__parse_freq`, and inline `record_opts__no_switch_events`.

## Control Flow

The header has no executable flow except the inline switch-event helper, which reports an explicit request to disable switch events.

## State and Persistence Behavior

`record_opts` is a caller-owned configuration aggregate. It controls runtime recording behavior but does not persist state itself.

## Dependencies and Integration Points

It includes time, bool, Linux perf event types, and `util/target.h`. It is consumed by record command option parsing, evsel/evlist configuration, auxtrace setup, and scripting wrappers.

## Risks and Edge Cases

The structure is broad and field interactions are complex; defaults must be initialized carefully before calling configuration helpers. Several boolean `*_set` fields distinguish default false from explicit user false. Control fd defaults must be invalid values when unused.

## Test Signals

Compile and configuration tests should validate initialized defaults, switch-event explicit-disable behavior, auxtrace option combinations, frequency/period fields, and record option parsing integration.
