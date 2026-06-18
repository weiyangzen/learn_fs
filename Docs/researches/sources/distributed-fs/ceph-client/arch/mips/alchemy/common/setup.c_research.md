# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/setup.c

## Purpose
`setup.c` provides Alchemy platform memory and I/O setup. It calibrates early delay loops, applies CPU erratum-related Config[OD] handling, sets default DMA coherency policy per CPU revision, calls board-specific setup, initializes global I/O resource ranges, and optionally fixes PCI big-physical address remapping.

## Important APIs, Types, And Functions
The architecture hook is `plat_mem_setup()`. `alchemy_dma_coherent()` returns the CPU/revision-specific default coherent DMA policy. Under `CONFIG_MIPS_FIXUP_BIGPHYS_ADDR`, exported `io_remap_pfn_range_pfn()` uses `fixup_bigphys_addr()` to translate 32-bit PCI memory window PFNs to the Au1500 PCI memory physical base.

## Control Flow
`plat_mem_setup()` calls `alchemy_set_lpj()`, sets or clears CP0 Config[OD] based on `au1xxx_cpu_needs_config_od()`, sets `dma_default_coherent` from `alchemy_dma_coherent()`, calls the board's `board_setup()`, and initializes `ioport_resource`/`iomem_resource` plus `set_io_port_base(0)`. The DMA coherency helper returns false for Au1000/Au1500/Au1100, false for Au1200 AB revision, and true for later/default variants.

The optional PCI fixup path leaves 36-bit physical addresses unchanged, maps addresses inside `ALCHEMY_PCI_MEMWIN_START..END` to `AU1500_PCI_MEM_PHYS_ADDR + phys_addr`, and otherwise returns the original address.

## State And Persistence
Persistent state includes CP0 Config[OD], global `dma_default_coherent`, board-level hardware state initialized by `board_setup()`, and global I/O resource ranges. The PCI PFN remap helper affects later mmap/remap behavior for PCI memory windows.

## Dependencies And Integration Points
It depends on CPU type/revision helpers, `alchemy_set_lpj()` from `clock.c`, board-provided `board_setup()`, DMA mapping globals, MIPS resource setup, CP0 register helpers, and PCI window constants. `MIPS_FIXUP_BIGPHYS_ADDR` is selected by top-level Kconfig for Alchemy PCI builds.

## Risks
Wrong DMA coherency policy causes data corruption, especially on Au1200 AB USB and older noncoherent cores. Config[OD] handling is tied to early SoC errata and performance; incorrect setting can either reintroduce errata or reduce bus performance. `board_setup()` runs before many drivers and must not depend on later platform devices. PCI address fixup assumes the configured PCI memory window constants and size are correct; otherwise userspace remaps can target wrong physical memory.

## Test Signals
Boot each CPU family and verify `dma_default_coherent` matches hardware expectations. Use DMA-heavy drivers on coherent and noncoherent variants, especially USB on Au1200 AB. Confirm board setup messages appear and I/O resource ranges match Alchemy constants. For PCI builds, mmap PCI BARs in the Alchemy PCI memory window and verify `io_remap_pfn_range_pfn()` maps to the expected physical base.
