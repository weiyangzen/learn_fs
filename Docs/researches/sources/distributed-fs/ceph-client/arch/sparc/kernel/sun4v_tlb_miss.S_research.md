# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_tlb_miss.S

Purpose: supplies sun4v fast TLB miss, TSB miss, access-exception, unaligned, privileged-action, floating unaligned, and trap-table patch handlers.

Important APIs/symbols: defines `sun4v_itlb_miss`, `sun4v_dtlb_miss`, `sun4v_itlb_load`, `sun4v_dtlb_load`, `sun4v_dtlb_prot`, `sun4v_itsb_miss`, `sun4v_dtsb_miss`, `sun4v_tsb_miss_common`, `sun4v_iacc*`, `sun4v_dacc*`, `sun4v_mna`, `sun4v_privact`, `sun4v_lddfmna`, `sun4v_stdfmna`, and `sun4v_patch_tlb_handlers()`.

Control flow: fast ITLB/DTLB paths read fault address/context from hypervisor scratchpad, compute TSB tag and pointer, load tag/PTE, validate tag and execute permissions, then call hypervisor MMU map traps to install entries. Misses branch to page-table walk code with fault code. Protection and bad real-address paths hand off to real fault handling or C error reporters. Access exceptions build encoded type/context arguments and enter TL0/TL1 trap frames. The patch function rewrites generic trap-table sites into branches to sun4v handlers and flushes the modified instructions.

State and persistence: updates MMU mappings through hypervisor fast traps, temporary trap-block fields for huge TSB, global sun4v error variables, and patched in-memory trap instructions.

Dependencies and integration points: depends on sun4v hypervisor fault-info layout, TSB format, page-table walk assembly, hugepage scratchpad registers, C fault/error functions, and instruction-cache flushing.

Risks: fast path clobber conventions are tight; wrong tag/PTE permission handling can map invalid translations. Hypervisor map failures at TL1 are fatal-report paths. Runtime patching must compute branch displacements correctly.

Test signals: user/kernel ITLB and DTLB misses, executable permission faults, write-protection faults, hugepage TSB paths, bad real-address reports, unaligned/floating unaligned traps, privileged action traps, and post-patch trap-vector behavior on sun4v.
