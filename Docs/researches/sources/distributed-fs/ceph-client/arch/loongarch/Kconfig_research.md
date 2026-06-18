# sources/distributed-fs/ceph-client/arch/loongarch/Kconfig

## Purpose

`Kconfig` defines the main LoongArch architecture configuration surface: 32/64-bit selection, CPU subtype, paging levels, toolchain capability probes, ACPI/EFI/PCI/NUMA/SMP/MMU support, unwinders, module support, and many generic-kernel feature selects. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public API is the Kconfig symbol set consumed by the build system and source `#ifdef`s, including `LOONGARCH`, `32BIT`, `64BIT`, `MACH_LOONGSON32`, `MACH_LOONGSON64`, paging-level symbols, toolchain probes, errata, and feature toggles. Concrete declarations observed in the file: Kconfig symbols: `LOONGARCH`, `32BIT`, `64BIT`, `32BIT_REDUCED`, `32BIT_STANDARD`, `GENERIC_BUG`, `GENERIC_BUG_RELATIVE_POINTERS`, `GENERIC_CALIBRATE_DELAY`, `GENERIC_CSUM`, `GENERIC_HWEIGHT`, `L1_CACHE_SHIFT`, `LOCKDEP_SUPPORT`, `STACKTRACE_SUPPORT`, `MACH_LOONGSON32`, `MACH_LOONGSON64`, `FIX_EARLYCON_MEM`, `PGTABLE_2LEVEL`, `PGTABLE_3LEVEL`, `PGTABLE_4LEVEL`, `PGTABLE_LEVELS`, `SCHED_OMIT_FRAME_POINTER`, `AS_HAS_EXPLICIT_RELOCS`, `AS_HAS_FCSR_CLASS`, `AS_HAS_THIN_ADD_SUB`, `AS_HAS_LSX_EXTENSION`, `AS_HAS_LASX_EXTENSION`, `AS_HAS_LBT_EXTENSION`, `AS_HAS_LVZ_EXTENSION`, `AS_HAS_SCQ_EXTENSION`, `CC_HAS_ANNOTATE_TABLEJUMP`, and 56 more. Build/script rules: `def_bool $(rustc-option,-Cllvm-args=--loongarch-annotate-tablejump)`, `(Note: power management support will enable this option`, `You can override this setting via writecombine=on/off boot parameter.`.

## Control Flow, State, And Persistence

Kconfig flow is dependency resolution, defaults, `select` propagation, and user choices. It persists in `.config` and generated autoconf headers that steer compilation.

## Dependencies And Integration Points

It integrates with generic kernel Kconfig menus, LoongArch Makefile flag selection, ACPI/EFI/PCI/SMP/MM subsystems, objtool/ORC support, and platform defconfigs.

## Risks And Test Signals

Risks are invalid selects, impossible dependencies, broken 32-bit/64-bit combinations, and enabling features without source/toolchain support. Test signals are `olddefconfig`, randconfig, 32-bit and 64-bit defconfig builds, toolchain-probe coverage, and boot smoke tests.
 A local static signal for this file is that it has 823 lines and 24225 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
