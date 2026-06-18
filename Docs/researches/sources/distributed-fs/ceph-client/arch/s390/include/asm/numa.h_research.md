# sources/distributed-fs/ceph-client/arch/s390/include/asm/numa.h

Purpose: This header exposes s390 NUMA setup only when NUMA is configured.

Important APIs/types/functions: `numa_setup()` is declared under `CONFIG_NUMA`; otherwise an empty inline stub is provided.

Control flow: Boot code calls `numa_setup()` unconditionally, and the stub compiles the call away for non-NUMA kernels.

State and persistence: NUMA topology state is maintained by implementation and generic NUMA core, not this header.

Dependencies and integration points: It integrates s390 topology discovery with Linux NUMA initialization.

Risks and test signals: Stub behavior must keep non-NUMA builds clean while NUMA builds populate nodes correctly. Tests should include NUMA and non-NUMA builds, boot topology, memory policy, and CPU/memory hotplug if supported.
