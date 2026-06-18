<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux.lds.S

Purpose: Main linker script for RISC-V `vmlinux`.

Important APIs/types/functions: Defines kernel text/rodata/data/bss/init layout, PE/EFI and alternative sections, exception tables, percpu areas, BPF/extable metadata, and architecture-specific symbols.

Control flow: Build-time only; controls final kernel image layout consumed by boot and runtime code.

State and persistence: Establishes symbol boundaries used by setup, memory protection, alternatives, module loading, unwinding, and init cleanup.

Dependencies and integration points: Coupled to boot head code, `setup.c` resource reporting, alternatives, vDSO/linker symbols, exception handling, KASAN/KCSAN/CFI sections, and generic vmlinux linker macros.

Risks: Misplaced sections can break boot, permissions, exception fixups, alternatives, or memory freeing. Alignment changes can affect huge-page mappings and KASLR.

Test signals: Full kernel link, boot, section permission checks, exception table fixups, initmem free, kallsyms, and linker map review.

Source read size: 174 lines, 3170 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux.lds.S -->
