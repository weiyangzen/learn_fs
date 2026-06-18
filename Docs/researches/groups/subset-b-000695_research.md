# subset-b-000695 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bitops.h

## Purpose

`bitops.h` selects LoongArch bit operation implementations and generic atomic/non-atomic bit helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 44 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: generic bitops include routing, ffs/fls variants, hweight, little-endian and ext2 atomic helpers. Symbol extraction from the file shows representative defines `_ASM_BITOPS_H`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/bitops/__ffs.h`, `asm-generic/bitops/__fls.h`, `asm-generic/bitops/atomic.h`, `asm-generic/bitops/builtin-__ffs.h`, `asm-generic/bitops/builtin-__fls.h`, `asm-generic/bitops/builtin-ffs.h`, `asm-generic/bitops/builtin-fls.h`, `asm-generic/bitops/ext2-atomic.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header configured through CONFIG_32BIT_REDUCED versus standard/64-bit builds; included only through linux/bitops.h. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: wrong include order or config selection can change atomicity or compiler builtin semantics. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bitrev.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bitrev.h

## Purpose

`bitrev.h` provides architecture bit-reversal primitives using LoongArch `bitrev` instructions. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 34 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: __arch_bitrev32, __arch_bitrev16 and __arch_bitrev8. Symbol extraction from the file shows representative defines `__LOONGARCH_ASM_BITREV_H__`, representative callable declarations or inline helpers `__arch_bitrev32`, `__arch_bitrev16`, `__arch_bitrev8`, and representative local types none visible in this header. Direct includes seen in the header are `linux/swab.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header feeds linux bitrev helpers and checksum/crypto/driver code that can use arch acceleration. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: u16 handling depends on the explicit byte swap before `bitrev.4b`; assembler support is the main build signal. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bitrev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bootinfo.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bootinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/branch.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/branch.h

## Purpose

`branch.h` normalizes exception return-address access for LoongArch pt_regs. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 20 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: exception_era and compute_return_era. Symbol extraction from the file shows representative defines `_ASM_BRANCH_H`, representative callable declarations or inline helpers `exception_era`, `compute_return_era`, and representative local types none visible in this header. Direct includes seen in the header are `asm/ptrace.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by trap handling and instruction emulation that must advance past a 4-byte instruction. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: assumes fixed-width 4-byte instructions; a wrong ERA update loops or skips faulting code. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/branch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bug.h

## Purpose

`bug.h` implements LoongArch BUG/WARN trap generation and bug-table metadata. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 62 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: ASM_BUG_FLAGS, ASM_BUG, BUG, __WARN_FLAGS, __BUG_ENTRY. Symbol extraction from the file shows representative defines `__ASM_BUG_H`, `_BUGVERBOSE_LOCATION`, `__BUGVERBOSE_LOCATION`, `_BUGVERBOSE_LOCATION`, `__BUG_ENTRY`, `__BUG_ENTRY`, `ASM_BUG_FLAGS`, `ASM_BUG`, `__BUG_FLAGS`, `__WARN_FLAGS`, `BUG`, `HAVE_ARCH_BUG`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/bug.h`, `asm/break.h`, `linux/objtool.h`, `linux/stringify.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates with generic bug handling, objtool annotations, break instruction encodings and optional verbose bug tables. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: metadata offsets, section alignment and reachability annotations must stay synchronized with generic BUG decoding. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cache.h

## Purpose

`cache.h` defines cache-line sizing and DMA alignment constants. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 15 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: L1_CACHE_SHIFT, L1_CACHE_BYTES, ARCH_DMA_MINALIGN, __read_mostly. Symbol extraction from the file shows representative defines `_ASM_CACHE_H`, `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `__read_mostly`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by allocator alignment, DMA mapping, percpu/cacheline annotations and data placement. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: too-small alignment can expose DMA coherency bugs; cache shift must match Kconfig/platform data. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cacheflush.h

## Purpose

`cacheflush.h` declares and wraps LoongArch cache and instruction-cache maintenance. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 99 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: cache_present/private/inclusive, cpu_last_level_cache_line_size, __flush_cache_all, local_flush_icache_all/range, flush_cache_line, cache_op. Symbol extraction from the file shows representative defines `_ASM_CACHEFLUSH_H`, `flush_icache_all`, `flush_icache_range`, `flush_icache_user_range`, `flush_cache_all`, `flush_cache_mm`, `flush_cache_dup_mm`, `flush_cache_range`, `flush_cache_page`, `flush_cache_vmap`, `flush_cache_vunmap`, `flush_icache_user_page`, representative callable declarations or inline helpers `cache_present`, `cache_private`, `cache_inclusive`, `cpu_last_level_cache_line_size`, `__flush_cache_all`, `local_flush_icache_all`, `local_flush_icache_range`, `flush_cache_line`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/cacheflush.h`, `asm/cacheops.h`, `asm/cpu-info.h`, `linux/mm.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header uses cache_desc data from cpu-info and cacheops encodings; integrates with text patching, module loading and user icache sync. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: range flushes issue full local icache flushes here, so correctness is favored over precision; missing remote synchronization can affect patched executable text. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cacheops.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cacheops.h

## Purpose

`cacheops.h` names cache operation leaves and operation encodings. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 43 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: Cache_LEAF0-5, Index_Writeback_Inv, Hit_Writeback_Inv and derived LEAF macros. Symbol extraction from the file shows representative defines `__ASM_CACHEOPS_H`, `CacheOp_Cache`, `CacheOp_Op`, `Cache_LEAF0`, `Cache_LEAF1`, `Cache_LEAF2`, `Cache_LEAF3`, `Cache_LEAF4`, `Cache_LEAF5`, `Index_Invalidate`, `Index_Writeback_Inv`, `Hit_Invalidate`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header consumed by cacheflush assembly `cacop` calls and low-level cache maintenance code. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: encoding drift would flush the wrong cache leaf or operation class. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cacheops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/checksum.h

## Purpose

`checksum.h` adds LoongArch optimized IP checksum helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 70 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: csum_fold, ip_fast_csum, do_csum and generic checksum fallback inclusion. Symbol extraction from the file shows representative defines `__ASM_CHECKSUM_H`, `_HAVE_ARCH_IPV6_CSUM`, `csum_fold`, `ip_fast_csum`, `do_csum`, representative callable declarations or inline helpers `csum_fold`, `ip_fast_csum`, `do_csum`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/checksum.h`, `linux/bitops.h`, `linux/in6.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header network stack uses these through asm/checksum.h for IPv4 and generic checksum paths. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: inline assembly carry folding must preserve end-around carry behavior; odd header lengths and alignment are key tests. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/clocksource.h

## Purpose

`clocksource.h` connects arch clocksource definitions to vDSO clocksource support. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 12 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: includes asm/vdso/clocksource.h. Symbol extraction from the file shows representative defines `__ASM_CLOCKSOURCE_H`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm/vdso/clocksource.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by timekeeping and vDSO fast time reads. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: minimal wrapper, so risk is include availability and ABI consistency with vDSO clock modes. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cmpxchg.h

## Purpose

`cmpxchg.h` implements atomic exchange and compare-exchange primitives. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 304 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: __xchg_small, __arch_xchg, arch_xchg, __cmpxchg_small, __arch_cmpxchg, arch_cmpxchg, arch_cmpxchg128. Symbol extraction from the file shows representative defines `__ASM_CMPXCHG_H`, `__xchg_amo_asm`, `__xchg_llsc_asm`, `arch_xchg`, `__cmpxchg_asm`, `arch_cmpxchg_local`, `arch_cmpxchg`, `arch_cmpxchg64_local`, `arch_cmpxchg64`, `system_has_cmpxchg128`, `__arch_cmpxchg128`, `arch_cmpxchg128`, representative callable declarations or inline helpers `__xchg_small`, `__cmpxchg_small`, and representative local types `__u128_halves`. Direct includes seen in the header are `asm-generic/cmpxchg-local.h`, `asm/barrier.h`, `asm/cpu-features.h`, `linux/bits.h`, `linux/build_bug.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header selects AMO or LL/SC sequences based on CPU features and width; used by atomics, locks, refcounts, percpu and KVM. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: byte/halfword subword masking, memory barriers and SC.Q availability are high-risk; run atomic litmus/KCSAN/locking tests. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu-features.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu-features.h

## Purpose

