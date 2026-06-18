# sources/distributed-fs/ceph-client/drivers/usb/atm/Kconfig

## Purpose
`drivers/usb/atm/Kconfig` defines USB DSL modem support and the selectable USB ATM mini-drivers. It gates the shared `usbatm` core on ATM support and offers SpeedTouch, Conexant AccessRunner, ADI/eagle, and parameterized generic modem drivers.

## Important APIs, Types, And Functions
- `menuconfig USB_ATM` is a tristate depending on `ATM` and selecting `CRC32`; it builds the shared `usbatm` module.
- `USB_SPEEDTOUCH`, `USB_CXACRU`, and `USB_UEAGLEATM` select `FW_LOADER` because they need firmware blobs.
- `USB_XUSBATM` provides generic support using module parameters for vendor/product and endpoint numbers.
- Help text documents module names: `usbatm`, `speedtch`, `cxacru`, `ueagle-atm`, and `xusbatm`.

## Control Flow
When `USB_ATM` is enabled, the child driver prompts become visible. Each selected mini-driver builds alongside the shared core and calls into `usbatm_usb_probe()`/`usbatm_usb_disconnect()` at runtime. Firmware-loading drivers select firmware loader support automatically.

## State And Persistence Behavior
The file defines build-time configuration state only. Runtime persistence is limited to module parameters in the C drivers, not this Kconfig file.

## Dependencies And Integration Points
It integrates USB host support from the parent Kconfig with the Linux ATM stack. The corresponding object mapping lives in `drivers/usb/atm/Makefile`; the C files implement the mini-driver hooks declared in `usbatm.h`.

## Risks And Edge Cases
`USB_ATM` depends on `ATM`, so users may not see USB DSL options unless ATM support is enabled. Firmware help links are historical and may be stale. Selecting a mini-driver without correct firmware files will build successfully but fail at runtime during heavy initialization.

## Test Signals
Run Kconfig with and without `CONFIG_ATM` to verify visibility. Build each mini-driver as `m` and confirm the shared `usbatm` module is included. Boot tests should check firmware request names and module autoload aliases.
