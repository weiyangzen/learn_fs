## sources/distributed-fs/ceph-client/drivers/scsi/sr.h

### Purpose
Shared private header for the SCSI CD-ROM driver. It defines the `Scsi_CD` per-device structure, common timeouts/retry counts, logging helper, and cross-file prototypes used by `sr.c`, `sr_ioctl.c`, and `sr_vendor.c`.

### Important APIs, Types, and Constants
- `MAX_RETRIES`, `SR_TIMEOUT`, and `IOCTL_TIMEOUT` define default command retry and timeout policy.
- `typedef struct scsi_cd Scsi_CD` stores capacity, `scsi_device`, vendor code, multisession offset, XA/READ_CD/media flags, GET_EVENT/TUR mismatch state, `cdrom_device_info`, lock, and `gendisk`.
- `sr_printk()` prefixes messages with SCSI device and CD-ROM name.
- Prototypes expose ioctl, CD-ROM operation, audio, XA, vendor initialization, media check, and block-length switching helpers.

### Control Flow and State
This header has no executable flow, but it defines the state that carries across probe, open, media checks, block I/O, ioctl handling, and vendor multisession detection. Bitfields track capability and event behavior compactly.

### Dependencies and Integration Points
It depends on the mutex type and forward-declares `struct scsi_device`. It is the internal contract between the three `sr_mod` compilation units.

### Risks and Test Signals
Because many flags are bitfields, additions need care around type, initialization, and concurrency expectations. Media-event state is documented as protected by block layer exclusion, so tests should stress repeated event clearing/open paths and ensure no stale `changed` or `ignore_get_event` behavior leaks across media changes.
