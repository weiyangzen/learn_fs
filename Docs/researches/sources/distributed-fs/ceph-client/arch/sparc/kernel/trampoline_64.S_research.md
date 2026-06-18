# sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_64.S

Purpose: implements sparc64 secondary CPU startup from firmware/hypervisor state to normal kernel `smp_callin()`.

Important APIs/symbols: exports `sparc64_cpu_startup` and `sparc64_cpu_startup_end`; uses PROM `call-method` for TLB locking, hypervisor fast MMU map traps on sun4v, `prom_entry_lock`, `tramp_stack`, `kern_locked_tte_data`, `num_kernel_image_mappings`, `init_irqwork_curcpu()`, `sun4v_register_mondo_queues()`, `init_cur_cpu_trap()`, PROM trap-table setup, and `smp_callin()`.

Control flow: startup branches by CPU family, programs Cheetah/Spitfire/Niagara cache and tick interrupt controls, locks kernel image mappings into I/D TLBs via OBP or hypervisor calls, sets privileged state and MMU contexts, switches to a temporary stack, initializes IRQ work and per-CPU trap state, optionally registers sun4v mondo queues, sets the firmware trap table to the kernel trap table, releases the PROM lock, loads the idle thread from the cookie pointer into `%g6/%g4`, sets the real kernel stack, enables interrupts, and calls `smp_callin()`.

State and persistence: mutates CPU MMU/TLB, cache-control, tick compare, trap-table, context, FPRS, ASI, stack, and current-task registers. No persistent storage.

Dependencies and integration points: invoked by `smp_64.c` CPU boot through PROM or sun4v hypervisor. Depends on locked kernel mappings, trap-block layout, firmware client interface buffers, and processor-family detection macros.

Risks: early code cannot touch `%g4/%g5/%g6` until trap table ownership is correct. PROM/hypervisor calls are serialized by `prom_entry_lock`. Mapping or trap-table mistakes strand the CPU before C code.

Test signals: secondary boot on Spitfire, Cheetah/Cheetah+, Niagara/sun4v, LDOM CPU start, mondo queue registration, TLB lock coverage for multiple kernel image mappings, and `sparc64_cpu_startup_end` length users.
