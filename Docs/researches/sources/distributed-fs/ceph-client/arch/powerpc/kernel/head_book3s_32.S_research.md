# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_book3s_32.S

## Purpose
Provides 32-bit Book3S kernel entry, Open Firmware and BootX handoff, early BAT/hash/MMU setup, exception vectors, 603/604 TLB/hash refill paths, SMP secondary startup, and BAT update helpers for non-8xx classic PowerPC systems.

## Important APIs, Types, And Functions
Key labels include `_stext`, `_start`, `__start`, `__secondary_hold`, `__secondary_start`, `copy_and_flush`, `load_segment_registers`, `update_bats`, and local helpers `early_hash_table`, `load_up_mmu`, `clear_bats`, `flush_tlbs`, `mmu_off`, `initial_bats`, `setup_disp_bat`, `setup_cpm_bat`, and `setup_usbgecko_bat`. Exception labels include `MachineCheck`, `DataAccess`, `InstructionAccess`, `InstructionTLBMiss`, `DataLoadTLBMiss`, `DataStoreTLBMiss`, `AltiVecUnavailable`, and `PerformanceMonitor`.

## Control Flow
The boot path handles Open Firmware trampolines, BootX, and direct firmware entry, then calls `early_init`, turns the MMU off, clears BATs and TLBs, installs initial BAT mappings and segment registers, creates an early hash table, initializes CPU and 6xx idle state, optionally relocates the kernel to `PHYSICAL_START`, then enables the MMU and enters `start_here`. Later, `start_here` installs thread and stack state, calls platform/MMU init, reloads final SDR1/BAT state with MMU off, and jumps to `start_kernel`. Exception vectors dispatch to C handlers or fast 603/604 TLB/hash refill code that constructs hardware PTEs and falls back to storage exceptions when access checks fail.

## State And Persistence
Persistent CPU state includes BAT registers, segment registers, SDR1, TLB entries, SPRG thread pointer, secondary hold globals, Abatron PTE pointers, and optional early debug BAT mappings. SMP paths install per-CPU stacks and thread state before `start_secondary`. State is architectural and boot-time only; no storage persistence exists.

## Dependencies And Integration Points
Depends on `head_32.h`, classic Book3S BAT/segment/hash MMU details, `early_init`, `prom_init`, `bootx_init`, `machine_init`, `MMU_init`, `MMU_init_hw_patch`, `__save_cpu_setup`, `__restore_cpu_setup`, `call_setup_cpu`, `init_idle_6xx`, `start_kernel`, `start_secondary`, `hash_page`, and KVM Book3S real-mode handlers when configured. It feeds page fault, IRQ, decrementer, FPU, Altivec, perf, and debug exception infrastructure.

## Risks And Edge Cases
Risk is concentrated in early real-mode relocation, BAT validity ordering, firmware-provided mappings, CHRP RTAS machine-check stack handling, 603 software LRU TLB refill, 604 hash fault shortcuts, little-endian DAR adjustment, and SMP secondary entry assumptions. Bad segment/BAT programming can make early exceptions unrecoverable. Open Firmware and BootX entry paths have unusual register contracts that are difficult to test in generic CI.

## Test Signals
Signals include boot on PowerMac/PReP/CHRP/QEMU ppc32, Open Firmware and BootX handoff coverage, SMP secondary startup, relocation to `PHYSICAL_START`, 603/604 page fault and TLB miss stress, hash table operation, BAT update tests, Altivec/FPU unavailable traps, and cross-builds for `CONFIG_PPC_BOOK3S_604`, `CONFIG_SMP`, `CONFIG_PPC_OF_BOOT_TRAMPOLINE`, early debug BAT options, and KVM Book3S handlers.
