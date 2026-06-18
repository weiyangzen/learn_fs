
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/paca.c

Purpose: allocation and initialization of per-CPU PACA structures and related hypervisor/MMU companion data used by low-level PowerPC exception, KVM, kexec, machine-check, and scheduler paths.

Important APIs/types/functions: `alloc_paca_data`; pSeries `alloc_shared_lppaca`, `init_lppaca`, `new_lppaca`; hash-MMU `new_slb_shadow`; exported `paca_ptrs`; `initialise_paca`; `setup_paca`; `allocate_paca_ptrs`; `allocate_paca`; `free_unused_pacas`; `copy_mm_to_paca`.

Control flow: early boot allocates the PACA pointer array with memblock, then allocates each CPU's `struct paca_struct` below the real-mode/bolted mapping limit. Boot CPU allocations use bottom-up memblock so node placement is suitable before NUMA mapping is reliable. `initialise_paca` fills default fields such as lock token, paca index, kernel TOC/base/MSR, hardware CPU id, kexec state, current task, and architecture pointers. pSeries guests allocate LPPACA unless in HV mode; secure guests allocate a shared page-aligned LPPACA pool and call `uv_share_page`. Hash MMU builds allocate SLB shadows when radix is not active. `setup_paca` installs the PACA pointer into r13 and SPRG PACA registers. After CPU count is finalized, unused pointer memory and radix-only boot SLB shadow allocations are freed.

State and persistence: PACA structures are long-lived per-CPU kernel state, referenced from SPRG/r13 and by many real-mode paths. LPPACA may be shared with hypervisor/ultravisor; SLB shadow holds persistent bolted SLB metadata; `copy_mm_to_paca` caches current mm slice page-size arrays in PACA.

Dependencies and integration: depends on memblock, NUMA early node mapping, pSeries LPPACA ABI, secure guest ultravisor sharing, Book3E TLB exception frames, hash/radix MMU selection, kexec state, and scheduler `init_task`.

Risks: PACA must be real-mode accessible, cache-line aligned, and allocated below required limits; boot CPU allocation happens before final feature parsing; shared LPPACA pool sizing assumes `nr_cpu_ids`; incorrect SPRG setup breaks low-level exceptions; freeing boot SLB shadow under radix is a special-case fixup.

Test signals: boot with varying `nr_cpu_ids`, NUMA and secure guest configs, pSeries/HV/non-HV modes, hash versus radix MMU, CPU hotplug/SMP startup, kexec, and machine-check paths that access PACA in real mode.
