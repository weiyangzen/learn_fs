# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_main.c

## Purpose

This file implements the Microchip LAN937x family-specific DSA switch operations that sit underneath the common KSZ driver framework. It handles variant PHY address maps, MDIO/VPHY access setup, switch reset, CPU and user port setup, MTU and ageing-time programming, RGMII delay tuning, phylink capability reporting, credit-based shaper register writes, and switch lifecycle hooks. The code is not a standalone bus driver; it is integrated through `ksz_common.h`, `ksz9477.h`, and `lan937x.h` and is invoked by the broader Microchip KSZ/LAN937x DSA driver.

## Important APIs, Types, And Functions

The variant address tables `lan9370_phy_addr`, `lan9371_phy_addr`, `lan9372_phy_addr`, `lan9373_phy_addr`, and `lan9374_phy_addr` map logical ports to internal PHY addresses, with `LAN937X_NO_PHY` marking RGMII/SGMII-style ports. `lan937x_create_phy_addr_map()` selects a table by `dev->info->chip_id` and optionally adds an offset derived from `REG_SW_CFG_STRAP_VAL` strap bits when side MDIO is used. `lan937x_mdio_bus_preinit()` clears `SW_PHY_REG_BLOCK` and selects SPI-indirect or side-MDIO access in `REG_VPHY_SPECIAL_CTRL__2`.

`lan937x_internal_phy_read()` and `lan937x_internal_phy_write()` implement indirect VPHY transactions through `REG_VPHY_IND_ADDR__2`, `REG_VPHY_IND_DATA__2`, and `REG_VPHY_IND_CTRL__2`, polling `VPHY_IND_BUSY`. Public wrappers `lan937x_r_phy()` and `lan937x_w_phy()` expose this to the common driver. `lan937x_reset_switch()` resets the switch, enables link auto ageing, masks global/port interrupts, acknowledges POR readiness, and reads the port interrupt status.

Port and switch setup are split across `lan937x_port_setup()`, `lan937x_config_cpu_port()`, `lan937x_setup()`, `lan937x_switch_init()`, `lan937x_teardown()`, and `lan937x_switch_exit()`. Runtime knobs include `lan937x_change_mtu()`, `lan937x_set_ageing_time()`, `lan937x_setup_rgmii_delay()`, `lan937x_phylink_get_caps()`, and `lan937x_tc_cbs_set_cinc()`.

## Control Flow

Initialization first builds a PHY address map and preinitializes the PHY access path according to whether side MDIO or SPI is used. Switch reset asserts `SW_RESET`, enables automatic ageing, then masks and acknowledges interrupts. Generic setup enables global VLAN filtering semantics (`ds->vlan_filtering_is_global`), half-duplex backoff behavior, MIB freeze, disables output clocks, and disables global VPHY support.

CPU port configuration iterates DSA CPU ports, records `dev->cpu_port`, enables tail tagging on the CPU port, enables queue splitting, backpressure, 802.1p priority, flow control on non-internal-PHY ports, and assigns port membership. User ports are then forced to disabled STP state. MTU changes compute frame length including VLAN header, FCS, and LAN937x tag for CPU ports, toggle jumbo mode at `FR_MIN_SIZE`, and write `PORT_MAX_FR_SIZE`.

The ageing timer path chooses seconds or microseconds mode depending on millisecond granularity, preserves a usable multiplier when possible, rejects values beyond hardware capacity, writes multiplier bits in `REG_SW_LUE_CTRL_0`, and splits the 20-bit period across `REG_SW_AGE_PERIOD__1` and `REG_SW_AGE_PERIOD__2`. RGMII delay setup only applies if per-port parsed RGMII delay flags are present and writes characterization values through DLL reset sequences.

## State And Persistence Behavior

Persistent driver state lives in `struct ksz_device` and its `dev->info`, `dev->ports`, `dev->phy_addr_map`, `dev->cpu_port`, and DSA switch pointers. Hardware state is persisted in switch registers until reset: global MAC/LUE settings, interrupt masks, VPHY access mode, per-port tail tags, member maps, MTU size, ageing timer, and RGMII tuning. There is no file-backed state. Several helper writes ignore return values in port setup and delay tuning, so later errors may only surface as bad link behavior rather than probe failure.

## Dependencies And Integration Points

The file depends on Linux regmap, DSA, phylink, bridge/VLAN definitions, and Microchip KSZ common helpers such as `ksz_read32()`, `ksz_rmw16()`, `ksz_pwrite16()`, `ksz9477_port_queue_split()`, `ksz_port_stp_state_set()`, and `dev->dev_ops->cfg_port_member()`. It consumes register definitions from `lan937x_reg.h` and variant helpers from `lan937x.h`. DSA integration is visible in CPU/user port iteration, `dsa_user_ports()`, `dsa_upstream_port()`, and CPU-port MTU tag accounting.

## Risks

The side-MDIO PHY address offset logic is strap-sensitive; incorrect straps or chip IDs can silently map ports to wrong PHYs. VPHY indirect reads return `0xffff` for non-internal PHYs but error codes for transaction failures, so callers must distinguish absent PHYs from bus errors. RGMII delay writes do not propagate errors. Ageing-time conversion is sensitive to millisecond-vs-second mode and integer rounding. `lan937x_teardown()` is empty, so cleanup relies on outer KSZ/DSA teardown and `lan937x_switch_exit()` reset behavior.

## Test Signals

Useful validation signals are successful probe for each LAN9370-LAN9374 chip ID, correct MDIO discovery in both SPI-indirect and side-MDIO modes, `ip link set mtu` behavior across the jumbo threshold and CPU-port tag overhead, bridge ageing-time programming including sub-second values and oversized rejection, RGMII TX/RX delay link stability, DSA tail-tag packet flow through CPU ports, and absence of unexpected global/port interrupt storms after reset.