`cpu-features.h` provides readable CPU feature predicates backed by boot CPU data. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 73 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: cpu_opt, cpu_has, cpu_has_fpu/lsx/lasx/lvz/lbt/csripi/extioi/msgint/avecint and related macros. Symbol extraction from the file shows representative defines `__ASM_CPU_FEATURES_H`, `cpu_opt`, `cpu_has`, `cpu_has_loongarch`, `cpu_has_loongarch32`, `cpu_has_loongarch64`, `cpu_has_cpucfg`, `cpu_has_lam`, `cpu_has_lam_bh`, `cpu_has_scq`, `cpu_has_ual`, `cpu_has_fpu`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm/cpu-info.h`, `asm/cpu.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used across FPU, KVM, interrupts, atomics, alternatives and feature-gated code. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: feature predicates mostly read cpu_data[0], so heterogeneous CPU assumptions need care; cpu_has_perf maps PMP in this tree. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu-features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu-info.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu-info.h

## Purpose

`cpu-info.h` defines per-CPU discovered hardware information. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 104 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: cache_desc, cpuinfo_loongarch, cpu_data, boot_cpu_data, cpu_probe, cpus_are_siblings, cpu_asid_mask, set_cpu_asid_mask. Symbol extraction from the file shows representative defines `__ASM_CPU_INFO_H`, `CACHE_LEVEL_MAX`, `CACHE_LEAVES_MAX`, `boot_cpu_data`, `current_cpu_data`, `raw_current_cpu_data`, `cpu_family_string`, `cpu_full_name_string`, representative callable declarations or inline helpers `cpu_probe`, `cpus_are_siblings`, `cpu_asid_mask`, `set_cpu_asid_mask`, and representative local types `cache_desc`, `cpuinfo_loongarch`. Direct includes seen in the header are `asm/loongarch.h`, `linux/cache.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header populated during CPU probing and then consumed by cache, MMU, scheduling topology, feature checks and /proc reporting. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: state persists for boot lifetime; wrong ASID/cache/topology values cause TLB reuse or cache maintenance bugs. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu-info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu.h

## Purpose

`cpu.h` defines PRID, CPU type and feature bit constants. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 166 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: cpu_type_enum, id_to_core_name, LOONGARCH_CPU_ISA_* and LOONGARCH_CPU_* feature masks. Symbol extraction from the file shows representative defines `_ASM_CPU_H`, `PRID_COMP_MASK`, `PRID_COMP_LOONGSON`, `PRID_SERIES_MASK`, `PRID_SERIES_LA132`, `PRID_SERIES_LA264`, `PRID_SERIES_LA364`, `PRID_SERIES_LA464`, `PRID_SERIES_LA664`, `PRID_PRODUCT_MASK`, `LOONGARCH_CPU_ISA_LA32R`, `LOONGARCH_CPU_ISA_LA32S`, representative callable declarations or inline helpers `id_to_core_name`, and representative local types `cpu_type_enum`. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header basis for cpu-info probing, feature predicates and user-visible CPU identification. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: numeric feature-bit ABI must remain stable within the kernel; name lookup returns Unknown for unsupported IDs. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpufeature.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpufeature.h

## Purpose

`cpufeature.h` maps ELF hwcap bits to CPU feature checks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 24 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: MAX_CPU_FEATURES, cpu_feature, cpu_have_feature. Symbol extraction from the file shows representative defines `__ASM_CPUFEATURE_H`, `MAX_CPU_FEATURES`, `cpu_feature`, representative callable declarations or inline helpers `cpu_have_feature`, and representative local types none visible in this header. Direct includes seen in the header are `asm/elf.h`, `uapi/asm/hwcap.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by user ABI capability exposure, ELF/vDSO and optimized library dispatch. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: relies on `elf_hwcap`; bounds and HWCAP naming must match uapi/asm/hwcap.h. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/crash_reserve.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/crash_reserve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/delay.h

## Purpose

`delay.h` declares busy-wait delay routines. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 26 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: __delay, __ndelay, __udelay, ndelay, udelay, MAX_UDELAY_MS. Symbol extraction from the file shows representative defines `_ASM_DELAY_H`, `ndelay`, `udelay`, `MAX_UDELAY_MS`, `MAX_UDELAY_MS`, `MAX_UDELAY_MS`, representative callable declarations or inline helpers `__delay`, `__ndelay`, `__udelay`, and representative local types none visible in this header. Direct includes seen in the header are `linux/param.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by drivers and early platform code before timers/sleeping may be available. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: calibration and HZ-dependent maximums determine overflow and latency behavior. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/dma.h

## Purpose

`dma.h` defines DMA-address limits for LoongArch. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 11 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: MAX_DMA_ADDRESS and MAX_DMA32_PFN. Symbol extraction from the file shows representative defines `__ASM_DMA_H`, `MAX_DMA_ADDRESS`, `MAX_DMA32_PFN`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header feeds generic DMA zone and GFP/DMA allocation constraints. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: PAGE_OFFSET and 32-bit PFN assumptions must match memory layout and device DMA masks. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/dmi.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/dmi.h

## Purpose

`dmi.h` provides DMI early mapping/allocation hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 24 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: dmi_early_remap, dmi_early_unmap, dmi_alloc, dmi_remap, dmi_unmap. Symbol extraction from the file shows representative defines `_ASM_DMI_H`, `dmi_early_remap`, `dmi_early_unmap`, `dmi_alloc`, representative callable declarations or inline helpers `dmi_remap`, `dmi_unmap`, and representative local types none visible in this header. Direct includes seen in the header are `linux/io.h`, `linux/memblock.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates DMI scanning with memblock and early ioremap. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: early allocations are permanent memblock allocations; mapping attributes must be safe for firmware tables. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/efi.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/efi.h

## Purpose

`efi.h` declares LoongArch EFI boot/runtime interfaces. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 35 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: efi_init, efi_runtime_init, efi_fdt_pointer, efifb_setup_from_dmi, EFI_ALLOC_ALIGN, EFI_RT_VIRTUAL_OFFSET, efi_get_max_initrd_addr, efi_get_kimg_min_align. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_EFI_H`, `ARCH_EFI_IRQ_FLAGS_MASK`, `arch_efi_call_virt_setup`, `arch_efi_call_virt_teardown`, `EFI_ALLOC_ALIGN`, `EFI_RT_VIRTUAL_OFFSET`, `EFI_KIMG_PREFERRED_ADDRESS`, representative callable declarations or inline helpers `efi_init`, `efi_runtime_init`, `efi_fdt_pointer`, `efifb_setup_from_dmi`, `efi_get_max_initrd_addr`, `efi_get_kimg_min_align`, and representative local types none visible in this header. Direct includes seen in the header are `linux/efi.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header connects EFI stub, runtime services, framebuffer setup and kernel image placement. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: runtime virtual offset and IRQ flag mask must match CSR/DMW layout; initrd placement affects boot reliability. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/efi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/elf.h

## Purpose

`elf.h` defines LoongArch ELF ABI, relocation constants, process personality and core-dump register views. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 371 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: EF_LOONGARCH_ABI_*, R_LARCH_*, ELF_CLASS/DATA/ARCH, ELF_PLAT_INIT, SET_PERSONALITY, ARCH_DLINFO, ELF_CORE_COPY_REGS. Symbol extraction from the file shows representative defines `_ASM_ELF_H`, `EF_LOONGARCH_ABI_LP64_SOFT_FLOAT`, `EF_LOONGARCH_ABI_LP64_SINGLE_FLOAT`, `EF_LOONGARCH_ABI_LP64_DOUBLE_FLOAT`, `EF_LOONGARCH_ABI_ILP32_SOFT_FLOAT`, `EF_LOONGARCH_ABI_ILP32_SINGLE_FLOAT`, `EF_LOONGARCH_ABI_ILP32_DOUBLE_FLOAT`, `R_LARCH_NONE`, `R_LARCH_32`, `R_LARCH_64`, `R_LARCH_RELATIVE`, `R_LARCH_COPY`, representative callable declarations or inline helpers `loongarch_dump_regs32`, `loongarch_dump_regs64`, `arch_setup_additional_pages`, `arch_elf_pt_proc`, `arch_check_elf`, and representative local types `unsigned`, `elf_greg_t`, `double`, `elf_fpreg_t`, `linux_binprm`, `arch_elf_state`. Direct includes seen in the header are `asm/current.h`, `asm/hwcap.h`, `asm/vdso.h`, `linux/auxvec.h`, `linux/fs.h`, `uapi/linux/elf.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by binfmt_elf, module relocation, dynamic loaders, ptrace/core dumps and vDSO setup. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: relocation and hwcap constants are ABI-sensitive; wrong register export breaks debuggers and user programs. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/entry-common.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/entry-common.h

## Purpose

`entry-common.h` supplies LoongArch entry-common include glue. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 7 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: includes stacktrace for on_thread_stack. Symbol extraction from the file shows representative defines `ARCH_LOONGARCH_ENTRY_COMMON_H`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm/stacktrace.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by generic entry code to access arch stack predicates. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: small wrapper; risk is missing dependency for entry instrumentation builds. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/entry-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/exception.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/exception.h

## Purpose

`exception.h` declares exception vectors and C exception handlers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 47 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: exception_table, show_registers, do_ade/ale/bce/bp/ri/fpu/fpe/lsx/lasx/lbt/watch/syscall/reserved/vint/page_fault, handle_* entry labels. Symbol extraction from the file shows representative defines `__ASM_EXCEPTION_H`, representative callable declarations or inline helpers `show_registers`, `cache_parity_error`, `do_ade`, `do_ale`, `do_bce`, `do_bp`, `do_ri`, `do_fpu`, `do_fpe`, `do_lsx`, `do_lasx`, `do_lbt`, and representative local types none visible in this header. Direct includes seen in the header are `asm/ptrace.h`, `linux/kprobes.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header assembly entry code dispatches to these handlers; page fault, kprobes, FPU and IRQ paths depend on exact calling convention. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: noinstr and asmlinkage annotations are correctness signals for tracing and entry validation. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/exception.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/exec.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/exec.h

