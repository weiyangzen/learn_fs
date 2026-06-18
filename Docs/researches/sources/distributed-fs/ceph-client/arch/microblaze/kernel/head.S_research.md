# sources/distributed-fs/ceph-client/arch/microblaze/kernel/head.S

Purpose: defines the earliest MicroBlaze kernel entry path, initial FDT/command-line capture, temporary TLB setup, MMU enable, stack/current initialization, and transition to `start_kernel`.

Important symbols and state: `swapper_pg_dir` reserves one page. `_start`/`real_start` are head entry symbols. `_fdt_start`, `cmd_line`, `tlb_skip`, and `kernel_tlb` are prepared for later C setup.

Control flow: boot disables MSR and stack-limit state, detects MSR instruction support, validates and copies an incoming FDT, optionally copies command line, invalidates all TLBs, creates initial kernel and LMB TLB mappings, enables virtual mode, sets SDA anchors, stack and current register, calls `machine_early_init()` and `mmu_init()`, then drops temporary mappings and jumps to `start_kernel` with MMU enabled.

State and persistence: mutates TLB entries, PID, MSR, boot command line, FDT staging area, `tlb_skip`, stack pointer, and current-task register.

Dependencies and integration: linker script must place head text, FDT space, and symbols correctly. `machine_early_init()` later copies exception vectors and clears BSS; `mmu_init()` replaces temporary mappings with page tables.

Risks and test signals: FDT copy assumes 64 KiB staging, TLB size selection is hand-coded, and wrong load/virtual offsets prevent boot. Test boot with linked and external DTB, cmdline pointer, MSR-instruction mismatch logs, small/large kernels, and MMU transition.
