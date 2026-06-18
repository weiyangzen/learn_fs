# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_nt.c lines 9388-11634

## Scope

This chunk covers the tail of Samba's `source3` spoolss RPC server implementation in `srv_spoolss_nt.c`. The requested range starts at the final allocation check in `fill_print_processor1`, then includes helper and RPC entry points for print processor enumeration, monitor enumeration, job lookup, printer registry data/key access, print processor directory discovery, TCP/IP port monitor XcvData handling, a long block of unsupported spoolss RPC operations, and the spoolss endpoint init/shutdown wrappers.

The code is part of the server-side implementation behind the generated `spoolss` NDR compatibility glue included at the end of the file. Most exported functions follow the Samba RPC naming pattern `_spoolss_<Operation>` and receive a `struct pipes_struct *p` plus an operation-specific generated request/response structure.

## Purpose

This range exposes the spoolss capabilities that Samba chooses to emulate directly and marks many less-used Windows print spooler calls as unsupported. The implemented paths are pragmatic compatibility surfaces:

- report one print processor, `winprint`, and one processor data type, `RAW`;
- report the local and TCP/IP port monitors, with optional monitor DLL and environment metadata;
- translate spoolss job IDs to backend print-system jobs and return level 1 or level 2 job info;
- read, write, enumerate, and delete printer registry data and subkeys through Samba's winreg-backed printer store;
- return the print processor directory path while tolerating deployments without a `prnproc$` share;
- handle XcvData commands for the TCP/IP port monitor, notably `MonitorUI` and `AddPort`, by decoding Windows port data and dispatching to Samba's configured port hook;
- reject unsupported RPCs with `WERR_NOT_SUPPORTED` or HRESULT not-supported values, usually also setting `p->fault_state = DCERPC_FAULT_OP_RNG_ERROR`;
- migrate legacy printing TDB state before the generated spoolss endpoint initialization runs, and clean up spoolss state on shutdown.

## Important APIs, Types, And Functions

Enumeration and buffer helpers:

- `enumprintprocessors_level_1` allocates one `union spoolss_PrintProcessorInfo`, fills level 1 with `winprint`, and returns the count.
- `_spoolss_EnumPrintProcessors` validates the in/out buffer, validates `r->in.environment` with `get_short_archi`, supports only level 1, computes `needed` with `SPOOLSS_BUFFER_UNION_ARRAY`, and applies `SPOOLSS_BUFFER_OK` for Windows-compatible insufficient-buffer behavior.
- `enumprintprocdatatypes_level_1` and `_spoolss_EnumPrintProcessorDataTypes` expose only the `RAW` datatype and reject processor names other than `winprint`.
- `fill_monitor_1`, `fill_monitor_2`, `enumprintmonitors_level_1`, `enumprintmonitors_level_2`, and `_spoolss_EnumMonitors` expose `SPL_LOCAL_PORT` and `SPL_TCPIP_PORT`; level 2 also returns an architecture string from `lp_parm_const_string(..., "spoolss", "architecture", GLOBAL_SPOOLSS_ARCHITECTURE)` and DLL names `localmon.dll`/`tcpmon.dll`.

Job and printer data operations:

- `getjob_level_1` and `getjob_level_2` scan a `print_queue_struct` array for the backend `sysjob`, then call `fill_job_info1` or `fill_job_info2`. Level 2 retrieves a per-job devmode with `print_job_devmode` and falls back to `spoolss_create_default_devmode`.
- `_spoolss_GetJob` maps a spoolss handle to `snum`, loads `spoolss_PrinterInfo2` from winreg, maps spoolss job ID to backend job ID via `get_print_db_byname` and `jobid_to_sysjob_pdb`, queries the print queue with `print_queue_status`, and returns level 1 or 2 job info.
- `_spoolss_GetPrinterDataEx` serves server-handle values from `getprinterdata_printer_server` and printer-handle values from winreg. It has a special `SPOOL_PRINTERDATA_KEY`/`ChangeId` path that returns a `REG_DWORD` from `winreg_printer_get_changeid`.
- `_spoolss_SetPrinterDataEx` requires a printer handle with `PRINTER_ACCESS_ADMINISTER`, writes data through `winreg_set_printer_dataex`, handles comma-delimited OID suffixes in `value_name` by storing a companion value under `SPOOL_OID_KEY`, and updates the printer change ID.
- `_spoolss_DeletePrinterDataEx`, `_spoolss_DeletePrinterKey`, `_spoolss_EnumPrinterKey`, and `_spoolss_EnumPrinterDataEx` wrap winreg delete/enumeration helpers and keep the printer change ID current after mutations.