## Purpose

`exec.h` declares stack randomization/alignment hook. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 10 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: arch_align_stack. Symbol extraction from the file shows representative defines `_ASM_EXEC_H`, representative callable declarations or inline helpers `arch_align_stack`, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by exec path when building a new user stack. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: must preserve ABI alignment while allowing ASLR behavior. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/extable.h

## Purpose

`extable.h` defines LoongArch exception-table entry layout and fixup helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 47 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: exception_table_entry, ARCH_HAS_RELATIVE_EXTABLE, swap_ex_entry_fixup, ex_handler_bpf, fixup_exception. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_EXTABLE_H`, `ARCH_HAS_RELATIVE_EXTABLE`, `swap_ex_entry_fixup`, representative callable declarations or inline helpers `ex_handler_bpf`, `ex_handler_bpf`, `fixup_exception`, and representative local types `exception_table_entry`. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by uaccess, BPF JIT and fault fixup handling. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: relative offsets and sort swapping must preserve type/data fields; BPF handler is conditional. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fixmap.h

## Purpose

`fixmap.h` defines fixed virtual address slots for early mappings. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 42 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: fixed_addresses, FIXADDR_SIZE/START, FIXMAP_PAGE_IO, __set_fixmap, fixrange_init. Symbol extraction from the file shows representative defines `_ASM_FIXMAP_H`, `NR_FIX_BTMAPS`, `FIXADDR_SIZE`, `FIXADDR_START`, `FIXMAP_PAGE_IO`, representative callable declarations or inline helpers `__set_fixmap`, `fixrange_init`, and representative local types `fixed_addresses`. Direct includes seen in the header are `asm-generic/fixmap.h`, `asm/kmap_size.h`, `linux/threads.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by early console, highmem kmap and pagetable initialization. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: slot order is ABI within arch memory setup; highmem expands per-CPU kmap slots. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fpregdef.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fpregdef.h

## Purpose

`fpregdef.h` names FPU registers for assembly sources. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 59 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: fa/ft/fs aliases and fcsr0-3 aliases depending on assembler support. Symbol extraction from the file shows representative defines `_ASM_FPREGDEF_H`, `fa0`, `fa1`, `fa2`, `fa3`, `fa4`, `fa5`, `fa6`, `fa7`, `ft0`, `ft1`, `ft2`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header consumed by LoongArch assembly for FPU save/restore and signal paths. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: FCSR aliases work around binutils behavior; changing them can break assembly builds. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fpregdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fprobe.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fprobe.h

## Purpose

`fprobe.h` selects generic fprobe header encoding behavior. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 12 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: undef ARCH_DEFINE_ENCODE_FPROBE_HEADER. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_FPROBE_H`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates with fprobe tracing infrastructure. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: documents that LoongArch object addresses lack enough fixed high bits for compact encoding. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fpu.h

## Purpose

`fpu.h` manages FPU, LSX and LASX ownership, save/restore and user context helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 326 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: kernel_fpu_begin/end, _save/_restore_fp/lsx/lasx, context copy helpers, is_*_enabled, own/lose/init_fpu, save_fpu_regs, thread_lsx/lasx_context_live. Symbol extraction from the file shows representative defines `_ASM_FPU_H`, `kernel_fpu_available`, `enable_fpu`, `disable_fpu`, `clear_fpu_owner`, representative callable declarations or inline helpers `kernel_fpu_begin`, `kernel_fpu_end`, `_init_fpu`, `_save_fp`, `_restore_fp`, `_save_fp_context`, `_restore_fp_context`, `_save_lsx`, `_restore_lsx`, `_init_lsx_upper`, `_restore_lsx_upper`, `_save_lsx_context`, and representative local types `sigcontext`. Direct includes seen in the header are `asm/cpu-features.h`, `asm/cpu.h`, `asm/current.h`, `asm/loongarch.h`, `asm/processor.h`, `asm/ptrace.h`, `linux/bitops.h`, `linux/ptrace.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header ties CPU feature detection, CSR_EUEN bits, thread flags, signal frames, context switch and kernel FPU users together. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: preemption windows, lazy ownership flags and upper SIMD state are high-risk; tests need signal, ptrace, context-switch and SIMD workloads. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ftrace.h

## Purpose

`ftrace.h` defines LoongArch ftrace and graph tracing hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 91 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: _mcount, prepare_ftrace_return, dyn_arch_ftrace, ftrace_init_nop, ftrace_call_adjust, arch_ftrace_get_regs, ftrace_graph_func. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_FTRACE_H`, `FTRACE_PLT_IDX`, `FTRACE_REGS_PLT_IDX`, `NR_FTRACE_PLTS`, `MCOUNT_INSN_SIZE`, `mcount`, `ARCH_SUPPORTS_FTRACE_OPS`, `ftrace_init_nop`, `ftrace_regs_get_frame_pointer`, `ftrace_graph_func`, `arch_ftrace_set_direct_caller`, representative callable declarations or inline helpers `_mcount`, `prepare_ftrace_return`, `ftrace_init_nop`, `ftrace_call_adjust`, `prepare_ftrace_return`, `arch_ftrace_get_regs`, `ftrace_graph_func`, and representative local types `dyn_ftrace`, `dyn_arch_ftrace`, `ftrace_ops`. Direct includes seen in the header are `linux/ftrace_regs.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by dynamic ftrace, function graph tracer, kprobes and module text patching. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: instruction patch size, callsite adjustment and pt_regs extraction must match generated prologues. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/futex.h

## Purpose

`futex.h` implements futex atomic operations against user memory. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 94 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: arch_futex_atomic_op_inuser and futex_atomic_cmpxchg_inatomic. Symbol extraction from the file shows representative defines `_ASM_FUTEX_H`, `__futex_atomic_op`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm/asm-extable.h`, `asm/barrier.h`, `asm/errno.h`, `linux/futex.h`, `linux/uaccess.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header uses LL/SC style user accesses and exception fixups; consumed by futex syscall code. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: must return correct -EFAULT/-ENOSYS behavior and preserve atomicity under faults and contention. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/gpr-num.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/gpr-num.h

## Purpose

`gpr-num.h` defines general-purpose register numbers for assembly and DWARF-like consumers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 52 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: __DEFINE_ASM_GPR_NUMS and register aliases. Symbol extraction from the file shows representative defines `__ASM_GPR_NUM_H`, `__DEFINE_ASM_GPR_NUMS`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by assembly, stack unwinding and generated offsets. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: numeric aliases must match LoongArch ABI register numbering. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/gpr-num.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hardirq.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hardirq.h

## Purpose

`hardirq.h` defines hard IRQ accounting support. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 34 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: irq_cpustat_t, ack_bad_irq, arch_irq_stat_cpu/arch_irq_stat. Symbol extraction from the file shows representative defines `_ASM_HARDIRQ_H`, `ack_bad_irq`, `NR_IPI`, `__ARCH_IRQ_STAT`, representative callable declarations or inline helpers `ack_bad_irq`, and representative local types `ipi_msg_type`, `struct`. Direct includes seen in the header are `linux/cache.h`, `linux/irq.h`, `linux/threads.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates generic irq_cpustat with LoongArch IRQ handling. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: per-CPU accounting layout must remain compatible with generic hardirq code. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/highmem.h

## Purpose

`highmem.h` defines highmem pkmap and kmap-local hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 43 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: pkmap_page_table, kmap_flush_tlb, LAST_PKMAP, PKMAP_NR/ADDR, arch_kmap_local_post_map/unmap. Symbol extraction from the file shows representative defines `_ASM_HIGHMEM_H`, `ARCH_HAS_KMAP_FLUSH_TLB`, `LAST_PKMAP`, `LAST_PKMAP_MASK`, `PKMAP_NR`, `PKMAP_ADDR`, `flush_cache_kmaps`, `arch_kmap_local_post_map`, `arch_kmap_local_post_unmap`, representative callable declarations or inline helpers `kmap_flush_tlb`, and representative local types none visible in this header. Direct includes seen in the header are `asm/kmap_size.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used only in highmem-capable builds with local TLB flushes after temporary mappings. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: PKMAP sizing and TLB flush coverage are key correctness signals. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hugetlb.h

