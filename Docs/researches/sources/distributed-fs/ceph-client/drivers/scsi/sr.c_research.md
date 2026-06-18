## sources/distributed-fs/ceph-client/drivers/scsi/sr.c

### Purpose
Implements the Linux SCSI CD-ROM block driver core. It registers the `sr` SCSI driver and SCSI CD-ROM block major, probes `TYPE_ROM` and `TYPE_WORM` devices, translates block requests into SCSI READ_10/WRITE_10 commands, integrates with the generic CD-ROM layer, handles media-change events, and manages disk capacity/sector-size revalidation.

### Important APIs and Functions
- `sr_template` is the `struct scsi_driver` with probe/remove, request initialization, completion, and runtime PM hooks.
- `sr_dops` is the `struct cdrom_device_ops` exported to the generic CD-ROM layer, delegating tray, lock, audio, packet, speed, status, multisession, MCN, and CDDA reads.
- `sr_probe()` allocates `struct scsi_cd`, `gendisk`, minor numbers, CD-ROM registration, runtime PM setup, capability probing, vendor initialization, and disk publication.
- `sr_init_command()` validates request/device/media state, allocates SCSI SG tables, maps block requests to READ_10 or WRITE_10, enforces hardware block alignment, caps transfer length to 16 bits, and fills command fields.
- `sr_done()` computes good bytes after SCSI completion, including partial-success handling for medium errors, volume overflow, illegal request with valid information, recovered errors, and late capacity trimming.
- `sr_check_events()` reconciles GET_EVENT_STATUS_NOTIFICATION, `sdev->changed`, and TEST_UNIT_READY to report media change/eject events robustly.
- `get_sectorsize()` issues READ_CAPACITY and normalizes 0/2340/2352-byte reports to 2048 while converting 2048-byte capacity to 512-byte sectors.
- `get_capabilities()` reads MMC mode page 0x2a, sets CD-ROM capability masks, speed, READ_CD support, audio support, writer/DVD/RAM flags, eject/changer support, and fallback SCSI-1 behavior.

### Control Flow and State
Probe claims a minor in `sr_index_bits`, guesses 2048-byte sectors, probes capabilities, initializes vendor logic, registers with the CD-ROM layer, revalidates media, and adds the disk. Open gets a SCSI device reference, resumes runtime PM, checks media changes, revalidates on change, then delegates to `cdrom_open()`. Normal block I/O flows through `sr_init_command()` into the SCSI midlayer and returns through `sr_done()`. Media event checks first use GET_EVENT, then TUR when clearing media change; repeated disagreement causes `ignore_get_event` so future checks rely on TUR. Remove deletes the gendisk and relies on disk release to unregister CD-ROM state and free `Scsi_CD`.

### State and Persistence Behavior
Persistent per-device state lives in `struct scsi_cd`: capacity, media presence, READ_CD capability, media-event mismatch counters, CD-ROM info, mutex, and disk pointer. `sdev->sector_size`, disk capacity, CD-ROM capability mask, and `sdev->changed` are updated across opens/revalidations. Runtime PM suspend refuses if media is present.

### Dependencies and Integration Points
The file integrates the block layer, blk-mq SCSI request allocation, SCSI device/error handling, runtime PM, generic CD-ROM core, and vendor/ioctl helpers from `sr.h`, `sr_ioctl.c`, and `sr_vendor.c`. The Makefile links `sr_mod` from `sr.o`, `sr_ioctl.o`, and `sr_vendor.o`.

### Risks and Test Signals
Risk centers on media-change races, GET_EVENT/TUR disagreement, block-size alignment, capacity updates near bad media, and ioctl fallback to raw SCSI. Tests should cover probe/remove, open with changed/no media, READ_CAPACITY sector sizes 512/2048/2340/2352/unsupported, read/write command generation, medium error partial completion, CD-ROM event polling, runtime suspend rejection with media, and generic packet delegation.
