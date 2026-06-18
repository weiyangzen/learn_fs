<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/trace/events/maple_tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/trace/events/maple_tree.h

## Purpose

`trace/events/maple_tree.h` stubs maple-tree tracepoints for userspace builds.

## Important APIs, Types, and Functions

It defines `trace_ma_op(a, b)`, `trace_ma_read(a, b)`, and `trace_ma_write(a, b, c, d)` as empty `do { } while (0)` macros.

## Control Flow and State

Trace calls compile to no-ops and record no state.

## Dependencies and Integration Points

It is included by imported maple-tree code through the shared test include path. It avoids pulling in kernel tracing infrastructure.

## Risks and Test Signals

The risk is losing trace visibility in userspace tests. Functional maple-tree tests should still pass; trace behavior is not validated here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/trace/events/maple_tree.h -->
