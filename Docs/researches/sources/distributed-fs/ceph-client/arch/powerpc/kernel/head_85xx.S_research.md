# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_85xx.S

## Purpose
Provides the 32-bit Freescale/NXP 85xx/e500 BookE kernel entry path, early MMU setup, exception vectors, fast TLB miss handlers, SMP secondary entry, SPE save/restore glue, and relocation helpers. It is the first architecture-specific code for these CPUs after firmware hands control to the kernel.

## Important APIs, Types, And Functions
Important exported labels include `_stext`, `_start`, `__early_start`, `__secondary_start`, `__secondary_hold_acknowledge`, `create_kaslr_tlb_entry`, `reloc_kernel_entry`, `switch_to_as1`, `restore_to_as0`, `abort`, and, with SPE, `load_up_spe` and `__giveup_spe`. It relies heavily on BookE SPRs such as IVPR/IVOR, MAS0-MAS7, SRR, CSRR, DBSR/DBCR0, DEAR, ESR, PIR, and SPRG thread/scratch registers. Local helpers include `get_phys_addr`, `finish_tlb_load`, and SPE kernel exception handling.

## Control Flow
Boot begins at `_start`, translates the device tree and kernel runtime addresses to physical addresses, optionally performs relocatable/KASLR setup, establishes an initial TLB1 mapping through `85xx_entry_mapping.S`, programs IVORs and IVPR, initializes DBCR/DBSR, detects secondary CPUs, sets up `init_task`, the initial stack, and `SPRG_THREAD`, then calls `early_init`, optional KASAN/relocation init, `machine_init`, and `MMU_init` before jumping to `start_kernel` via `rfi`. Exception vectors under `interrupt_base` use `head_booke.h` prolog macros for normal, critical, debug, machine-check, syscall, timer, doorbell, hypervisor, and SPE paths. Data and instruction TLB errors try a fast page-table walk via `FIND_PTE`; valid hits branch to `finish_tlb_load`, while permission or missing-PTE cases restore scratch state and fall back to the storage exception handlers.

## State And Persistence
The file establishes persistent per-CPU execution state in SPRs, TLB entries, thread save slots, `SPRG_THREAD`, MAS defaults, IVOR mappings, and secondary CPU rendezvous globals. It also writes debugger-visible `abatron_pteptrs`, relocation globals such as `kernstart_addr`, and per-CPU hugepage CAM allocation state through `next_tlbcam_idx`. No filesystem state is touched; persistence lasts until CPU reset or later architecture code rewrites the same registers.

## Dependencies And Integration Points
Depends on BookE exception macros from `head_booke.h`, `85xx_entry_mapping.S`, e500 MMU/TLB layout, Linux PTE bit definitions, KVM BookE hooks, CPU feature fixups, SPE support, and platform calls such as `early_init`, `machine_init`, `MMU_init`, `start_kernel`, `start_secondary`, `call_setup_cpu`, `loadcam_entry`, and `relocate_init`. It integrates with page fault handling (`do_page_fault`), IRQ/timer handlers, debug handlers, KASAN, dynamic memory start, KASLR, SMP bring-up, and optional embedded hypervisor facilities.

## Risks And Edge Cases
The high-risk areas are early address translation before normal mappings exist, preserving the executing TLB entry while invalidating firmware mappings, 64-bit physical address handling, hugepage CAM replacement, KUAP fault rejection, KVM interception in exception prologs, SPE state ownership, and second relocation when `PAGE_OFFSET` changes physical backing. Bad IVOR offsets or MAS bit construction can make the CPU unrecoverable before printk works. TLB miss fast paths must avoid clobbering scratch registers and must reject invalid permissions precisely.

## Test Signals
Useful signals are successful 85xx/e500 boot to `start_kernel`, SMP secondary startup, kexec/KASLR boot, page fault and TLB miss stress, hugetlb mappings, SPE user/kernel traps, BookE KVM entry/exit smoke tests, watchdog/decrementer/doorbell interrupt delivery, and cross-build coverage for E500, E500MC, 32/64-bit physical address, SPE, KASAN, SMP, and relocatable kernels.