## Purpose

`hugetlb.h` provides hugetlb pte operations. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 76 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: huge_pte_clear, huge_ptep_get_and_clear, huge_ptep_clear_flush, huge_pte_none, huge_ptep_set_access_flags. Symbol extraction from the file shows representative defines `__ASM_HUGETLB_H`, `__HAVE_ARCH_HUGE_PTE_CLEAR`, `__HAVE_ARCH_HUGE_PTEP_GET_AND_CLEAR`, `__HAVE_ARCH_HUGE_PTEP_CLEAR_FLUSH`, `__HAVE_ARCH_HUGE_PTE_NONE`, `__HAVE_ARCH_HUGE_PTEP_SET_ACCESS_FLAGS`, representative callable declarations or inline helpers `huge_pte_clear`, `huge_ptep_get_and_clear`, `huge_ptep_clear_flush`, `huge_pte_none`, `huge_ptep_set_access_flags`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/hugetlb.h`, `asm/page.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates huge pages with generic hugetlb and LoongArch pte helpers. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: must flush TLBs on clearing and preserve access/dirty semantics. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hw_breakpoint.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hw_irq.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hw_irq.h

## Purpose

`hw_irq.h` declares low-level IRQ initialization and dispatch. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 19 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: init_IRQ, do_IRQ. Symbol extraction from the file shows representative defines `__ASM_HW_IRQ_H`, `ARCH_IRQ_INIT_FLAGS`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `linux/atomic.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header connects platform interrupt setup and generic irq entry. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: minimal declarations; calling convention and initialization order are the main risks. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/idle.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/idle.h

## Purpose

`idle.h` declares architecture idle entry. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 9 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: arch_cpu_idle. Symbol extraction from the file shows representative defines `__ASM_IDLE_H`, representative callable declarations or inline helpers `__arch_cpu_idle`, and representative local types none visible in this header. Direct includes seen in the header are `linux/linkage.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by CPU idle loop and power-management paths. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: must preserve interrupt state and wake reliably. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/idle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/image.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/image.h

## Purpose

`image.h` defines LoongArch kernel image header layout and flags. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 52 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: loongarch_kernel_header, MZ_MAGIC, kernel image load/entry fields. Symbol extraction from the file shows representative defines `__ASM_IMAGE_H`, representative callable declarations or inline helpers `loongarch_header_check_dos_sig`, and representative local types `loongarch_image_header`. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by boot loaders, EFI stub and compressed/uncompressed kernel image validation. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: layout is external boot ABI; magic, endianness and field offsets must remain stable. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/inst.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/inst.h

## Purpose

`inst.h` models LoongArch instruction encodings and instruction patch/generation helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 809 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: opcode enums, format structs, union loongarch_instruction, loongarch_gpr, is_branch/break/pc/stack/ra helpers, simu_pc/branch, larch_insn_* read/write/patch/generate, emit_* helpers, unaligned access emulation. Symbol extraction from the file shows representative defines `_ASM_INST_H`, `INSN_NOP`, `INSN_BREAK`, `INSN_HVCL`, `ADDR_IMMMASK_LU52ID`, `ADDR_IMMMASK_LU32ID`, `ADDR_IMMMASK_LU12IW`, `ADDR_IMMMASK_ORI`, `ADDR_IMMMASK_ADDU16ID`, `ADDR_IMMSHIFT_LU52ID`, `ADDR_IMMSBIDX_LU52ID`, `ADDR_IMMSHIFT_LU32ID`, representative callable declarations or inline helpers `is_imm_negative`, `is_break_ins`, `is_pc_ins`, `is_branch_ins`, `is_ra_save_ins`, `is_stack_alloc_ins`, `is_self_loop_ins`, `simu_pc`, `simu_branch`, `insns_not_supported`, `insns_need_simulation`, `arch_simulate_insn`, and representative local types `reg0i15_op`, `reg0i26_op`, `reg1i20_op`, `reg1i21_op`, `reg2_op`, `reg2i5_op`, `reg2i6_op`, `reg2i12_op`, `reg2i14_op`, `reg2i16_op`. Direct includes seen in the header are `asm/asm.h`, `asm/ptrace.h`, `linux/bitops.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header central to alternatives, ftrace, kprobes, BPF, module PLT, KVM emulation and unaligned access traps. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: bitfield layout, immediate sign extension and text patch synchronization are critical; test with tracing, probes and branch-range cases. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/inst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/io.h

## Purpose

`io.h` defines MMIO, port IO and memory mapping helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 91 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: ioremap variants, virt_to_phys/phys_to_virt integration, read/write accessors through generic IO. Symbol extraction from the file shows representative defines `_ASM_IO_H`, `early_memremap`, `early_memunmap`, `ioremap`, `iounmap`, `ioremap_wc`, `ioremap_cache`, `mmiowb`, `__io_aw`, `virt_to_phys`, `phys_to_virt`, `ARCH_HAS_VALID_PHYS_ADDR_RANGE`, representative callable declarations or inline helpers `early_ioremap`, `early_iounmap`, `ioremap_prot`, `valid_phys_addr_range`, `valid_mmap_phys_addr_range`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/io.h`, `asm/addrspace.h`, `asm/cpu.h`, `asm/page.h`, `asm/pgtable-bits.h`, `asm/string.h`, `linux/kernel.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by drivers, firmware table mapping and platform code. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: mapping attributes and barriers must match device ordering; unaligned or cached MMIO mappings are risky. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq.h

## Purpose

`irq.h` defines IRQ stack, vector numbering, interrupt domains and ACPI interrupt-controller state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 144 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: irq_stack, on_irq_stack, NR_VECTORS, AVEC encoding, NR_IRQS, acpi_vector_group, get_percpu_irq, interrupt-controller fwnode globals. Symbol extraction from the file shows representative defines `_ASM_IRQ_H`, `IRQ_STACK_SIZE`, `IRQ_STACK_START`, `NR_IRQS_LEGACY`, `NR_VECTORS`, `NR_LEGACY_VECTORS`, `AVEC_IRQ_SHIFT`, `AVEC_IRQ_BIT`, `AVEC_IRQ_MASK`, `AVEC_CPU_SHIFT`, `AVEC_CPU_BIT`, `AVEC_CPU_MASK`, representative callable declarations or inline helpers `on_irq_stack`, `spurious_interrupt`, `arch_trigger_cpumask_backtrace`, `complete_irq_moving`, `get_percpu_irq`, and representative local types `acpi_vector_group`, `acpi_madt_lio_pic`, `acpi_madt_eio_pic`, `acpi_madt_ht_pic`, `acpi_madt_bio_pic`, `acpi_madt_msi_pic`, `acpi_madt_lpc_pic`, `fwnode_handle`. Direct includes seen in the header are `asm-generic/irq.h`, `linux/irqdomain.h`, `linux/irqreturn.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates CPU, LIO, EIO, PCH, MSI and ACPI MADT interrupt setup. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: vector math, MAX_IO_PICS and domain handles affect all interrupt delivery. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq_regs.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq_regs.h

## Purpose

`irq_regs.h` stores current IRQ pt_regs in thread_info. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 27 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: get_irq_regs and set_irq_regs. Symbol extraction from the file shows representative defines `__ASM_IRQ_REGS_H`, `ARCH_HAS_OWN_IRQ_REGS`, representative callable declarations or inline helpers `get_irq_regs`, `set_irq_regs`, and representative local types none visible in this header. Direct includes seen in the header are `linux/thread_info.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by generic IRQ/tracing code to find interrupted register state. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: nested IRQ paths depend on restoring the previous regs pointer. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq_work.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq_work.h

## Purpose

`irq_work.h` advertises IRQ work interrupt support. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 10 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: arch_irq_work_has_interrupt. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_IRQ_WORK_H`, representative callable declarations or inline helpers `arch_irq_work_has_interrupt`, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header enabled only for SMP systems with CSR IPI support. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: incorrect feature gating can make irq_work rely on unavailable IPIs. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irqflags.h

## Purpose

