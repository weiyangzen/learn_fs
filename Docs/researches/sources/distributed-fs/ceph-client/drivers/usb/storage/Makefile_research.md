# sources/distributed-fs/ceph-client/drivers/usb/storage/Makefile

## Purpose

`drivers/usb/storage/Makefile` maps USB storage Kconfig symbols to core, UAS, and vendor-specific object files, and sets include paths and symbol namespace defaults for the USB_STORAGE namespace.

## Important APIs, Types, and Functions

`ccflags-y` adds the SCSI driver include path and defines `DEFAULT_SYMBOL_NAMESPACE="USB_STORAGE"`. `usb-storage-y` is composed from `scsiglue.o`, `protocol.o`, `transport.o`, `usb.o`, `initializers.o`, `sierra_ms.o`, `option_ms.o`, and `usual-tables.o`, with `debug.o` conditionally added for `CONFIG_USB_STORAGE_DEBUG`. Vendor module aggregates include `ums-alauda-y := alauda.o`, `ums-cypress-y := cypress_atacb.o`, `ums-datafab-y := datafab.o`, `ums-eneub6250-y := ene_ub6250.o`, and `ums-freecom-y := freecom.o`.

## Control Flow

There is no runtime flow. Kbuild uses the object lists to compile either built-in objects or loadable modules based on the selected Kconfig symbols.

## State and Persistence Behavior

The Makefile contributes no runtime state. Its build decisions persist only as generated build artifacts and module composition.

## Dependencies and Integration Points

The file integrates with Kbuild, the USB storage Kconfig symbols, the SCSI include tree, and module namespace handling. It ensures optional vendor modules link against the USB storage core interfaces they import.

## Risks and Test Signals

Risks include object-list drift from Kconfig, namespace mismatch for exported USB storage symbols, missing debug object when `CONFIG_USB_STORAGE_DEBUG` is enabled, and broken vendor module aggregation. Test signals include clean incremental builds across `USB_STORAGE_DEBUG` on/off, modpost namespace checks, and successful module generation for each `ums-*` target.
