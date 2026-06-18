# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_nt.c lines 1-9387

## Scope

This chunk covers the first 9387 lines of Samba's source3 SPOOLSS RPC server implementation. The range starts at the file header and includes the main handle model, printer open/close/delete paths, notification back-channel setup and refresh logic, printer and job enumeration, printer driver enumeration and installation/deletion, printer mutation, forms, ports, and the beginning of print-processor helper code. The chunk ends inside `fill_print_processor1`; later print processor, monitor, dataex, Xcv, and remaining RPC entry points are outside this chunk.

The implementation is an RPC-facing adapter over Samba's source3 printing, registry, messaging, authentication, loadparm, and SMB client subsystems. It presents Windows spooler semantics while persisting printer metadata through Samba's winreg-backed printing store and delegating real queue operations to the configured printing backend.

## Purpose

The code implements most of the server-side behavior for the `spoolss` RPC pipe in source3. Its responsibilities in this range are:

- Maintain server-local `struct printer_handle` state for open SPOOLSS policy handles.
- Open, close, delete, add, update, and reset print server and printer handles.
- Translate Samba print queue/job state into MS-RPRN `spoolss_*Info*` structures.
- Manage printer change notifications, including the legacy client callback channel used by `RemoteFindFirstPrinterChangeNotifyEx` and `RouterRefreshPrinterChangeNotify`.
- Enumerate printers, jobs, drivers, forms, and ports with Windows-compatible buffer sizing behavior.
- Add and delete printer drivers, including driver file movement and registry updates.
- Start, write, end, abort, pause, resume, purge, and rename print jobs.
- Store and retrieve printer data under the default `PrinterDriverData` key through the `*PrinterDataEx` variants.
- Synchronize printer metadata into the `DsSpooler` registry key and optionally publish/unpublish printers in AD.

The file deliberately returns `WERROR` DOS/Win32-style status codes rather than NTSTATUS for public spoolss operations, matching Windows spooler behavior.

## Important APIs, Types, And Globals

Key public RPC entry points covered by this chunk:

- `_spoolss_OpenPrinter` and `_spoolss_OpenPrinterEx`: create server, printer, or port-monitor handles, reload printcap state, normalize access masks, and enforce host/user/security descriptor access.
- `_spoolss_ClosePrinter`, `_spoolss_DeletePrinter`, `_spoolss_SetPrinter`, `_spoolss_GetPrinter`, and `_spoolss_EnumPrinters`: core printer object lifecycle and query/update APIs.
- `_spoolss_RemoteFindFirstPrinterChangeNotifyEx`, `_spoolss_RouterRefreshPrinterChangeNotify`, and `_spoolss_FindClosePrinterNotify`: notification registration, refresh, and teardown.
- `_spoolss_StartDocPrinter`, `_spoolss_StartPagePrinter`, `_spoolss_WritePrinter`, `_spoolss_EndPagePrinter`, `_spoolss_EndDocPrinter`, and `_spoolss_AbortPrinter`: job submission state machine.
- `_spoolss_EnumJobs`, `_spoolss_SetJob`, and `_spoolss_ScheduleJob`: job enumeration and control.
- `_spoolss_GetPrinterDriver2`, `_spoolss_EnumPrinterDrivers`, `_spoolss_AddPrinterDriver`, `_spoolss_AddPrinterDriverEx`, `_spoolss_DeletePrinterDriver`, `_spoolss_DeletePrinterDriverEx`, and `_spoolss_GetPrinterDriverDirectory`: driver metadata, storage paths, and install/delete flows.
- `_spoolss_AddPrinter`, `_spoolss_AddPrinterEx`, `_spoolss_AddJob`, `_spoolss_EnumForms`, `_spoolss_GetForm`, `_spoolss_AddForm`, `_spoolss_DeleteForm`, `_spoolss_SetForm`, `_spoolss_EnumPorts`, `_spoolss_EnumPrinterData`, `_spoolss_SetPrinterData`, `_spoolss_DeletePrinterData`, and `_spoolss_ResetPrinter`: auxiliary SPOOLSS APIs.

