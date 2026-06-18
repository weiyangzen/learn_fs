## sources/distributed-fs/ceph-client/drivers/dma/dw/Makefile

Purpose: Kbuild rules for the classic DesignWare AHB DMA core, variant implementations, platform/PCI glue, optional ACPI/OF helpers, and RZ/N1 DMAMUX.

Important APIs/types/functions: builds `dw_dmac_core.o` from `core.o`, `dw.o`, and `idma32.o`, optionally adding `acpi.o`. Builds platform module from `platform.o` plus `of.o` under `CONFIG_OF`, and PCI module from `pci.o`.

Control flow: object composition wires shared core logic with register-variant operations and bus glue based on configuration.

State and persistence: no runtime state.

Dependencies and integration: matches the source architecture: bus glue calls variant probe functions, which install operation callbacks and delegate to `do_dma_probe()`.

Risks and test signals: build regressions show as unresolved variant/core symbols. Test with ACPI and OF toggled independently and with platform and PCI symbols as modules or built-in.
