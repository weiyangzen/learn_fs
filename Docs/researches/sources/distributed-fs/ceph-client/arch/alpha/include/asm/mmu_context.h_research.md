<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu_context.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu_context.h

**Purpose:** Defines Alpha MMU context management: address-space-number allocation, PCB reloads, mm switch hooks, lazy-TLB entry, and page-fault declaration. It is the bridge between Linux `mm_struct` context arrays and Alpha PALcode ASNs/TB behavior.

**Important APIs/types/functions:** `__reload_thread`, `EV4_MAX_ASN`, `EV5_MAX_ASN`, `EV6_MAX_ASN`, `MAX_ASN`, `cpu_last_asn`, ASN version masks, `__get_new_mm_context`, `ev5_switch_mm`, `check_mmu_context`, `ev5_activate_mm`, `init_new_context`, and `enter_lazy_tlb`.

**Control flow:** Context switches compare the target mm context version for the current CPU against `cpu_last_asn`; stale versions allocate a new ASN and may flush all user TB entries with `tbiap()` when hardware ASNs wrap. SMP temporarily marks `asn_lock`, defers reloads via `need_new_asn`, and clears the lock in `check_mmu_context` after `alpha_switch_to` returns.

**State and persistence behavior:** Persistent runtime state is per-mm `mm->context[cpu]`, per-CPU or global `last_asn`, `cpu_data[].need_new_asn`, and PCB `asn`/`ptbr`. The file does not persist data to disk, but bad context versioning can expose stale translations across processes.

**Dependencies and integration points:** Depends on Alpha PAL calls (`PAL_swpctx`, `tbiap`, `imb`), `asm/smp.h`, `asm/machvec.h`, `asm/io.h`, Linux scheduler/mm types, and generic mmu hooks. It integrates with context switching in `switch_to.h`, TLB flushing, page fault handling, and process setup.

**Risks:** ASN wrap and SMP races are the key hazards. EV4 ASNs are documented as unreliable, so assumptions must follow configured CPU family. Missing `check_mmu_context` after a switch can leave deferred ASN work pending. `ptbr` setup assumes Alpha kernel virtual-to-physical layout.

**Test signals:** Build Alpha generic and EV5/EV6 configurations, boot SMP and UP kernels, stress fork/exec/context switching, run memory isolation tests across ASID reuse, and exercise TLB-heavy workloads after `flush_tlb_mm` and ASN wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu_context.h -->
