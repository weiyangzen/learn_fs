<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Makefile

## Purpose

Builds the rdmavt library object from its component implementation files.

## Important APIs, Types, And Functions

`rdmavt-y` includes `vt.o`, `ah.o`, `cq.o`, `mad.o`, `mcast.o`, `mmap.o`, `mr.o`, `pd.o`, `qp.o`, `rc.o`, `srq.o`, and `trace.o`. `CFLAGS_trace.o = -I$(src)` ensures trace header lookup.

## Control Flow

When `CONFIG_INFINIBAND_RDMAVT` is enabled, kbuild compiles and links these objects into `rdmavt.o`.

## State And Persistence Behavior

No runtime state exists here.

## Dependencies And Integration Points

Integrates the local rdmavt verbs, queue-pair, RC, SRQ, MR, CQ, mmap, multicast, MAD, AH, PD, and trace files.

## Risks And Edge Cases

Omitting a component breaks exported symbols or driver callbacks. Trace include flags are required for generated trace code to compile.

## Test Signals

Module build tests should confirm all listed objects compile and that tracepoints resolve.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Makefile -->
