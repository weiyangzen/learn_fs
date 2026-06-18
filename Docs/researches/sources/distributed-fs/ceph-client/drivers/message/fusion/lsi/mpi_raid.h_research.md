<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_raid.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_raid.h

## Purpose

`mpi_raid.h` defines the MPI Integrated RAID control ABI: RAID action requests/replies, volume progress indicators, SCSI IO passthrough to physical disks, and mailbox request/reply formats. It is used by Fusion management paths to create, delete, enable, disable, activate, scrub, resync, update, and inspect integrated RAID objects.

## Important APIs, Types, and Definitions

- `MSG_RAID_ACTION_REQUEST` carries an `Action`, volume ID/bus, physical disk number, message context, action data word, and optional action-data SGE.
- RAID action constants include status, indicator structure, create/delete/disable/enable volume, quiesce/enable physical IO, change volume or physical disk settings, offline/online/fail/replace physical disk, create/delete physical disk, activate/inactivate volume, set resync/data scrub rates, device firmware update mode, and set volume name.
- `ActionDataWord` flags control create behavior (`DO_NOT_SYNC`, `LOW_LEVEL_INIT`), delete behavior (keep/delete physical disks, keep/zero LBA0), disable full rebuild, activate all/inactivate all, resync/scrub rate masks, and device firmware update timeout.
- `MSG_RAID_ACTION_REPLY` returns action status, IOC status/log info, volume status, and action data.
- `MPI_RAID_VOL_INDICATOR` reports total blocks and blocks remaining for long-running operations.
- `MSG_SCSI_IO_RAID_PT_REQUEST` and reply provide SCSI passthrough to a physical disk, with CDB, LUN, control, sense address, data length, SGL, SCSI status/state, transfer count, sense count, and response info.
- `MSG_MAILBOX_REQUEST` and `MSG_MAILBOX_REPLY` provide a 10-byte command mailbox with SGL and mailbox status.

## Control Flow

Management code fills `MSG_RAID_ACTION_REQUEST` with a specific action, object identifiers, and optional DMA-backed action data, then waits for `MSG_RAID_ACTION_REPLY`. For actions returning progress, callers interpret `ActionData` or fetch an indicator structure. Physical disk passthrough follows the same shape as initiator SCSI IO: build CDB/control/sense/SGL fields, post to firmware, and translate reply SCSI/IOC status. Mailbox requests are a lower-level command path for firmware-defined RAID management operations.

## State and Persistence Behavior

Unlike many MPI headers, these messages can alter persistent storage state. Creating/deleting volumes and physical disks, zeroing LBA0, changing settings, setting volume names, setting resync/scrub rates, activation/inactivation, and firmware update mode can change metadata on disks or persistent firmware configuration. Replies report current volume and action status, but durable state is also surfaced by RAID config pages and RAID/IR events in `mpi_ioc.h`.

## Dependencies and Integration Points

The header depends on base MPI types and SGE unions. It is included by `mptbase.h`; `mptbase.c` decodes RAID events and status text, while `mptsas.c` consumes integrated RAID and IR2 events, topology state, and physical disk data. `mpi_cnfg.h` provides RAID Volume and RAID PhysDisk config pages that complement these action messages. `mpi_log_sas.h` provides IR log codes for failures returned in `IOCLogInfo`.

## Risks and Edge Cases

RAID actions are high impact and can destroy data, especially delete volume, delete physical disk, fail/offline disk, and zero LBA0 flags. Action data SGE length and format are action-specific and not self-described here. The passthrough path can send arbitrary CDBs to member disks, bypassing normal volume semantics. Status fields must distinguish action-level status from IOC transport status and SCSI status. Persistent action completion can be asynchronous, so a successful reply may not mean resync, scrub, rebuild, or firmware update has finished.

## Test Signals

Validation should cover harmless status/indicator actions first, then controlled create/delete/change operations on disposable media or simulation. Tests should verify action status mapping, rate-mask packing, device firmware update timeout packing, passthrough sense/status handling, and mailbox status handling. Runtime signals include expected RAID events, RAID config page changes, volume status transitions, and clear error logs for failed or invalid actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_raid.h -->