Important local types and globals:

- `static struct printer_handle *printers_list`: process-local list of active printer policy-handle objects. Destructors remove entries and close notification backchannels.
- `struct printer_session_counter` and `counter_list`: per-printer session counters used in `PrinterInfo0`.
- `struct notify_back_channel` and `back_channels`: cached anonymous SMB IPC connections and spoolss RPC client pipes back to notifying clients, keyed by client address.
- `printer_std_mapping` and `printserver_std_mapping`: generic-to-specific access mappings for printer and print server objects.
- `struct notify2_message_table` and `notify_info_data_table`: tables mapping notify fields to construction functions and encoded value types.
- `drv_cversion`: list of driver cversions considered during driver deletion.
- `spoolss_paths`: maps driver and print-processor path components to shares and local directory names.

Key helper families:

- Handle helpers: `find_printer_index_by_hnd`, `close_printer_handle`, `get_printer_snum`, `open_printer_hnd`, `set_printer_hnd_printertype`, and `set_printer_hnd_name`.
- Printer info constructors: `construct_printer_info0` through `construct_printer_info8`.
- Driver info constructors: `fill_printer_driver_info1`, `fill_printer_driver_info2`, `fill_printer_driver_info3`, `fill_printer_driver_info4`, `fill_printer_driver_info5`, `fill_printer_driver_info6`, and `fill_printer_driver_info8`.
- Job info constructors: `fill_job_info1`, `fill_job_info2`, `enumjobs_level1`, `enumjobs_level2`, and `enumjobs_level3`.
- Mutation helpers: `update_printer`, `update_printer_sec`, `update_printer_devmode`, `check_printer_ok`, `update_dsspooler`, `add_printer_hook`, `delete_printer_hook`, and `add_port_hook`.
- Notification helpers: `srv_spoolss_replyopenprinter`, `srv_spoolss_replycloseprinter`, `receive_notify2_message_list`, `build_notify2_messages`, `send_notify2_printer`, `construct_notify_printer_info`, and `construct_notify_jobs_info`.

## Control Flow

Handle creation starts in `_spoolss_OpenPrinter` or `_spoolss_OpenPrinterEx`. The legacy API wraps the Ex call with a synthetic user level. `_spoolss_OpenPrinterEx` validates the printer name and userlevel input, reloads printer shares as root through `delete_and_reload_printers`, creates a `printer_handle`, and classifies the handle as print server, printer, TCP port monitor, or local port monitor. Name resolution accepts `\\server`, `\\server\printer`, share names, stored printer names, and Xcv monitor names. Printer name lookups are cached in gencache under `PRINTERNAME/*`, with negative cache entries pruned after mutation.

Access flow diverges by handle type. Server and port-monitor handles map generic access through `printserver_std_mapping`, allow only server-specific bits, and require root, `SePrintOperatorPrivilege`, or Builtin Print Operators membership for administer access. Printer handles map generic access through `printer_std_mapping`, default empty access to `PRINTER_ACCESS_USE`, downgrade administer to use for client-driver printers, check hosts allow/deny, `user_ok_token`, and `print_access_check`, and then persist an initial winreg printer key if needed.

Close/delete flow uses the policy-handle destructor. `_spoolss_ClosePrinter` auto-ends an active document, closes the handle, and zeros the returned handle. `printer_entry_destructor` tears down notification state and removes the handle from `printers_list`. `_spoolss_DeletePrinter` ends active documents, removes the winreg printer key, runs `delete_printer_handle`, and calls the configured `deleteprinter command` hook if present.

