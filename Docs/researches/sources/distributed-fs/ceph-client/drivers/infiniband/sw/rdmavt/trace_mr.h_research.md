# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_mr.h

## Purpose
`trace_mr.h` declares memory-region and SGE trace events for rdmavt memory mapping and lkey validation/debugging paths.

## Important APIs, types, and functions
`rvt_mr_template` records MR identity, IOVA, user base, lkey, segment indexes, virtual address, page, length, and offset for page/FMR/user segment events. `rvt_sge_template` records an SGE, incoming `ib_sge`, MR pointer, virtual and requested addresses, lkey, lengths, indexes, and whether the PD is user-owned. `rvt_map_mr_sg` records fast-reg scatterlist mapping arguments.

## Control flow
The header only defines tracepoint schemas. MR implementation code emits these events while building MR page segments, joining SGEs, and mapping scatterlists for memory registration.

## State and persistence
Trace payloads snapshot MR/SGE fields and can expose kernel virtual addresses and page pointers to privileged tracing consumers. Driver state is unchanged by tracing.

## Dependencies and integration points
It depends on `ib_verbs.h`, `rdma_vt.h`, `rdmavt_mr.h`, local `mr.h`, and tracepoint macros. It integrates with rdmavt MR registration, fast registration, and SGE validation paths.

## Risks
Pointer and address-heavy trace payloads are useful for debugging but must remain limited to kernel tracing contexts. The fast assignment currently sets `__entry->n = sge->m`, which looks suspicious because both `m` and `n` become the same value; changes should verify intended SGE index reporting. Type or layout changes in MR/SGE structures require trace field updates.

## Test signals
Enable MR trace events during user MR registration, FMR/fast-reg mapping, lkey validation, and SG list coalescing. Validate emitted `m`/`n`, lkey, and length fields against expected MR layout.
