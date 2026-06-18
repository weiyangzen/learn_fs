# sources/distributed-fs/ceph-client/arch/sparc/mm/init_64.h

Purpose: shared declarations for SPARC64 memory initialization state used by C and assembly, especially TLB miss handling and PROM mapping code.

Important APIs/types/functions: defines `MAX_PHYS_ADDRESS`, declares `kern_linear_pte_xor`, locked/unlocked TLB/context globals, `mmu_info`, `prom_world`, `kern_locked_tte_data`, and `struct linux_prom_translation { virt, size, data }`. Exposes `prom_trans[512]` and `prom_trans_ents` for kernel TLB miss handling in `ktlb.S`.

Control flow: header only; no runtime control flow.

State and persistence: declares persistent globals owned by `init_64.c` and consumed by assembly/runtime MMU code.

Dependencies/integration: includes `asm/page.h`; comments identify assembler consumers and SMP boot usage. It is the ABI contract between `init_64.c`, trap/TLB miss assembly, and PROM world transitions.

Risks: changing structure layout or symbol names breaks assembly consumers. `MAX_PHYS_ADDRESS` depends on `MAX_PHYS_ADDRESS_BITS` being correctly set by architecture headers.

Test signals: SPARC64 build and link, objdump/symbol checks for assembly references, boot through TLB miss handling and PROM callbacks.