Notification flow has two paths. For live change notifications, `_spoolss_RemoteFindFirstPrinterChangeNotifyEx` stores notification options on the handle, resolves the RPC peer address, checks `lp_print_notify_backchannel`, opens an anonymous IPC/spoolss pipe back to the client via `spoolss_connect_to_client`, calls `ReplyOpenPrinter`, registers this server PID for print notify messages, and subscribes to `MSG_PRINTER_NOTIFY2`. Incoming notify2 message lists are unpacked from the messaging blob, grouped by printer name, filtered by each handle's requested notify fields, converted into `spoolss_Notify` entries, and sent to the client through `RouterReplyPrinterEx`. For refresh notifications, `_spoolss_RouterRefreshPrinterChangeNotify` synthesizes a full `spoolss_NotifyInfo` snapshot for either all printers on a server handle or all requested printer/job fields on a printer handle.

Enumeration and query flow use Windows-style two-pass buffer semantics. Entry points initialize `needed`, `count`, and returned pointers; construct arrays on `p->mem_ctx`; compute NDR sizes with `SPOOLSS_BUFFER_UNION*`; and either return the data or null it with `WERR_INSUFFICIENT_BUFFER` if `offered` is too small. `_spoolss_EnumPrinters` dispatches by level and flags, reloads printer shares, creates winreg printer records, obtains `PrinterInfo2`, and constructs levels 0, 1, 2, 4, and 5. `_spoolss_GetPrinter` handles print-server security descriptor level 3 specially, otherwise builds levels 0 through 8 for a printer handle.

Job submission flow is handle-stateful. `_spoolss_StartDocPrinter` requires document info level 1, rejects duplicate starts, accepts only `RAW` and `XPS_PASS`, resolves the remote host, and calls `print_job_start`, storing the returned job id on the handle. `_spoolss_StartPagePrinter` and `_spoolss_EndPagePrinter` toggle `page_started` and end the page in the backend. `_spoolss_WritePrinter` streams data to `print_job_write` and maps ENOSPC to `WERR_NO_SPOOL_SPACE`. `_spoolss_EndDocPrinter` calls `print_job_end` with `NORMAL_CLOSE` and clears the handle job id. `_spoolss_AbortPrinter` requires a started document and calls `print_job_delete`.

Printer mutation flow enters `_spoolss_SetPrinter`. Level 0 maps to pause/resume/purge queue controls. Level 2 updates printer metadata, optional devmode, and optional security descriptor. Level 3 updates only the security descriptor. Level 4 converts the partial info into level 2 semantics. Level 7 publishes or unpublishes in AD when ADS support and security mode allow it. Level 8 updates only the devmode. `update_printer` canonicalizes server, share, printer name, and Samba attributes with `check_printer_ok`, enforces `PRINTER_ACCESS_ADMINISTER`, optionally runs the configured `addprinter command` for driver/comment/port/location changes, updates `DsSpooler`, and writes the merged info back through winreg.

Driver flow is registry-backed with filesystem staging. `_spoolss_GetPrinterDriver2` locates the printer's configured driver and fills the requested info level, downgrading Windows 8 v4 requests to v3. `_spoolss_EnumPrinterDrivers` validates the requested server name, iterates registered driver versions per architecture, and fills driver info arrays. `_spoolss_AddPrinterDriverEx` validates copy flags and accepted levels, normalizes the driver structure, moves files to the print$ download area, writes the winreg driver record, and sends a local `MSG_PRINTER_DRVUPGRADE` message. `do_drv_upgrade_printer` handles that message by iterating all printers and updating change IDs for printers using the changed driver. Deletion validates print-operator privilege, environment, and in-use status, then removes registry records and optionally unused/all files depending on `DeletePrinterDriverEx` flags.

Form and port flow is simpler. Forms are enumerated and mutated through winreg helper functions, with add/delete/set requiring root or `SePrintOperatorPrivilege` and updating printer change IDs for printer handles. Ports are enumerated either from `enumports command` output or a default `Samba Printer Port`; level 2 currently reports all ports as Local Monitor/write ports. `add_port_hook` exists in this chunk for configured `addport command` execution, but the XcvData dispatch that uses port monitor hooks is later in the file.

