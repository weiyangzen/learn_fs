# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hw_breakpoint.h

## Purpose

`hw_breakpoint.h` defines hardware breakpoint/watchpoint state and perf hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 147 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: arch_hw_breakpoint_ctrl, arch_hw_breakpoint, encode/decode_ctrl_reg, arch_install/uninstall_hw_breakpoint, breakpoint_handler, watchpoint_handler, get_num_brps/wrps. Symbol extraction from the file shows representative defines `__ASM_HW_BREAKPOINT_H`, `LOONGARCH_BREAKPOINT_EXECUTE`, `LOONGARCH_BREAKPOINT_LOAD`, `LOONGARCH_BREAKPOINT_STORE`, `LOONGARCH_BREAKPOINT_LEN_1`, `LOONGARCH_BREAKPOINT_LEN_2`, `LOONGARCH_BREAKPOINT_LEN_4`, `LOONGARCH_BREAKPOINT_LEN_8`, `LOONGARCH_MAX_BRP`, `LOONGARCH_MAX_WRP`, `CSR_CFG_ADDR`, `CSR_CFG_MASK`, representative callable declarations or inline helpers `encode_ctrl_reg`, `decode_ctrl_reg`, `arch_bp_generic_fields`, `arch_check_bp_in_kernelspace`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `hw_breakpoint_slots`, `hw_breakpoint_pmu_read`, `breakpoint_handler`, `watchpoint_handler`, and representative local types `arch_hw_breakpoint_ctrl`, `arch_hw_breakpoint`, `task_struct`, `notifier_block`, `perf_event`, `perf_event_attr`. Direct includes seen in the header are `asm/loongarch.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates ptrace, perf events, CSR watchpoint registers and context switching. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: slot count comes from cpu_data; control bit encoding and ASID handling are high-risk. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
