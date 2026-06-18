# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kexec.h

## Purpose

`kexec.h` defines kexec relocation limits and machine hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 72 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: KEXEC_SOURCE_MEMORY_LIMIT, KEXEC_DESTINATION_MEMORY_LIMIT, KEXEC_CONTROL_MEMORY_* and machine_kexec functions. Symbol extraction from the file shows representative defines `_ASM_KEXEC_H`, `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `ARCH_HAS_KIMAGE_ARCH`, `arch_kimage_file_post_load_cleanup`, representative callable declarations or inline helpers `crash_setup_regs`, `arch_kimage_file_post_load_cleanup`, `load_other_segments`, `kexec_reboot`, and representative local types `kimage_arch`, `void`, `kimage`. Direct includes seen in the header are `asm/page.h`, `asm/stacktrace.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by kexec/kdump image loading and crash transitions. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: control code placement and page-size alignment must suit identity/DMW mappings. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
