# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Makefile

## Purpose
The Makefile builds the Altera Triple-Speed Ethernet driver and combines its component objects.

## Important build rules
- `obj-$(CONFIG_ALTERA_TSE) += altera_tse.o` selects the module/built-in target.
- `altera_tse-objs := altera_tse_main.o altera_tse_ethtool.o altera_msgdma.o altera_sgdma.o altera_utils.o` links the main driver, ethtool support, both DMA engines, and common utilities into one object.

## Control flow and integration
kbuild evaluates `CONFIG_ALTERA_TSE` and links all listed objects into `altera_tse`. Runtime DMA backend selection is handled by the full driver, not by separate build targets.

## State and persistence behavior
No runtime state exists. Build artifacts are the only effect.

## Dependencies and integration points
It depends on the Kconfig symbol and all listed source files. The DMA files researched here are integrated through this composite target.

## Risks and edge cases
Any source listed in `altera_tse-objs` must compile for every enabled `ALTERA_TSE` build, even if a platform only uses one DMA backend. Object list drift can break runtime match data or unresolved symbols.

## Test signals
Build `ALTERA_TSE=y` and `m`, confirm `altera_msgdma.o` and `altera_sgdma.o` are included, and verify `ALTERA_TSE=n` omits the composite object.
