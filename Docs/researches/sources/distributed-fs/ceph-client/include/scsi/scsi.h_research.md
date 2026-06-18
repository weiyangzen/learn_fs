<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi.h

## Purpose
This is a public SCSI initiator header collecting common mid-layer constants, timeout defaults, mode-select structures, well-known LUN helpers, disposition and queuecommand statuses, result-byte helpers, SCSI levels, inquiry qualifiers, ioctls, and good/check-condition status predicates.

## Important APIs, Types, And Functions
It exports `enum scsi_timeouts`, `struct ccs_modesel_head`, well-known LUN constants, `scsi_is_wlun()`, `scsi_status_is_check_condition()`, `enum scsi_disposition`, `enum scsi_qc_status`, `status_byte()`, `host_byte()`, sense byte macros, default long command timeouts, `IDENTIFY()`, SCSI level constants, legacy ioctl constants, and `scsi_status_is_good()`.

## Control Flow
The only executable logic is inline status classification. `scsi_status_is_check_condition()` rejects negative results, masks reserved bit 0, and compares against `SAM_STAT_CHECK_CONDITION`. `scsi_status_is_good()` rejects negative results and `DID_NO_CONNECT`, masks bit 0, then accepts GOOD, CONDITION_MET, obsolete intermediate successes, and COMMAND_TERMINATED for compatibility.

## State And Persistence
No state is owned here. Constants define ABI and mid-layer interpretation of packed result integers.

## Dependencies And Integration Points
It includes `scsi_common.h`, `scsi_proto.h`, and `scsi_status.h`. It is included broadly by drivers, transports, generic SG/ioctl code, and mid-layer error handling.

## Risks
Result-byte packing is an ABI convention; mixing shifted SG status values with SAM status values causes misclassification. Legacy ioctl values overlap with cdrom ranges and must stay stable. `scsi_status_is_good()` intentionally accepts obsolete statuses, which can surprise newer protocol logic.

## Test Signals
Unit-style status tests for negative values, DID_NO_CONNECT, check condition, obsolete intermediate status, and command terminated; ioctl ABI compile checks; and well-known LUN detection for ordinary and `0xc100`-based LUNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi.h -->
