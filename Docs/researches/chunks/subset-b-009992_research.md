# sources/user-network-fs/samba/source4/torture/rpc/spoolss.c lines 1-8667

## Purpose

This chunk is the first, large part of Samba's `smbtorture` RPC test coverage for the MS-SPOOLSS print spooler interface. It builds a torture-suite harness around a live `spoolss` DCE/RPC pipe, opens a print-server handle, discovers the server's spooler architecture, enumerates server resources, opens and creates printers, mutates printer configuration, exercises job submission, and cross-checks spooler state against the remote registry service.

The code is test code rather than production spooler implementation. Its value is in encoding protocol expectations: successful and failing `WERROR` values, buffer-resizing behavior, level-specific structure equivalence, security descriptor and devmode persistence, registry layout compatibility, printer data key semantics, and server-specific skip/relaxation rules for Samba, Windows versions, and unsupported RPC operations.

The requested chunk ends at line 8667 inside `torture_rpc_spoolss_printer_setup_common()`, immediately after it decides whether to use an existing XPS driver or upload a local CUPS/Adobe-style driver. Driver upload/removal implementation and the final suite registration live after this chunk.

## Important Types and Context

- `struct test_spoolss_context` is the common print-server test fixture. It stores the `spoolss_pipe`, server architecture string, server `policy_handle`, and cached enumeration results for ports, drivers, monitors, print processors, and printers across levels.
- `struct torture_driver_context` describes local and remote driver directories/environments plus a level-8 `spoolss_AddDriverInfo8` record. The first chunk initializes this for printer fixture setup but relies on later-file helpers for complete upload/removal behavior.
- `struct torture_printer_context` is the per-printer fixture. It tracks the spoolss pipe, level-2 printer add/set info, associated driver context, mode flags (`ex`, `wellknown`), whether a driver was added or found, optional devmode, and the opened printer handle.
- Comparison and sizing macros (`COMPARE_*`, `CHECK_NEEDED_SIZE_*`, `CHECK_ALIGN`, `DO_ROUND`) implement repeated assertions across info levels and NDR-computed byte sizes. The size checks are guarded by the `spoolss_check_size` torture setting.
- Registry key constants (`TOP_LEVEL_PRINT_*`, `TOP_LEVEL_CONTROL_*`) encode expected Windows registry paths for print server, printers, forms, environments, and drivers.

## RPC and Helper API Coverage

The chunk covers these SPOOLSS RPC surfaces:

- Server and printer handles: `OpenPrinter`, `OpenPrinterEx`, `ClosePrinter`, secondary authenticated close behavior, bad-name handling, and server-handle `GetPrinter`/`SetPrinter` level rules.
- Enumeration APIs: `EnumPorts`, `EnumPrinterDrivers`, `EnumMonitors`, `EnumPrintProcessors`, `EnumPrintProcessorDataTypes`, `EnumPrinters`, `EnumForms`, `EnumJobs`, `EnumPrinterData`, `EnumPrinterDataEx`, `EnumPrinterKey`, and `EnumPerMachineConnections`.
- Directory and driver discovery: `GetPrintProcessorDirectory`, `GetPrinterDriverDirectory`, `GetPrinterDriver2`, `GetCorePrinterDrivers`, and `GetPrinterDriverPackagePath`.
- Printer metadata mutation: `SetPrinter` for normal fields, control commands, security descriptors, devmodes, rename behavior, c_setprinter observation, and `ChangeID`.
- Forms: `GetForm`, `AddForm`, `SetForm`, `DeleteForm`, with print-server and printer-handle variants.
- Jobs: `StartDocPrinter`, `StartPagePrinter`, `WritePrinter`, `EndPagePrinter`, `EndDocPrinter`, `GetJob`, `SetJob`, `AddJob`, and named job property APIs.
- Printer data and key-value storage: `GetPrinterData`, `SetPrinterData`, `DeletePrinterData`, `GetPrinterDataEx`, `SetPrinterDataEx`, `DeletePrinterDataEx`, and `DeletePrinterKey`.
- Printer and driver provisioning: `AddPrinter`, `AddPrinterEx`, `DeletePrinter`, well-known printer list behavior, and initial setup for printer driver fallback.
- Print processor and per-machine connection management: `AddPrintProcessor`, `DeletePrintProcessor`, `AddPerMachineConnection`, `DeletePerMachineConnection`.

