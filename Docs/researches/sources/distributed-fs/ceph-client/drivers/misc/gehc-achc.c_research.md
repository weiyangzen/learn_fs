# sources/distributed-fs/ceph-client/drivers/misc/gehc-achc.c

## Purpose
SPI driver for GE Healthcare ACHC hardware that controls reset and firmware update of an attached NXP Kinetis device through its EzPort programming interface. It exposes sysfs controls for reset and firmware flashing.

## Important APIs, Types, And Functions
`struct achc_data` stores the main SPI device, ancillary EzPort SPI device, reset GPIO, and mutex. EzPort helpers implement reset sequencing, programming-mode entry/exit, status reads, write-enable, bulk/sector erase, flash transfer, flash compare, firmware-data flashing, and firmware loading. Sysfs callbacks are `update_firmware_store()` and `reset_show/store()`. Probe configures SPI mode/speed, creates the ancillary EzPort device from the second `reg` cell, and acquires reset GPIO.

## Control Flow
Probe sets conservative SPI parameters for the main device, allocates state, reads the EzPort chip-select value from DT, creates the ancillary device, registers cleanup, and requests reset GPIO. Writing `1` to `update_firmware` locks the device, enters programming mode by asserting chip select and resetting, requests `achc.bin`, erases as needed, programs in 2048-byte transfers with sector erase at 4 KiB boundaries, verifies by FAST_READ, soft-resets EzPort, exits programming mode, and unlocks. The reset sysfs attribute simply reads or drives the reset GPIO under the same mutex.

## State, Persistence, And Dependencies
Persistent state is firmware stored in target flash and reset line state. Driver state is the SPI devices, GPIO descriptor, and mutex. Dependencies include SPI core, ancillary SPI devices, firmware loader, GPIO descriptors, OF property parsing, sleep delays, and sysfs device groups.

## Integration Points
The OF compatible and SPI ID are `ge,achc`. The driver expects two `reg` entries so it can create an EzPort ancillary device. Firmware is loaded by name `achc.bin` through the kernel firmware search path. Sysfs attributes are attached via driver `dev_groups`.

## Risks
Firmware update is destructive and has no version or image validation beyond readback comparison. Secure EzPort mode can block verification; flashing treats `-EACCES` from verification as acceptable. Bulk erase may be triggered when flash security is set. Fixed delays and retry counts may not suit all target revisions. The update path holds a device mutex for the entire firmware operation, blocking reset access.

## Test Signals
Test missing second `reg`, ancillary creation cleanup, reset GPIO polarity, firmware request failure, write-enable timeout, sector alignment rejection, secure-mode behavior, verification mismatch, soft-reset warning path, and concurrent reset/update sysfs accesses.
