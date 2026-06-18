# sources/distributed-fs/ceph-client/arch/arc/mm/tlbex.S

Purpose: assembly fast-path handlers for ARC instruction and data TLB misses.

Important macros/entry points: `EV_TLBMissI` and `EV_TLBMissD` are exception entries. `TLBMISS_FREEUP_REGS`/`TLBMISS_RESTORE_REGS` save scratch registers using ARCompact global/per-CPU storage or ARCv2 stack slots. `LOAD_FAULT_PTE` walks the current page tables. `CONV_PTE_TO_TLB` converts Linux PTE bits to ARC PD0/PD1(/PD1HI). `COMMIT_ENTRY_TO_MMU` writes the hardware TLB.

Control flow: on TLB miss, the handler saves minimal registers, reads fault address, locates current PGD, walks configured page-table levels, handles THP PMD entries, validates permissions for instruction or data access, sets accessed/dirty bits, converts PTE to TLB descriptors, commits the entry, restores registers, and returns with `rtie`. Missing page tables or permission failures branch to `do_slow_path_pf`, restore registers, and enter the normal exception prologue for `do_page_fault()`.

State and persistence: mutates PTE accessed/dirty bits and hardware TLB entries. ARCompact uses `ex_saved_reg1` scratch storage; ARCv2 uses stack. It reads current PGD from `ARC_REG_SCRATCH_DATA0` on ARCv2.

Dependencies and integration: tightly coupled with page-table bit layout, MMU context setup, low-level exception vectors, `fault.c`, `tlb.c`, THP, PAE40 PTE size, and ARC aux register definitions.

Risks: this is latency-critical and register-fragile. Any mismatch in PTE bit definitions, page-table level shifts, scratch register protocol, or ECR cause decoding can corrupt TLB state or fault recursively. SMP ARCompact scratch storage must remain per-CPU and cache-line separated.

Test signals: instruction/data TLB miss boot coverage, user read/write/execute faults, vmalloc faults that go slow path, THP mappings, PAE40 builds, SMP stress, and low-level exception return correctness.
