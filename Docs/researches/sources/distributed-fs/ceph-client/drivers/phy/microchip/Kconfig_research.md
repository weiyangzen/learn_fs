# sources/distributed-fs/ceph-client/drivers/phy/microchip/Kconfig

Purpose: Defines build-time configuration entries for the Microchip PHY drivers in this directory: Sparx5/LAN969x SerDes and LAN966x SerDes muxing.

Important APIs, types, and flow: `PHY_SPARX5_SERDES` is a tristate that selects `GENERIC_PHY`, depends on `ARCH_SPARX5 || ARCH_LAN969X || COMPILE_TEST`, `OF`, and `HAS_IOMEM`, and describes 10G/25G SerDes support for Microchip Sparx5. `PHY_LAN966X_SERDES` is a tristate that selects `GENERIC_PHY`, depends on `SOC_LAN966 || MCHP_LAN966X_PCI || COMPILE_TEST`, `OF`, and `MFD_SYSCON`, and describes LAN966X SerDes muxing support.

State, dependencies, and integration points: These symbols gate compilation through the local Makefile and determine whether platform devices matching the compatible strings can bind. The dependencies ensure DT probing and MMIO are available; LAN966x additionally requires syscon because the driver uses shared HSIO/config registers.

Risks and test signals: Build coverage should include built-in, module, and disabled variants, plus `COMPILE_TEST` on non-Microchip architectures. Dependency drift is the main risk: if driver code grows new APIs such as clocks or resets, Kconfig must gain matching dependencies.