It also uses WINREG RPC (`OpenHKLM`, `OpenKey`, `CloseKey`, `QueryValue`) as an independent observation channel for spooler state.

## Control Flow

The top-level setup path for non-printer server tests is:

1. `torture_rpc_spoolss_setup_common()` opens an RPC connection to `ndr_table_spoolss`.
2. `test_OpenPrinter_server()` opens the server pseudo-printer using `\\server` and stores `server_handle`.
3. `test_get_environment()` reads `Architecture` via `GetPrinterData` and stores the environment string.
4. Server tests use the shared context and close the server handle through `torture_rpc_spoolss_teardown_common()`.

Most enumeration helpers follow the same two-call pattern: call once with no buffer or zero offered size, expect `WERR_INSUFFICIENT_BUFFER` or `WERR_MORE_DATA`, allocate the returned `needed` size, call again, assert `WERR_OK`, then optionally compare the returned size against local NDR sizing. Examples include `EnumPorts`, `EnumPrinterDrivers`, `EnumMonitors`, `EnumPrinters`, `GetPrinter`, `GetForm`, `EnumForms`, `GetJob`, `EnumJobs`, `GetPrinterData`, `GetPrinterDataEx`, and winreg `QueryValue`.

Cross-level tests use the highest or richest level as the reference:

- `EnumPorts` compares level 1 names against level 2 names.
- `EnumPrinterDrivers` compares levels 1, 2, 3, 4, 5, and 6 to level 8 where fields overlap.
- `EnumMonitors` compares level 1 to level 2 and verifies level-2 `environment`.
- `EnumPrinters` compares levels 0, 1, 4, and 5 to level 2 where practical.
- `GetPrinter` iterates levels 0-8 and, when level 2 names a driver, probes `GetPrinterDriver2` for that driver.

Printer-handle tests flow through `call_OpenPrinterEx()` and `test_existing_printer_openprinterex()`: open a printer, test SDs, info levels, forms, form registry mirrors, printer data enumeration, key enumeration, pause/resume, real print job creation/deletion, data set/get/delete matrices, optional secondary close rejection, and finally close the handle.

Printer creation setup begins in `torture_rpc_spoolss_printer_setup_common()`: initialize a driver record, set `LPT1:` as the target port, fill remote printserver metadata, derive a local driver directory for the architecture, prefer installed "Microsoft XPS Document Writer" or v4 drivers, otherwise attempt driver upload from `/usr/share/cups/drivers`.

## State and Persistence Behavior

This chunk intentionally mutates spooler state and then checks persistence or cleanup:

- `test_SetPrinter_errors()` checks command and info-level error surfaces for zeroed `SetPrinter` inputs, including printer control commands and invalid levels.
- `test_PrinterInfo()` encodes a broad field persistence matrix for level 2, 4, 5, and 6 printer fields, including expected errors for unknown ports, drivers, separator files, and print processors. It is currently skipped with `torture_skip()`, but the intended coverage remains documented in code.
- `test_PrinterInfo_SD()` saves the original security descriptor, runs level-2/level-3 equivalence and set/get tests, adds many ACEs to stress SD size/round-trip behavior, then restores the original descriptor.
- `test_PrinterInfo_DevMode()` saves the original global devmode, compares level 8 and level 2, mutates copies/form name through level 8 and level 2 setters, tests individual public devmode fields, probes `OpenPrinterEx` devmode behavior, then restores the original devmode.
- Forms are added, verified through spoolss and optionally winreg, updated by `SetForm`, found via enumeration, and deleted. Duplicate adds and deleting built-in/invalid forms have expected error codes.
- Print jobs are created by full document/page/write/end flows, then enumerated, fetched, renamed through `SetJob` level 1, paused/resumed, and finally deleted. A separate matrix sets, retrieves, enumerates, and deletes named job properties for string, int32, int64, byte, and blob property types.
- Printer data tests write values under `PrinterDriverData` and arbitrary subkeys using multiple registry types, verify spoolss and winreg consistency, enumerate both legacy and Ex views, and delete values/keys afterward.
- `test_ChangeID()` verifies that `ChangeID` is identical through `GetPrinterData`, `GetPrinterDataEx`, and `GetPrinter` level 0, does not change for read-only operations, and increases after `SetPrinter` mutations.
- `test_printer_rename()` renames a printer via level-2 `SetPrinter`, validates the new name, conditionally checks old-name lookup failure on non-Samba servers, opens by the new name, and leaves later cleanup to the fixture.
- `test_csetprinter()` creates a second printer to observe `info0.c_setprinter` before and after add/open operations, then closes and deletes the new printer.
- `test_set_printer_printserverhandle()` mutates the print-server security descriptor by adding an ACE for a fixed SID, verifies it appears, removes it, and verifies it is gone.

Cleanup is generally inline and assertion-driven. If a mid-test assertion aborts, residual state is possible: test forms, printer data keys, print jobs, added printers, per-machine connections, or modified security/devmode state may remain unless surrounding torture teardown later handles it.

## Registry Integration

The winreg helpers provide a second view of spooler persistence:

- `test_winreg_OpenHKLM()`, `test_winreg_OpenKey[_opts]()`, `test_winreg_CloseKey()`, and `test_winreg_QueryValue()` wrap WINREG RPC with the same buffer-resize idiom.
- `test_winreg_symbolic_link()` checks that `SYSTEM\\CurrentControlSet\\Control\\Print\\Printers` is a registry symbolic link to the Software print-printer path on non-Samba targets.
- `test_GetPrinterInfo_winreg()` compares `GetPrinter` level 2 fields against values under both Control and Software printer keys, including strings, DWORDs, binary devmode, and binary security descriptor.
- `test_GetPrintserverInfo_winreg()` compares print-server level-3 SD to `ServerSecurityDescriptor`.
- `test_GetDriverInfo_winreg()` compares driver info levels 8, 6, and 3 to registry driver keys, including stripped file basenames, dates, versions, multi-string fields, and Windows-version-specific binary date/version handling.
- `test_PrintProcessors()` verifies that enumerated print processors have corresponding environment registry keys.
- `test_PrinterData_winreg()`, `test_Forms_winreg()`, `test_PrinterInfo_winreg()`, `test_PrintserverInfo_winreg()`, `test_DriverInfo_winreg()`, and `test_PrintProcessors_winreg()` open a separate winreg pipe, run the consistency check, close HKLM, and free the pipe.
- `test_PrinterData_DsSpooler()` verifies that `SetPrinter` level-2 fields are reflected under the printer's `DsSpooler` key as REG_SZ/REG_DWORD data.

## Dependencies and Integration Points

The file depends on Samba's generated NDR/RPC bindings for SPOOLSS, WINREG, security descriptors, and helper libraries:

- Generated RPC/NDR headers: `ndr_spoolss.h`, `ndr_spoolss_c.h`, `ndr_winreg_c.h`, `ndr_security.h`, `ndr_misc.h`.
- DCE/RPC and torture framework: `torture/rpc/torture_rpc.h`, `torture/torture.h`, `torture/ndr/ndr.h`.
- Security helpers: `security_descriptor_equal`, ACL equality, SID parse/create, `security_descriptor_dacl_add/del`.
- Registry value helpers: `push_reg_sz`, `pull_reg_sz`, `push_reg_multi_sz`, `pull_reg_multi_sz`, `reg_val_data_string`, `str_regtype`.
- Client and transport helpers: `dcerpc_server_name`, secondary auth connection, SMB/SMB2 includes for later driver/file work.
- Talloc memory management and Samba utility routines such as `data_blob_talloc_zero`, `data_blob_string_const`, `generate_random_buffer`, `strlen_m_term`, `IVAL`, `SIVAL`, `SBVAL`, and `push_nttime`.

