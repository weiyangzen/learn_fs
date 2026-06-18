# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/mac.h

## Purpose

`mac.h` declares the generic MAC helper surface implemented by `mac.c`. It lets family-specific modules install common bus, link, LED, receive-address, multicast, VLAN, PCIe, flow-control, counter, and adaptive-IFS routines into their `struct e1000_mac_operations` tables without re-declaring each function locally.

## Important APIs

The header groups declarations for LED handling (`e1000e_blink_led_generic`, `e1000e_setup_led_generic`, `e1000e_cleanup_led_generic`, `e1000e_led_on_generic`, `e1000e_led_off_generic`, `e1000e_id_led_init_generic`), link checks (`e1000e_check_for_copper_link`, `e1000e_check_for_fiber_link`, `e1000e_check_for_serdes_link`), flow control (`e1000e_setup_link_generic`, `e1000e_config_fc_after_link_up`, `e1000e_force_mac_fc`, `e1000e_set_fc_watermarks`), bus/semaphore helpers (`e1000e_get_bus_info_pcie`, `e1000e_get_hw_semaphore`, `e1000e_put_hw_semaphore`, `e1000e_get_auto_rd_done`, `e1000e_disable_pcie_master`, `e1000e_set_pcie_no_snoop`), and address/filter helpers (`e1000e_init_rx_addrs`, `e1000e_rar_set_generic`, `e1000e_rar_get_count_generic`, `e1000e_update_mc_addr_list_generic`, `e1000_clear_vfta_generic`, `e1000_write_vfta_generic`, `e1000_check_alt_mac_addr_generic`).

## Control Flow

The header contains no executable flow. Its declarations enable compile-time wiring from family files into runtime operation dispatch. For example, `ich8lan.c` uses generic multicast update, RAR setting for older variants, collision-distance configuration, PCIe master disable, and copper speed/duplex helpers while replacing LED and RAR behavior for PCH variants.

## State And Persistence Behavior

Declared functions mutate MAC registers and `struct e1000_hw` runtime state, and some read NVM-backed defaults. The header itself stores no state and defines no persistent layout. Its role in persistence is indirect: functions such as `e1000_check_alt_mac_addr_generic` and `e1000e_valid_led_default` read NVM words, and semaphore helpers guard NVM/PHY access.

## Dependencies And Integration Points

Consumers must include e1000e core type definitions first so `struct e1000_hw`, `s32`, `u16`, `u32`, and `u8` are known. The declarations are used by silicon-specific files and by generic driver code that calls through `hw->mac.ops`. Any signature change must be reflected in operation-table types in `hw.h` and all family initializers.

## Risks

The main risk is API drift between this header, `mac.c`, and operation-table expectations. Because these helpers are widely reused, changing semantics for one family can silently affect others. Flow-control and semaphore helpers are especially sensitive because they participate in reset, link, and NVM paths.

## Test Signals

Build coverage should catch missing prototypes or signature mismatches. Runtime signals are the same as the `mac.c` helper areas: link setup, address filters, multicast/VLAN programming, LED identify, semaphore acquisition, flow-control negotiation, and PCIe reset behavior across all families that include this header.
