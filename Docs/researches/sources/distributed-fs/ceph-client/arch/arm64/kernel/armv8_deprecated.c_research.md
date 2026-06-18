<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c` emulates or controls deprecated AArch32 instructions on arm64, including SWP/SWPB, CP15 barrier operations, and SETEND, with sysctl-configurable modes. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `CREATE_TRACE_POINTS`, `ARM_OPCODE_CONDTEST_FAIL`, `ARM_OPCODE_CONDTEST_PASS`, `ARM_OPCODE_CONDTEST_UNCOND`, `ARM_OPCODE_CONDITION_UNCOND`, `__SWP_LL_SC_LOOPS`, `__user_swpX_asm`, `__user_swp_asm`, `__user_swpb_asm`, `TYPE_SWPB`; types: `insn_emulation_mode`, `legacy_insn_status`, `insn_emulation`, `ctl_table`, `pt_regs`; functions/prototypes/exports: `aarch32_check_condition`, `emulate_swpX`, `swp_handler`, `try_emulate_swp`, `cp15barrier_handler`, `cp15_barrier_set_hw_mode`, `try_emulate_cp15_barrier`, `setend_set_hw_mode`, `compat_setend_handler`, `a32_setend_handler`, `t16_setend_handler`, `try_emulate_setend`, `enable_insn_hw_mode`, `disable_insn_hw_mode`, `run_all_cpu_set_hw_mode`, `run_all_insn_set_hw_mode`, `update_insn_emulation_mode`, `emulation_proc_handler`, `register_insn_emulation`, `try_emulate_armv8_deprecated`, `armv8_deprecated_init`. The file is 642 lines / 15818 bytes. Direct includes are `linux/cpu.h`, `linux/init.h`, `linux/list.h`, `linux/perf_event.h`, `linux/sched.h`, `linux/slab.h`, `linux/sysctl.h`, `linux/uaccess.h`, `asm/cpufeature.h`, `asm/insn.h`, `asm/sysreg.h`, `asm/system_misc.h`, `asm/traps.h`, `trace-events-emulation.h`.

### Control Flow
Undefined-instruction handlers decode instruction condition fields, emulate memory operations or endian changes when configured, optionally enable hardware handling on all CPUs, and expose per-instruction mode controls through proc/sysctl.

### State, Persistence, And Dependencies
Notable global/static state symbols are `insn`, `current_mode`, `min`, `max`, `sysctl`, `__maybe_unused`, `cc_bits`, `emulate_swpX`, `type`, `res`, `swp_handler`, `destreg`, `rn`, `try_emulate_swp`, `insn_swp`, `cp15barrier_handler`, `cp15_barrier_set_hw_mode`, `try_emulate_cp15_barrier`, and 17 more. Each `insn_emulation` records current mode, status, min mode, and counters; hardware mode changes are applied per CPU under a mutex. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Instruction decode bugs, user access faults during SWP emulation, inconsistent per-CPU hardware mode, or unsafe sysctl changes can break compat applications.

### Test Signals
Run AArch32 compatibility tests using SWP, CP15 barriers, and SETEND; exercise sysctl mode changes, perf emulation events, and faulting user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/armv8_deprecated.c -->
