## sources/distributed-fs/ceph-client/drivers/scsi/sr_ioctl.c

### Purpose
Implements the generic CD-ROM operation callbacks for the SCSI CD-ROM driver. It wraps SCSI packet commands for TOC, audio playback, tray/door control, drive/disc status, multisession metadata, media catalog number, speed selection, generic packet execution, raw sector reads, and optional XA detection.

### Important APIs and Functions
- `sr_do_ioctl()` is the central packet executor. It waits out SCSI error handling, calls `scsi_execute_cmd()`, interprets sense keys, retries UNIT_ATTENTION and becoming-ready states, marks `SDev->changed`, and maps errors to Linux/CD-ROM return codes.
- `sr_read_tochdr()` and `sr_read_tocentry()` issue READ_TOC/PMA/ATIP and decode track/session metadata.
- `sr_play_trkind()` tries PLAY_AUDIO_TI and falls back to `sr_fake_playtrkind()` for ATAPI-like devices by translating track/index ranges to PLAY_AUDIO_MSF.
- `sr_tray_move()`, `sr_lock_door()`, `sr_drive_status()`, `sr_disk_status()`, `sr_get_last_session()`, `sr_get_mcn()`, `sr_reset()`, `sr_select_speed()`, and `sr_audio_ioctl()` implement `cdrom_device_ops`.
- `sr_read_cd()` and `sr_read_sector()` read non-2048-byte sector formats using READ_CD or by temporarily switching block length through `sr_set_blocklength()`.
- `sr_is_xa()` optionally probes XA mode by raw-reading a sector when module parameter `xa_test` is enabled.

### Control Flow and State
Most callbacks build a `struct packet_command`, set command bytes, buffer, length, direction, and timeout, then delegate to `sr_do_ioctl()`. `sr_do_ioctl()` owns retry flow: UNIT_ATTENTION sets media changed and may retry up to 10 times; NOT_READY with ASC/ASCQ 04/01 sleeps two seconds and retries; invalid opcode maps to `-EDRIVE_CANT_DO_THIS`. `sr_read_sector()` remembers READ_CD support in `cd->readcd_known` and falls back to MODE_SELECT plus READ_10 when necessary.

### State and Persistence Behavior
The file updates `SDev->changed`, `cd->readcd_known`, and, through vendor helpers, `cd->device->sector_size`. It consumes `cd->ms_offset`, `cd->xa_flag`, and `cd->readcd_cdda` set elsewhere. `xa_test` is a module parameter and off by default because the probe can trigger firmware bugs.

### Dependencies and Integration Points
The implementation sits between generic `cdrom.c` operations and the SCSI midlayer. It depends on `sr.h`, SCSI sense helpers, SCSI ioctl interfaces, CD-ROM UAPI structs, user access helpers, and `sr_vendor.c` for block-length switching.

### Risks and Test Signals
Risk includes long retry sleeps in ioctl context, fragile sense-key mapping, vendor firmware that hangs on XA/raw reads, and temporary block-size switching failure. Tests should cover TOC decoding in LBA/MSF modes, no-media and becoming-ready behavior, PLAY_AUDIO_TI fallback, tray/door commands, speed clamping, READ_CD unsupported fallback, XA disabled/enabled paths, and permission-gated raw packet handling through `sr.c`.
