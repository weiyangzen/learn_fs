<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.c

## Purpose

`option_ms.c` handles Option mobile broadband devices that initially enumerate as ZeroCD mass-storage devices. It identifies genuine Option-branded storage presentations and optionally sends a mode-switch command to make the device re-enumerate as a modem.

## Important APIs, Types, and Functions

The module parameter `option_zero_cd` selects force-modem or allow-storage behavior. `option_inquiry()` sends a raw Bulk-Only INQUIRY CBW and checks the returned vendor string for `Option` or `ZCOPTION`. `option_rezero()` sends a raw REZERO-style CBW that triggers mode switching and drains optional response/CSW data. `option_ms_init()` is the init hook declared in `option_ms.h`.

## Control Flow

During unusual-device initialization, `option_ms_init()` first performs the vendor INQUIRY because some IDs are ambiguous. Non-Option or indeterminate devices are left alone. In default force-modem mode, the driver sends the mode-switch CBW, logs failure if the transfer was not good, and returns `-EIO` to stop storage binding so the device can re-enumerate. In allow-storage mode, it leaves the mass-storage interface active and returns success.

## State and Persistence Behavior

No per-device state is kept. The only state is the module parameter. The meaningful persistent side effect is on the USB device: a successful mode switch changes its exposed function until device firmware or re-enumeration changes it again.

## Dependencies and Integration Points

The file depends on usb-storage bulk pipes and raw transfer helpers, module parameters, slab allocation, and unusual-device init wiring. It shares only its public `option_ms_init()` prototype through `option_ms.h`.

## Risks and Test Signals

Risks include handcrafted CBW bytes, ignoring response contents, fixed 1024-byte response buffer assumptions, and returning `-EIO` even after a successful forced switch. Tests should cover true Option and non-Option devices with shared IDs, both module parameter modes, short/stalled response reads, CSW drain failures, and re-enumeration behavior after successful switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/option_ms.c -->
