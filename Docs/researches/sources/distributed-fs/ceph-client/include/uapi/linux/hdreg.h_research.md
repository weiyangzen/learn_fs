<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdreg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hdreg.h

## Purpose
`hdreg.h` defines the legacy ATA/IDE ioctl ABI, command constants, taskfile layouts, geometry data, drive identity layout, and driver tuning controls historically used by IDE block devices and tools such as `hdparm`.

## Important APIs, types, and functions
The header exports taskfile header sizes, `ide_reg_valid_t`, `ide_task_request_t`, `ide_ioctl_request_t`, `struct hd_drive_cmd_hdr`, userspace task/HOB headers, `TASKFILE_*` data phase flags, many ATA command opcodes (`WIN_READ`, `WIN_WRITE`, `WIN_SMART`, `WIN_IDENTIFY`, `WIN_SETFEATURES`, security and SMART subcommands), `struct hd_geometry`, ioctl numbers `HDIO_GET*`, `HDIO_SET*`, `HDIO_DRIVE_TASKFILE`, `HDIO_DRIVE_TASK`, `HDIO_DRIVE_CMD`, bus states, and the large userspace `struct hd_driveid` matching ATA identify words.

## Control flow
User space issues ioctl calls against a block device to read geometry/identity, query or set IDE driver options, reset devices, or submit raw ATA taskfiles. For identity data, the kernel returns a 512-byte word layout decoded by tools. For raw commands, userspace supplies register-valid masks, taskfile bytes, data-phase direction, and buffers.

## State and persistence behavior
Some ioctls only sample state, while others alter drive or controller state: DMA, write cache, acoustic management, address mode, bus state, transfer mode, keep-settings, reset behavior, and raw ATA side effects. `hd_driveid` is a snapshot of device firmware identify data.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with legacy IDE, libata compatibility paths, block device ioctls, ATA/ATAPI firmware, and disk management tools.

## Risks and test signals
Risks include destructive raw ATA commands, 28/48-bit taskfile mistakes, user pointer/compat layout problems, obsolete ioctls that no longer apply to libata, endianness and word-swapping in identify strings, and security/SMART command misuse. Test signals include `hdparm -I` identity decoding, ioctl permission tests, compat ioctl tests, non-destructive SMART reads, invalid taskfile rejection, reset paths, and checks that obsolete commands fail safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdreg.h -->
