# sources/distributed-fs/ceph-client/arch/arm64/mm/context.c

Purpose: implements ARM64 user ASID allocation, rollover, pinning, TLB flush coordination, and TTBR switching.

Important APIs/types/functions: `asid_bits`, `asid_generation`, `asid_map`, per-CPU `active_asids`/`reserved_asids`, `tlb_flush_pending`, pinned ASID map/counters, `verify_cpu_asid_bits`, `flush_context`, `new_context`, `check_and_switch_context`, `arm64_mm_context_get`, `arm64_mm_context_put`, `post_ttbr_update_workaround`, `cpu_do_switch_mm`, `asids_update_limit`, and `asids_init`.

Control flow: context switching fast-paths when the mm ASID matches the current generation and this CPU has a nonzero active ASID. Slow path takes `cpu_asid_lock`, allocates or refreshes the ASID, performs pending local TLB flush after rollover, installs the active ASID, applies branch predictor hardening, and switches TTBRs unless TTBR0 PAN defers it. Rollover rebuilds the ASID bitmap from KPTI reservations, pinned ASIDs, and per-CPU reserved active ASIDs, then marks all CPUs pending for local TLB flush.

State and persistence: maintains kernel memory allocator state and per-mm `context.id`/`pinned`. No disk persistence. Pinned ASIDs reserve slots across rollovers for external users; KPTI reserves paired kernel/user ASIDs.

Dependencies/integration: core scheduler/mm context switch, CPU feature detection, KPTI, CnP, SW TTBR0 PAN, TLB flush code, branch predictor hardening, Cavium erratum workaround, and exported pinned-ASID APIs.

Risks: memory ordering around active ASID cmpxchg and rollover is subtle. Too many pinned ASIDs can starve the allocator, so `max_pinned_asids` must leave room for CPUs and rollover. ASID bit mismatch on hotplug is fatal. TTBR update ordering and errata workaround are architecture-critical.

Test signals: process context-switch stress, ASID rollover under many mms, CPU hotplug with ASID bit validation, pinned ASID get/put exhaustion, KPTI pair allocation, CnP/SW PAN configurations, and TLB stale-translation litmus tests.
