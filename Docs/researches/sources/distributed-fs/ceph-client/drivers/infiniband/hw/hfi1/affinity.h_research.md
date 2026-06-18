<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.h

## Purpose

This header declares the HFI1 affinity policy interface and shared data structures used by HFI1 initialization, MSI-X management, completion-vector mapping, and user process placement.

## Important APIs, types, and functions

`enum irq_type` classifies interrupts as SDMA, receive context, netdev context, general, or other. `enum affinity_flags` names broader affinity policies. `struct cpu_mask_set` pairs an allowed CPU mask with a used mask and generation counter. `struct hfi1_affinity_node` stores one NUMA node's interrupt and completion-vector masks plus per-CPU completion-vector counters. `struct hfi1_affinity_node_list` stores global node list state, real CPU mask, process CPU mask, topology counts, and the mutex protecting node affinity state.

The header exports init/cleanup, IRQ affinity get/put, process affinity get/put, completion-vector setup/cleanup/lookup, and the global `node_affinity` object.

## Control Flow

The header has no independent execution path. It defines the call surface used by module initialization to create global affinity state, by per-device probe to initialize node/device masks, by MSI-X allocation to assign and release IRQ CPUs, by RDMAVT to map completion vectors, and by user-context code to recommend CPU placement.

## State and Persistence

The structures describe runtime-only affinity state. `node_affinity` is global, while `hfi1_affinity_node` records are dynamically allocated per NUMA node and referenced by device data. CPU mask contents change as interrupts, completion vectors, and processes are assigned and released.

## Dependencies and Integration Points

The header includes `hfi.h`, so it relies on HFI1 device and context types plus Linux cpumask/list/mutex infrastructure made available through driver headers. It is consumed by `affinity.c` and other HFI1 files that need CPU assignment services.

## Risks

Because the structs are shared with device code, field changes require coordinated updates in init, teardown, and lookup paths. The global `node_affinity` extern makes initialization order important. `IRQ_OTHER` exists in the enum, but `affinity.c` treats unknown/default IRQ types as invalid for assignment, so callers should not expect a fallback policy for it.

## Test Signals

Build coverage across HFI1 is required after any header change. Runtime signals are successful device affinity initialization, MSI-X setup and teardown, completion-vector CPU lookup, user process affinity assignment, and clean module unload freeing all per-node records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.h -->