`irqflags.h` implements local interrupt enable/disable/save/restore. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 85 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: arch_local_irq_enable/disable/save/restore, arch_local_save_flags, arch_irqs_disabled_flags/disabled, raw_irqs_disabled_flags. Symbol extraction from the file shows representative defines `_ASM_IRQFLAGS_H`, representative callable declarations or inline helpers `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_irq_save`, `arch_local_irq_restore`, `arch_local_save_flags`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, and representative local types none visible in this header. Direct includes seen in the header are `asm/loongarch.h`, `linux/compiler.h`, `linux/stringify.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header uses CSR_CRMD.IE via csrxchg/csrrd and backs generic irqflags/locking code. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: memory clobbers and mask register constraints are critical for ordering and correctness. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/jump_label.h

## Purpose

`jump_label.h` implements static key patch-site layout. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 64 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: JUMP_LABEL_NOP_SIZE, JUMP_TABLE_ENTRY, ARCH_STATIC_BRANCH_ASM, arch_static_branch, arch_static_branch_jump. Symbol extraction from the file shows representative defines `__ASM_JUMP_LABEL_H`, `HAVE_JUMP_LABEL_BATCH`, `JUMP_LABEL_NOP_SIZE`, `JUMP_LABEL_TYPE`, `JUMP_LABEL_TYPE`, `JUMP_TABLE_ENTRY`, `ARCH_STATIC_BRANCH_ASM`, representative callable declarations or inline helpers `arch_static_branch`, `arch_static_branch_jump`, and representative local types none visible in this header. Direct includes seen in the header are `asm/asm.h`, `linux/stringify.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by jump labels/static branches and runtime code patching. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: entry layout differs by 32/64-bit; branch patching depends on exact NOP size. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kasan.h

## Purpose

`kasan.h` defines KASAN shadow layout and initialization hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 87 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: KASAN_SHADOW_OFFSET/SCALE_SIZE, KASAN_SHADOW_START/END, kasan_init, kasan_early_init, kasan_populate_early_shadow. Symbol extraction from the file shows representative defines `__ASM_KASAN_H`, `KASAN_SHADOW_SCALE_SHIFT`, `KASAN_SHADOW_OFFSET`, `XRANGE_SHIFT`, `XRANGE_SHADOW_SHIFT`, `XRANGE_SHADOW_MASK`, `XRANGE_SIZE`, `XKPRANGE_UC_SEG`, `XKPRANGE_CC_SEG`, `XKPRANGE_WC_SEG`, `XKVRANGE_VC_SEG`, `XKPRANGE_CC_START`, representative callable declarations or inline helpers `kasan_mem_to_shadow`, `addr_has_metadata`, `kasan_init`, `kasan_early_init`, and representative local types none visible in this header. Direct includes seen in the header are `asm/addrspace.h`, `asm/io.h`, `asm/pgtable.h`, `linux/linkage.h`, `linux/mmzone.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates memory sanitizer with LoongArch virtual memory layout. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: shadow address arithmetic must match vmalloc/module/kernel ranges. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kdebug.h

## Purpose

`kdebug.h` defines die notifier event values. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 18 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: enum die_val with DIE_OOPS, DIE_FP, DIE_TRAP, DIE_RI, DIE_PAGE_FAULT and related values. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_KDEBUG_H`, representative callable declarations or inline helpers none visible in this header, and representative local types `die_val`. Direct includes seen in the header are `linux/notifier.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by die chains, kprobes/kgdb and exception diagnostics. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: event numbering is internal but consumers must agree on semantic event types. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kexec.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kfence.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kfence.h

## Purpose

`kfence.h` adapts KFENCE guard pool mapping. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 71 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: arch_kfence_init_pool and split_pte helpers when enabled. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_KFENCE_H`, representative callable declarations or inline helpers `arch_kfence_init_pool`, `kfence_protect_page`, and representative local types none visible in this header. Direct includes seen in the header are `asm/pgtable.h`, `asm/tlb.h`, `linux/kfence.h`, `linux/vmalloc.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates KFENCE with page-table permissions and TLB/cache synchronization. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: guard-page protection depends on correct PTE splitting and flushing. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kgdb.h

## Purpose

`kgdb.h` defines KGDB register layout and breakpoint instruction. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 97 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: BREAK_INSTR_SIZE, CACHE_FLUSH_IS_SAFE, NUMREGBYTES, BUFMAX, kgdb_arch_set_pc, sleeping_thread_to_gdb_regs. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_KGDB_H`, `GDB_SIZEOF_REG`, `DBG_PT_REGS_BASE`, `DBG_PT_REGS_NUM`, `DBG_PT_REGS_END`, `DBG_FPR_BASE`, `DBG_FPR_NUM`, `DBG_FPR_END`, `DBG_FCC_BASE`, `DBG_FCC_NUM`, `DBG_FCC_END`, `DBG_FCSR_NUM`, representative callable declarations or inline helpers `kgdb_breakinst`, `arch_kgdb_breakpoint`, `kgdb_breakpoint_handler`, `kgdb_breakpoint_handler`, and representative local types `dbg_loongarch_regnum`. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header connects KGDB to LoongArch pt_regs, software breakpoints and debug exception flow. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: register byte layout and PC updates must match GDB remote protocol expectations. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kprobes.h

## Purpose

`kprobes.h` defines kprobe instruction slots and handlers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 58 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: kprobe_opcode_t, arch_specific_insn, flush_insn_slot, kprobe_fault_handler, kprobe_exceptions_notify, arch_prepare_kprobe, arch_post_kprobe_handler. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KPROBES_H`, `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot`, `kretprobe_blacklist_size`, representative callable declarations or inline helpers `arch_remove_kprobe`, `kprobe_fault_handler`, `kprobe_breakpoint_handler`, `kprobe_singlestep_handler`, `kprobe_breakpoint_handler`, `kprobe_singlestep_handler`, and representative local types `u32`, `arch_specific_insn`, `prev_kprobe`, `kprobe_ctlblk`. Direct includes seen in the header are `asm-generic/kprobes.h`, `asm/cacheflush.h`, `asm/inst.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header uses instruction decoding/patching and exception notifiers for dynamic probes. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: single-step simulation and prohibited instruction detection are key test areas. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_csr.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_csr.h

## Purpose

`kvm_csr.h` maps LoongArch guest CSR IDs to KVM software/hardware handling flags. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 217 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: KVM_CSR_* flag table macros, kvm_emu_iocsr, kvm_read/write/set/change_sw_gcsr, KVM_PMU_EVENT_ENABLED. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_CSR_H__`, `gcsr_read`, `gcsr_write`, `gcsr_xchg`, `read_gcsr_crmd`, `write_gcsr_crmd`, `read_gcsr_prmd`, `write_gcsr_prmd`, `read_gcsr_euen`, `write_gcsr_euen`, `read_gcsr_misc`, `write_gcsr_misc`, representative callable declarations or inline helpers `kvm_emu_iocsr`, `kvm_read_sw_gcsr`, `kvm_write_sw_gcsr`, `kvm_set_sw_gcsr`, `kvm_change_sw_gcsr`, and representative local types none visible in this header. Direct includes seen in the header are `asm/kvm_vcpu.h`, `asm/loongarch.h`, `linux/kvm_host.h`, `linux/uaccess.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by KVM exits, CSR emulation, PMU virtualization and guest state save/restore. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: CSR classification errors can expose host state or lose guest state. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_dmsintc.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_dmsintc.h

## Purpose

`kvm_dmsintc.h` declares the KVM device-model software interrupt controller constants. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 27 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: DMSINTC IRQ/device constants and registration prototype. Symbol extraction from the file shows representative defines `__ASM_KVM_DMSINTC_H`, representative callable declarations or inline helpers `kvm_loongarch_register_dmsintc_device`, `dmsintc_inject_irq`, `dmsintc_set_irq`, `dmsintc_deliver_msi_to_vcpu`, and representative local types `loongarch_dmsintc`, `dmsintc_state`. Direct includes seen in the header are `linux/kvm_types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by LoongArch KVM virtual interrupt device setup. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: small ABI surface; risk is mismatch with userspace device attributes. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_dmsintc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_eiointc.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_eiointc.h

## Purpose

`kvm_eiointc.h` defines KVM extended IO interrupt controller state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 84 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: EIOINTC constants, loongarch_eiointc, kvm_loongarch_register_eiointc_device, eiointc_set_irq. Symbol extraction from the file shows representative defines `__ASM_KVM_EIOINTC_H`, `EIOINTC_IRQS`, `EIOINTC_ROUTE_MAX_VCPUS`, `EIOINTC_IRQS_U64_NUMS`, `EIOINTC_IRQS_NODETYPE_COUNT`, `EIOINTC_BASE`, `EIOINTC_SIZE`, `EIOINTC_NODETYPE_START`, `EIOINTC_NODETYPE_END`, `EIOINTC_IPMAP_START`, `EIOINTC_IPMAP_END`, `EIOINTC_ENABLE_START`, representative callable declarations or inline helpers `kvm_loongarch_register_eiointc_device`, `eiointc_set_irq`, and representative local types `loongarch_eiointc`. Direct includes seen in the header are `kvm/iodev.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header emulates extended IO interrupt routing for LoongArch guests. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: bitmap/routing state must remain synchronized with vCPU interrupt injection. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_eiointc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_host.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_host.h

