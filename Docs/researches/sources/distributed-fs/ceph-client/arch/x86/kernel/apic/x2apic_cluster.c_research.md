# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_cluster.c

## Purpose
This file implements the logical cluster x2APIC driver. It groups CPUs by x2APIC cluster, builds logical destination masks, and sends one IPI per cluster when possible for efficient large-system delivery.

## Important APIs, Types, And Functions
`apic_cluster(apicid)` derives the cluster from the APIC ID. `x86_cpu_to_logical_apicid` maps Linux CPU to logical x2APIC ID. Per-CPU `ipi_mask` is a scratch mask, and per-CPU `cluster_masks` points to the shared mask for that CPU's cluster. Key functions are `x2apic_send_IPI()`, `__x2apic_send_IPI_mask()`, `x2apic_calc_apicid()`, `init_x2apic_ldr()`, `prefill_clustermask()`, `alloc_clustermask()`, `x2apic_prepare_cpu()`, `x2apic_dead_cpu()`, and `x2apic_cluster_probe()`. The `apic_x2apic_cluster` driver uses logical destination mode and MSR APIC accessors.

## Control Flow
The driver probes only when `x2apic_mode` is active. Probe allocates the logical APIC ID array, registers a CPU hotplug prepare state, initializes the current CPU LDR state, and returns success. CPU prepare computes `(cluster << 16) | bit-within-cluster`, allocates or reuses a shared cluster mask, and allocates per-CPU scratch space. Mask IPI delivery copies the target mask, optionally removes self, collapses targets by shared cluster mask, ORs logical destination bits, and sends one x2APIC ICR per cluster.

## State And Persistence
The logical APIC ID array persists after probe. Cluster masks are dynamically allocated per cluster and reused across CPUs in the same cluster. CPU death clears the CPU from its cluster mask and frees scratch masks.

## Dependencies And Integration Points
It depends on CPU hotplug, cpumask allocation, x2APIC MSR ICR helper from `local.h`, `default_cpu_present_to_apicid()`, native x2APIC read/write/EOI callbacks, and APIC driver probing. It integrates with large-system IPI delivery and vector/MSI destination calculations through `calc_dest_apicid`.

## Risks
Cluster mask lifetime and sharing must be correct across boot and hotplug. Logical destination computation assumes 16 APIC IDs per cluster. Missing `weak_wrmsr_fence()` would violate x2APIC MSR ordering, but the send paths include it. Allocation failure during probe or CPU prepare disables or blocks this backend.

## Test Signals
Validate x2APIC cluster-mode boot, CPU hotplug, IPI delivery to masks spanning multiple clusters, NMI all-but-self, effective interrupt affinity, and logs showing cluster x2APIC routing.
