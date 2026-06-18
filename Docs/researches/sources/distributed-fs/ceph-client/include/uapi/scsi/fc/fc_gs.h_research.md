# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_gs.h

## Purpose
`fc_gs.h` defines Fibre Channel Generic Services Common Transport (FC-CT) header and generic accept/reject values. It is the shared wrapper for directory/name service and other fabric service transactions.

## Important APIs, Types, and Constants
`struct fc_ct_hdr` is the 16-byte FC-CT header with revision, originator ID, service type/subtype, command/response code, maximum/residual size, reject reason, explanation, and vendor byte fields. `FC_CT_HDR_LEN` documents expected size. `enum fc_ct_rev` currently defines revision `FC_CT_REV`.

`enum fc_ct_fs_type` names fabric service types including alias, management, time, and directory service. `enum fc_ct_cmd` defines generic reject and accept response codes (`FC_FS_RJT`, `FC_FS_ACC`). `enum fc_ct_reason` and `enum fc_ct_explan` describe reject reason and explanation values shared by service subprotocols.

## Control Flow and State
There is no executable code. FC-CT control flow is request/response dispatch: a consumer sends a frame with `FC_TYPE_CT`, parses `ct_fs_type` and `ct_fs_subtype` to select a service, interprets `ct_cmd` either as a service command or as `FC_FS_ACC`/`FC_FS_RJT`, and uses reason/explanation fields when rejected.

## State and Persistence Behavior
The header carries per-transaction state only: requested service, command, sizing, and reject metadata. Persistent fabric database state is managed by the switch/name server and by FC transport registration logic.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Name-service definitions in `fc_ns.h` rely on this CT framework, and FC BSG CT passthrough uses the first CT preamble words described here.

## Risks and Test Signals
Risks are endian conversion errors for `ct_cmd`/`ct_mr_size`, service-type/subtype mismatch, and accepting malformed short CT payloads. Test signals include known-good CT accept/reject payload decode tests, compile-time size checks, and BSG CT passthrough tests against a name server or mocked fabric service.