Directory and XcvData support:

- `getprintprocessordirectory_level_1` builds the processor directory path with `compose_spoolss_server_path(..., SPOOLSS_PRTPROCS_PATH, ...)`.
- `_spoolss_GetPrintProcessorDirectory` checks for the optional `prnproc$` share with `find_service`, but still returns a local path if that share is absent.
- `push_monitorui_buf`, `xcvtcp_monitorui`, `pull_port_data_1`, and `pull_port_data_2` marshal or unmarshal NDR structures used by monitor UI and port creation commands.
- `xcvtcp_addport` decodes `spoolss_PortData1` or `spoolss_PortData2`, builds either `socket://host:port/` for `PROTOCOL_RAWTCP_TYPE` or `lpr://host/queue` for `PROTOCOL_LPR_TYPE`, and calls `add_port_hook`.
- `xcvtcp_cmds`, `process_xcvtcp_command`, `xcvlocal_cmds`, and `process_xcvlocal_command` provide small command dispatch tables. Local port monitor management is compiled out via `#if 0`.
- `_spoolss_XcvData` validates a port monitor handle, requires `SERVER_ACCESS_ADMINISTER`, allocates the caller-requested output buffer, dispatches by monitor type, copies output data back, and sets `status_code` to zero on success.

Unsupported operations and lifecycle:

- `_spoolss_AddPrintProcessor` returns `WERR_OK` but intentionally ignores the add.
- `_spoolss_AddPort` returns `WERR_NOT_SUPPORTED`, matching the comment about Windows Server 2003 behavior.
- Many remaining operations, including printer driver package APIs, change notification APIs, per-machine connection APIs, job named property APIs, BIDI data, and numbered unknown operations, set `p->fault_state = DCERPC_FAULT_OP_RNG_ERROR` and return `WERR_NOT_SUPPORTED` or `HRES_ERROR_NOT_SUPPORTED`.
- `spoolss_init_server` runs `nt_printing_tdb_migrate(global_messaging_context())` before delegating to the generated `spoolss__op_init_server`.
- `spoolss_shutdown_server` calls `srv_spoolss_cleanup()` before delegating to `spoolss__op_shutdown_server`.

## Control Flow

The enumeration RPCs use a shared pattern:

1. Reject malformed `[in,out]` buffers where `buffer == NULL` but `offered != 0`.
2. Initialize output count, needed size, and info pointer to zero/null defaults.
3. Validate operation-specific selectors, such as architecture, print processor name, or level.
4. Allocate and fill a talloc-backed union array.
5. Compute the required NDR buffer size with `SPOOLSS_BUFFER_UNION_ARRAY`.
6. Return either success with copied data or `WERR_INSUFFICIENT_BUFFER` through `SPOOLSS_BUFFER_OK`, preserving Windows spoolss sizing semantics.

`_spoolss_GetJob` is a deeper pipeline:

1. Validate the caller buffer and printer handle.
2. Convert the handle to `snum` and service name.
3. Load printer metadata from the internal winreg path.
4. Open the print TDB for the service and translate the public spoolss job ID to a backend `sysjob`.
5. Query live queue status from the print backend.
6. Fill level-specific job data, including devmode fallback for level 2.
7. Free queue and printer metadata, size the returned union, and report buffer status.

The printer data/key functions split by handle and operation:

- `GetPrinterDataEx` handles server values locally, printer values via the winreg printer binding, and `ChangeId` as a special synthetic value.
- Set/delete operations enforce administrative access before mutating winreg state.
- Enumeration functions return enough size information for retry when the offered buffer is too small.
- Mutations call change-ID update helpers so clients can detect printer property changes.

