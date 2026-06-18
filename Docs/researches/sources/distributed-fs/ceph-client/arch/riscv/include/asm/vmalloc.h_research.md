<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vmalloc.h

Purpose: Declares RISC-V vmalloc huge mapping capabilities and ioremap maximum order.

Important APIs/types/functions: Defines `IOREMAP_MAX_ORDER`, `arch_vmap_pud_supported()`, and `arch_vmap_pmd_supported()`.

Control flow: vmap/ioremap code asks whether PUD/PMD huge mappings are supported for a protection; helpers reflect current page-table level enablement.

State and persistence: Reads global `pgtable_l4_enabled`/`pgtable_l5_enabled`; no private state.

Dependencies and integration points: Used by vmalloc, ioremap, module/BPF mappings, and page-table geometry.

Risks: Returning support for folded/unavailable levels can create invalid vmalloc mappings.

Test signals: vmalloc/ioremap huge mapping tests, Sv39/Sv48/Sv57 boots, and debug page-table checks.

Source read size: 25 lines, 574 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vmalloc.h -->
