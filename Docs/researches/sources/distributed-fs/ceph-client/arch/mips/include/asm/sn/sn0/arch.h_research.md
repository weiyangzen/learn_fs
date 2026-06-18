<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/arch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/arch.h

Purpose: Defines SN0/IP27 architecture limits for CPUs, NASIDs, regions, partitions, memory slots, and CPUs per node.

Important APIs/types/functions: `MAXCPUS`, `MAX_NASIDS`, `MAX_REGIONS`, `MAX_PARTITIONS`, `NASID_MASK_BYTES`, `MAX_MEM_SLOTS`, `SLOT_SHIFT`, `SLOT_MIN_MEM_SIZE`, and `CPUS_PER_NODE`.

Control flow: Topology and memory-discovery code uses these compile-time limits to size masks/arrays and interpret slot/NASID geometry.

State and persistence: No mutable state is stored; constants constrain topology state held elsewhere.

Dependencies and integration points: Included by generic SN architecture and KLCONFIG headers.

Risks: Changing limits affects array sizes and firmware topology assumptions. N-mode versus M-mode changes maximum memory slots.

Test signals: SN topology discovery, memory slot reporting, and build coverage for SN0 modes are relevant.

Source read size: 56 lines, 1496 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/arch.h -->
