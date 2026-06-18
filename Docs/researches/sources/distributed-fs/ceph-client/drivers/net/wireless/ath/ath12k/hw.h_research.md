# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hw.h

## Purpose

`hw.h` defines ath12k target defaults, firmware/board filenames, bus identifiers, hardware capability/parameter structures, hardware operation callbacks, firmware/board IE layouts, and small helper mappings for pdev/mac/SRNG IDs. It is the central hardware-variant configuration contract used by core, HAL, WMI, datapath, firmware, and bus code.

## Important APIs, Types, and Functions

Target defaults cover vdev/station counts, peer keys, AST skid/offload limits, chain masks, RX timeouts, decap modes, scan/roam/offload limits, multicast tables, TX debug log size, RX batch mode, MSDU descriptors, fragment entries, beacon offload, WDS entries, DMA burst, and EMA max profile period.

Firmware and board constants include directory/name strings for board-2, board, caldata, AMSS, M3, auxiliary microcode, and regdb files, plus board magic and PCIe payload/userpd constants.

Enums define CCK/OFDM hardware rates, bus type, and M3 firmware loader type.

`struct ath12k_hw_ring_mask` maps datapath ring classes to external IRQ groups. `struct ath12k_hw_params` stores per-chip capabilities and configuration: firmware layout, radio count, QMI service ID, CE configs/maps, RXDMA shape, monitor support, power-management flags, REO LUT/shadow register support, MHI config, WMI init hook, QMI feature bitmap, rfkill, RDDM, MLO limits, ACPI, dynamic SMPS, IOVA mask, CE remap/address tables, board offset, and primary-link-only datapath behavior.

`struct ath12k_hw_ops` provides hardware-specific helpers for pdev/mac/SRNG ID translation, RXDMA ring selection, TX completion ring identification, skb ring selection, and frame link-agnostic checks.

Inline helpers `ath12k_hw_get_mac_from_pdev_id()`, `ath12k_hw_mac_id_to_pdev_id()`, and `ath12k_hw_mac_id_to_srng_id()` call hardware ops when present or default to zero.

Firmware/board IE definitions include `struct ath12k_fw_ie`, board/regdb IE enums, and `ath12k_bd_ie_type_str()`.

## Control Flow and Integration

Chip-specific tables populate `ath12k_hw_params` and `ath12k_hw_ops` during device matching. Core and boot code use these values to size WMI resources, request firmware/board files, configure CE/MHI/QMI, set datapath ring counts, select monitor/RXDMA behavior, and gate suspend/ASPM/current-channel/MLO behavior. HAL and datapath code repeatedly call the inline ID mapping helpers and hardware ops when setting up rings and peer RX/TX state.

## State and Persistence Behavior

The header defines mostly immutable configuration tables referenced through `ab->hw_params`. Those parameters control long-lived driver state allocation sizes, firmware resource requests, interrupt masks, RX/TX ring topology, and feature gates for the lifetime of the device.

## Dependencies and Integration Points

It includes MHI and UUID kernel headers plus `wmi.h` and `hal.h`. It references CE pipe/config structures, service-to-pipe maps, HAL descriptor types, WMI resource configuration, MHI controller configs, ACPI GUIDs, and mac80211 management/link-vif types.

## Risks and Contract Notes

- The mutual include relationship with `hal.h` is guarded but tight; adding new direct type dependencies can create incomplete-type issues.
- Default inline ID mapping helpers return zero when ops are absent. That is only correct for single-radio/simple hardware.
- Resource macros depend on `ab->profile_param`; callers must ensure profile parameters are initialized before using them.
- `ath12k_hw_params` is broad and feature-packed; adding a new hardware family requires careful audit of every boolean default, especially RXDMA, REO LUT, shadow regs, MLO, and primary-link-only behavior.
- Firmware/board filenames and IE IDs are external ABI with linux-firmware and board tooling.

## Test Signals

Useful validation includes booting every supported hardware table, WMI resource sizing tests for profile modes, firmware/board file lookup, CE/service map checks, ring mask interrupt routing, pdev/mac/SRNG ID translation tests, monitor support gating, suspend/ASPM feature tests, MLO peer limit tests, and static build coverage for PCI and AHB buses.
