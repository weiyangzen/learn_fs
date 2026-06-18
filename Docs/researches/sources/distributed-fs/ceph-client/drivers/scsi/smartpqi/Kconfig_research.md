# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Kconfig

## Purpose
Defines the kernel configuration option for the Microchip PQI storage controller driver. `SCSI_SMARTPQI` can be built in, built as module `smartpqi`, or disabled.

## Important APIs, Types, And Functions
The public interface is the Kconfig symbol `SCSI_SMARTPQI`, declared as `tristate "Microchip PQI Driver"`. It depends on `PCI`, `SCSI`, and `!S390`, and selects `SCSI_SAS_ATTRS` plus `RAID_ATTRS`.

## Control Flow
During kernel configuration, selecting this option enables compilation of the smartpqi driver objects through the companion Makefile. The help text identifies the supported controller family, module name, a Microchip URL, and a note that `aacraid` will not manage smartpqi controllers.

## State And Persistence Behavior
This file has no runtime state. Its selected value persists only in the kernel `.config` and determines whether the driver is included in the build or emitted as a loadable module.

## Dependencies And Integration Points
It integrates with the SCSI and PCI Kconfig menus and forces the SAS transport and RAID attribute support needed by the driver. Documentation integration is through `Documentation/scsi/smartpqi.rst`.

## Risks
Dependency mistakes can make the driver visible on unsupported architectures or hide it from valid PCI/SCSI builds. The `select` statements pull in support code automatically, so missing or excessive selects can affect minimal kernel configurations. The note about `aacraid` is operationally important because choosing the wrong driver can leave controllers unmanaged.

## Test Signals
Signals are Kconfig resolution tests (`y`, `m`, and `n` where allowed), build tests with PCI/SCSI enabled and on S390-disabled paths, module-name validation (`smartpqi.ko`), and menu/help rendering checks.
