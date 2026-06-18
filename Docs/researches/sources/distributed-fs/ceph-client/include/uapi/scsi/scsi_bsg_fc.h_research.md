# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_fc.h

## Purpose
`scsi_bsg_fc.h` defines the Fibre Channel transport Block SCSI Generic (BSG) SG_IO v4 request and reply ABI. It lets privileged userspace issue FC host or remote-port management operations such as add/delete rport, ELS, CT, and vendor-specific commands through the SCSI transport BSG path.

## Important APIs, Types, and Constants
`FC_BSG_HST_*` and `FC_BSG_RPT_*` msgcodes identify host-class and rport-class operations, with `FC_BSG_CLS_MASK`, `FC_BSG_HST_MASK`, and `FC_BSG_RPT_MASK` for classification. Host request payloads are `struct fc_bsg_host_add_rport`, `fc_bsg_host_del_rport`, `fc_bsg_host_els`, `fc_bsg_host_ct`, and `fc_bsg_host_vendor`. Rport request payloads are `struct fc_bsg_rport_els` and `fc_bsg_rport_ct`.

`struct fc_bsg_request` is the packed SG_IO v4 command descriptor with a msgcode and unioned request data. `struct fc_bsg_reply` is the request-sense reply, with `result`, `reply_payload_rcv_len`, and unioned `vendor_reply` or `ctels_reply`. `struct fc_bsg_ctels_reply` records CT/ELS completion status and reject details with `FC_CTELS_STATUS_*` values.

## Control Flow and State
The userspace flow is: open the BSG device for an FC host or rport, populate an SG_IO v4 request whose request CDB is `struct fc_bsg_request`, attach request/reply payload buffers for the ELS/CT/vendor data, and inspect `struct fc_bsg_reply` after completion. Host operations may cause the driver to log in to or enumerate a remote port; CT/ELS operations may use existing rport context or transient host-level routing.

## State and Persistence Behavior
The header itself has no state, but commands can mutate FC transport state: add-rport can create/enumerate a remote port, del-rport can request logout/removal, and ELS/CT exchanges can change fabric or endpoint state depending on payload. `result < 0` means an errno-style failure with no per-msg reply data; nonnegative results use SCSI status semantics plus message-specific reply union data.

## Dependencies and Integration Points
It includes `<linux/types.h>` and depends conceptually on SG_IO v4 BSG, SCSI FC transport classes, `fc_els.h`, `fc_gs.h`, `fc_ns.h`, and vendor ID formatting from `scsi_netlink.h`. The `vendor_cmd[]` and `vendor_rsp[]` flexible arrays are integration points for vendor-specific tools.

## Risks and Test Signals
Risks include msgcode/class mismatch, failure to keep ELS command byte in sync with the first request payload byte, confusion between transport status and LS_RJT/CT reject payload status, and unsafe vendor flexible-array sizing. Tests should issue mocked or hardware-backed BSG ELS and CT requests, verify reject reporting in both payload and `rjt_data` modes, and validate add/delete rport behavior under login failures.
