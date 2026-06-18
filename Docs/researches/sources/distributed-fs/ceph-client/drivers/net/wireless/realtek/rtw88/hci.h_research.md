# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/hci.h

## Purpose

`hci.h` defines the host-controller-interface abstraction used by the generic `rtw88` core to run over PCIe, USB, and SDIO. It hides bus-specific TX, firmware download, reserved-page writes, H2C writes, power-save signaling, queue flushing, and register access behind `struct rtw_hci_ops` plus inline wrappers.

## Important APIs, Types, and Functions

`struct rtw_hci_ops` contains function pointers for packet TX, TX kickoff, queue flush, setup/start/stop, deep and link power-save entry, interface configuration, optional dynamic RX aggregation, firmware page writes, reserved-page writes, H2C data writes, and 8/16/32-bit MMIO-like register access.

Inline wrappers such as `rtw_hci_tx_write()`, `rtw_hci_setup()`, `rtw_hci_start()`, `rtw_hci_stop()`, `rtw_hci_write_data_h2c()`, `rtw_read8/16/32()`, and `rtw_write8/16/32()` centralize the calls. Helper wrappers provide set/clear operations, masked reads/writes, RF register access through chip ops, HCI type lookup, and optional queue flushing.

## Control Flow

Most wrappers directly dispatch into `rtwdev->hci.ops`. Optional operations such as `dynamic_rx_agg` and `flush_queues` are guarded by null checks. RF read/write wrappers assert that `rtwdev->mutex` is held before calling chip-specific RF operations. Masked writes perform read-modify-write operations and `rtw_write32_mask()` warns on unaligned 32-bit addresses.

## State and Persistence

This header does not own state. It routes operations through `rtwdev->hci`, whose `type`, `ops`, bus-specific parameters, and power-management addresses are initialized by the bus driver. Register writes and RF writes persist in hardware; queue flushes and power-save operations affect bus/device runtime state.

## Dependencies and Integration Points

Every file in this subset depends on `hci.h` either directly or indirectly for register access. It integrates the generic core with PCIe, USB, and SDIO modules, chip RF operations, firmware download paths in `mac.c`, H2C/reserved-page writes in `fw.c`, debugfs raw register access in `debug.c`, and MAC queue flushing.

## Risks

Because these wrappers are thin, invalid or missing HCI ops will crash or misbehave at call sites. Read-modify-write helpers are not atomic with respect to other hardware writers unless the caller holds the appropriate lock. Masked helpers assume nonzero masks because they call `__ffs(mask)`. RF helpers require the mutex; violating that contract should trip lockdep and can race PHY/RF state.

## Test Signals

Bus-specific tests should verify each HCI implementation fills all mandatory ops and that generic bring-up works over PCIe, USB, and SDIO. Lockdep should be enabled to catch RF access without `rtwdev->mutex`. Register mask tests should verify set/clear/read/write helpers preserve unrelated bits and handle byte/word/dword widths correctly.
