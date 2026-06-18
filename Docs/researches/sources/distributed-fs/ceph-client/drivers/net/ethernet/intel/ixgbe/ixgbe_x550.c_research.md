# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.c

## Purpose
`ixgbe_x550.c` is the hardware-specific operations layer for Intel ixgbe X550, X550EM_x, and x550em_a controllers. It plugs X550-specific MAC, PHY, EEPROM, I2C/link, firmware-host-interface, flow-control, SFP, reset, low-power, and malicious-driver-detection behavior into the generic ixgbe core through `struct ixgbe_info` tables at the end of the file.

## Important APIs, types, and functions
- Exported device descriptors: `ixgbe_X550_info`, `ixgbe_X550EM_x_info`, `ixgbe_x550em_x_fw_info`, `ixgbe_x550em_a_info`, and `ixgbe_x550em_a_fw_info` bind MAC type, invariant setup, operation tables, mailbox ops, and model values.
- Exported helpers: `ixgbe_set_fw_drv_ver_x550()`, `ixgbe_set_source_address_pruning_x550()`, `ixgbe_set_ethertype_anti_spoofing_x550()`, `ixgbe_enable_mdd_x550()`, `ixgbe_disable_mdd_x550()`, `ixgbe_restore_mdd_vf_x550()`, and `ixgbe_handle_mdd_x550()`.
- Operation tables: `mac_ops_X550`, `mac_ops_X550EM_x`, `mac_ops_X550EM_x_fw`, `mac_ops_x550em_a`, `mac_ops_x550em_a_fw`, EEPROM ops, PHY ops, and `link_ops_x550em_x`.
- Firmware PHY path: `ixgbe_fw_phy_activity()`, `ixgbe_get_phy_id_fw()`, `ixgbe_identify_phy_fw()`, `ixgbe_setup_fw_link()`, `ixgbe_reset_phy_fw()`, and `ixgbe_check_overtemp_fw()`.
- EEPROM path: host-interface read/write/buffer/checksum/update helpers around `FW_READ_SHADOW_RAM_CMD`, `FW_WRITE_SHADOW_RAM_CMD`, and `FW_SHADOW_RAM_DUMP_CMD`.
- Link and PHY paths: CS4227/CS4223 SFP support, IOSF sideband accessors, KR/iXFI/SFI/SGMII setup, external Base-T LASI interrupt handling, LPLU entry, MDIO clock setup, and X550EM reset.

## Control flow and integration
Probe-time code in the generic driver selects one exported `ixgbe_info` and calls its invariant function. The generic code then uses the operation tables in this file as virtual methods. `ixgbe_reset_hw_X550em()` is the central reset flow for embedded variants: stop adapter, clear pending TX, set MDIO speed, initialize and identify PHY ops, optionally un-stall external Base-T PHY firmware, configure SFP modules, reset PHY, choose MAC reset type based on link state and `force_full_reset`, reacquire permanent MAC address, initialize receive address registers, and restore mux/MDIO details.

Link setup is media dependent. Fiber/SFP uses SFP identification plus CS4227/CS4223 line-side programming. Copper Base-T may set an internal KR/iXFI path to match the external PHY. Backplane uses KR/KX advertisement and restart. Firmware-controlled PHYs marshal setup and status through `ixgbe_fw_phy_activity()` rather than direct MDIO register access.

## State and persistence behavior
The file mutates persistent hardware-facing state in `struct ixgbe_hw`: PHY type, PHY ID/revision, advertised speeds, EEE capabilities, semaphore masks, link address, MAC operation pointers, EEPROM word size/type, control word cache, management interface selection, permanent MAC, flow-control state, and `mac.set_lben`. It also writes persistent NVM shadow RAM and can trigger flash updates through firmware. Hardware registers affected include RX enable, spoofing controls, source address pruning bitmaps, IOSF sideband control/data, MDIO/PHY registers, ESDP mux bits, MDD registers, and WQBR queue-block registers.

## Dependencies
The implementation depends on ixgbe common, X540, mailbox, PHY, type, and register definitions plus Linux kernel primitives for delays, bit operations, endianness conversion, and MMIO. Major external integration points are firmware host-interface commands, MDIO, I2C combined transactions, CS4227/CS4223 retimers, port expanders, PF/VF virtualization registers, and generic ixgbe reset/link/EEPROM helper functions.

## Risks
- Semaphore and token paths are correctness-critical. Missed release paths can deadlock PHY, EEPROM, or I2C access across ports.
- Several flows intentionally ignore or overwrite earlier `status` values after later writes; regression tests should watch for lost errors in setup/reset sequences.
- Firmware PHY setup depends on strict command layout and endian conversion. Bad size, checksum, or retry behavior can silently prevent link.
- SFP and CS4227 support is highly variant-specific; wrong lane or slice calculations can affect another port.
- MDD queue-to-VF mapping depends on MRQC mode and queue grouping constants.

## Test signals
Useful signals include successful probe across all exported X550 variants, EEPROM checksum validate/update, link up/down on SFP, KR, SGMII, Base-T and firmware PHY devices, reset under active link and no-link cases, LASI over-temperature/link-change interrupts, source pruning and anti-spoofing behavior under SR-IOV, MDD detection/restoration with VFs, and fault injection for host-interface, IOSF, MDIO, and semaphore failures.
