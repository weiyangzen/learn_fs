# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bootinfo.h

## Purpose

`bootinfo.h` declares firmware, board and early platform boot state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 54 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: loongson_board_info, loongson_system_configuration, fw_arg0-2, efi_system_table, init_environ, memblock_init, platform_init, init_numa_memory, io_master. Symbol extraction from the file shows representative defines `_ASM_BOOTINFO_H`, `NR_WORDS`, representative callable declarations or inline helpers `init_environ`, `memblock_init`, `platform_init`, `init_numa_memory`, `io_master`, and representative local types `loongson_board_info`, `loongson_system_configuration`. Direct includes seen in the header are `asm/setup.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header consumed by setup, NUMA, EFI and platform initialization before normal allocators are fully available. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: incorrect firmware arguments or core topology fields affect memory discovery, CPU/node layout and IO-master decisions. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
