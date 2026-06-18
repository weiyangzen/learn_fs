## sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/Makefile

Purpose: Kbuild fragment for the DesignWare AXI DMAC platform driver.

Important APIs/types/functions: no C APIs are declared here. The only build rule maps `CONFIG_DW_AXI_DMAC` to `dw-axi-dmac-platform.o`.

Control flow: when the Kconfig symbol is enabled, this object is linked into the kernel or module according to the symbol mode.

State and persistence: no runtime state.

Dependencies and integration: depends on the parent DMA Kbuild and the `CONFIG_DW_AXI_DMAC` symbol defined elsewhere. It integrates the platform implementation with the DMA driver build.

Risks and test signals: build regressions show up as missing object linkage when `CONFIG_DW_AXI_DMAC=y/m`. A minimal test signal is a kernel build with the symbol enabled and module autoload/probe for compatible device-tree nodes.