## Purpose

`kvm_host.h` defines LoongArch KVM VM/vCPU architecture state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 370 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: kvm_vm_stat, kvm_vcpu_stat, kvm_context, kvm_world_switch, kvm_arch, loongarch_csrs, kvm_vcpu_arch, feature helpers, TLB/MM fault and guest-entry prototypes. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_HOST_H__`, `__KVM_HAVE_ARCH_INTC_INITIALIZED`, `KVM_GET_IOC_CSR_IDX`, `KVM_GET_IOC_CPUCFG_IDX`, `KVM_MAX_VCPUS`, `KVM_MAX_CPUCFG_REGS`, `KVM_HALT_POLL_NS_DEFAULT`, `KVM_REQ_TLB_FLUSH_GPA`, `KVM_REQ_STEAL_UPDATE`, `KVM_REQ_PMU`, `KVM_REQ_AUX_LOAD`, `KVM_GUESTDBG_SW_BP_MASK`, representative callable declarations or inline helpers `readl_sw_gcsr`, `writel_sw_gcsr`, `kvm_guest_has_msgint`, `kvm_guest_has_fpu`, `kvm_guest_has_lsx`, `kvm_guest_has_lasx`, `kvm_guest_has_lbt`, `kvm_guest_has_pmu`, `kvm_get_pmu_num`, `kvm_vm_support`, `kvm_arch_pmi_in_guest`, `kvm_arch_vcpu_dump_regs`, and representative local types `kvm_vm_stat`, `kvm_vcpu_stat`, `kvm_arch_memory_slot`, `kvm_context`, `kvm_world_switch`, `kvm_phyid_info`, `kvm_phyid_map`, `kvm_arch`, `loongarch_csrs`, `emulation_result`. Direct includes seen in the header are `asm/inst.h`, `asm/kvm_dmsintc.h`, `asm/kvm_eiointc.h`, `asm/kvm_ipi.h`, `asm/kvm_mmu.h`, `asm/kvm_pch_pic.h`, `asm/loongarch.h`, `linux/cpumask.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header central integration point between generic KVM, LoongArch world switch, MMU, IRQ, timer, PMU and userspace ioctl state. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: state persistence is per-VM/vCPU; feature flags, CSR arrays and TLB flushing are high-risk. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_ipi.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_ipi.h

## Purpose

`kvm_ipi.h` defines KVM IPI emulation state and helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 45 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: LoongArch IPI register layout, device state and set/clear/send helpers. Symbol extraction from the file shows representative defines `__ASM_KVM_IPI_H`, `LARCH_INT_IPI`, `IOCSR_IPI_BASE`, `IOCSR_IPI_SIZE`, `IOCSR_IPI_STATUS`, `IOCSR_IPI_EN`, `IOCSR_IPI_SET`, `IOCSR_IPI_CLEAR`, `IOCSR_IPI_BUF_20`, `IOCSR_IPI_BUF_28`, `IOCSR_IPI_BUF_30`, `IOCSR_IPI_BUF_38`, representative callable declarations or inline helpers `kvm_loongarch_register_ipi_device`, and representative local types `loongarch_ipi`, `ipi_state`. Direct includes seen in the header are `kvm/iodev.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by virtual CPU interrupt delivery and IOCSR/IPI emulation. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: concurrency around pending bits and vCPU routing is the primary risk. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_ipi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_mmu.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_mmu.h

## Purpose

`kvm_mmu.h` implements helpers for KVM stage page tables. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 151 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: kvm_pte_t, kvm_ptw_ctx, kvm_set_pte, kvm_pte_* accessors, kvm_pgtable_offset, kvm_pgtable_addr_end, kvm_ptw_enter/exit. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_MMU_H__`, `KVM_MMU_CACHE_MIN_PAGES`, `KVM_PAGE_WRITEABLE`, `_KVM_FLUSH_PGTABLE`, `_KVM_HAS_PGMASK`, `kvm_pfn_pte`, `kvm_pte_pfn`, representative callable declarations or inline helpers `kvm_set_pte`, `kvm_pte_young`, `kvm_pte_huge`, `kvm_pte_dirty`, `kvm_pte_writeable`, `kvm_pte_mkyoung`, `kvm_pte_mkold`, `kvm_pte_mkdirty`, `kvm_pte_mkclean`, `kvm_pte_mkhuge`, `kvm_pte_mksmall`, `kvm_pte_mkwriteable`, and representative local types `unsigned`, `struct`, `int`, `kvm_ptw_ctx`. Direct includes seen in the header are `asm/pgalloc.h`, `asm/tlb.h`, `linux/kvm_host.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by KVM MMU fault handling, aging, hugepage and TLB flush paths. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: PTE flag translation, page-size levels and lock handling need MMU notifier and dirty-log tests. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_para.h

## Purpose

`kvm_para.h` defines guest paravirtual hypercall interface. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 189 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: KVM_HCALL_* encodings, kvm_steal_time, kvm_hypercall0-5, kvm_para_available, kvm_arch_para_features/hints. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_KVM_PARA_H`, `HYPERVISOR_KVM`, `HYPERVISOR_VENDOR_SHIFT`, `HYPERCALL_ENCODE`, `KVM_HCALL_CODE_SERVICE`, `KVM_HCALL_CODE_SWDBG`, `KVM_HCALL_CODE_USER_SERVICE`, `KVM_HCALL_SERVICE`, `KVM_HCALL_FUNC_IPI`, `KVM_HCALL_FUNC_NOTIFY`, `KVM_HCALL_SWDBG`, `KVM_HCALL_USER_SERVICE`, representative callable declarations or inline helpers `kvm_hypercall0`, `kvm_hypercall1`, `kvm_hypercall2`, `kvm_hypercall3`, `kvm_hypercall4`, `kvm_hypercall5`, `kvm_para_available`, `kvm_arch_para_features`, `kvm_para_available`, `kvm_arch_para_features`, `kvm_arch_para_hints`, `kvm_check_and_clear_guest_paused`, and representative local types `kvm_steal_time`. Direct includes seen in the header are `uapi/asm/kvm_para.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header guest kernels use `hvcl` hypercalls for KVM services and steal-time accounting. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: argument register conventions and clobbers are ABI-sensitive. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_pch_pic.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_pch_pic.h

## Purpose

`kvm_pch_pic.h` defines KVM PCH PIC emulation state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 76 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: PCH PIC constants, state struct and registration/set-irq helpers. Symbol extraction from the file shows representative defines `__ASM_KVM_PCH_PIC_H`, `PCH_PIC_SIZE`, `PCH_PIC_INT_ID_START`, `PCH_PIC_INT_ID_END`, `PCH_PIC_MASK_START`, `PCH_PIC_MASK_END`, `PCH_PIC_HTMSI_EN_START`, `PCH_PIC_HTMSI_EN_END`, `PCH_PIC_EDGE_START`, `PCH_PIC_EDGE_END`, `PCH_PIC_CLEAR_START`, `PCH_PIC_CLEAR_END`, representative callable declarations or inline helpers `kvm_loongarch_register_pch_pic_device`, `pch_pic_set_irq`, `pch_msi_set_irq`, and representative local types `pch_pic_id`, `loongarch_pch_pic`, `kvm_kernel_irq_routing_entry`. Direct includes seen in the header are `kvm/iodev.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header models Loongson PCH interrupt controller for guests. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: level/edge state and irq routing must match userspace-visible virtual hardware. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_pch_pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_types.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_types.h

## Purpose

