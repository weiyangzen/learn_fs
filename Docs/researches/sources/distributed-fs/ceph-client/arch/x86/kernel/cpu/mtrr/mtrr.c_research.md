# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/mtrr.c

Purpose: implements the common x86 MTRR management API. It initializes the active backend, tracks usage counts, synchronizes MTRR changes across CPUs, exposes driver-facing add/delete and write-combining helpers, and finalizes boot-time MTRR state.

Important APIs/types/functions: global state includes `num_var_ranges`, `mtrr_usage_table[]`, `mtrr_mutex`, `mtrr_if`, and `changed_by_mtrr_cleanup`. Public functions are `mtrr_add_page()`, `mtrr_add()`, `mtrr_del_page()`, `mtrr_del()`, `arch_phys_wc_add()`, `arch_phys_wc_del()`, `arch_phys_wc_index()`, `mtrr_bp_init()`, `mtrr_save_state()`, and initcall `mtrr_init_finalize()`. Helpers include `have_wrcomb()`, `init_table()`, `mtrr_rendezvous_handler()`, `types_compatible()`, and `set_mtrr()`.

Control flow: boot initializes reserved high physical bits, selects generic or legacy backend, reads variable range count, initializes usage counts, reads generic MTRR state, optionally runs cleanup, and builds the lookup map. Runtime add validates type/alignment/width, checks WC support, locks CPU hotplug and `mtrr_mutex`, reuses compatible overlapping regions or finds a free register, then updates all online CPUs through `stop_machine_cpuslocked()`. Delete decrements usage and disables the register at zero. Finalization copies the map to heap, emits inconsistent-state warnings, or registers legacy syscore restore.

State and persistence: usage counts are in `mtrr_usage_table[]`; backend hardware state is CPU MSRs or legacy registers; the effective map is owned by `generic.c`. MTRR changes persist only for the running boot. `arch_phys_wc_add()` returns offset handles to distinguish real MTRR indexes from no-op/PAT cases.

Dependencies and integration points: used by drivers and architecture memory-type code through exported MTRR and WC APIs. Depends on backend `mtrr_ops`, stop-machine, CPU hotplug locks, PCI chipset checks for WC errata, PAT state, E820 cleanup interactions, and syscore.

Risks: MTRR changes must be synchronized across CPUs with caches/TLBs handled by backend code. Overlap compatibility rules are subtle and can reject valid requests or allow harmful mixed types. Usage-count bugs can leak scarce registers or disable active mappings. PAT-enabled systems return success without MTRR changes, so callers must treat handles opaquely.

Test signals: boot with generic MTRRs enabled/disabled by BIOS, cleanup changed vs unchanged, driver `arch_phys_wc_add/del`, overlapping compatible and incompatible add requests, replacement of same-type enclosed regions, register exhaustion, CPU hotplug during add/delete, and `/proc/mtrr` count behavior.
