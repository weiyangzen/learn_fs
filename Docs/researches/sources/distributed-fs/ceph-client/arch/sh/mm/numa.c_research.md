# sources/distributed-fs/ceph-client/arch/sh/mm/numa.c

Purpose: initializes per-node boot memory metadata for SH NUMA configurations.

Important function: `setup_bootmem_node`.

Control flow: derives node memory ranges from memblock/PFN data, allocates node data, and records node start/span information for the generic NUMA MM.

State and persistence: populates `NODE_DATA` and online node memory metadata.

Dependencies and integration: depends on memblock, PFN helpers, sections symbols, and generic NUMA support.

Risks: incorrect node ranges break allocation locality or boot memory accounting.

Test signals: NUMA boot logs, node memory in sysfs, and allocation tests across configured nodes.
