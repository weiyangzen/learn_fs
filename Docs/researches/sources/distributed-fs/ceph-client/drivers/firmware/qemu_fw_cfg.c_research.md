# sources/distributed-fs/ceph-client/drivers/firmware/qemu_fw_cfg.c

## Purpose
`qemu_fw_cfg.c` exposes QEMU's firmware configuration device under `/sys/firmware/qemu_fw_cfg`. It supports ACPI, device tree, and optional command-line platform-device creation, then publishes fw_cfg directory entries by selector key and by firmware-provided path name.

## Important APIs, Types, And Functions
- Global device state: `fw_cfg_rev`, register base/size, `fw_cfg_dev_base`, `fw_cfg_reg_ctrl`, `fw_cfg_reg_data`, `fw_cfg_reg_dma`, and `fw_cfg_dev_lock`.
- Register access: `fw_cfg_sel_endianness()`, `fw_cfg_read_blob()`, optional `fw_cfg_write_blob()`, and DMA helpers under `CONFIG_VMCORE_INFO`.
- Sysfs entry model: `struct fw_cfg_sysfs_entry`, `struct fw_cfg_sysfs_attribute`, `fw_cfg_sysfs_entry_ktype`, and binary `raw` attribute.
- Directory registration: `fw_cfg_register_dir_entries()`, `fw_cfg_register_file()`, `fw_cfg_build_symlink()`, and recursive kset cleanup.
- Probe/remove: `fw_cfg_do_platform_probe()`, `fw_cfg_sysfs_probe()`, `fw_cfg_sysfs_remove()`, `fw_cfg_sysfs_init()`, and `fw_cfg_sysfs_exit()`.
- Optional command line: `fw_cfg_cmdline_set()` and `fw_cfg_cmdline_get()` for `ioport=` and `mmio=`.

## Control Flow
Module init creates the top-level firmware kobject and registers a platform driver. Probe refuses a second device, creates `by_key` and `by_name`, maps IO or MMIO resources, resolves register offsets, verifies the `QEMU` signature, reads revision, creates `rev`, reads the firmware file directory, allocates one sysfs entry per file, adds metadata attributes plus a raw binary file, and best-effort builds a path-like symlink tree under `by_name`.

Reads acquire the ACPI global lock when available, serialize device access with `fw_cfg_dev_lock`, select the fw_cfg key with endian handling, skip to the requested offset by reading bytes, and copy the requested data. Optional VMCORE_INFO support writes guest vmcoreinfo through the DMA register path when supported.

## State And Persistence
The driver uses global singleton state for the one system fw_cfg device. Sysfs kobjects and the entry cache persist while the module/device is active. It does not persist host data; it reflects QEMU-provided firmware blobs and optionally writes vmcoreinfo to fw_cfg for crash dump support.

## Dependencies And Integration Points
It integrates with platform devices from ACPI, OF, or command line; sysfs/kobject infrastructure; firmware kobject; IO/MMIO mapping; ACPI global locking; crash dump/vmcoreinfo; and QEMU's fw_cfg UAPI structs. It is architecture-sensitive because default register offsets differ by architecture.

## Risks
The device is singleton and uses global state, so a second probe returns `-EBUSY`. Firmware-provided names may collide or contain awkward path components; symlink creation is best effort. Raw reads use byte skipping for offsets and can be slow. Command-line parsing must avoid resource overflow and malformed offset combinations. DMA support assumes physical addresses are acceptable because fw_cfg does not need IOMMU protection.

## Test Signals
On QEMU, `/sys/firmware/qemu_fw_cfg/rev`, `by_key/*/{size,key,name,raw}`, and `by_name` links should appear. Signature verification should reject non-QEMU devices. Reads of known fw_cfg blobs, command-line `ioport`/`mmio` registration, and vmcoreinfo write warnings are key validation signals.
