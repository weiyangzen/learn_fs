# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_64.S

## Purpose

`head_64.S` is the common 64-bit PowerPC kernel entry file. It contains the first 256 bytes of real-mode entry and secondary hold code, includes Book3S exception vectors or opens Book3E text, includes common interrupt return code, handles Book3E thread start/stop helpers, initializes secondary CPUs, manages Open Firmware and kexec/OPAL entry paths, relocates or copies the kernel, turns on 64-bit mode and relocation, clears BSS, calls early setup, and finally enters `start_kernel`.

## Important APIs, entry points, and labels

Primary global entry is `__start`. Fixed low-memory secondary coordination labels are `__secondary_hold_spinloop`, `__secondary_hold_acknowledge`, optional `__run_at_load`, and `__secondary_hold`. Book3E helpers include `book3e_start_thread`, `book3e_stop_thread`, `fsl_secondary_thread_init`, and use of `book3e_secondary_core_init` and `book3e_secondary_thread_init` from the Book3E exception file. SMP entries include `generic_secondary_smp_init`, `pmac_secondary_start`, `__secondary_start`, and `start_secondary_resume`. Other important routines are `copy_and_flush`, `enable_64b_mode`, `relative_toc`, and local Book3S helpers `__mmu_off` and `start_initialization_book3s`.

## Control flow

Execution begins at `__start`, fixes endian state, and branches to `__start_initialization_multiplatform`. Secondary CPUs can enter the low-address `__secondary_hold` loop, write their hardware CPU id to the acknowledge slot, and wait for a real address in `__secondary_hold_spinloop`. The common initialization path enables 64-bit mode, poisons PACA/TOC until initialized, distinguishes Open Firmware entry from kexec-style entry by `r5`, saves boot parameters, computes a runtime TOC, runs Book3E or Book3S early initialization, and derives the current runtime base.

For Open Firmware trampoline builds, `__boot_from_prom` runs at physical address, optionally relocates to the current address, calls `prom_init`, and does not return. After prom or kexec entry, `__after_prom_start` processes relocatable mode, optionally runs `relocate`, updates Book3E IVPR after relocation, copies the kernel from runtime base to `PAGE_OFFSET` or only copies interrupt regions for run-at-load cases, flushes dcache and icache through `copy_and_flush`, and branches to `start_here_multiplatform`.

At `start_here_multiplatform`, the file recomputes TOC, clears BSS, records OPAL debug entry when enabled, sets RI on Book3S, records `kernstart_addr` for relocatable kernels, builds the initial stack, optionally runs KASAN early init, calls C `early_setup`, then uses SRR0/SRR1 and RFI to enter `start_here_common` with relocation enabled. `start_here_common` stores the kernel stack in PACA, loads TOC, marks interrupts soft and hard disabled, and calls `start_kernel`.

Secondary CPU flow maps physical IDs to PACA entries, uses emergency stacks until normal stacks are safe, optionally restores CPU state, waits on `PACAPROCSTART`, calls `early_setup_secondary`, enables relocation, and enters `start_secondary`.

## State and persistence behavior

The file owns fixed low-memory state used by bootloaders and secondary CPUs: spinloop target, acknowledge word, and `__run_at_load`. It initializes PACA (`SPRG_PACA`, `r13`), `PACAKSAVE`, IRQ soft-mask fields, `kernstart_addr`, optional OPAL entry storage, and Book3E `booting_thread_hwid`. It also manipulates MSR, SRR0/SRR1, HID4 on PowerMac, PIR/TIR/TENS/TENC on Book3E threaded cores, and cache state during copying.

## Dependencies and integration points

`head_64.S` includes `exceptions-64s.S` for Book3S and `interrupt_64.S` for common interrupt return code. It calls C functions `prom_init`, `early_setup`, `early_setup_secondary`, `start_kernel`, and `start_secondary`, plus platform CPU restore callbacks through `cur_cpu_spec`. It integrates with relocatable kernel support, kexec, OPAL, Open Firmware, pseries secondary startup, PowerMac secondary startup, Book3E initialization, KASAN, and PACA allocation.

## Risks and invariants

This code executes before normal C runtime exists. TOC, PACA, stack, endian mode, relocation state, and cache coherency must be handled in the right order. The first 256-byte section has fixed offsets known to external tools and boot protocols. Secondary hold code must fit below the first exception vector. Kernel copying must avoid executing stale icache lines. Relocatable `__run_at_load` behavior is known to kexec tools and must not move unexpectedly. Branches before relocation must remain position-safe.

## Test signals

Signals include successful pseries, powernv/OPAL, kexec, Open Firmware trampoline, relocatable and run-at-load boots; SMP secondary bring-up and hotplug; PowerMac secondary starts; Book3E threaded core selection; KASAN early boot; correct `kernstart_addr`; and absence of early traps before `start_kernel`. Build coverage should include Book3S, Book3E, SMP, kexec, relocatable, PPC_OF_BOOT_TRAMPOLINE, OPAL early debug, and PowerMac options.
