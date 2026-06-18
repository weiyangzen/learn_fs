# sources/distributed-fs/ceph-client/arch/powerpc/kexec/Makefile

## Purpose
Selects PowerPC kexec, kexec-file, vmcore-info, and crash-dump objects for the kernel build and disables instrumentation on sensitive transition code.

## Important APIs, Types, And Functions
Uses Kbuild assignments for `core.o`, `core_$(BITS).o`, `ranges.o`, `relocate_32.o`, `file_load.o`, `file_load_$(BITS).o`, `elf_$(BITS).o`, `vmcore_info.o`, and `crash.o`. It disables GCOV, KCOV, UBSAN, and KASAN instrumentation for selected core objects.

## Control Flow
Kbuild evaluates `CONFIG_PPC32`, `CONFIG_KEXEC_FILE`, `CONFIG_VMCORE_INFO`, and `CONFIG_CRASH_DUMP` to include the correct objects for the selected architecture width and feature set.

## State And Persistence
No runtime state. It controls build artifacts and instrumentation flags.

## Dependencies And Integration Points
Integrates PowerPC architecture kexec code with generic kexec, crash dump, and vmcore infrastructure. Instrumentation disables are important because kexec transition code runs with unusual MMU/IRQ/stack constraints.

## Risks And Edge Cases
Omitting an object causes unresolved symbols or missing runtime support. Accidentally enabling sanitizers or coverage in transition code can break no-allocation/no-instrumentation assumptions during kexec.

## Test Signals
Build matrices for 32-bit, 64-bit, `CONFIG_KEXEC_FILE`, `CONFIG_CRASH_DUMP`, and sanitizer configs verify object selection and instrumentation exclusions.