`kvm_types.h` provides LoongArch KVM type aliases. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 11 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: architecture-specific KVM typedef hooks. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_KVM_TYPES_H`, `KVM_ARCH_NR_OBJS_PER_MEMORY_CACHE`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header included by generic KVM headers to complete arch type definitions. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: minimal wrapper; build coverage is the main signal. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_vcpu.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_vcpu.h

## Purpose

`kvm_vcpu.h` declares vCPU exit handling, emulation and interrupt helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 140 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: larch_inst, exit_handle_fn, kvm_check_requests, kvm_handle_* exits, kvm_queue_irq, kvm_complete_iocsr_read, kvm_save/restore_timer, kvm_init/reset_vcpu. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_VCPU_H__`, `CPU_SIP0`, `CPU_SIP1`, `CPU_PMU`, `CPU_TIMER`, `CPU_IPI`, `CPU_AVEC`, `CPU_IP0`, `CPU_IP1`, `CPU_IP2`, `CPU_IP3`, `CPU_IP4`, representative callable declarations or inline helpers `kvm_emu_mmio_read`, `kvm_emu_mmio_write`, `kvm_complete_mmio_read`, `kvm_complete_iocsr_read`, `kvm_complete_user_service`, `kvm_emu_idle`, `kvm_pending_timer`, `kvm_handle_fault`, `kvm_deliver_intr`, `kvm_deliver_exception`, `kvm_own_fpu`, `kvm_lose_fpu`, and representative local types `union`, `int`, `kvm_vcpu`. Direct includes seen in the header are `asm/loongarch.h`, `linux/kvm_host.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header connects KVM guest exits to instruction decoding, CSR/IOCSR, MMU, IRQ and timer emulation. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: exit dispatch ordering and PC advancement are high-risk under nested faults or emulation failures. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_vcpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/lbt.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/lbt.h

## Purpose

`lbt.h` manages LoongArch binary-translation extension state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 113 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: _init/_save/_restore_lbt, context copy helpers, is_lbt_enabled/owner, own/lose/init_lbt, thread_lbt_context_live. Symbol extraction from the file shows representative defines `_ASM_LBT_H`, representative callable declarations or inline helpers `_init_lbt`, `_save_lbt`, `_restore_lbt`, `_save_lbt_context`, `_restore_lbt_context`, `_save_ftop_context`, `_restore_ftop_context`, `is_lbt_enabled`, `is_lbt_owner`, `enable_lbt`, `disable_lbt`, `__own_lbt`, and representative local types none visible in this header. Direct includes seen in the header are `asm/cpu.h`, `asm/current.h`, `asm/loongarch.h`, `asm/processor.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header uses CSR_EUEN.LBTEN and thread flags during exceptions, signal and context switching. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: lazy ownership and user context save/restore need tests with LBT-capable CPUs. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/lbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/linkage.h

## Purpose

`linkage.h` defines assembly symbol and CFI wrappers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 80 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: SYM_FUNC_START/END, SYM_CODE_START/END, SYM_SIGFUNC_START/END. Symbol extraction from the file shows representative defines `__ASM_LINKAGE_H`, `__ALIGN`, `__ALIGN_STR`, `SYM_FUNC_START`, `SYM_FUNC_START_NOALIGN`, `SYM_FUNC_START_LOCAL`, `SYM_FUNC_START_LOCAL_NOALIGN`, `SYM_FUNC_START_WEAK`, `SYM_FUNC_START_WEAK_NOALIGN`, `SYM_FUNC_END`, `SYM_CODE_START`, `SYM_CODE_END`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by LoongArch assembly entry, vdso/signal trampoline and unwinding metadata. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: signal trampoline CFI is ABI-sensitive and includes a nop workaround for a libgcc issue. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/local.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/local.h

## Purpose

`local.h` implements per-CPU local counters using atomics/AMO or LL/SC. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 188 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: local_t, LOCAL_INIT, local_read/set/add/sub/inc/dec, local_add/sub_return, local_cmpxchg, local_try_cmpxchg, local_add_unless. Symbol extraction from the file shows representative defines `_ARCH_LOONGARCH_LOCAL_H`, `LOCAL_INIT`, `local_read`, `local_set`, `local_add`, `local_sub`, `local_inc`, `local_dec`, `local_xchg`, `local_inc_not_zero`, `local_dec_return`, `local_inc_return`, representative callable declarations or inline helpers `local_add_return`, `local_sub_return`, `local_add_return`, `local_sub_return`, `local_cmpxchg`, `local_try_cmpxchg`, and representative local types `struct`. Direct includes seen in the header are `asm/asm.h`, `asm/cmpxchg.h`, `linux/atomic.h`, `linux/bitops.h`, `linux/percpu.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used where operations are CPU-local but still need atomic instruction semantics. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: AMO versus LL/SC paths must agree on return value and barriers. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/loongarch.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/loongarch.h

## Purpose

`loongarch.h` is the master LoongArch register, CSR, IOCSR, exception and FPU constant header. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 1629 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: read_cpucfg, csr/iocsr accessors, LOONGARCH_CSR_* fields, interrupt bits, IOCSR extioi/IPI definitions, rdtime helpers, CSR helper macros, exception codes, FPU CSR masks. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_H`, `read_cpucfg`, `REG_ZERO`, `REG_RA`, `REG_TP`, `REG_SP`, `REG_A0`, `REG_A1`, `REG_A2`, `REG_A3`, `REG_A4`, `REG_A5`, representative callable declarations or inline helpers `rdtime_h`, `rdtime_l`, `rdtime_d`, `get_csr_cpuid`, `csr_any_send`, `read_csr_excode`, `write_csr_index`, `read_csr_pagesize`, `write_csr_pagesize`, `read_csr_tlbrefill_pagesize`, `write_csr_tlbrefill_pagesize`, and representative local types none visible in this header. Direct includes seen in the header are `larchintrin.h`, `linux/bits.h`, `linux/linkage.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header included by most arch code: entry, MMU, IRQ, KVM, FPU, perf, topology and platform drivers. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: large hardware ABI surface; bit shifts, typo-compatible names and 32/64-bit access width choices require broad build and boot testing. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/loongarch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/loongson.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/loongson.h

## Purpose

`loongson.h` defines Loongson platform MMIO regions and chipset registers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 142 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: LOONGSON_REG ranges, LS7A register bases, xconf_read/write, ls7a_read/write, enable_gpe_wakeup, enable_pci_wakeup. Symbol extraction from the file shows representative defines `__ASM_LOONGSON_H`, `LOONGSON_REG`, `LOONGSON_LIO_BASE`, `LOONGSON_LIO_SIZE`, `LOONGSON_LIO_TOP`, `LOONGSON_BOOT_BASE`, `LOONGSON_BOOT_SIZE`, `LOONGSON_BOOT_TOP`, `LOONGSON_REG_BASE`, `LOONGSON_REG_SIZE`, `LOONGSON_REG_TOP`, `LOONGSON_GPIODATA`, representative callable declarations or inline helpers `xconf_writel`, `xconf_writeq`, `enable_gpe_wakeup`, `enable_pci_wakeup`, and representative local types `enum`. Direct includes seen in the header are `asm/addrspace.h`, `asm/bootinfo.h`, `linux/init.h`, `linux/io.h`, `linux/irq.h`, `linux/pci.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by platform, ACPI, PCI, IRQ and power-management code for Loongson systems. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: hard-coded physical addresses and uncached mappings are platform ABI; wrong register offsets can affect interrupts or wakeup. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/loongson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/mmu.h

## Purpose

