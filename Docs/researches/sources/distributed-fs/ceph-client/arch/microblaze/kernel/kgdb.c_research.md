# sources/distributed-fs/ceph-client/arch/microblaze/kernel/kgdb.c

Purpose: implements MicroBlaze KGDB register translation, breakpoint handling, and architecture KGDB operations.

Important APIs and state: `pt_regs_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, `microblaze_kgdb_break()`, `sleeping_thread_to_gdb_regs()`, `kgdb_arch_set_pc()`, `kgdb_arch_handle_exception()`, `kgdb_arch_init()`, and `arch_kgdb_ops`. Static `pvr` snapshots immutable PVR registers for GDB.

Control flow: register export copies `pt_regs`, BTR, PVR, and special MMU registers into GDB slots. Import updates writable `pt_regs` values except r0 and special read-only slots. Break handling invokes KGDB core and skips the architecture breakpoint instruction when needed. Continue packets may set `regs->pc`.

State and persistence: KGDB init stores PVR data. Handlers mutate debugged task registers and PC.

Dependencies and integration: entered from `_debug_exception` in `entry.S`; depends on breakpoint byte order and `get_pvr()`.

Risks and test signals: sleeping-thread helper is marked untested. Wrong GDB register layout breaks remote debugging. Test kernel and user breakpoints, continue-with-address, endian-specific breakpoint encoding, and PVR register visibility.
