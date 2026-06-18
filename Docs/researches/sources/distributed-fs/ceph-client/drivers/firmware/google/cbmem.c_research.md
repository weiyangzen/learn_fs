# sources/distributed-fs/ceph-client/drivers/firmware/google/cbmem.c

Purpose: Exposes coreboot CBMEM entries as sysfs devices under the coreboot bus, including physical address, size, and a binary `mem` attribute backed by the mapped memory region.

Important APIs/types/functions: `cbmem_entry` stores the mapped buffer and size. `mem_read()` and `mem_write()` implement the binary attribute. `address_show()` and `size_show()` expose metadata. `cbmem_entry_probe()` maps `dev->cbmem_entry.address`/`entry_size` using `devm_memremap()`.

Control flow: The coreboot bus matches `LB_TAG_CBMEM_ENTRY`. Probe allocates per-device state, stores it with `dev_set_drvdata()`, maps the firmware memory, and lets default groups expose attributes. Reads use `memory_read_from_buffer()`, while writes update the mapped buffer within bounds.

State and persistence behavior: State is per coreboot device and devm-managed. Writes to the mapped CBMEM region mutate firmware memory visible through the sysfs file, but the driver itself does not persist metadata.

Dependencies and integration points: Depends on `coreboot_table.h`, coreboot table enumeration, sysfs binary attributes, and memory remapping. It exports each CBMEM entry as `/sys/bus/coreboot/devices/cbmem-<id>/`.

Risks and test signals: Writable CBMEM is admin-only but still risky because firmware-provided memory contents are mutable from userspace. Bounds checks protect sysfs writes, but invalid firmware addresses or sizes can map wrong memory. Test by booting with CBMEM entries, reading size/address/mem, verifying partial reads/writes, and checking behavior on malformed entries.
