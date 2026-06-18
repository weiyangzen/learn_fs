# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hif.h

## Purpose

`hif.h` defines the ath12k host interface abstraction. It is the bus/transport-facing operations table used by common core, HAL, HTC, CE, power management, MSI, panic, and coredump code without hard-coding PCI or AHB behavior.

## Important APIs, Types, and Functions

`struct ath12k_hif_ops` contains callbacks for 32-bit register read/write, IRQ enable/disable, device start/stop, power up/down, suspend/resume, HTC service-to-pipe mapping, MSI vector/address lookup, CE IRQ control, CE MSI index lookup, panic handling, and coredump download.

Inline wrappers include `ath12k_hif_map_service_to_pipe()`, `ath12k_hif_get_user_msi_vector()`, `ath12k_hif_get_msi_address()`, `ath12k_hif_get_ce_msi_idx()`, CE/global IRQ enable/disable, suspend/resume, start/stop, read/write32, power up/down, panic handler, and coredump download.

## Control Flow and Integration

Bus drivers install `ab->hif.ops`. Core and HTC call `map_service_to_pipe()` to bind WMI/HTT/control endpoints to CE pipes. HAL calls `ath12k_hif_write32()` when publishing UMAC ring pointers through MMIO. Interrupt setup uses MSI helpers and IRQ wrappers. Power management and crash paths call suspend/resume, power, panic, and coredump wrappers if provided.

## State and Persistence Behavior

The header owns no storage; it dispatches to persistent bus-specific state behind `ab->hif.ops`. Some optional methods have fallback behavior: unsupported MSI vector lookup returns `-EOPNOTSUPP`, missing MSI address and CE IRQ methods are no-ops, missing CE MSI index maps CE ID directly, missing suspend/resume returns success, missing power-up returns `-EOPNOTSUPP`, and missing panic handler returns `NOTIFY_DONE`.

## Dependencies and Integration Points

It includes `core.h` and is consumed by HAL, HTC, CE, core boot/shutdown, PCI/AHB bus implementations, PM, and crash-dump code.

## Risks and Contract Notes

- Required callbacks such as read/write32, IRQ enable/disable, start, stop, and service-to-pipe mapping are called without null checks.
- Optional callback fallbacks can hide unsupported platform behavior if callers do not check return values.
- `ath12k_hif_power_down()` silently no-ops when unsupported, while `power_up()` reports unsupported; caller expectations must match bus behavior.
- `get_ce_msi_idx()` defaulting to CE ID is only valid for transports whose MSI data layout matches CE numbering.

## Test Signals

Build/test every bus implementation, verify HTC service-to-pipe maps, MSI vector assignment, IRQ enable/disable sequencing, suspend/resume on platforms with and without callbacks, panic notifier return behavior, and HAL MMIO ring pointer writes through the transport.
