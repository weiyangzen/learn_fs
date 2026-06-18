# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Kconfig

## Purpose

`legacy/Kconfig` defines build-time configuration for precomposed USB gadget drivers. These entries select libcomposite and the specific USB function modules needed to build fixed-purpose gadget modules such as audio, ethernet, serial, MIDI, HID, FunctionFS, UVC webcam, mass storage, and debug-port gadgets.

## Important APIs, Types, and Functions

This is Kconfig data, not C code. Important symbols include `USB_ZERO`, `USB_AUDIO`, `GADGET_UAC1`, `GADGET_UAC1_LEGACY`, `USB_ETH`, `USB_ETH_RNDIS`, `USB_ETH_EEM`, `USB_G_NCM`, `USB_GADGETFS`, `USB_FUNCTIONFS`, `USB_FUNCTIONFS_ETH`, `USB_FUNCTIONFS_RNDIS`, `USB_FUNCTIONFS_GENERIC`, `USB_MASS_STORAGE`, `USB_GADGET_TARGET`, `USB_G_SERIAL`, `USB_MIDI_GADGET`, `USB_G_PRINTER`, `USB_CDC_COMPOSITE`, `USB_G_ACM_MS`, `USB_G_MULTI`, `USB_G_HID`, `USB_G_DBGP`, `USB_G_WEBCAM`, and `USB_RAW_GADGET`.

## Control Flow

Menu selection controls which modules are built and which lower-level function drivers are selected. For example, `USB_G_WEBCAM` selects `USB_F_UVC` and videobuf2 memory backends; `USB_AUDIO` selects UAC1/UAC2 function implementations based on sub-options; `USB_ETH` selects ECM/subset and optionally RNDIS/EEM; `USB_FUNCTIONFS` selects `USB_F_FS` and optional ethernet/RNDIS/generic configurations.

## State and Persistence Behavior

Kconfig choices are persisted only in the kernel build configuration (`.config`). They have no runtime state here, but they determine which module parameters, descriptors, and composite bind paths exist in the built kernel.

## Dependencies and Integration Points

The file integrates the legacy gadget directory with libcomposite, function drivers under `drivers/usb/gadget/function`, ALSA, networking, block layer, TTY, target core, V4L2, and raw gadget support. It also controls help text and module names consumed by users and distributions.

## Risks and Test Signals

Risks include missing `select` lines causing link failures, overbroad selects pulling invalid dependencies, config combinations that expose functions without prerequisites, and help text drifting from behavior. Test signals are allmodconfig/allnoconfig builds, targeted builds for every tristate, dependency-resolution checks, and module-load tests for each enabled legacy gadget.
