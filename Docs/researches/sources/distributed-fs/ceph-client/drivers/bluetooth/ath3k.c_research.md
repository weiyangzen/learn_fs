# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/ath3k.c

## Purpose

`ath3k.c` is a USB firmware download driver for Atheros AR30xx Bluetooth controllers. It does not register an HCI device itself; instead it prepares supported USB devices by loading firmware, patch, and system configuration files, switching them into normal mode, and causing them to re-enumerate for the main Bluetooth USB HCI driver.

## Important APIs, Types, And Functions

`struct ath3k_version` models the vendor `GETVERSION` response, including ROM/build/RAM versions and reference clock. `ath3k_table` is the USB device table for supported AR3011/AR3012 and OEM variants. `ath3k_blist_tbl` marks AR3012 devices requiring patch and sysconfig loading via `BTUSB_ATH3012`.

Firmware transfer helpers include `ath3k_load_firmware` for the legacy `ath3k-1.fw` image and `ath3k_load_fwfile` for AR3012 `.dfu` files. Vendor control helpers include `ath3k_get_state`, `ath3k_get_version`, `ath3k_set_normal_mode`, and `ath3k_switch_pid`. `ath3k_load_patch` selects `ar3k/AthrBT_0x%08x.dfu` based on ROM version and verifies the patch trailer against ROM/build versions. `ath3k_load_syscfg` selects `ar3k/ramps_0x%08x_<clock>.dfu` based on ROM version and reference clock. `ath3k_probe` orchestrates all of this.

## Control Flow

On USB probe, the driver rejects nonzero interface numbers. If the matched id lacks `driver_info`, it searches the AR3012 blacklist table for a more specific match. AR3012 devices with `bcdDevice > 0x0001` are treated as already handled and return `-ENODEV`, allowing another driver to bind. Older AR3012 devices load patch, load syscfg, set normal mode, and send a vendor PID-switch request. Legacy devices request `ath3k-1.fw`, send the first firmware header bytes through a vendor control request, then stream remaining data over bulk endpoint `0x02` in 4096-byte chunks with a short xHCI compatibility delay.

## State And Persistence

The driver keeps no per-interface runtime state beyond the probe call. State lives in the controller firmware state queried by vendor requests. A successful probe changes device firmware state and likely causes USB re-enumeration. Firmware data is requested, streamed, and released during probe.

## Dependencies And Integration Points

The driver depends on USB core, firmware loader, Bluetooth logging helpers, and unaligned little-endian helpers. It is selected by `CONFIG_BT_ATH3K`, which depends on `BT_HCIBTUSB`, because the prepared controller is expected to be used by the standard btusb transport after firmware loading. It advertises `MODULE_FIRMWARE(ath3k-1.fw)` but AR3012 paths also require versioned files under `ar3k/`.

## Risks

Firmware filename generation and version validation are critical. A missing, stale, or mismatched patch is rejected; a syscfg reference-clock mismatch can prevent device startup. Bulk transfer errors can currently return the USB error, but if a short write reports `err == 0` and `len != size`, callers receive zero from `ath3k_load_firmware`; that pattern deserves attention if changing error handling. The device table is large and OEM-heavy, so ID drift can break only specific laptops. Timing delays around xHCI and normal-mode/PID switch should not be casually removed.

## Test Signals

Signals include USB probe logs, firmware request success/failure messages, successful re-enumeration into btusb, and absence of repeated firmware-download loops. Test old AR3011 firmware, AR3012 patch/syscfg, missing firmware, mismatched patch trailer, and device IDs with `bcdDevice > 0x0001`.
