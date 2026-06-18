# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.h

## Purpose
Provides RT2800 PCI-specific firmware constants and include guard. It documents the supported RT2800E/RT2800ED family at the header level and supplies firmware names and the firmware image base used by `rt2800pci.c`.

## Important APIs, Types, And Functions
Defines `FIRMWARE_RT2860` (`rt2860.bin`), `FIRMWARE_RT3290` (`rt3290.bin`), and `FIRMWARE_IMAGE_BASE` (`0x2000`). No functions or structures are declared.

## Control Flow
`rt2800pci_get_firmware_name()` chooses one of the firmware name macros, and `rt2800pci_write_firmware()` writes the selected image to `FIRMWARE_IMAGE_BASE`. Module metadata uses the same names to advertise firmware requirements.

## State And Persistence
No runtime state is defined. These constants become part of the firmware loading contract between kernel driver and userspace firmware storage.

## Dependencies And Integration Points
Consumed only by the PCI implementation. It integrates with the Linux firmware loader through module metadata and with RT2800 PBF/program-RAM write logic.

## Risks
Changing firmware names or image base breaks device boot. The header does not express firmware size; `rt2800_check_firmware()` and PCI write code must enforce length/version constraints.

## Test Signals
Successful `request_firmware()` for both filenames, firmware version logging, and PCI probe on RT3290 and non-RT3290 devices.
