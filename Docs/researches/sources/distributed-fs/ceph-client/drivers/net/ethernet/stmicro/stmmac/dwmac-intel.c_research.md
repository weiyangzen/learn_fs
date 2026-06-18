# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c

## Purpose
`dwmac-intel.c` is the Intel PCI DWMAC glue driver for Quark, Elkhart Lake, Tiger Lake, Alder Lake, Raptor Lake, and PSE variants. It creates STMMAC platform data for PCI devices, handles SerDes power sequencing over an Intel MDIO ad-hoc address, configures PTP clock frequency and cross timestamping, programs PMC/FIA/ModPHY registers for TSN lanes, maps DMI board data to PHY addresses for Quark, configures MSI/MSI-X vectors, and invokes the shared STMMAC PCI/core probe.

## Important APIs, Types, And Functions
- `struct intel_priv_data` stores MDIO ad-hoc address, cross timestamp adjustment, PSE flag, TSN lane register list, and ModPHY register tables for 1G/2.5G.
- `struct stmmac_pci_info` wraps per-device setup callbacks referenced from the PCI ID table.
- `stmmac_pci_find_phy_addr()` maps PCI function numbers to PHY addresses through DMI tables for Quark/Galileo/IOT2000.
- `serdes_status_poll()`, `intel_serdes_powerup()`, and `intel_serdes_powerdown()` sequence SerDes PLL, reset, power state, rate, PCLK, and PSE RX clock gate bits over MDIO.
- `tgl_get_interfaces()` reads SerDes link mode and exposes SGMII or 2500BASE-X to phylink.
- `intel_mgbe_ptp_clk_freq_config()` programs GMAC GPIO bits to choose 200 MHz PTP clock mapping for PSE and PCH variants.
- `intel_crosststamp()` triggers internal auxiliary timestamp snapshots, reads PTP and ART values, and reports cross timestamps using `CSID_X86_ART`.
- `intel_tsn_lane_is_available()`, `intel_set_reg_access()`, and `intel_mac_finish()` interact with Intel PMC IPC to verify TSN lane availability and program 1G/2.5G ModPHY registers before SerDes re-power.
- `intel_mgbe_common_data()` fills queue counts, DMA/AXI settings, TSO/SPH flags, FIFO sizes, PTP, PCS/XPCS, VLAN fail queue, cross timestamping, and MSI vector offsets.
- Per-platform setup functions (`ehl_*`, `tgl_*`, `adls_*`, `adln_*`, `quark_default_data()`) specialize bus IDs, PHY interface, clock rates, queue counts, SerDes callbacks, safety features, host DMA width, and ModPHY tables.
- `stmmac_config_multi_msi()` and `stmmac_config_single_msi()` allocate PCI IRQ vectors and fill STMMAC resource IRQ fields.
- `intel_eth_pci_probe()` allocates platform data, enables PCI, maps BAR0, runs per-ID setup, configures MSI, and calls `stmmac_dvr_probe()`.

## Control Flow
PCI probe allocates Intel/private/STMMAC platform structures, enables the PCI device, maps BAR0, initializes default invalid MSI vector indices, runs the setup callback from the PCI ID table, builds `stmmac_resources`, tries multi-MSI then single IRQ fallback, and probes STMMAC. Remove calls `stmmac_dvr_remove()` and unregisters the fixed-rate STMMAC clock created by common data.

For mGbE variants, setup fills queue/traffic scheduling defaults, DMA burst/AXI settings, fixed-rate STMMAC clock, PTP controls, PCS selection for SGMII/1000BASE-X, MDIO masks to skip ad-hoc and XPCS addresses, cross timestamping support, VLAN fail queue, and MSI vector layout. SerDes power-up occurs through STMMAC callbacks, selecting 1G or 2.5G rate and polling for PLL/reset/power-state transitions. `mac_finish` can program PMC ModPHY tables and repower SerDes for requested interface.

Quark setup is simpler: it fills common GMAC defaults, determines PHY address by DMI/function mapping or fallback, sets RMII, and configures DMA burst settings.

## State And Persistence
State persists in `intel_priv_data`, STMMAC platform data, fixed-rate clock registration, PCI device power state, SerDes MDIO registers, PMC-programmed ModPHY registers, and GMAC GPIO/PTP control registers. Cross timestamp state temporarily sets STMMAC internal snapshot flags and uses aux timestamp locks/FIFO state.

## Dependencies And Integration Points
Depends on PCI, DMI, Intel PMC IPC, x86 ART CPUID support, STMMAC core/PTP helpers, XPCS/phylink PCS, MDIO bus operations, clock provider APIs, and PCI MSI/MSI-X. The PCI ID table maps many Intel device IDs to setup structures.

## Risks
- `intel_tsn_lane_is_available()` loops `j <= max_tsn_lane_regs`, which appears to read one element past the array length when `max_tsn_lane_regs` is set to `ARRAY_SIZE(...)`; this deserves review.
- SerDes status polling uses only ten short retries, so slow hardware transitions may fail power sequencing.
- Cross timestamping conflicts with external snapshot mode and relies on interrupt/FIFO behavior; failure paths must clear internal snapshot flags.
- Multi-MSI vector offsets are platform-data dependent; invalid queue counts or vector bases can map wrong IRQs.
- Fixed-rate clock registration must be unwound on all probe/remove failure paths to avoid leaks.
- PMC IPC register programming is platform-specific and can fail when firmware denies access or TSN lanes are unavailable.

## Test Signals
Test PCI probe/remove on each ID class, DMI PHY mapping for Galileo/IOT2000, multi-MSI and single-MSI fallback, SGMII/2500BASE-X SerDes power cycles, link mode switching through `mac_finish`, PTP clock frequency selection, cross timestamp reads, suspend/resume PCI D-state transitions, WOL where enabled, queue traffic across RX/TX queues, and safety/error interrupt paths. Static analysis should inspect the TSN lane loop bound.
