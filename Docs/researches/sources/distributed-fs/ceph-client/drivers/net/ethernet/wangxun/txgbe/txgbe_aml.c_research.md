# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.c

## Purpose
`txgbe_aml.c` handles AML-family TXGBE module GPIO interrupts, firmware host-interface PHY/module commands, module EEPROM reads, SFP/QSFP capability decoding, link setup, and phylink MAC callbacks for 10/25/40G AML devices.

## Important APIs, Types, and Functions
Exports are `txgbe_gpio_init_aml()`, `txgbe_gpio_irq_handler_aml()`, `txgbe_test_hostif()`, `txgbe_read_eeprom_hostif()`, `txgbe_set_phy_link()`, `txgbe_identify_module()`, `txgbe_setup_link()`, and `txgbe_phylink_init_aml()`. Internal helpers include host-interface command builders, `txgbe_sfp_to_linkmodes()`, `txgbe_qsfp_to_linkmodes()`, `txgbe_get_mac_link()`, `txgbe_reconfig_mac()`, and phylink callbacks.

## Control Flow
AML up calls `txgbe_setup_link()`, which clears link interface/support masks, sets `WX_FLAG_NEED_MODULE_RESET`, and schedules service work. The service task later calls `txgbe_identify_module()`, which checks module-present GPIO, asks firmware for module info, validates SFP/QSFP identifiers, converts module EEPROM fields into phylink supported/advertising/interface masks, and sets `WX_FLAG_NEED_LINK_CONFIG`. A later service pass calls `txgbe_set_phy_link()` to send selected speed/autoneg/duplex to firmware. GPIO IRQs mask GPIO interrupts, detect module reset pins, set module-reset work, acknowledge EOI, and unmask.

## State and Persistence Behavior
Runtime state lives in `struct txgbe`: `link_support`, `advertising`, `link_interfaces`, and `link_port`, plus `struct wx` flags, speed, phylink, GPIO, flow-control, MAC registers, and PTP cyclecounter state. Firmware link configuration persists in device firmware/hardware until changed or reset. Module EEPROM reads are transient.

## Dependencies and Integration Points
The file depends on `wx_host_interface_command()`, phylink fixed-link APIs, GPIO/MMIO registers from shared and TXGBE type headers, PTP reset helpers, SR-IOV VF link notifications, and TXGBE hardware helpers such as `txgbe_enable_sec_tx_path()`. Ettool module EEPROM operations call `txgbe_read_eeprom_hostif()`.

## Risks and Edge Cases
`txgbe_read_eeprom_hostif()` copies four bytes per rounded dword into `data`, which assumes the caller buffer can hold rounded length. Unsupported modules return errors and leave link config pending. AML fixed-link phylink is driven by hardware status rather than an external PHY, so stale port status can misreport link. `txgbe_phylink_init_aml()` should destroy phylink if `phylink_set_fixed_link()` fails.

## Test Signals
Test SFP and QSFP module insertion/removal GPIO IRQs, unsupported module IDs, passive/active DAC, SR/LR/ER/CR speeds, 10/25/40G link setup, firmware command failures, module EEPROM page reads, PTP reset on link change, and VF link notifications.