`mmu.h` defines LoongArch mm_context state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 16 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: mm_context_t containing ASID array and related lock/state. Symbol extraction from the file shows representative defines `__ASM_MMU_H`, representative callable declarations or inline helpers none visible in this header, and representative local types `struct`. Direct includes seen in the header are `linux/atomic.h`, `linux/spinlock.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by mm_struct context handling and ASID allocation. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: state persists per address space; ASID generation and locking interact with TLB flush correctness. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/mmu_context.h

## Purpose

`mmu_context.h` implements ASID and page-directory switching. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 171 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: asid_version_mask, asid_first_version, asid_valid, enter_lazy_tlb, get_new_mmu_context, init_new_context, atomic_update_pgd_asid, switch_mm_irqs_off, destroy_context, activate_mm. Symbol extraction from the file shows representative defines `_ASM_MMU_CONTEXT_H`, `cpu_context`, `asid_cache`, `cpu_asid`, `switch_mm_irqs_off`, `activate_mm`, `deactivate_mm`, representative callable declarations or inline helpers `asid_version_mask`, `asid_first_version`, `asid_valid`, `enter_lazy_tlb`, `atomic_update_pgd_asid`, `switch_mm_irqs_off`, `switch_mm`, `destroy_context`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/mm_hooks.h`, `asm/cacheflush.h`, `asm/tlbflush.h`, `linux/errno.h`, `linux/mm_types.h`, `linux/sched.h`, `linux/slab.h`, `linux/smp.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header uses cpu_data ASID masks and CSR ASID/PGD registers during context switch. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: stale ASIDs or non-atomic PGD/ASID updates can cause cross-process translations. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/module.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/module.lds.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/module.lds.h

## Purpose

`module.lds.h` adds LoongArch module linker-script hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 9 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: currently an empty guarded linker include. Symbol extraction from the file shows representative defines none visible in this header, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header included by module linker scripts for arch-specific sections. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: minimal file; future sections must preserve module loader expectations. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/module.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/numa.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/numa.h

## Purpose

`numa.h` defines LoongArch NUMA address/node helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 54 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: NODE_ADDRSPACE_SHIFT, pa_to_nid, nid_to_addrbase, numa_off, __cpuid_to_node, early_numa_add_cpu, numa_add/remove_cpu, set_cpuid_to_node, early_cpu_to_node. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_NUMA_H`, `NODE_ADDRSPACE_SHIFT`, `pa_to_nid`, `nid_to_addrbase`, representative callable declarations or inline helpers `early_numa_add_cpu`, `numa_add_cpu`, `numa_remove_cpu`, `numa_clear_node`, `set_cpuid_to_node`, `early_cpu_to_node`, `early_numa_add_cpu`, `numa_add_cpu`, `numa_remove_cpu`, `set_cpuid_to_node`, `early_cpu_to_node`, and representative local types none visible in this header. Direct includes seen in the header are `linux/nodemask.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by boot memory discovery, CPU hotplug and scheduler topology. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: node-id derivation from physical address bits must match firmware and hardware routing. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_header.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_header.h

## Purpose

`orc_header.h` defines ORC unwind table header emission. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 18 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: ORC_HEADER macro and ORC hash dependency. Symbol extraction from the file shows representative defines `_ORC_HEADER_H`, `ORC_HEADER`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm/orc_hash.h`, `linux/compiler.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by generated ORC unwind metadata. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: header format must match unwinder and objtool/orc tooling. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_lookup.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_lookup.h

## Purpose

`orc_lookup.h` defines ORC lookup table geometry and bounds. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 31 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: LOOKUP_BLOCK_ORDER/SIZE, orc_lookup, orc_lookup_end, LOOKUP_START_IP, LOOKUP_STOP_IP. Symbol extraction from the file shows representative defines `_ORC_LOOKUP_H`, `LOOKUP_BLOCK_ORDER`, `LOOKUP_BLOCK_SIZE`, `LOOKUP_START_IP`, `LOOKUP_STOP_IP`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by ORC unwinder to map instruction pointers into unwind entries. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: text bounds and block size must match generated tables. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_lookup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_types.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_types.h

## Purpose

`orc_types.h` defines LoongArch ORC unwind entry format. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 58 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: ORC_REG_* constants, ORC_TYPE_* constants, struct orc_entry. Symbol extraction from the file shows representative defines `_ORC_TYPES_H`, `ORC_REG_UNDEFINED`, `ORC_REG_PREV_SP`, `ORC_REG_SP`, `ORC_REG_FP`, `ORC_REG_MAX`, `ORC_TYPE_UNDEFINED`, `ORC_TYPE_END_OF_STACK`, `ORC_TYPE_CALL`, `ORC_TYPE_REGS`, `ORC_TYPE_REGS_PARTIAL`, representative callable declarations or inline helpers none visible in this header, and representative local types `orc_entry`. Direct includes seen in the header are `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header consumed by unwinder, generated tables and stacktrace code. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: packed field meaning is an internal ABI between generator and runtime unwinder. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/orc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/page.h

## Purpose

`page.h` defines page size-derived constants, page-table scalar types and address conversion helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 110 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: HPAGE_*, ARCH_PFN_OFFSET, clear_page, copy_page, pte_t/pgd_t/pgprot_t, __pa, __va, virt_to_page, virt_addr_valid. Symbol extraction from the file shows representative defines `_ASM_PAGE_H`, `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `ARCH_PFN_OFFSET`, `copy_user_page`, `pte_val`, `__pte`, `pgd_val`, `__pgd`, `pgprot_val`, representative callable declarations or inline helpers `clear_page`, `copy_page`, `__virt_addr_valid`, and representative local types `page`, `vm_area_struct`, `struct`, `struct`, `struct`, `struct`, `page`, `page`. Direct includes seen in the header are `asm-generic/getorder.h`, `asm-generic/memory_model.h`, `asm/addrspace.h`, `linux/const.h`, `linux/kernel.h`, `linux/pfn.h`, `vdso/page.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by all memory-management, allocator, highmem and driver address conversion code. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: DMW/TLB virtual-to-page split and PHYS_OFFSET assumptions are high-risk. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/paravirt.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/paravirt.h

## Purpose

`paravirt.h` declares optional paravirtual initialization hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 29 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: pv_ipi_init, pv_time_init, pv_spinlock_init. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_PARAVIRT_H`, representative callable declarations or inline helpers `pv_ipi_init`, `pv_time_init`, `pv_spinlock_init`, `pv_ipi_init`, `pv_time_init`, `pv_spinlock_init`, and representative local types none visible in this header. Direct includes seen in the header are none visible in this header. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used when PARAVIRT is enabled to initialize PV IPI/time/spinlock behavior. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: stubbed to zero when disabled; feature detection should keep bare-metal paths unchanged. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/paravirt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pci.h

## Purpose

`pci.h` defines LoongArch PCI policy constants and MCFG init hook. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 25 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: PCIBIOS_MIN_IO/MEM/CARDBUS_IO, HAVE_PCI_MMAP, pcibios_assign_all_busses, mcfg_addr_init. Symbol extraction from the file shows representative defines `_ASM_PCI_H`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `PCIBIOS_MIN_CARDBUS_IO`, `HAVE_PCI_MMAP`, `pcibios_assign_all_busses`, representative callable declarations or inline helpers `mcfg_addr_init`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/pci.h`, `asm/io.h`, `linux/ioport.h`, `linux/list.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates generic PCI with LoongArch IO mapping and ACPI/MCFG setup. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: resource minima and MCFG address derivation affect enumeration and mmap behavior. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/percpu.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/percpu.h

## Purpose

`percpu.h` implements optimized this_cpu operations using LoongArch per-CPU base. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 184 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: set_my_cpu_offset, __my_cpu_offset, PERCPU_OP, this_cpu_read/write/add/and/or/xchg/cmpxchg helpers. Symbol extraction from the file shows representative defines `__ASM_PERCPU_H`, `__my_cpu_offset`, `PERCPU_OP`, `__pcpu_op_1`, `__pcpu_op_2`, `__pcpu_op_4`, `__pcpu_op_8`, `_percpu_read`, `_percpu_write`, `__percpu_xchg`, `_protect_cmpxchg_local`, `_pcp_protect`, representative callable declarations or inline helpers `set_my_cpu_offset`, `op`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/percpu.h`, `asm/cmpxchg.h`, `asm/loongarch.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header uses CSR/percpu base register and cmpxchg primitives; consumed throughout scheduler, IRQ and counters. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: inline assembly size selection and preemption protection are critical. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/perf_event.h

## Purpose

`perf_event.h` adapts perf pt_regs access for LoongArch. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 19 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: perf_arch_bpf_user_pt_regs and perf_arch_fetch_caller_regs. Symbol extraction from the file shows representative defines `__LOONGARCH_PERF_EVENT_H__`, `perf_arch_bpf_user_pt_regs`, `perf_arch_fetch_caller_regs`, representative callable declarations or inline helpers none visible in this header, and representative local types none visible in this header. Direct includes seen in the header are `asm/ptrace.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by perf sampling, BPF helpers and callchain capture. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: caller register snapshot must set PC and frame state in the format perf expects. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgalloc.h

## Purpose

`pgalloc.h` implements page-table page allocation/population hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 106 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: pmd/pud/p4d_populate, pagetable_init, pgd_alloc, pte_alloc_one_kernel, pmd_alloc_one, pud_alloc_one, populate_kernel_pte. Symbol extraction from the file shows representative defines `_ASM_PGALLOC_H`, `__HAVE_ARCH_PMD_ALLOC_ONE`, `__HAVE_ARCH_PUD_ALLOC_ONE`, `__HAVE_ARCH_PTE_ALLOC_ONE_KERNEL`, `__pte_free_tlb`, `__pmd_free_tlb`, `__pud_free_tlb`, representative callable declarations or inline helpers `pmd_populate_kernel`, `pmd_populate`, `pud_populate`, `p4d_populate`, `pagetable_init`, `pgd_alloc`, `pte_alloc_one_kernel`, `pmd_alloc_one`, `pud_alloc_one`, `populate_kernel_pte`, and representative local types none visible in this header. Direct includes seen in the header are `asm-generic/pgalloc.h`, `linux/mm.h`, `linux/sched.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates generic mm page-table allocation with LoongArch pgtable types and TLB delayed free. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: allocation zeroing, ptdesc conversion and folded-level assumptions need boot and memory-stress tests. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgalloc.h -->
