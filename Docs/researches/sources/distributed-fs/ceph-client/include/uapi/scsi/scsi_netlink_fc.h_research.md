# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_netlink_fc.h

## Purpose
`scsi_netlink_fc.h` defines Fibre Channel transport-specific netlink event messages layered on the generic SCSI netlink ABI. It currently exposes asynchronous FC events from kernel to userspace.

## Important APIs, Types, and Constants
`FC_NL_ASYNC_EVENT` is the FC transport message type. `FC_NL_MSGALIGN()` mirrors generic 8-byte alignment. `struct fc_nl_event` embeds `struct scsi_nl_hdr` as the first member, then carries seconds, vendor ID, host number, data length, event number, event code, and either a single `event_data` word or flexible byte payload.

## Control Flow and State
Kernel FC transport code fills the embedded SCSI netlink header with transport `SCSI_NL_TRANSPORT_FC` and msgtype `FC_NL_ASYNC_EVENT`, appends `fc_nl_event`, and multicasts on the FC event group. Userspace first validates the generic header, then interprets FC event fields and optional vendor payload using `event_datalen`.

## State and Persistence Behavior
Events are transient notifications. `seconds`, `event_num`, and `event_code` snapshot a transport event; vendor payload interpretation is external. No persistent state is stored by the header.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<scsi/scsi_netlink.h>`. Integration points are FC transport class event emitters, netlink listeners, vendor diagnostics, and userspace daemons that react to FC topology or link events.

## Risks and Test Signals
Risks are flexible-array length validation, header-not-first regressions, vendor ID formatting mismatches, and interpreting `event_data` when `event_datalen` indicates a byte payload. Tests should verify struct alignment, first-member embedding, valid/invalid event length parsing, and multicast receive behavior for FC async events.
