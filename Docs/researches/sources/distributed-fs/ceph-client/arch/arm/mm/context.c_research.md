## sources/distributed-fs/ceph-client/arch/arm/mm/context.c

### Purpose
Implements ARM MMU context switching with ASID allocation, rollover handling, per-CPU active/reserved ASID tracking, optional PID-in-CONTEXTIDR updates, and safe TTBR0 switching for classic MMU systems.

### Important APIs, Types, And Functions
Key state includes `asid_generation`, `asid_map`, per-CPU `active_asids`, per-CPU `reserved_asids`, `cpu_asid_lock`, and `tlb_flush_pending`. Main entry point is `check_and_switch_context(mm, tsk)`. Helpers include `flush_context`, `check_update_reserved_asid`, `new_context`, `cpu_set_reserved_ttbr0`, and erratum-specific `a15_erratum_get_cpumask`.

### Control Flow
`check_and_switch_context` first syncs vmalloc page tables, switches TTBR0 to reserved global mappings on non-LPAE, then fast-paths if the current ASID generation is valid and active. Otherwise it locks ASID state, allocates/reuses an ASID, handles generation rollover by reserving active ASIDs and queuing TLB flushes, performs pending local TLB/BP flush, records CPU membership, and finally calls `cpu_switch_mm`.

### State, Dependencies, And Integration
ASID state persists for the running kernel and is protected by a raw spinlock plus atomic64 per-CPU values. It depends on SMP, TLB flush, proc-fns, thread notifiers, and `check_vmalloc_seq`. It integrates with scheduler context switches, CPU errata workarounds, trace/debug context IDs, and speculative-walk mitigation.

### Risks And Test Signals
Risks include ASID reuse without required TLB invalidation, reserved ASID loss across rollover, TTBR0 updates racing speculative walks, and PID/context ID corruption. Test with heavy fork/exec on SMP, CPU hotplug, vmalloc faults across processes, ASID rollover stress, and ARM erratum-specific TLB shootdown tests.
