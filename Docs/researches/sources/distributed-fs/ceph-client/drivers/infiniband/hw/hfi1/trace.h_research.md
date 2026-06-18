# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.h

## Purpose

`trace.h` is the umbrella include for HFI1 tracepoint definitions. It defines common packet receive-type symbolic formatting and includes the individual trace systems for debug, miscellaneous device events, context setup, packet headers, RC, receive path, transmit path, MMU, iowait, and TID.

## Important APIs and Integration

`packettype_name()` and `show_packettype()` map `RHF_RCV_TYPE_*` values to printable trace symbols. The included trace headers each set their own `TRACE_SYSTEM` and provide their own `TRACE_INCLUDE_FILE` footer, so this umbrella is primarily a convenience include used by implementation files such as `trace.c` and `tid_rdma.c`.

The include order matters because some trace headers use common helpers or macros from earlier includes, and `trace.c` relies on this file after defining `CREATE_TRACE_POINTS` to instantiate all included events in one compilation unit.

## State, Risks, and Test Signals

This header has no runtime state. Risks are build-time and trace-generation oriented: include guard mistakes, duplicate `TRACE_SYSTEM` handling, missing trace header includes, or stale receive-type mappings can break tracepoint generation or reduce diagnostic value. Test signals are successful compilation with tracepoints enabled and runtime availability of expected HFI1 trace systems under ftrace/perf.
