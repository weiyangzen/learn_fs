<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif_bsg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif_bsg.h

## Purpose

`qla_edif_bsg.h` defines the userspace BSG ABI for qla2xxx EDIF. It specifies vendor subcommands, authentication ELS request/reply envelopes, application registration messages, FC session info/stat replies, SA update input, doorbell event payloads, SA completion AENs, and authentication completion commands.

## Important APIs, Types, And Data

- `enum auth_els_sub_cmd` defines ELS operations: `SEND_ELS`, `SEND_ELS_REPLY`, and `PULL_ELS`.
- `struct extra_auth_els`, `qla_bsg_auth_els_request`, and `qla_bsg_auth_els_reply` extend generic FC BSG ELS requests/replies with exchange address, control flags, version, and reserved fields.
- `struct app_id` carries `EDIF_APP_ID` and ABI version. Most commands embed it so the driver can reject unknown applications.
- `struct app_start`, `app_start_reply`, and `app_stop` define app lifecycle messages.
- `struct app_pinfo_req`, `app_pinfo_reply`, and `app_pinfo` return per-port WWPN, port ID, remote type, remote online state, and EDIF auth state.
- `struct app_sinfo_req`, `app_stats_reply`, and `app_sinfo` return rekey and byte counters.
- `struct qla_sa_update_frame` is the userspace SA update/delete command, including flags, SA index hint field, salt, SPI, key bytes, WWNs, and port ID.
- `QL_VND_SC_*` constants define vendor subcommands dispatched by `qla_edif_app_mgmt()`.
- `struct edif_read_dbell`, `edif_app_dbell`, `edif_sa_update_aen`, `auth_complete_cmd`, and `aen_complete_cmd` define doorbell read, SA completion event, auth success/failure, and event-ack payloads.

## Control Flow

Userspace opens the FC BSG path and sends vendor commands identified by `QL_VND_SC_*`. The driver first validates `app_id`, then dispatches to the EDIF app management flow. `APP_START` activates doorbells; `READ_DBELL` either returns queued `edif_app_dbell` records or parks the BSG job until an event or timeout; `SA_UPDATE` installs or deletes keys in firmware; `AUTH_OK`/`AUTH_FAIL` resolves pending login authentication; `GET_FCINFO` and `GET_STATS` copy variable-length arrays back to userspace. Authentication ELS traffic uses the separate request/reply wrappers around FC BSG ELS commands.

## State And Persistence Behavior

This header only defines ABI data. Persistence is in the kernel objects that consume these messages and in firmware SA tables. Reserved arrays in most structures preserve ABI size and forward-compatibility room. Flexible arrays in `app_pinfo_reply` and `app_stats_reply` require the caller and driver to agree on `num_ports` and transfer lengths.

## Dependencies And Integration Points

The header depends on FC BSG request/reply types, `port_id_t`, endian definitions, and `WWN_SIZE`. It is consumed by `qla_edif.c` and by userspace EDIF authentication tooling. It must remain synchronized with command dispatch in `qla_edif_app_mgmt()` and payload copies in all EDIF BSG handlers.

## Risks And Edge Cases

- This is a UAPI-like contract even though it lives in the driver tree. Changing structure layout, packing, constants, or version semantics can break existing authentication applications.
- `app_pinfo_req.remote_pid` uses endian-conditional byte layout. Cross-architecture userspace/kernel expectations should be tested.
- Variable-length replies depend on userspace-provided counts and buffer sizes. The driver must avoid copying more elements than requested or returning uninitialized padding.
- `qla_sa_update_frame.fast_sa_index` is a 10-bit bitfield inside a packed structure, which can be fragile across compilers or ABI consumers if not mirrored exactly.
- Key length flags (`SAU_FLG_KEY128`/`SAU_FLG_KEY256`) and GMAC/delete flags are security-sensitive; ambiguous combinations need deterministic handling.

## Test Signals

ABI tests should assert structure sizes, offsets, packing, command numbers, auth-state values, and endian-specific port ID layout on little- and big-endian builds. Integration tests should send every vendor subcommand with valid and invalid `app_id`, short buffers, oversized reply buffers, zero-port and multi-port queries, SA update/delete variants, doorbell reads with empty and populated queues, and auth completion by both WWPN and D_ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif_bsg.h -->
