# sources/distributed-fs/ceph-client/arch/x86/kernel/ldt.c

Purpose: Implements x86 `modify_ldt()` and LDT context management for processes, including fork duplication, mm teardown, per-CPU LDTR loading, and page-table-isolation aliases for user-visible LDT mappings.

Important APIs/types/functions: exposes `load_mm_ldt()`, `switch_ldt()`, `ldt_dup_context()`, `destroy_context_ldt()`, `ldt_arch_exit_mmap()`, and `SYSCALL_DEFINE3(modify_ldt)`. Internal helpers manage allocation, PTI mapping/unmapping, segment refresh, `install_ldt()`, read/write operations, and 16-bit segment policy.

Control flow: `modify_ldt` routes reads, default reads, and writes. Writes validate `struct user_desc`, reject invalid entries and disallowed 16-bit segments, allocate a new immutable `ldt_struct`, copy old entries, install the changed descriptor, map it into the alternate PTI slot if needed, publish it with release ordering, IPI all CPUs using the mm to reload LDTR, unmap the old slot, and free the old LDT. Reads copy current entries and zero-fill requested trailing space.

State and persistence: each `mm_struct` may own one `context.ldt`. LDT entries persist until replaced, duplicated on fork, or freed on mm destruction. Under PTI the same LDT content is mapped read-only into one of two fixed alias slots at `LDT_BASE_ADDR`, toggling slots so CPUs can keep using the old mapping until reloaded.

Dependencies and integration points: depends on x86 descriptor loading, mm context locks and semaphores, TLB shootdown, PTI page-table helpers, paravirt LDT allocation/free hooks, Xen PV detection, user-copy helpers, and mm fork/exit hooks.

Risks: lock order is explicitly `ldt_usr_sem`, `mmap_lock`, `context.lock`. LDTR updates rely on IPIs before freeing the old LDT. PTI alias mapping must be read-only, non-global, and synchronized to user page tables. Xen PV disallows 16-bit segments because ESPFIX64 is unavailable. RCU conversion is warned against because IRQ and IPI ordering are subtle.

Test signals: `modify_ldt` ABI tests should read/write/clear descriptors, reject invalid contents and 16-bit segments when disabled, fork with inherited LDT, switch between tasks with and without LDT, run with PTI on/off, CPU hotplug under active LDT users, Xen PV behavior, and stress concurrent LDT updates plus context switches.
