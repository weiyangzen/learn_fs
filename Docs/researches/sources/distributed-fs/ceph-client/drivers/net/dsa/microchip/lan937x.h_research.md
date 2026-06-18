# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x.h

## Purpose
`lan937x.h` declares the LAN937x chip-specific operations consumed by the common KSZ driver. These functions implement LAN937x reset, setup, port configuration, side MDIO, PHY access, MTU, phylink capability, RGMII delay, ageing, and CBS credit increment behavior.

## Important APIs, Types, and Functions
The header declares `lan937x_reset_switch()`, `lan937x_setup()`, `lan937x_teardown()`, `lan937x_port_setup()`, `lan937x_config_cpu_port()`, `lan937x_switch_init()`, `lan937x_switch_exit()`, `lan937x_mdio_bus_preinit()`, `lan937x_create_phy_addr_map()`, `lan937x_r_phy()`, `lan937x_w_phy()`, `lan937x_change_mtu()`, `lan937x_phylink_get_caps()`, `lan937x_setup_rgmii_delay()`, `lan937x_set_ageing_time()`, and `lan937x_tc_cbs_set_cinc()`.

## Control Flow
There is no local control flow. `ksz_common.c` assigns these functions into `lan937x_dev_ops`, and then common DSA setup invokes them through `struct ksz_dev_ops` at lifecycle and feature-specific points.

## State and Persistence
The header defines no state. LAN937x runtime state is held in `struct ksz_device`, per-port structures, and LAN937x hardware registers managed by the implementation file outside this subset.

## Dependencies and Integration Points
This header is included by `ksz_common.c`. Its prototypes depend on `struct ksz_device`, `struct dsa_switch`, and `struct phylink_config` declarations supplied by the including context and KSZ common headers.

## Risks and Edge Cases
Prototype drift between this header, the LAN937x implementation, and `lan937x_dev_ops` will break builds or feature dispatch. Side MDIO functions are only meaningful for chip data with `phy_side_mdio_supported`; mismatched capability wiring would fail MDIO setup in common code.

## Test Signals
Compile LAN937x-enabled builds and probe LAN9370/1/2/3/4 devices. Runtime signals include successful side-MDIO preinit and PHY address mapping, correct CPU port setup, LAN937x-specific phylink capabilities and RGMII delays, MTU changes, ageing timer programming, and CBS offload through `lan937x_tc_cbs_set_cinc()`.
