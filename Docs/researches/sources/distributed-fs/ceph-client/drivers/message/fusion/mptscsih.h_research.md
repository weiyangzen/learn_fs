# sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.h

## Purpose
`mptscsih.h` is the shared interface for the Fusion MPT generic SCSI host layer. It defines scan/domain-validation completion flags, internal command flags, queue-depth defaults, setup defaults, the `INTERNAL_CMD` request descriptor, and exported function prototypes used by transport-specific Fusion drivers such as `mptsas.c`.

## Important APIs, types, and functions
- Scan/DV result flags: `MPT_SCANDV_GOOD`, `MPT_SCANDV_DID_RESET`, `MPT_SCANDV_SENSE`, `MPT_SCANDV_SOME_ERROR`, `MPT_SCANDV_SELECTION_TIMEOUT`, `MPT_SCANDV_ISSUE_SENSE`, `MPT_SCANDV_FALLBACK`, and `MPT_SCANDV_BUSY`.
- Internal command flags: `MPT_ICFLAG_BUF_CAP`, `MPT_ICFLAG_ECHO`, `MPT_ICFLAG_EBOS`, `MPT_ICFLAG_PHYS_DISK`, `MPT_ICFLAG_TAGGED_CMD`, `MPT_ICFLAG_DID_RESET`, and `MPT_ICFLAG_RESERVED`.
- Queue constants: `MPT_SCSI_CMD_PER_DEV_HIGH`, `MPT_SCSI_CMD_PER_DEV_LOW`, `MPT_SCSI_CMD_PER_LUN`, and `MPT_SCSI_MAX_SECTORS`.
- Setup defaults: `MPTSCSIH_DOMAIN_VALIDATION`, `MPTSCSIH_MAX_WIDTH`, `MPTSCSIH_MIN_SYNC`, `MPTSCSIH_SAF_TE`, and `MPTSCSIH_PT_CLEAR`.
- `INTERNAL_CMD` describes internally generated SCSI CDBs: data pointer/DMA address, transfer size, opcode, firmware channel/id, LUN, flags, physical disk number, and reserved bytes.
- Exported lifecycle hooks: remove, shutdown, optional suspend/resume, info/show-info, host attribute groups.
- Exported I/O and SCSI midlayer hooks: `mptscsih_qcmd`, `mptscsih_sdev_configure`, `mptscsih_sdev_destroy`, `mptscsih_change_queue_depth`, `mptscsih_bios_param`, and completion callbacks.
- Exported error/reset hooks: task management issue/complete, abort, device reset, bus reset, host reset, IOC reset, and response-code logging.
- Exported RAID/lookup helpers: physical disk detection, RAID id-to-number mapping, SCSI lookup access, and running command flush.

## Control flow
Protocol drivers include this header to wire their `scsi_host_template` and MPT callback registration to the generic SCSI implementation. Normal queuecommand calls enter `mptscsih_qcmd()`, completions enter `mptscsih_io_done()`, error handlers call the exported reset routines, and scan/domain-validation/internal command flows use `INTERNAL_CMD` plus `mptscsih_scandv_complete()`.

## State and persistence behavior
The header does not define persistent storage. It describes transient command and status state consumed by `mptscsih.c`: internal command payloads, scan/DV status flags, command flags, and exported hooks that operate on adapter and SCSI host state. The setup constants are compile-time/default policy values rather than persisted configuration.

## Dependencies and integration points
The prototypes rely on Fusion MPT types (`MPT_ADAPTER`, `MPT_SCSI_HOST`, `MPT_FRAME_HDR`), Linux PCI power-management types, SCSI host/device/command types, block geometry types, and sysfs attribute group definitions. The header is the integration contract between generic Fusion SCSI services and specific Fusion transport modules.

## Risks and edge cases
- `#endif` for the include guard appears before the `INTERNAL_CMD` typedef and extern declarations, so repeated inclusion protection only covers the constants. This reflects the local source but is unusual and could cause duplicate declarations if included multiple times in one translation unit.
- Many exported APIs assume valid `VirtDevice`/`VirtTarget` hostdata and initialized adapter fields; the header cannot express those preconditions.
- Queue and sector constants are shared policy knobs. Changing them can alter midlayer queueing, chain-buffer pressure, and device behavior across all transport drivers.
- `INTERNAL_CMD::physDiskNum` is `u8` while comments and code use `-1` sentinel assignments; consumers rely on unsigned wraparound semantics.

## Test signals
- Compile all Fusion protocol drivers that include this header to catch prototype or include-guard regressions.
- Exercise normal I/O, exported completion callbacks, error handlers, queue-depth changes, RAID helper paths, and internal command paths from at least one transport driver.
- Static analysis should flag the unusual include-guard layout, unsigned sentinel use, and assumptions around external type availability.