`_spoolss_XcvData` is command-dispatch control flow:

1. Locate the server-side handle and require a local or TCP/IP port monitor handle.
2. Require server administrative access on the handle.
3. Allocate an output `DATA_BLOB` of `r->in.out_data_size` if requested.
4. Dispatch to TCP/IP or local monitor command tables.
5. For TCP/IP `AddPort`, peek the port data version at byte offset 128, NDR-decode the matching structure, convert the Windows port description into a CUPS-style device URI, and run `add_port_hook`.
6. Copy monitor command output back to the RPC response when available.

The final generated-interface control flow is explicit: the local wrappers are selected by `DCESRV_INTERFACE_SPOOLSS_INIT_SERVER` and `DCESRV_INTERFACE_SPOOLSS_SHUTDOWN_SERVER`, then the generated `ndr_spoolss_scompat.c` include wires these functions into the endpoint table.

## State And Persistence Behavior

Persistent state touched by this chunk is primarily the Samba printer registry and print TDB state:

- Printer data values and subkeys are stored, enumerated, and deleted through winreg printer helpers such as `winreg_set_printer_dataex`, `winreg_get_printer_dataex`, `winreg_enum_printer_key_internal`, and `winreg_delete_printer_key`.
- Printer change IDs are updated after successful printer data/key mutations, using either binding-handle helpers or internal helpers depending on the call path.
- Spoolss job IDs are mapped to backend print jobs through the per-printer print TDB opened by `get_print_db_byname`; the TDB handle is explicitly released after lookup.
- `print_queue_status` queries live backend queue state and returns a heap-allocated queue array that this chunk frees with `SAFE_FREE`.
- `_spoolss_XcvData` can persistently add a port by invoking `add_port_hook`; this delegates the actual system or configuration mutation outside this file.
- `spoolss_init_server` migrates legacy `nt_printing.tdb` content before exposing the endpoint. Failed migration aborts startup with `NT_STATUS_UNSUCCESSFUL`.
- `spoolss_shutdown_server` releases spoolss server resources through `srv_spoolss_cleanup`.

Transient memory is consistently talloc-scoped to `p->mem_ctx`, `tmp_ctx`, or the allocated info arrays. The code uses `TALLOC_FREE` on error paths and temporary contexts for winreg binding operations.

## Dependencies And Integration Points

Core local dependencies:

- Generated NDR types from the spoolss IDL, including `struct spoolss_EnumPrintProcessors`, `union spoolss_PrintProcessorInfo`, `struct spoolss_GetJob`, `struct spoolss_PrinterEnumValues`, `struct spoolss_PortData1`, and `struct spoolss_XcvData`.
- Samba RPC server state through `struct pipes_struct`, `p->mem_ctx`, `p->msg_ctx`, `p->dce_call`, and `p->fault_state`.
- Handle lookup and authorization through `find_printer_index_by_hnd`, `get_printer_snum`, `struct printer_handle`, `PRINTER_ACCESS_ADMINISTER`, and `SERVER_ACCESS_ADMINISTER`.
- Loadparm configuration through `lp_const_servicename`, `lp_servicename`, `lp_parm_const_string`, `GLOBAL_SECTION_SNUM`, and `GLOBAL_SPOOLSS_ARCHITECTURE`.
- Winreg printer storage through `winreg_printer_binding_handle`, `winreg_get_printer_internal`, `winreg_get_printer`, `winreg_get_printer_dataex`, `winreg_set_printer_dataex`, `winreg_delete_printer_dataex_internal`, `winreg_delete_printer_key`, and change-ID helpers.
- Printing backend/TDB integration through `get_print_db_byname`, `jobid_to_sysjob_pdb`, `release_print_db`, `print_queue_status`, `print_job_devmode`, and `spoolss_create_default_devmode`.
- NDR marshalling and unmarshalling through `ndr_push_struct_blob`, `ndr_pull_struct_blob`, `ndr_push_spoolss_MonitorUi`, and `ndr_pull_spoolss_PortData*`.
- Server lifecycle integration through `nt_printing_tdb_migrate`, `srv_spoolss_cleanup`, and the generated `ndr_spoolss_scompat.c` endpoint glue.

