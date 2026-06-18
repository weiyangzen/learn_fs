# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.h

## Purpose
`efc_els.h` declares the ELS/CT/BLS discovery I/O object and all protocol send helpers used by libefc state machines.

## Important APIs, Types, And Functions
`struct efc_els_io_req` wraps list/refcount state, node ownership, callback pointer, retry budget, delayed retry timer, display name, and `struct efc_disc_io`. The header defines `EFC_STATUS_INVALID`, `EFC_ELS_IO_POOL_SZ`, the hardware SRRS callback typedef, ELS allocation/free helpers, command send helpers, response send helpers, CT response, BLS accept/reject, and list-empty query.

## Control Flow And State
The header shows that ELS I/O is reference-counted, node-owned, linked for shutdown tracking, and completed asynchronously through callbacks. State machines call send helpers and later receive events from `efc_els_io_cleanup`.

## Dependencies And Integration Points
It depends on `struct efc_node`, `struct efc_disc_io`, FC frame headers, CT headers, and SLI/BLS parameter types via included umbrella headers. It is the protocol construction interface for device, fabric, and name-server code.

## Risks And Test Signals
Risks include calling send helpers after `node->els_io_enabled` is false and mismatched event counters for request vs response I/O. Test signals include pool exhaustion, timer cancellation/expiry, all declared ELS helper paths, and shutdown that waits for `els_ios_list` to become empty.
