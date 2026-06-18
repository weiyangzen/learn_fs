# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_8xx.S

## Purpose
Implements low-level startup, exception vectors, MPC8xx software TLB refill, early MMU/cache setup, optional pinned TLB mappings, and 8xx errata workarounds for 32-bit PowerPC 8xx embedded processors.

## Important APIs, Types, And Functions
Key labels are `_stext`, `_start`, `__start`, `start_here`, `initial_mmu`, `mmu_pin_tlb`, `FixupPGD`, and `FixupDAR`. The file defines optional perf counters `itlb_miss_counter`, `dtlb_miss_counter`, and `instruction_counter`. It uses 8xx MMU SPRs such as MI/MD_CTR, MI/MD_EPN, MI/MD_TWC, MI/MD_RPN, M_TWB, M_TW, DAR, DSISR, IMMR, IC_CST, DC_CST, and DER.

## Control Flow
Firmware enters `__start` with boot arguments; the code saves the device tree pointer, calls `initial_mmu`, enables IR/DR with `rfi`, and then runs normal initialization at `start_here`. The exception table handles reset, machine check, external IRQ, alignment, program, decrementer, syscall, single-step, software emulation, 8xx instruction/data TLB misses, TLB errors, breakpoints, and unknown traps. TLB miss handlers perform a software table walk via `M_TWB`, populate MI/MD TLB registers from Linux PTEs, optionally increment perf counters, then return directly with `rfi`. TLB error paths build `pt_regs` and call `do_page_fault`; special 8xx bug paths repair bad DAR values for cache-block instructions and can fill missing kernel PGD entries from `swapper_pg_dir`.

## State And Persistence
The file initializes early ITLB/DTLB entries, cache enable state, protection-mode SPRs, optional pinned text/data/IMMR TLB entries, `SPRG_THREAD`, the initial stack, `M_TWB`, Abatron debugger PTE pointers, and optional perf counters. These are CPU-local architectural state plus global counters; there is no durable persistence.

## Dependencies And Integration Points
Depends on `head_32.h`, 8xx PTE bit layout, `asm/code-patching-asm.h` patch sites, `machine_init`, `MMU_init`, `early_init`, `kasan_early_init`, `start_kernel`, `do_page_fault`, `do_IRQ`, `timer_interrupt`, `alignment_exception`, `program_check_exception`, `emulation_assist_interrupt`, and optional pinning symbols such as `VIRT_IMMR_BASE`. It integrates with perf events via patched miss counters and with vmapped-stack overflow handlers when configured.

## Risks And Edge Cases
The 8xx path is sensitive to exact MI/MD register programming, Linux-PTE-to-hardware-bit conversion, 512K/8M page encodings, cache mode setup, and the DAR fixup instruction decoder. Incorrect handling of the `RPN_PATTERN` DAR tag, `dcbi/dcbx/icbi` emulation, or missing PGD repair can turn recoverable TLB misses into silent bad mappings. Pinned TLB configurations reduce available TLB capacity and must match text/data/IMMR layout.

## Test Signals
Useful signals include MPC8xx boot with MMU enabled, page fault stress, instruction and data TLB miss counters under perf, cache-block instruction tests that trigger DAR fixup, pinned-TLB boot variants, device-tree IMMR access, external IRQ and decrementer delivery, and build coverage across `CONFIG_8xx`, `CONFIG_PIN_TLB_*`, `CONFIG_PERF_EVENTS`, and `CONFIG_VMAP_STACK`.
