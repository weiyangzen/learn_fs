## sources/distributed-fs/ceph-client/include/uapi/linux/edd.h

Purpose: This header defines BIOS Enhanced Disk Drive data structures used to pass INT 13h boot disk information from early x86 boot code into the kernel and userspace-visible firmware interfaces.

Important APIs and types: Constants define boot parameter offsets (`EDDNR`, `EDDBUF`, MBR signature buffers), maximum record counts, BIOS function numbers, magic values, and flags. `struct edd_device_params` is a packed representation of EDD device parameters, including geometry, sector count, bytes per sector, host bus/interface type, interface path union, device path union, checksum, and reserved fields. `struct edd_info` adds BIOS device number, version, interface support, legacy geometry, and params. `struct edd` groups MBR signatures and up to `EDDMAXNR` EDD records.

Control flow and state: Early setup code gathers BIOS EDD data into boot parameters, kernel setup copies it into EDD structures, and firmware code uses it to identify the BIOS boot disk. The header itself has no functions, but its packed layout is consumed by assembly and firmware code, making size and alignment critical.

Persistence and dependencies: EDD data is boot-time firmware state, not persistent kernel state. The header depends on `<linux/types.h>` and excludes C structs for assembly builds.

Integration points: It integrates with x86 boot setup, firmware/edd driver code, disk identification, MBR signatures, and bootloader/kernel handoff.

Risks and test signals: Risks include changing packed structure sizes, BIOS-provided malformed checksums, truncation to six EDD records or sixteen MBR signatures, legacy geometry mismatch, and host/device path union interpretation. Tests should compare structure sizes to `EDDEXTSIZE` and `EDDPARMSIZE` expectations, boot with BIOS EDD-enabled devices, validate checksum handling, confirm sysfs/firmware output, and cover systems with no EDD support.
