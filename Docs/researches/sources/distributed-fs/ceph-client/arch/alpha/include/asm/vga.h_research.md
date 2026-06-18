<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/vga.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/vga.h

**Purpose:** Provides VGA text-memory accessors and hose-aware address fixups for Alpha systems whose VGA device is not on hose 0.

**Important APIs/types/functions:** `scr_writew`, `scr_readw`, `scr_memsetw`, `scr_memcpyw`, `scr_memmovew`, `vga_readb`, `vga_writeb`, `pci_vga_hose`, VGA port/memory classifiers, `FIXUP_IOADDR_VGA`, `FIXUP_MEMADDR_VGA`, and `VGA_MAP_MEM`.

**Control flow:** Console code uses direct memory operations for RAM-like addresses and raw I/O operations for I/O addresses. When `CONFIG_VGA_HOSE` is enabled, legacy VGA port/memory addresses are rebased through `pci_vga_hose` resources.

**State and persistence behavior:** The selected VGA hose is global runtime state declared here and set by console/core logic.

**Dependencies and integration points:** Depends on Alpha I/O helpers, PCI controller resources, console code, and string `memset16`.

**Risks:** Incorrect hose selection sends VGA reads/writes to the wrong PCI window. `scr_memsetw` assumes count in bytes and converts to 16-bit count for memory.

**Test signals:** Boot VGA console on multi-hose systems, switch consoles, load fonts, and test `CONFIG_VGA_HOSE` selection from firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/vga.h -->
