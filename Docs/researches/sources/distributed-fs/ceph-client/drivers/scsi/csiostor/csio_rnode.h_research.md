# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.h

## Purpose
`csio_rnode.h` defines the remote FCoE node interface. It names rnode state-machine events, statistics, role flags, the `struct csio_rnode` layout, identity/access macros, and public functions for lookup, confirmation, firmware event handling, registration, unregistration, and device-loss handling.

## Important APIs, Types, and Constants
- `enum csio_rn_ev` includes login, PRLI, received PLOGI/PRLI/LOGO/PRLO, down, close, and name-missing events.
- `struct csio_rnode_stats` tracks error, invalid/nomem errors, unexpected/dropped events, firmware event counts, state-machine event counts, and LUN/target reset stats.
- Role flags: `CSIO_RNFR_INITIATOR`, `CSIO_RNFR_TARGET`, `CSIO_RNFR_FABRIC`, `CSIO_RNFR_NS`, and `CSIO_RNFR_NPORT`.
- `struct csio_rnode` stores state-machine linkage, owning lnode, firmware flowid, pending host completion queue, FC identifiers, FCP flags, current/previous event, role, firmware rdev entry pointer, service parameters, FC transport rport attributes, and stats.
- Access macros expose flowid, WWPN, WWNN, and owning lnode.
- Public APIs include readiness/state string helpers, port-ID lookup, rnode confirmation from firmware entry, firmware event handling, put/free, FC transport register/unregister, and device-loss handling.

## Control Flow and State
Like lnodes, rnodes embed `struct csio_sm` as the first field so they can be state-machine objects and list nodes. They are owned by a single lnode and linked into that lnode's `rnhead`. Firmware flow IDs and FC WWNs/NPort IDs are used together to reconcile relogin and changed-session cases. Role flags determine whether the rnode becomes a SCSI target, fabric object, name server, initiator, or generic NPort.

## Dependencies and Integration Points
The header includes `csio_defs.h` and depends on types from firmware storage APIs, FC transport, and lnode definitions through including users. It is consumed by lnode, SCSI, attribute, and transport integration code.

## Risks and Edge Cases
- `stats.n_evt_fw` is sized to `PROTO_ERR_IMPL_LOGO + 1`; firmware event values must be validated before indexing.
- `host_cmpl_q` must be drained before `csio_rnode_exit()`; the implementation asserts this.
- The public `csio_reg_rnode()`/`csio_unreg_rnode()` functions interact with FC transport and must tolerate repeated or out-of-order firmware events.
- `rdev_entry` points into firmware event payload ownership; lifetime assumptions are enforced by current event processing and should not be extended casually.

## Test Signals
Validation should include state transitions to ready/offline/disappeared/uninit, state string output, lookup by NPort ID, flowid/WWPN confirmation behavior, role flag mapping, FC rport registration side effects, and device-loss cleanup. SCSI reset counters and event stats provide additional observability during error handling tests.
