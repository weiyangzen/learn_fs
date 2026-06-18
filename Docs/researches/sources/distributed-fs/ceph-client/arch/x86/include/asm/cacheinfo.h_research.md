
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheinfo.h

Purpose: cache-control and cache-init declarations for MTRR/PAT management.

Important APIs and control flow: exports `memory_caching_control` flag bits `CACHE_MTRR` and `CACHE_PAT`, plus functions to disable/enable caches, delay AP cache initialization, initialize/restore boot CPU cache state, and initialize AP cache state.

State, dependencies, and risks: state is global cache-control mode plus per-CPU MTRR/PAT hardware state. Dependencies include early CPU init and memory-type setup. Risks include disabling caches at unsafe times, AP/BP ordering bugs, and inconsistent MTRR/PAT state across CPUs. Test signals are boot on PAT/MTRR systems, CPU hotplug, memory-type selftests, and cache attribute warnings.
