# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_misc.h

## Purpose

`trace_misc.h` defines miscellaneous HFI1 tracepoints for interrupt sources, RcvArray writes, and optional fault-injection diagnostics.

## Important Events

- `hfi1_interrupt` records the device, interrupt source name, and source number using the supplied interrupt-source table callback.
- `hfi1_csr_template` is a small CSR write template instantiated as `hfi1_write_rcvarray`, which records an MMIO address and value.
- Under `CONFIG_FAULT_INJECTION`, `hfi1_fault_opcode` records injected opcode faults by QP and opcode, and `hfi1_fault_packet` records packet receive error flags, context, lengths, eager index, and related packet metadata.

## Control Flow and State

The events are passive instrumentation. They snapshot interrupt, CSR, or fault-injection data when called. There is no persistent state in this header.

## Dependencies and Integration Points

This file depends on HFI1 device structures, interrupt-source tables, packet helpers, and common device trace macros. `hfi1_write_rcvarray` is especially useful with expected receive and TID RDMA code because `tid_rdma.c` programs and invalidates RcvArray entries while allocating or clearing TID flows.

## Risks and Test Signals

The main risk is calling tracepoints with invalid device or packet pointers during error paths. Test signals include interrupt trace output naming the correct source, RcvArray write traces matching expected receive programming, and fault-injection traces appearing only when the kernel option is enabled.