Externally visible integration points include Windows print clients calling MS-RPRN spoolss methods, Samba's registry service that stores printer configuration, the configured print backend, and administrator-provided hooks for adding TCP/IP or LPR ports.

## Risks And Maintenance Notes

- Several APIs intentionally return hard-coded capability sets. Clients only see `winprint`, `RAW`, `Local Port`, and `Standard TCP/IP Port`; expanding support requires coordinated client-compatibility and registry changes.
- The `[in,out]` buffer handling relies on `SPOOLSS_BUFFER_OK` and `SPOOLSS_BUFFER_*` macros. Changing these paths can break Windows clients that expect `needed` to be valid with `WERR_INSUFFICIENT_BUFFER` or `WERR_MORE_DATA`.
- `_spoolss_GetJob` assumes successful spoolss-to-backend job ID translation before queue lookup. Races where a job disappears between TDB lookup and `print_queue_status` are reported as `WERR_INVALID_PARAMETER`, matching the existing NT compatibility comment but potentially surprising callers.
- Level 2 job info depends on a valid devmode. The fallback to a default devmode prevents NULL devmode from being a normal failure, so regressions in `spoolss_create_default_devmode` can make job queries fail.
- `_spoolss_SetPrinterDataEx` mutates `r->in.value_name` in place when splitting a comma-delimited OID suffix. That assumes the generated request string is mutable in this context.
- The OID side write deliberately ignores its own return status and preserves the primary data write result. This can leave main data updated without companion OID metadata.
- `_spoolss_DeletePrinterDataEx` returns `WERR_NOT_ENOUGH_MEMORY` for NULL key/value input, which is semantically odd but part of current behavior.
- `xcvtcp_addport` peeks the port data version at fixed offset `128` before NDR-decoding. Incorrect assumptions about structure layout or client-encoded buffers could reject otherwise valid calls with `WERR_GEN_FAILURE` or `WERR_UNKNOWN_PORT`.
- The TCP/IP port URI construction accepts host, queue, and port values from decoded client input before passing them to `add_port_hook`; downstream validation is important.
- Many unsupported calls set an RPC fault state as well as a not-supported result. Tests should preserve both if clients depend on this exact failure mode.
- `spoolss_init_server` now depends on successful print TDB migration. Startup failures in migration block the entire spoolss endpoint.

## Test Signals

Useful validation for this chunk should cover both RPC-visible behavior and backend state side effects:

- Enum print processors with valid and invalid environments; valid requests at level 1 should report exactly `winprint`, invalid levels should return `WERR_INVALID_LEVEL`, and undersized buffers should set `needed`.
- Enum print processor data types with processor name `winprint`, a wrong processor name, NULL processor name, and undersized buffers; successful data should be `RAW`.
- Enum monitors at levels 1 and 2; level 2 should include configured or default architecture plus `localmon.dll` and `tcpmon.dll`.
- GetJob for existing, missing, and raced-away jobs; level 1 and level 2 should map public job IDs through the print TDB and level 2 should work when no per-job devmode exists.
- Get/Set/Delete/Enum printer data and keys through a printer handle with and without `PRINTER_ACCESS_ADMINISTER`; successful mutations should advance `ChangeId`.
- GetPrinterDataEx for a server handle and for `SPOOL_PRINTERDATA_KEY`/`ChangeId`, including small offered-buffer cases that should return `WERR_MORE_DATA` while preserving type.
- GetPrintProcessorDirectory with and without a configured `prnproc$` share.
- XcvData on TCP/IP and local monitor handles, on non-monitor handles, with and without `SERVER_ACCESS_ADMINISTER`; TCP/IP `MonitorUI` should return `tcpmonui.dll`, and `AddPort` should accept both port data versions for raw TCP and LPR protocols.
- Unsupported RPC methods should continue to return not-supported results and, where implemented that way in this range, set `DCERPC_FAULT_OP_RNG_ERROR`.
- Server startup tests should exercise successful and failed `nt_printing_tdb_migrate`; shutdown tests should verify `srv_spoolss_cleanup` is reached before generated shutdown.
