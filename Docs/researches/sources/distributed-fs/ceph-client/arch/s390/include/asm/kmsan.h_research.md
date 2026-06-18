# sources/distributed-fs/ceph-client/arch/s390/include/asm/kmsan.h

Purpose: This header provides s390 KMSAN address metadata hooks, especially for lowcore aliases.

Important APIs/types/functions: `is_lowcore_addr()`, `arch_kmsan_get_meta_or_null()`, and `kmsan_virt_addr_valid()` are defined for non-module code.

Control flow: When KMSAN sees a lowcore address, the hook resolves the current CPU prefixed lowcore to its real per-CPU lowcore page before asking generic KMSAN for metadata. Address validity checks disable preemption to avoid scheduler recursion while `pfn_valid()` uses RCU.

State and persistence: State is KMSAN shadow/origin metadata and per-CPU lowcore mappings; the header only redirects lookup behavior.

Dependencies and integration points: It depends on lowcore, KMSAN core, memory-zone validity, preemption controls, and raw CPU IDs.

Risks and test signals: Lowcore alias handling is subtle: returning shared metadata for all lowcores would create false positives or missed reports. Tests should include KMSAN boot, lowcore field accesses, CPU hotplug, module/non-module builds, and invalid virtual address checks.
