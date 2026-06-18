# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Makefile

Purpose: maps Xilinx Ethernet Kconfig symbols to objects.

Important build rules: `ll_temac-objs := ll_temac_main.o ll_temac_mdio.o` creates the LocalLink TEMAC composite object. `CONFIG_XILINX_LL_TEMAC` builds `ll_temac.o`, `CONFIG_XILINX_EMACLITE` builds `xilinx_emaclite.o`, and `CONFIG_XILINX_AXI_EMAC` builds `xilinx_emac.o` from `xilinx_axienet_main.o` and `xilinx_axienet_mdio.o`.

Integration: this file defines module composition and makes the MDIO support part of each composite driver where needed.

State and persistence: no runtime state.

Risks and tests: missing an object would produce unresolved references such as TEMAC MDIO setup/teardown or AXI MDIO helpers. Build tests should cover all three Xilinx drivers as modules and built-in.
