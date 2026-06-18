# sources/distributed-fs/ceph-client/drivers/power/reset/nvmem-reboot-mode.c

## Purpose
generic reboot-mode backend that stores reboot magic in an NVMEM cell.

## Important APIs, Types, and Functions
private structure containing `struct reboot_mode_driver` and `struct nvmem_cell`, write callback, and platform probe.

## Control Flow
probe obtains an NVMEM cell from DT, initializes reboot-mode driver, and registers it; reboot notifier writes selected magic bytes to the cell before reboot.

## State and Persistence Behavior
selected mode persists in nonvolatile or retention-backed cell until bootloader/firmware consumes or overwrites it.

## Dependencies and Integration Points
OF, NVMEM consumer API, reboot-mode core.

## Risks and Edge Cases
cell size/endianness must match bootloader contract; NVMEM write failures occur late in reboot notifier path; repeated writes may affect flash-backed endurance.

## Test Signals
mode property parsing through reboot-mode core, NVMEM cell sizing, write failure injection, and bootloader mode consumption.
