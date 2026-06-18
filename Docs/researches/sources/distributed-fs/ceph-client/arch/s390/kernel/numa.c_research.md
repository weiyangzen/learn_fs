# sources/distributed-fs/ceph-client/arch/s390/kernel/numa.c

Purpose: minimal s390 NUMA setup that presents a single online node while allocating `pg_data_t` structures for all possible nodes.

Important API and state: `numa_setup()` clears possible nodes, marks node 0 possible and online, allocates `NODE_DATA(nid)` for each `MAX_NUMNODES` entry from memblock, and sets node 0 span to all DRAM pages.

Control flow: runs during early memory setup; there is no dynamic state beyond node maps and `NODE_DATA`.

Dependencies and integration: depends on generic NUMA node maps, memblock allocation, `memblock_end_of_DRAM()`, and `asm/numa.h`.

Risks and test signals: this intentionally does not model multi-node topology. Test boot memory maps, `/sys/devices/system/node`, `numactl --hardware`, node 0 span, and boot with unusual memory holes.
