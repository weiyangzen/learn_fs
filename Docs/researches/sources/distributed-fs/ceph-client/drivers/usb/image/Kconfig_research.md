# sources/distributed-fs/ceph-client/drivers/usb/image/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/image/Kconfig` defines the kernel configuration menu entries for legacy USB imaging devices. It exposes options for the Mustek MDC800 digital camera driver and the Microtek X6USB scanner driver. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

The file defines the `USB_MDC800` tristate symbol with prompt `USB Mustek MDC800 Digital Camera support` and the `USB_MICROTEK` tristate symbol with prompt `Microtek X6USB scanner support`. `USB_MICROTEK` declares `depends on SCSI` because the scanner is presented through the SCSI generic layer. The file also emits the menu comment `USB Imaging devices`.

## Control Flow

There is no runtime control flow. During kernel configuration, selecting `y` builds the matching driver into the kernel, selecting `m` builds it as a loadable module, and leaving it unset omits it. The selected symbols are consumed by the adjacent Makefile to include `mdc800.o` or `microtek.o`.

## State and Persistence Behavior

The only persistent state is the generated kernel configuration value in `.config` and derived build artifacts. The help text documents runtime device-node expectations for the MDC800 (`/dev/mustek` with major 180 minor 32) and SCSI generic exposure for Microtek scanners, but this Kconfig file does not create devices or store runtime data.

## Dependencies and Integration Points

The file integrates with the Linux Kconfig system, `drivers/usb/image/Makefile`, the `mdc800` and `microtek` driver sources in the same directory, and the SCSI subsystem dependency for `USB_MICROTEK`. Userspace integration is documented for `gphoto` for MDC800 and SCSI generic scanner access for Microtek devices.

## Risks and Edge Cases

The options are for old hardware and user-facing help text names specific historical tools and manual device-node creation. If `USB_MICROTEK` were selectable without SCSI, builds or runtime scanner exposure would be broken, so the dependency is important. Kconfig symbol renames would need synchronized Makefile and documentation updates.

## Test Signals

Test signals are `make oldconfig/menuconfig` visibility checks, build coverage for `USB_MDC800=y/m`, build coverage for `USB_MICROTEK=y/m` with SCSI enabled, verification that `USB_MICROTEK` is hidden or unavailable when SCSI is disabled, and module-name checks for `mdc800` and `microtek`.
