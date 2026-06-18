# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Kconfig

Purpose: Kconfig menu for Xilinx Ethernet drivers.

Important options: `NET_VENDOR_XILINX` gates the vendor menu. `XILINX_EMACLITE` enables 10/100 Ethernet Lite and selects PHYLIB. `XILINX_AXI_EMAC` enables AXI Ethernet, depends on `HAS_IOMEM` and `XILINX_DMA`, and selects PHYLINK and DIMLIB. `XILINX_LL_TEMAC` enables the LocalLink TEMAC driver and selects PHYLIB.

Integration: the Makefile uses these symbols to build `xilinx_emaclite.o`, `xilinx_emac.o`, and `ll_temac.o`. Dependency selection determines whether PHYLIB, PHYLINK, and DIM support are available to the corresponding sources.

State and persistence: no runtime state; selected options affect compiled objects and helper subsystem availability.

Risks and tests: the main risk is dependency drift with driver code, especially AXI EMAC's phylink/DIM requirements and LL TEMAC's PHYLIB path. Build matrix tests for each symbol as module and built-in are the key signal.
