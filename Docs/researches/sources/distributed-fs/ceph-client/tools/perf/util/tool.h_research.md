# sources/distributed-fs/ceph-client/tools/perf/util/tool.h

## Purpose

`tool.h` defines the `struct perf_tool` event-processing callback interface shared by perf commands.

## Important APIs, Types, and Functions

It declares callback typedefs for sample events, generic events, attr events, session events, auxtrace events, compressed events, and ordered-event rounds. `struct perf_tool` contains callbacks for samples, mmap, comm, namespaces, cgroup, fork/exit, lost data, aux/itrace, context switch, ksymbol, BPF, text poke, attr/update, tracing data, build-id/id-index, auxtrace, maps, stat, time conversion, features, compressed records, schedstat, and behavior flags. `struct delegate_tool` embeds a `perf_tool` plus a delegate pointer.

## Control Flow and State

The header defines the shape of the dispatch table but no implementation logic. Command code fills or overrides callbacks after `perf_tool__init()`.

## Dependencies and Integration Points

It is the ABI between `perf_session` event readers and command-specific processors such as report, script, top, record, inject, and stat.

## Risks and Test Signals

Adding a perf event type requires updating this struct, initialization, delegation, and session dispatch together. Compile tests and callback coverage tests should catch missing fields.
