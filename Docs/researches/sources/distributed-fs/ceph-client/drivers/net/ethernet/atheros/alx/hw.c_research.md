# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.c

## Purpose
Implements low-level ALX hardware access for PCIe, MAC, PHY/MDIO, ASPM, speed/duplex setup, flow control, RSS disable, basic MAC/DMA configuration, MSI-X masking, PHY identification, and MIB statistics accumulation.

## Important APIs, Types, and Functions
MDIO helpers include `alx_read_phy_reg()`, `alx_write_phy_reg()`, `alx_read_phy_ext()`, and `alx_write_phy_ext()`, all serialized by `hw->mdio_lock`. Reset/config functions include `alx_reset_pcie()`, `alx_reset_mac()`, `alx_reset_phy()`, `alx_configure_basic()`, `alx_start_mac()`, and `alx_enable_aspm()`. Link helpers include `alx_setup_speed_duplex()`, `alx_read_phy_link()`, `alx_post_phy_link()`, `alx_phy_configured()`, and `alx_clear_phy_intr()`. Address/stats helpers include `alx_get_perm_macaddr()`, `alx_set_macaddr()`, `alx_get_phy_info()`, and `alx_update_hw_stats()`.

## Control Flow and State
The hardware layer reads/writes MMIO registers through inline accessors in `hw.h`. PHY access chooses MDIO clock based on current link state and supports Clause 22 and extended MMD-like access. Probe/reset flows call PCIe reset first, decide whether PHY is already configured, optionally reset PHY, reset MAC, configure speed/duplex, load MAC address, and later configure queues/DMA via `alx_configure_basic()`. Hardware MIB counters are accumulated into `hw->stats` because reads clear the hardware counters.

## Dependencies and Integration Points
Depends on PCI config space, MMIO register definitions from `reg.h`, Linux MDIO constants, ethtool advertisement conversion, and helper fields in `struct alx_hw`. `main.c` calls these helpers under `alx->mtx` for lifecycle and link state.

## Risks and Test Signals
Risk areas include reset timing, ASPM programming, PHY workaround coverage for revisions, clear-on-read stats, and advertisement translation. `ethadv_to_hw_cfg()` appears to map advertised 1000 full to `ALX_DRV_PHY_100 | DUPLEX` rather than a 1000 field, which deserves verification against hardware definitions. Tests should cover MAC reset timeout, link transitions at 10/100/1000, wake/ASPM after suspend, MIB counter accumulation, and MDIO timeout/error paths.
