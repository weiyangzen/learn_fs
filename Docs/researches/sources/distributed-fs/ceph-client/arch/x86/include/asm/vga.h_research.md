# sources/distributed-fs/ceph-client/arch/x86/include/asm/vga.h

Purpose: Defines x86 direct VGA framebuffer memory mapping and byte access helpers.

Important APIs/types/functions: `VGA_MAP_MEM(x, s)` converts a physical VGA address to a virtual address with `phys_to_virt()` and, when AMD memory encryption is enabled, calls `set_memory_decrypted()` for the region. `vga_readb(x)` and `vga_writeb(x, y)` are direct byte load/store macros.

Control flow: VGA users call `VGA_MAP_MEM()` before accessing framebuffer memory. The macro conditionally changes page encryption attributes, then returns the virtual start address.

State and persistence: It can mutate kernel page attributes for VGA memory by marking pages decrypted. The VGA memory contents persist in device memory, not in this header.

Dependencies and integration points: Includes `asm/set_memory.h`; relies on `phys_to_virt`, `PAGE_SHIFT`, and `CONFIG_AMD_MEM_ENCRYPT`. Used by generic VGA console/framebuffer code.

Risks: Page count is `(s) >> PAGE_SHIFT`, so non-page-rounded sizes need callers to be careful. Failing to decrypt on encrypted-memory systems breaks device access; decrypting the wrong range affects memory confidentiality/integrity.

Test signals: VGA console/framebuffer boot tests, SME/SEV encrypted-memory boots with VGA output, and build tests.
