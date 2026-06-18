<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/85xx_entry_mapping.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/85xx_entry_mapping.S

Purpose: Low-level BookE/85xx assembly routine for replacing firmware/boot TLB state with controlled kernel or kexec entry mappings.

Important APIs/types/functions: Assembler flow guarded by `ENTRY_MAPPING_BOOT_SETUP` or `ENTRY_MAPPING_KEXEC_SETUP`; uses MAS0-MAS7, PID0-2, MAS6, TLB search/write/invalidate instructions, temporary TLB1 mapping, and final `rfi` transfers.

Control flow: The code finds the TLB entry currently executing, protects it, invalidates other entries, creates a temporary mapping in the alternate address space, switches via SRR0/SRR1, clears PIDs/search state, invalidates the original mapping, installs either a 64MiB kernel virtual mapping or eight 256MiB identity mappings for kexec, jumps into the final mapping, and clears the temporary entry.

State and persistence: Mutates processor TLBs, PID registers, MAS registers, and MSR address-space bits. The changes persist as the initial translation environment for subsequent kernel execution.

Dependencies and integration points: Depends on BookE MMU SPR definitions, `TLBSYNC`, `MSR_KERNEL`, `KERNELBASE`, and caller-provided registers such as `r20`/current address context. Included by 85xx head/kexec setup paths.

Risks: This runs with fragile early boot constraints. A wrong ESEL, PID, TSIZE, or address-space bit can strand execution without translation. Kexec identity mapping only covers the first 2GiB.

Test signals: PPC_85xx boot tests, kexec/kdump on e500/85xx, early TLB dump inspection, and build coverage for both boot and kexec setup macros.

Source read size: 230 lines, 5509 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/85xx_entry_mapping.S -->
