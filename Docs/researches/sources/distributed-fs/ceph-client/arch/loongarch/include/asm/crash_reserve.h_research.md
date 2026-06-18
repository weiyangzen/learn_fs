# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/crash_reserve.h

## Purpose

`crash_reserve.h` sets kdump crashkernel reservation alignment and address limits. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 12 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: CRASH_ALIGN, CRASH_ADDR_LOW_MAX, CRASH_ADDR_HIGH_MAX, memblock_end_of_DRAM. Symbol extraction from the file shows representative defines `_LOONGARCH_CRASH_RESERVE_H`, `CRASH_ALIGN`, `CRASH_ADDR_LOW_MAX`, `CRASH_ADDR_HIGH_MAX`, representative callable declarations or inline helpers `memblock_end_of_DRAM`, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by crashkernel reservation during early memblock setup. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: alignment/limit mistakes can reserve unusable memory or exceed firmware-addressable ranges. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
