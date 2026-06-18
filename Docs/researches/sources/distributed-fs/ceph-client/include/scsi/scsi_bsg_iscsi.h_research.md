<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_bsg_iscsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_bsg_iscsi.h

## Purpose
This header defines the iSCSI transport BSG SG_IO v4 message ABI shared by kernel and userspace. It currently models host-class vendor messages and their replies.

## Important APIs, Types, And Functions
Key constants are `ISCSI_DEFAULT_BSG_TIMEOUT`, class masks `ISCSI_BSG_CLS_MASK` and `ISCSI_BSG_HST_MASK`, and message code `ISCSI_BSG_HST_VENDOR`. ABI structures are `struct iscsi_bsg_host_vendor`, `struct iscsi_bsg_host_vendor_reply`, `struct iscsi_bsg_request`, and `struct iscsi_bsg_reply`.

## Control Flow
There is no executable control flow. BSG consumers inspect `msgcode`, dispatch host vendor messages, use `vendor_id` to identify the recipient format, and return either a negative errno-style result or a packed SCSI result plus reply payload length.

## State And Persistence
No persistent state is represented. Request and reply structures are transient user/kernel ABI payloads, with flexible vendor command/response arrays.

## Dependencies And Integration Points
The header includes `scsi/scsi.h` and references vendor-id formatting rules from `scsi_netlink.h`. It integrates with iSCSI transport `bsg_request` callbacks and SG_IO v4 user commands.

## Risks
The timeout comment says seconds while the macro multiplies by `HZ`, so callers must interpret it as jiffies in-kernel. Flexible arrays require bounds validation. Vendor payloads are opaque, so ABI validation must happen in the transport callback.

## Test Signals
Validate SG_IO v4 host-vendor dispatch, negative errno result handling, packed SCSI result handling, reply length accounting, timeout behavior, and rejection of unknown class/message codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_bsg_iscsi.h -->
