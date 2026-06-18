# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_subset.c

## Purpose

`cdc_subset.c` supports very simple USB networking links that use a minimal subset of CDC Ethernet behavior: bulk Ethernet frames with no class-specific runtime control, no extra framing, and generally point-to-point semantics. It exists for legacy host-to-host cables, embedded/PDA firmware, and bootloader/device modes selected by Kconfig options.

## Important APIs, types, and functions

Most logic is declarative `struct driver_info` and `usb_device_id` data behind `CONFIG_USB_*` feature blocks. Optional helpers include `always_connected()` for PDA-style devices and `m5632_recover()` for ALi M5632 reset recovery. Driver info variants describe ALi M5632, AnchorChips/Cypress AN2720, Belkin/eTEK, Epson, KC2190, Linux PDA/gadget, Yopy, and blob bootloader devices. The USB driver delegates probe/disconnect/suspend/resume to `usbnet`.

## Control flow

At module load, only device entries enabled by Kconfig are compiled into the `products` table. `usbnet_probe()` uses the matched `driver_info` to select endpoint numbers, flags, optional `check_connect`, and optional recovery behavior. Runtime packet flow is generic `usbnet` Ethernet transfer without RX/TX fixups. The dummy pre/post reset callbacks always return success and avoid special reset handling in this driver.

## State and persistence

The file has no private per-device state. Runtime state is held by `usbnet`; configuration is compile-time through Kconfig and the USB ID table. No hardware nonvolatile settings or filesystem state are written.

## Dependencies and integration points

It depends on `usbnet`, USB device matching, Kconfig-selected hardware support, netdev/ethernet helpers, and USB suspend/resume. It integrates with the older Linux USB gadget ecosystem and host-to-host cable devices by identifying vendor/product IDs and endpoint quirks.

## Risks

The main risks are accidental binding to devices that need richer protocol handling, endpoint assumptions for old hardware, and the lack of link/reset handshakes for unplug/replug scenarios. Product support is compile-time gated; a build with no hardware options emits a preprocessor warning. Some supported hardware explicitly does not interoperate with Windows framing or needs power-cycle recovery because vendor docs are unavailable.

## Test signals

Test each enabled Kconfig ID, endpoint override behavior, plain Ethernet frame TX/RX without fixups, suspend/resume, ALi recovery reset behavior, always-connected devices, reset callbacks, and coexistence with CDC Ethernet/RNDIS/gadget alternatives for devices exposing multiple configurations.
