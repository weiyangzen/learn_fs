# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_usbat.h

## Purpose

`unusual_usbat.h` lists USBAT bridge devices that need the `USB_PR_USBAT` transport and either CD or flash initialization.

## Important APIs, Types, and Functions

The file has four `UNUSUAL_DEV()` rows. HP CD devices use `USB_SC_8070`, `USB_PR_USBAT`, and `init_usbat_cd`; SCM/SanDisk flash devices use `USB_SC_SCSI`, `USB_PR_USBAT`, `init_usbat_flash`, and `US_FL_SINGLE_LUN`.

## Control Flow

Macro expansion routes matching bridges to the USBAT subdriver. The selected initializer runs before the control thread starts, and `US_FL_SINGLE_LUN` constrains flash readers to LUN 0 where needed.

## State and Persistence Behavior

No state is kept in the header. Runtime bridge/media state is owned by the USBAT initializer and transport.

## Dependencies and Integration Points

It depends on `init_usbat_cd`, `init_usbat_flash`, and USBAT protocol support. It integrates with usb-storage probe, specialized transport selection, and SCSI LUN scanning policy.

## Risks and Edge Cases

The CD rows are exact revision `0x0001`; flash rows are narrow for SanDisk and broad for SCM. Incorrect ranges can select the wrong initializer type, which is more serious here because CD and flash setup differ.

## Test Signals

Build USBAT support, attach represented CD and flash bridges, confirm initializer selection, test media access, LUN behavior, reset, and disconnect cleanup.
