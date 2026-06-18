# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_aml.h

## Purpose
`txgbe_aml.h` declares AML-family TXGBE GPIO, firmware host-interface, module, link, EEPROM, and phylink helper functions.

## Important APIs, Types, and Functions
It declares `txgbe_gpio_init_aml()`, `txgbe_gpio_irq_handler_aml()`, `txgbe_test_hostif()`, `txgbe_read_eeprom_hostif()`, `txgbe_set_phy_link()`, `txgbe_identify_module()`, `txgbe_setup_link()`, and `txgbe_phylink_init_aml()`.

## Control Flow
There is no executable flow. `txgbe_main.c`, `txgbe_irq.c`, and `txgbe_ethtool.c` call these APIs for AML probe, link service, GPIO IRQ handling, and module EEPROM access.

## State and Persistence Behavior
The header owns no state. Implementations mutate `struct wx`, `struct txgbe`, firmware, GPIO, MAC, and phylink state.

## Dependencies and Integration Points
It requires declarations for `struct wx`, `struct txgbe`, `struct txgbe_hic_i2c_read`, and `irqreturn_t` from included context. It links AML-specific code into the generic TXGBE driver.

## Risks and Edge Cases
Callers must gate AML-only routines by MAC type where appropriate; SP devices do not need GPIO/module firmware paths. Prototype drift affects multiple compilation units.

## Test Signals
Build TXGBE and exercise AML probe/open/link/ethtool EEPROM paths, plus SP devices where AML hooks should be skipped.
