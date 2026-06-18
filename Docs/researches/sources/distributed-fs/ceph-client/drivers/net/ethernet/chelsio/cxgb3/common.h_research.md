# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/common.h

## Purpose
`common.h` is the central hardware/common interface for Chelsio T3 `cxgb3`. It defines logging macros, global constants, adapter/PHY/MAC/SGE/TP/MC5/MC7 parameter and statistics structures, PHY operation contracts, helper wrappers, and prototypes for the hardware, interrupt, link, MAC, TP, SGE, and PHY implementation files.

## Important APIs, Types, And Functions
- Logging/debug macros are `CH_ERR`, `CH_WARN`, `CH_ALERT`, `CH_MSG`, and `CH_DBG`, with an extra `NETIF_MSG_MMIO` category.
- Constants cover ports, frame sizes, EEPROM size, RSS table, TCB, MTU table, congestion windows, TP SRAM size, pause bits, IRQ stats, TP version fields, SGE queue counts, async/immediate packet sizes, descriptor flits, and MAC accumulation timing.
- Core hardware structs include `adapter_info`, `adapter_params`, `vpd_params`, `pci_params`, `mc5`, `mc7`, `mac_stats`, `tp_mib_stats`, `tp_params`, `qset_params`, `sge_params`, `mc5_params`, `trace_params`, and `link_config`.
- PHY abstractions include `mdio_ops`, `cphy_ops`, `cphy`, module type enums, loopback direction, interrupt cause bits, and EDC firmware sizes.
- Inline helpers include `t3_mdio_read`, `t3_mdio_write`, `cphy_init`, `for_each_port`, `adapter_info`, `uses_xaui`, `is_10G`, `is_offload`, `core_ticks_per_usec`, and `is_pcie`.
- Prototypes cover register helpers, MDIO/PHY helpers, interrupt control, link events, adapter prep/init/reset/firmware, MAC operations, MC5, TP offload and stats, MTU/trace/scheduler configuration, SGE context operations, and all supported PHY prep functions.

## Control Flow And State
This header defines the contracts that structure T3 driver flow. Adapter prep fills `adapter_params`, VPD/PCI fields, and `adapter_info`; hardware init configures MC5/MC7, TP, SGE, MACs, firmware, and RSS; open/close/link operations use `link_config`, `cphy_ops`, and MAC prototypes; interrupts flow through common interrupt prototypes and PHY/MAC handlers; offload and iSCSI/RDMA paths query control structures and context setup functions.

## State And Persistence Behavior
Most structures describe software mirrors of persistent hardware configuration: VPD clock/MAC data, PCI mode, memory sizes, MTU/congestion tables, TP page sizing, queue parameters, MAC/TP/MC5/MC7 counters, link configuration, and trace filters. `cphy` stores module type, capabilities, MDIO interface, FIFO errors, and an EDC firmware cache.

## Dependencies And Integration Points
The header depends on Linux kernel, netdevice, ethtool, MDIO, delay, and version headers. It includes `adapter.h` late, after common types are defined. It is included by nearly every `cxgb3` hardware, PHY, MAC, SGE, and offload source file, making it the main ABI inside the driver.

## Risks And Edge Cases
Because it is a central header, changes have broad build and behavior blast radius. Structure layouts must match code assumptions in debugfs, ioctl/offload paths, and hardware context programming. PHY operation callbacks are optional for some features but many call paths assume the relevant pointer exists for the selected PHY. Constants such as frame sizes, queue counts, and EDC cache size encode hardware limits.

## Test Signals
Signals include full driver build coverage, probe on multiple board types, link/autoneg behavior across PHYs, MAC/TP/SGE stats reads, firmware/version checks, offload control queries, SGE context setup/teardown, and static checks for prototype drift.
