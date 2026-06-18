# sources/distributed-fs/ceph-client/arch/s390/kernel/early.c

## Purpose
Performs early s390 architecture initialization before the generic kernel start. It handles decompressor-consumed command-line parameters, early KASAN, storage keys, lowcore setup, hardware description, topology probing, SCLP detection, and early exception handling.

## Important APIs, Types, And Functions
`startup_init()` is the main entry from `head.S`. `__do_early_pgm_check()` handles early program checks. Other helpers include `kasan_early_init()`, `init_kernel_storage_key()`, `setup_arch_string()`, `setup_topology()`, `setup_lowcore_early()`, `save_vector_registers()`, `setup_low_address_protection()`, `setup_access_registers()`, `setup_boot_command_line()`, and `sort_amode31_extable()`.

## Control Flow
Early params already processed by the decompressor are registered as ignored. `startup_init()` initializes KASAN/time/storage keys, disables lockdep, sorts AMODE31 exception tables, sets early lowcore PSWs and return-LPSWE instructions, derives machine/hypervisor strings from STSI, copies the boot command line, saves vector registers for crash dump, probes topology, detects SCLP features, enables low-address protection, initializes access registers, and re-enables lockdep.

## State And Persistence
State includes `early_command_line`, `arch_hw_string`, lowcore early PSWs, topology maximum nesting, storage keys, and boot CPU vector save area for crash dump.

## Dependencies And Integration Points
Depends on STSI, SCLP, lowcore, control registers, boot data, extable sorting, KASAN, FPU/vector helpers, and `entry.h` early handler symbols.

## Risks And Edge Cases
This code runs before normal kernel services are fully available. Early exceptions must use early console and disabled wait. Instrumentation is disabled in the Makefile because tracing/sanitizers here can break boot.

## Test Signals
Signals include early boot on LPAR/z/VM/KVM, earlyprintk panic diagnostics, storage-key configurations, topology reporting, decompressor param handling, and crash dump vector-save validation.