## State And Persistence Behavior

Process-local state:

- `printers_list` tracks all active policy handles in this process. Handle lifetime is tied to `talloc` and DCERPC policy-handle management.
- Each `printer_handle` stores the handle type, share/server name, granted access, notification registration data, active document/page flags, current job id, and any devmode supplied at open.
- `back_channels` caches outbound anonymous IPC/spoolss connections to client machines for change notification callbacks. Reference counting is manual through `active_connections`; the final close shuts down the SMB client connection and deregisters messaging.
- `counter_list` stores per-printer session counters used only in `PrinterInfo0`; `srv_spoolss_cleanup` frees it.

Persistent or cross-process state:

- Printer metadata, devmodes, security descriptors, driver metadata, forms, and printer data values are stored through winreg helper APIs such as `winreg_get_printer`, `winreg_update_printer`, `winreg_set_printer_dataex`, `winreg_add_driver_internal`, and `winreg_printer_*form*`.
- Real queue state and job data live in the configured printing backend and Samba print TDBs accessed through `print_queue_status`, `print_job_start`, `print_job_write`, `print_job_end`, `print_job_delete`, `get_print_db_byname`, and job id mapping helpers.
- Printer share inventory is derived from loadparm/printcap. Enumeration and open paths reload printers as root with `delete_and_reload_printers`; add-printer hooks call `reload_services`.
- The `DsSpooler` registry key is synchronized by `update_dsspooler`, including driver, description, share, printer name, port, location, separator, start/end time, priority, keep-printed-jobs, spooling mode, server names, and UNC name. Field changes emit printer notification events and prune printer-name cache where names change.
- Driver install persists files into the print$ download area and writes the corresponding winreg driver record. Driver deletion can also remove driver files when requested.
- Optional external hooks run configured shell commands: `addprinter command`, `deleteprinter command`, `addport command`, and `enumports command`. Commands may run with temporary root privileges when the caller has print-operator privilege.
- Messaging is used for printer notifications, configuration reload broadcasts, and driver upgrade propagation.

## Dependencies And Integration Points

Major Samba integration points:

- DCERPC server framework: `pipes_struct`, policy handles, `dcesrv_call_session_info`, `dcesrv_connection_get_remote_address`, generated `ndr_spoolss` structures, and generated client calls for callback RPCs.
- Authentication and authorization: Unix uid checks, `security_token_has_privilege`, Builtin Print Operators SID checks, `print_access_check`, `user_ok_token`, and security descriptor merge/equality helpers.
- Loadparm configuration: printer shares, host allow/deny, client-driver behavior, forced printer names, default devmode, print notify backchannel, add/delete/enum port/printer hooks, server architecture, and reported OS version.
- Registry-backed printing: `winreg_*printer*`, `winreg_*driver*`, `winreg_*form*`, and print server security descriptor helpers.
- Printing backend: queue status, queue controls, job lifecycle, job name mutation, queue-to-job id mapping, and per-printer print TDB access.
- Messaging and notify: `MSG_PRINTER_NOTIFY2`, `MSG_PRINTER_DRVUPGRADE`, `MSG_SMB_CONF_UPDATED`, `print_notify_register_pid`, notification event emitters, and `global_event_context`.
- SMB client stack: name resolution, anonymous credentials, `cli_full_connection_creds`, protocol checks, and unauthenticated spoolss pipe open for notification backchannels.
- Active Directory publishing: guarded by `HAVE_ADS` and `SEC_ADS`, using printer GUID retrieval/storage and `nt_printer_publish`.

Protocol compatibility details are embedded throughout. Examples include reporting server OS version/architecture registry values, accepting `XPS_PASS`, downgrading v4 driver queries to v3, returning `WERR_CAN_NOT_COMPLETE` for certain network enum cases, returning empty strings to satisfy NT4 unmarshalling, and emulating Windows buffer-needed behavior.

