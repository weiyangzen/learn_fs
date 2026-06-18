# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_msgs.h

## Purpose

`cm_msgs.h` provides small inline helpers and constants for interpreting and formatting InfiniBand CM MAD fields. It centralizes QP type encoding/decoding and REP QPN extraction over the packed IBTA message structures.

## Important APIs, Types, And Functions

- `IB_CM_CLASS_VERSION` defines CM class version 2, matching IB specification 1.2 behavior used by `cm.c`.
- `cm_req_get_qp_type()` decodes the REQ transport service type and extended transport type into `IB_QPT_RC`, `IB_QPT_UC`, or `IB_QPT_XRC_TGT`.
- `cm_req_set_qp_type()` writes REQ transport fields for UC, XRC initiator, or default RC.
- `enum cm_msg_response` identifies whether a MRA or REJ is responding to REQ, REP, or another message class.
- `cm_rep_get_qpn()` returns the local QPN field for normal QPs or the local EE context number for XRC initiator flows.

## Control Flow

The helpers are inline switch/field-access routines. They use `IBA_GET()` and `IBA_SET()` macros from the IBTA field definitions and keep values in the network-byte-order conventions expected by CM message structs.

## State And Persistence

No state is stored. The header only transforms fields in caller-owned CM message buffers.

## Dependencies And Integration Points

The header depends on `<rdma/ibta_vol1_c12.h>`, `<rdma/ib_mad.h>`, and `<rdma/ib_cm.h>`. `cm.c` uses it to format REQs, decode incoming REQs, decide QP behavior, and parse REP QPN/EECN fields.

## Risks

- Unsupported or malformed transport encodings return 0, so callers must treat that as invalid.
- XRC initiator/target naming is direction-sensitive: REQ encoding for `IB_QPT_XRC_INI` is later decoded on the peer as `IB_QPT_XRC_TGT`.
- REP QPN extraction must match QP type or XRC connections can use the wrong endpoint identifier.

## Test Signals

Signals include unit-style validation of REQ transport field encodings for RC, UC, and XRC; malformed transport type rejection by CM request handling; and REP parsing tests for normal QP versus XRC EECN fields.
