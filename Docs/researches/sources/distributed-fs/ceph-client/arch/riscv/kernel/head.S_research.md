# sources/distributed-fs/ceph-client/arch/riscv/kernel/head.S

Purpose: Contains the RISC-V kernel image header, primary boot entry, MMU relocation, secondary CPU entry, M-mode setup, and register sanitization.

Important APIs/types/functions: Defines `_start`, `_start_kernel`, `relocate_enable_mmu`, `secondary_start_sbi`, spinwait secondary path, `.Lsetup_trap_vector`, `.Lsecondary_park`, and M-mode `reset_regs`.

Control flow: Firmware enters `_start`, whose image header advertises load offset, size, flags, magic, and optional EFI PE header. `_start_kernel` masks interrupts, configures M-mode PMP or S-mode counters, clears BSS, records boot hart, sets initial stack/task, calls `setup_vm`, enables MMU with trampoline and final page tables, installs trap vector, enables user CFI firmware feature if available, initializes early sanitizer hooks, and tails into `start_kernel`. Secondary harts enter through SBI or spinwait, load boot stack/task, enable MMU, install trap vector, and call `smp_callin`.

State and persistence: Sets boot CPU hart ID, initial thread stack/task state, SATP, TVEC, PMP, counter enable CSRs, scratch CSR, shadow call stack state, and spinwait boot arrays.

Dependencies and integration points: Depends on linker image symbols, `efi-header.S`, page-table setup, `head.h` helper prototypes, SBI firmware, SMP, user CFI FWFT, SCS, KASAN, and RISC-V boot protocol.

Risks and test signals: Boot header ABI, SATP relocation, BSS clearing, hart lottery, and firmware feature locking are early-fatal if wrong. Test U-Boot/EFI/OpenSBI boot, M-mode and S-mode configs, no-MMU/MMU variants, SMP spinwait and SBI paths, KASLR page-table setup, and early trap park diagnostics.
