# sources/distributed-fs/ceph-client/arch/xtensa/kernel/vectors.S

Purpose: Contains the primary Xtensa exception, interrupt, debug, double-exception, and register window vectors executed directly by the processor.

Important APIs, types, and functions: `_UserExceptionVector`, `_KernelExceptionVector`, `_DoubleExceptionVector`, `window_overflow_restore_a0_fixup`, `_DebugInterruptVector`, generated `_LevelNInterruptVector` entries, `_SimulateUserKernelVectorException`, and `_Window{Overflow,Underflow}{4,8,12}`.

Control flow: User/kernel vectors save minimal registers, choose the fast handler from the per-CPU exception table, and jump without literals. The double-exception vector distinguishes user/window exceptions, kernel TLB miss repair, registered fixups, and unrecoverable conditions. Medium interrupt vectors remap higher-level interrupts to level-1-style exception dispatch. Window overflow/underflow vectors spill/fill register windows at fixed 64-byte spacing.

State and persistence: Uses special registers `excsave1`, `depc`, `exccause`, `ps`, `epcN`, and window registers; reads/writes exception-table scratch fields such as KSTK, FIXUP, and DOUBLE_SAVE; writes user/kernel stack exception frames.

Dependencies and integration: Requires exact offsets from `asm-offsets.h`, table initialization from `traps.c`, linker placement from `vmlinux.lds.S`, page-fault fast paths, TLB refill handling, and Xtensa window ABI conventions.

Risks: Vector code cannot use literals in critical paths; size/alignment contracts are strict; double-exception fixup state is intentionally fragile; any mismatch with `struct exc_table` offsets or linker vector addresses causes early fatal faults.

Test signals: Boot with relocated and merged vectors, user/kernel faults, window overflow/underflow stress, double exceptions from user access and vmalloc TLB misses, debug interrupts, and high interrupt levels.
