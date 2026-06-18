# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.h

## Purpose
`csio_lnode.h` defines the local FCoE node data model and public lnode API. It describes FCF records, local-node flags, FC transport events, lnode statistics, service parameters, the `struct csio_lnode` layout, logging/access macros, hardware-to-lnode notifications, and functions used by hardware, SCSI, FC transport, and rnode code.

## Important APIs, Types, and Constants
- Limits: `CSIO_FCOE_MAX_NPIV` and `CSIO_FCOE_MAX_RNODES`.
- Tunables: `csio_fcoe_rnodes` and `csio_fdmi_enable`.
- `struct csio_fcf_info` stores FCF priority, MAC/name/fabric identifiers, VLAN, FCoE size, FC-MAP, FKA, FCFI, login/capability bits, port ID, SPMA MAC, and kref.
- Lnode flags include `CSIO_LNF_FIPSUPP`, `CSIO_LNF_NPIVSUPP`, `CSIO_LNF_LINK_ENABLE`, and `CSIO_LNF_FDMI_ENABLE`.
- `enum csio_ln_fc_evt` names FC transport async events: link up/down, RSCN, and attribute update.
- `struct csio_lnode_stats` records link, error, event, rnode, FDMI, request, and byte counters.
- `struct csio_lnode_params` stores R_A_TOV, FCFI, and logging level.
- `struct csio_service_parms` stores common/class FC service parameters plus WWPN/WWNN and vendor version.
- `struct csio_lnode` owns state-machine state, hardware pointer, port/device IDs, FCF list/reference, management request, MAC/NPort ID/service parameters, firmware flow IDs, child/parent relationships, pending completions, rnode list, target scan counters, FC vport, FC host statistics, stats, and params.
- Public APIs include firmware event handling, readiness/state formatting, WWPN lookup, physical port stats, scan completion, hardware notifications, port disable/enable, FC async events, FDMI start, lnode start/stop/close/init/exit.

## Control Flow and State
The first field of `struct csio_lnode` is `struct csio_sm`, allowing generic state-machine helpers and list embedding. Physical lnodes are siblings on `hw->sln_head`; NPIV lnodes are children on a physical lnode's `cln_head`. `pln == NULL` identifies physical lnodes, while `pln != NULL` identifies NPIV. Flow IDs connect driver objects to firmware FCF/VNP state, and flags record whether link and FDMI operations are enabled.

## Dependencies and Integration Points
The header depends on Linux kref, timers, workqueue, SCSI FC ELS definitions, `csio_defs.h`, and `csio_hw.h`. It is included by initialization, mailbox, rnode, SCSI, attribute, and hardware event code. FC transport code consumes `struct fc_vport`, `struct fc_host_statistics`, and lnode WWN/service parameter fields.

## Risks and Edge Cases
- `struct csio_lnode` is embedded in `Scsi_Host.hostdata`; allocation and conversion must remain consistent with `csio_ln_to_shost()`.
- FCF info lifetime is shared through kref for NPIV children; parent teardown must coordinate with children.
- `stats.n_evt_fw` is indexed by firmware event causes up to `PROTO_ERR_IMPL_LOGO`; callers must bounds-check firmware causes.
- The macros `csio_ln_wwpn()` and `csio_ln_wwnn()` expose raw byte arrays; callers must preserve FC byte ordering.

## Test Signals
Tests should assert correct physical/NPIV classification, child count changes, FCF kref behavior, state string output, WWPN lookup across siblings/children, target scan counters, and FC host attribute updates after VNP read. Runtime counters should reflect link up/down, rnode allocation/free, FDMI errors, and dropped/unexpected firmware events.
