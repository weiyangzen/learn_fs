# sources/distributed-fs/ceph-client/drivers/interconnect/trace.h

## Purpose

This header defines tracepoints for interconnect bandwidth setting. It is included by the interconnect core trace compilation unit and uses Linux trace event macros to expose path, device, node, bandwidth request, aggregate bandwidth, and return-code information to ftrace/perf tooling.

## Important APIs And Events

`TRACE_SYSTEM` is `interconnect`. `TRACE_EVENT(icc_set_bw)` records a single node update in a path with `struct icc_path *p`, `struct icc_node *n`, request index `i`, and requested `avg_bw`/`peak_bw`. Its payload stores `path_name`, requesting device name from `p->reqs[i].dev`, node name, requested average/peak bandwidth, and aggregate node average/peak bandwidth. `TRACE_EVENT(icc_set_bw_end)` records path-level completion with path name, first request device, and return code.

`TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` align with the local include pattern used by the C file that instantiates trace definitions through `<trace/define_trace.h>`.

## Control Flow And Integration

The header itself has no executable flow. When the interconnect core calls the generated tracepoint hooks, enabled trace consumers receive formatted entries. The header depends on `struct icc_path` internals, especially `p->name` and `p->reqs[]`, and on `struct icc_node` bandwidth aggregate fields.

## State, Risks, And Test Signals

Tracepoints persist as ABI-like observability interfaces: changing field names or print formats can break user scripts. `icc_set_bw_end` assumes `p->reqs[0].dev` is valid; call sites must only trace initialized paths. `icc_set_bw` depends on index `i` matching an existing request. Test signals include successful trace header compilation, `tracefs` event presence under `events/interconnect/`, enabling events while running interconnect clients, and entries showing expected path/device/node names and return codes.