## Risks And Maintenance Notes

- The notification backchannel is complex and fragile. It opens anonymous SMB connections back to client addresses, caches channels globally, and manually decrements `active_connections`. Bugs can leak IPC connections, deregister messaging too early, or send notifications to stale clients.
- `srv_spoolss_replycloseprinter` has defensive handling for impossible-looking backchannel state and removes/frees channels on null subfields. Changes around this code need careful lifetime review because `printer_entry_destructor` can call it during handle teardown.
- `set_printer_hnd_name` mutates a discarded-const pointer while parsing `\\server\printer` names. It relies on incoming NDR strings being mutable in practice and should be treated cautiously.
- External hook command strings quote arguments but still execute configured shell commands. The security model depends on administrator-controlled smb.conf hooks and privilege bracketing with `become_root`/`unbecome_root`.
- Printer add/update flow assumes the external add-printer hook and service reload make the new or changed share visible immediately. Failure modes often map to broad `WERR_ACCESS_DENIED` or `WERR_INVALID_HANDLE`, which can obscure root causes.
- Access checks are split between handle-open time, handle granted access, print backend checks, and specific privilege checks. Reusing a handle after privilege or configuration changes may retain previously granted access until close.
- Driver deletion has several edge cases: driver in-use detection, overlapping driver files, version-specific deletion, and "delete unused files" behavior depend on helper functions mutating the driver file list correctly.
- Buffer sizing uses NDR size helpers and `SPOOLSS_BUFFER_OK` macros. Any constructor that fills pointers inconsistently can produce wrong `needed` sizes or clients receiving null data with success.
- Job enumeration skips untracked system jobs when no Samba job id mapping exists. This avoids bad IDs but can make queue counts differ from backend counts.
- `update_dsspooler` writes many independent registry values and returns on the first failure, so partial updates are possible. It also sends notifications only for selected changes.
- Forms and security descriptor updates require change-id updates for printer handles; missing these updates can make Windows clients cache stale properties.
- The requested chunk ends inside `fill_print_processor1`, so print-processor enumeration behavior is only partially covered here.

## Test Signals

Useful direct and integration tests for this chunk:

- RPC client tests for `OpenPrinterEx`, `EnumPrinters`, `GetPrinter`, `ClosePrinter`, and invalid name/server cases, including two-pass insufficient-buffer behavior.
- Authorization tests for printer use vs administer, server administer, print-operator privilege, Builtin Print Operators membership, hosts allow/deny, and denied `SetPrinter`/security descriptor changes.
- Printer mutation tests that update comment, location, port, driver, devmode, and security descriptor, then verify winreg state, `DsSpooler` values, change IDs, cache pruning, and notifications.
- Job lifecycle tests covering `StartDocPrinter`, `WritePrinter`, `EndDocPrinter`, `AbortPrinter`, `EnumJobs`, `SetJob` pause/resume/delete/noop, duplicate StartDoc, invalid datatypes, and ENOSPC mapping.
- Notification tests for `RemoteFindFirstPrinterChangeNotifyEx`, `RouterRefreshPrinterChangeNotify`, notify option filtering, print-server vs printer-handle ids, `FindClosePrinterNotify`, and backchannel-disabled behavior.
- Driver tests for add, enumerate, get, delete, delete-ex flags, architecture validation, v4-to-v3 downgrade, in-use detection, overlapping files, and driver-upgrade change-id messages.
- Form and port tests for enum/get/add/delete/set forms, change-id updates, default port enumeration, and `enumports command` output parsing.
- Regression tests for Windows compatibility return codes: invalid levels, no-more-items, insufficient buffer, unknown driver/environment/port/printprocessor, can-not-complete network enum, and NT4 empty-string enum-printer-data behavior.