The tests are tightly integrated with live server capabilities and torture settings:

- `samba3`, `samba4`, `w2k3`, and `dangerous` settings change expectations, skip behavior, or destructive-operation protection.
- `spoolss_check_size` enables local NDR size validation for returned buffers.
- `NCACN_NP` transport is required for the secondary-pipe close rejection test.
- Local filesystem availability of `/usr/share/cups/drivers` influences whether setup can upload a fallback driver.

## Risks and Edge Cases

- Many tests depend on real spooler state and can be flaky against servers with no printers, missing XPS drivers, unsupported levels, unusual registry layouts, or restricted permissions.
- The file has several server-specific relaxations and skips; protocol behavior differs between Samba, Windows Server versions, and NT4-like servers.
- `test_EnumPrinterData_consistency()` assumes `EnumPrinterData` and `EnumPrinterDataEx` use compatible ordering for value names.
- `test_DeletePrinterKey()` can wipe printer registry keys when passed an empty key name, guarded by the `dangerous` setting.
- `test_PrinterInfo()` is currently skipped despite containing broad persistence expectations, so regressions in those fields may not be caught unless the skip is removed.
- Some helpers use fixed names (`torture_value*`, `torturedataex`, `testform_*`, `SAMBA smbtorture Test Printer (Copy 2)`, `torture_printer*`) and may collide with leftover state from prior failed runs.
- The printer setup path may delete an existing printer with the same torture name before retrying add; that is expected for cleanup of prior runs but risky if names collide with non-test objects.
- Devmode and security descriptor tests deliberately modify global printer state and restore it afterward; aborting between mutation and restore can leave changed printer defaults or ACLs.
- Job tests create multiple print jobs and expect deletion to work. Servers that actually print jobs quickly or apply queue policies may produce timing-sensitive results.
- Driver and package APIs may return `HRESULT` values mapped through `WIN32_FROM_HRESULT`, unlike most tests that assert `WERROR` directly.

## Test Signals

Strong positive signals:

- First-call insufficient-buffer or more-data paths report correct `needed` sizes, second calls succeed, and optional NDR size checks match.
- Enumeration counts match across comparable levels, and shared fields are equal across levels.
- `GetPrinterData`, `GetPrinterDataEx`, `EnumPrinterData`, `EnumPrinterDataEx`, and winreg views agree on type, size, and bytes.
- Security descriptors and devmodes round-trip between levels 2/3 and 2/8 respectively, including larger modified descriptors and driverextra devmode data.
- `ChangeID` is stable on reads and increases after real `SetPrinter` mutation.
- Added forms, printer data values, job properties, per-machine connections, and temporary printers can be observed and then deleted.
- Invalid inputs return the encoded expected errors, including `WERR_INVALID_LEVEL`, `WERR_INVALID_PARAMETER`, `WERR_INVALID_PRINTER_NAME`, `WERR_UNKNOWN_PORT`, `WERR_UNKNOWN_PRINTER_DRIVER`, `WERR_UNKNOWN_PRINTPROCESSOR`, `WERR_INVALID_ENVIRONMENT`, `WERR_FILE_EXISTS`, `WERR_NO_MORE_ITEMS`, and HRESULT success/failure for core driver APIs.

Weak or conditional signals:

- `test_PrinterInfo()` is skipped, so its detailed field persistence matrix is documentation until re-enabled.
- Some checks warn instead of failing where Windows/Samba behavior differs or historic behavior is unclear.
- Later suite registration and complete printer teardown are outside this chunk, so this research covers setup and helper behavior but not all final test-case wiring.
