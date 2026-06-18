# sources/distributed-fs/ceph-client/include/uapi/linux/major.h

Purpose: exposes legacy and reserved Linux major device numbers for character and block devices.

Important APIs and types: constants include well-known majors for memory/ramdisk, floppy/PTY/IDE/TTY/LP/VCS/loop, SCSI disks/tapes/CD-ROM/generic, misc, framebuffer, MTD, netlink, NBD, DASD, raw, USB, MMC, Xen block, MSR, CPUID, IBM terminal devices, block extended major, and many legacy hardware assignments.

Control flow: no executable flow. Code and tools use these values to interpret or construct device numbers, though modern systems normally allocate many majors dynamically.

State and persistence: no state. The values are ABI allocations and device-node compatibility anchors.

Dependencies and integration points: integrates device-number documentation, static `/dev` creation, udev-like tools, old drivers, block/char device registration, and compatibility code.

Risks and test signals: risks include collisions, using static majors for dynamically allocated drivers, and confusing overlapping historical aliases such as ramdisk/mem or VCS/loop. Test static device-node creation, driver registration conflicts, documentation consistency, and userspace tools that decode `st_rdev`.
