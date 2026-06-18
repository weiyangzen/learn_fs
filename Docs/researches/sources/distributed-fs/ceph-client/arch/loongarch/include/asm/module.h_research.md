# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/module.h

## Purpose

`module.h` defines LoongArch module GOT/PLT relocation support. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 126 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: mod_section, mod_arch_specific, got_entry, plt_entry, plt_idx_entry, emit_got_entry, emit_plt_entry, get_plt_entry, get_got_entry. Symbol extraction from the file shows representative defines `_ASM_MODULE_H`, `RELA_STACK_DEPTH`, representative callable declarations or inline helpers `emit_got_entry`, `emit_plt_entry`, `emit_plt_idx_entry`, `get_plt_idx`, `get_plt_entry`, `get_got_entry`, and representative local types `mod_section`, `mod_arch_specific`, `got_entry`, `plt_entry`, `plt_idx_entry`. Direct includes seen in the header are `asm-generic/module.h`, `asm/inst.h`, `asm/orc_types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header module loader uses this for long-branch/call relocation, ORC metadata and GOT/PLT section sizing. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: instruction sequence generation and duplicate entry lookup must match relocation ranges. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
