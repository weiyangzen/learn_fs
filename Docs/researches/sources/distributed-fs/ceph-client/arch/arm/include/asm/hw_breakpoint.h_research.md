# sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_breakpoint.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_breakpoint.h` defines ARM hardware
breakpoint/watchpoint control fields and debug architecture limits. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `_ARM_HW_BREAKPOINT_H`, `ARM_DEBUG_ARCH_RESERVED`, `ARM_DEBUG_ARCH_V6`,
`ARM_DEBUG_ARCH_V6_1`, `ARM_DEBUG_ARCH_V7_ECP14`, `ARM_DEBUG_ARCH_V7_MM`, `ARM_DEBUG_ARCH_V7_1`,
`ARM_DEBUG_ARCH_V8`, `ARM_DEBUG_ARCH_V8_1`, `ARM_DEBUG_ARCH_V8_2`, `ARM_DEBUG_ARCH_V8_4`,
`ARM_BREAKPOINT_EXECUTE`, `ARM_BREAKPOINT_LOAD`, `ARM_BREAKPOINT_STORE`, `ARM_FSR_ACCESS_MASK`,
`ARM_BREAKPOINT_PRIV`, `ARM_BREAKPOINT_USER`, `ARM_BREAKPOINT_LEN_1`, and 24 more; types:
`task_struct`, `arch_hw_breakpoint_ctrl`, `arch_hw_breakpoint`, `perf_event_attr`, `notifier_block`,
`perf_event`, `pmu`; functions/prototypes: `arch_check_bp_in_kernelspace`, `arch_get_debug_arch`,
`arch_get_max_wp_len`, `clear_ptrace_hw_breakpoint`, `arch_install_hw_breakpoint`,
`arch_uninstall_hw_breakpoint`, `hw_breakpoint_pmu_read`, `hw_breakpoint_slots`,
`arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`. The file is
146 lines / 3848 bytes, and the exported surface is primarily an include-time contract for other
kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Most behavior is
selected through preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`,
CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `task_struct`, `arch_hw_breakpoint_ctrl`,
`arch_hw_breakpoint`, `perf_event_attr`, `notifier_block`, `perf_event`, `pmu`. External state or
implementation hooks include `arch_bp_generic_fields`, `arch_check_bp_in_kernelspace`,
`hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_get_debug_arch`,
`arch_get_max_wp_len`, `clear_ptrace_hw_breakpoint`. There is no userspace filesystem persistence in
this file; persistence is either kernel memory, CPU register state, hardware register state, or
generated ABI values. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hw_breakpoint.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
