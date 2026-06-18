# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon_boot.h

Purpose: defines the small subset of Octeon bootloader data structures and fixed addresses needed by the Linux SMP and hotplug paths. It lets the kernel restart secondary cores through bootloader vectors without importing the full bootloader header set.

Important APIs and types: `struct boot_init_vector` describes per-core boot-vector entries: boot code address, app start function, saved `k0`, boot-info pointer, and flags. `struct linux_app_boot_info` mirrors bootloader state such as signature, available core mask, TLB initialization address, exception base, CompactFlash base addresses, and LED display base. Constants include `LABI_SIGNATURE`, `LABI_ADDR_IN_BOOTLOADER`, `BOOTLOADER_BOOT_VECTOR`, `LINUX_APP_BOOT_BLOCK_NAME`, and `AVAIL_COREMASK_OFFSET_IN_LINUX_APP_BOOT_BLOCK`.

Control flow and integration: `smp.c` reads `linux_app_boot_info` during hotplug capability detection, updates boot vectors before resetting or NMI-starting cores, and uses the available core mask to return dead cores to firmware control. The header has no executable control flow of its own.

State and persistence: the structures describe physical bootloader-resident state. Kernel writes to boot vectors and availability masks affect firmware-visible memory during the running boot, but not persistent storage.

Dependencies: depends on Linux fixed-width types and Octeon boot memory layout conventions. Endianness-specific field layout is used for `linux_app_boot_info`, so consumers rely on correct `__BIG_ENDIAN_BITFIELD` selection.

Risks: hardcoded offsets and addresses must match bootloader layout. A mismatch can corrupt firmware data or fail CPU hotplug. The bitfield ordering differences are subtle and should not be refactored without checking bootloader ABI.

Test signals: SMP boot should start all firmware-supplied cores; CPU hotplug should update available core masks and restart cores through the boot vector; boards without supported LABI data should log that hotplug is unsupported rather than crashing.
