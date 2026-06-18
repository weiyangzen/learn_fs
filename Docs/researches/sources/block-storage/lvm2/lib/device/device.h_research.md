# File Research: sources/block-storage/lvm2/lib/device/device.h

## Purpose
Defines LVM2's in-memory device object model and the core device I/O API. This header is the shared contract for device cache entries, persistent device IDs, WWIDs, external device info, list wrappers, and low-level read/open/close operations.

## Main Data Structures
- Device flags describe open state, O_DIRECT state, cache membership, scan results, MD/NVMe identity, device-ID matching, and whether a preferred ID should be updated.
- `struct dev_ext` wraps optional external device information sources, currently `DEV_EXT_UDEV`.
- Device ID type constants cover sysfs WWID/serial, multipath UUID, MD UUID, loop backing file, crypt UUID, LV UUID, devname, SCSI WWID forms, and NVMe EUI64/NGUID/UUID.
- `struct dev_wwid` stores parsed SCSI/NVMe WWIDs on `dev->wwids`.
- `struct dev_id` stores one typed ID on `dev->ids`; `dev->id` points to the selected ID currently used.
- `struct dev_use` represents one devices-file entry, including matched device pointer, partition number, id type/name, devname, and PVID.
- `struct device` is the primary object containing aliases, IDs, WWIDs, dev_t, file descriptors, block sizes, cached size/end, flags, external info, duplicate preference reason, LV IDs, and PV PVID.
- `dev_io_reason_t` annotates I/O by purpose, such as signatures, labels, metadata headers/content, LV content, and logging.

## Exported API Surface
Declares external-info helpers, device size sequencing, direct block-size/size/readahead/discard operations, open/close variants, fd/name accessors, flush, multipath initialization, VPD/WWID parsing helpers, device list utilities, and `strdup_pvid`.

## Dependencies
Depends on libdevmapper list/pool/types and LVM `id.h`. Many APIs are implemented across the broader `lib/device` tree, not only in this group.

## Risk Notes
`struct device` is shared widely and uses pointer identity. Flags encode scan state and matching state that filters and label scanning depend on. ID strings and PVID buffers are handled with fixed LVM ID lengths, so allocation and termination rules matter.
