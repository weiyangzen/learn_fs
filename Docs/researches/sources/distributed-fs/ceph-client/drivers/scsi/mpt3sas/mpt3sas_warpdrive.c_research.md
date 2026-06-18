# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_warpdrive.c

Purpose: implements WarpDrive direct I/O support for eligible MPT RAID0 volumes. It determines whether a RAID volume can bypass the virtual volume handle and rewrites read/write CDBs to target the correct physical disk member when an I/O falls wholly within one stripe.

Important APIs/types/functions: `mpt3sas_get_num_volumes()` enumerates RAID volume Page 1 handles. `_warpdrive_disable_ddio()` clears `direct_io_enabled` across known RAID devices. `mpt3sas_init_warpdrive_properties()` validates a `_raid_device` and records member handles, stripe/block exponents, maximum LBA, and direct-I/O eligibility. `mpt3sas_setup_direct_io()` maps READ/WRITE(10/16) volume LBAs to member LBAs and sets `scsiio_tracker.direct_io`.

Control flow: initialization returns early unless `ioc->is_warpdrive` is true, physical disks are hidden, exactly one volume exists, and physical disk count/configuration can be read. It rejects volumes with too many members, member LBAs wider than 32 bits, non-RAID0 type, or invalid stripe/block sizes. During command setup, only READ/WRITE(10/16) commands are considered; the code computes I/O size in volume blocks, rejects out-of-range or cross-stripe requests, selects the member with `sector_div()`, updates `DevHandle`, rewrites the CDB LBA, and marks direct I/O.

State and persistence: computed direct-I/O state lives in `_raid_device` fields such as `direct_io_enabled`, `pd_handle[]`, `stripe_exponent`, `block_exponent`, `max_lba`, `stripe_sz`, and `block_sz`. No persistent controller state is written; it is runtime optimization metadata derived from firmware config pages.

Dependencies and integration points: depends on MPT RAID volume and physical disk configuration helpers, SCSI command helpers, unaligned endian accessors, and command-private `scsiio_tracker`. It integrates with the SCSI I/O build path that supplies `Mpi25SCSIIORequest_t` before request submission.

Risks and test signals: correctness depends on stripe math, block exponent derivation, member handle ordering, and CDB rewrite safety. `find_first_bit()` only proves a bit exists, not that stripe/block sizes are powers of two; non-power-of-two values would produce questionable exponents. Tests should cover single and multiple volume enumeration, hidden/exposed disk mode, RAID0 versus non-RAID0, cross-stripe rejection, READ/WRITE(10/16) LBA rewrite, maximum-LBA rejection, and member handle failure cleanup.
