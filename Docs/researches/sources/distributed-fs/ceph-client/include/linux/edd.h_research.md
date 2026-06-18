# sources/distributed-fs/ceph-client/include/linux/edd.h

## Purpose
This header exposes BIOS Enhanced Disk Drive data collected during early x86 boot. It wraps the UAPI EDD structures and declares the global kernel `edd` table.

## Important APIs, types, and functions
It includes `uapi/linux/edd.h` and declares `extern struct edd edd` outside assembly.

## Control flow, state, and persistence
The persistent state is populated by boot code from BIOS int 13h EDD information and later used by firmware/EDD drivers to identify BIOS boot disks. The header has no functions.

## Dependencies and integration points
It integrates with x86 boot setup code, boot parameters, and `drivers/firmware/edd.c`. The comment emphasizes that setup assembly is sensitive to UAPI structure sizes.

## Risks and test signals
Risks include structure-size drift, bootloader/BIOS malformed records, and incorrect disk matching. Tests should verify boot-time population, UAPI layout stability, and mapping between BIOS devices and kernel block devices.
