# sources/user-network-fs/samba/source4/torture/rpc/spoolss.c lines 8668-11725

## Chunk Scope

This chunk is part of Samba's RPC torture coverage for the `spoolss` interface. It starts in the tail of printer fixture setup, covers printer teardown and most per-printer torture tests, registers the `spoolss` and `spoolss.printer` suites, then defines the printer-driver add/delete/upload test helpers and the `spoolss.driver` suite. It is not production spooler code; it is integration-test code that drives real DCE/RPC `spoolss`, `winreg`, SMB1, and SMB2 operations against a target server and checks Windows-compatible behavior.

The chunk depends on local context defined earlier in the file, especially `struct test_spoolss_context`, `struct torture_printer_context`, `struct torture_driver_context`, the `TORTURE_*` printer/driver names, and helper wrappers such as `test_OpenPrinter_server`, `test_EnumJobs_args`, `test_DoPrintTest*`, `test_PrinterInfo*`, `test_SetPrinterDataEx*`, `test_DriverInfo_winreg`, and `test_EnumPrinterDrivers_findone`.

## Purpose

The first half validates behavior of printers created by `AddPrinter` and `AddPrinterEx`: job creation, job enumeration, purge, security descriptors, devmode persistence, registry-backed printer information, printer data keys/values, DsSpooler values, GDI printer information contexts, bidirectional data calls, publish/unpublish state, Branch Office job logging, and server OS version reporting.

The second half validates printer driver lifecycle semantics: querying the driver directory, uploading candidate driver files over SMB, calling `AddPrinterDriver` and `AddPrinterDriverEx` at levels 1, 2, 3, 4, 6, and 8, verifying driver registry state through `winreg`, deleting drivers with normal and extended delete APIs, and checking whether associated driver files remain or are removed according to delete flags.

## Important Types, APIs, and Helpers

- `struct torture_printer_context`: fixture state for printer tests. This chunk reads `spoolss_pipe`, `info2`, `driver`, `ex`, `wellknown`, `added_driver`, `have_driver`, `devmode`, and `handle`.
- `struct torture_driver_context`: fixture state for driver tests. This chunk fills local and remote environments/directories, `spoolss_AddDriverInfo8`, and the `ex` selector for `AddPrinterDriverEx` versus `AddPrinterDriver`.
- `struct test_spoolss_context`: print-server fixture state, used here by `test_printserver_info_winreg`.
- `spoolss` RPC calls used directly in this chunk include `CreatePrinterIC`, `PlayGDIScriptOnPrinterIC`, `DeletePrinterIC`, `SendRecvBidiData`, `LogJobInfoForBranchOffice`, `GetPrinterDriverDirectory`, `AddPrinterDriver`, `AddPrinterDriverEx`, `DeletePrinterDriver`, and `DeletePrinterDriverEx`.
- Wrapper tests used by this chunk include printer open/close, pause/resume, purge, print job creation, job enumeration, printer info/security/devmode checks, registry checks, and driver enumeration.
- SMB dependencies are split by purpose: `smb2_connect`, `torture_smb2_testfile`, `smb2_util_write`, and `smb2_util_close` test spooling through a printer share, while `smbcli_full_connection`, `smbcli_mkdir`, `smbcli_open`, `smbcli_write`, `smbcli_unlink`, and `smbcli_close` upload, verify, and remove driver files in the print driver share.
- NDR and binary helpers include `ndr_pull_spoolss_OSVersion`, `data_blob_*`, `IVAL`, `CVAL`, `SVAL`, `GUID_from_string`, `GUID_string2`, and NT time comparison helpers.

## Printer Fixture Flow

`torture_rpc_spoolss_printer_setup`, `torture_rpc_spoolss_printerex_setup`, `torture_rpc_spoolss_printerwkn_setup`, and `torture_rpc_spoolss_printerexwkn_setup` allocate a `torture_printer_context`, set whether `AddPrinterEx` and well-known-printer modes should be used, set the printer name, and delegate to `torture_rpc_spoolss_printer_setup_common` from the preceding chunk. The common setup path may upload and register a printer driver before adding the test printer. The well-known printer setup variants currently call `torture_skip` before delegating, so the level-1 well-known add paths are intentionally disabled.

`torture_rpc_spoolss_printer_teardown_common` reverses the fixture. For non-well-known printers it deletes the opened printer, re-enumerates local printers, and asserts the name is gone. If setup added a driver, teardown first removes uploaded driver files with `remove_printer_driver`, then also calls `DeletePrinterDriverEx` with `DPD_DELETE_ALL_FILES`. Teardown deliberately warns rather than immediately failing on driver cleanup errors after the printer-delete phase, because leaked test driver files should be reported but should not hide the primary cleanup path. The public teardown wrapper frees the fixture with `talloc_free`.

## Printer Test Control Flow

Most printer test entry points are thin fixture-aware wrappers registered by `torture_tcase_printer`. They fetch the `torture_printer_context`, obtain `p->binding_handle`, and call lower-level helpers with assertions:

- `test_print_test`, `test_print_test_extended`, and `test_print_test_properties` pause the printer, create or inspect jobs, and resume it. The extended test downgrades a failure to skip for Samba3 targets. The properties test skips Samba3 and Samba4 targets.
- `test_print_test_smbd` connects to static printer share `print1` over SMB2, creates a file named `smbd_spooler_job`, writes payload bytes, then verifies `EnumJobs` over `spoolss` can see a job with that document name. It intentionally avoids dynamically added printers because different spoolss worker processes may observe the new printer at different times.
- `test_print_test_purge` pauses the printer, creates eight jobs, asserts the queue length is eight, purges the printer, asserts the queue is empty, and resumes.
- `test_printer_sd`, `test_printer_dm`, `test_printer_info_winreg`, `test_printer_change_id`, `test_printer_keys`, `test_printer_data_consistency`, `test_printer_data_keys`, `test_printer_data_values`, `test_printer_data_set`, `test_printer_data_winreg`, and `test_printer_data_dsspooler` delegate to earlier helper coverage for printer security descriptors, devmode, registry synchronization, change IDs, key enumeration, data enumeration, and data mutation.
- `test_printer_ic` skips Samba targets, creates a printer information context, probes `PlayGDIScriptOnPrinterIC` with undersized buffers expecting `WERR_NOT_ENOUGH_MEMORY`, then succeeds with a 4-byte font-count buffer and again with enough space for all `UNIVERSAL_FONT_ID` entries before deleting the GDI handle.
- `test_printer_bidi` skips Samba targets, verifies an arbitrary BIDI action returns `WERR_NOT_SUPPORTED`, and only continues to schema enumeration if the printer has `PRINTER_ATTRIBUTE_ENABLE_BIDI`.
- `test_printer_publish_toggle` reads levels 7 and 2, then toggles publish state through `SetPrinter` level 7. Its helpers validate both level-2 `PRINTER_ATTRIBUTE_PUBLISHED` and level-7 action/GUID behavior, including pending publish/unpublish states.
- `test_print_job_enum` purges first, verifies level 1 and 2 enumeration on an empty queue, verifies invalid level 100 returns `WERR_INVALID_LEVEL`, creates eight jobs, repeats the enumeration assertions, deletes each job, and resumes.
- `test_printer_log_jobinfo` directly calls `LogJobInfoForBranchOffice` with zero, one, and forty-two branch-office job-data entries, expecting invalid parameter for an empty container and success for populated containers.
- `test_printer_os_versions` compares `GetPrinter` level 0 version bytes with the server's `OSVersion` printer data value decoded as `spoolss_OSVersion`.

## Suite Registration

`torture_tcase_printer` is the shared per-printer test registrar. It adds open-printer, set-printer, print-job, printer-info, security descriptor, devmode, registry, change-id, printer-data, driver-registry, rename, GDI IC, BIDI, publish-toggle, job enumeration, branch-office job logging, and OS-version tests to an existing `torture_tcase`.

`torture_rpc_spoolss_printer` creates the `printer` suite and adds separate fixture cases for `addprinter`, `addprinterex`, `addprinterwkn`, and `addprinterexwkn`. Only the normal and Ex cases get the full `torture_tcase_printer` registration in this chunk; well-known cases are fixture-created but skipped by setup.

`torture_rpc_spoolss` creates the top-level `spoolss` suite. It registers many print-server tests from earlier chunks under a `printserver` tcase and then adds the printer suite. This is the integration point that makes the printer fixture tests part of the public spoolss torture suite.

## Driver Add/Delete Helpers

`test_GetPrinterDriverDirectory_getdir` implements the common two-call "query needed buffer, then retry" pattern for `GetPrinterDriverDirectory` level 1 and returns the directory name when requested.

`get_driver_from_info` and `get_environment_from_info` normalize `spoolss_AddDriverInfoCtr` levels into driver name and architecture strings for logging. They support levels 1, 2, 3, 4, 6, and 8, matching the add-driver matrix in this chunk.

`test_AddPrinterDriver_exp` and `test_AddPrinterDriverEx_exp` are direct RPC wrappers that assert NT transport success and compare the returned `WERROR` to the caller's expected result. Level-specific helpers build the relevant `spoolss_AddDriverInfo*` structure:

- Level 1 is expected to fail with `WERR_INVALID_LEVEL` even after `driver_name` is set.
- Level 2 progressively fills required fields and expects `WERR_INVALID_PARAMETER` until `config_file` is present, then expects success. For `AddPrinterDriverEx`, a zero flag call near the end is still expected to be invalid.
- Levels 3 and 4 are supported by both normal and Ex APIs and verify that enumerated paths begin with the remote driver directory when a reference directory is supplied.
- Levels 6 and 8 are only valid for `AddPrinterDriverEx`; normal `AddPrinterDriver` should return `WERR_INVALID_LEVEL`. For Ex, the tests verify enumeration, path prefixes, driver date, and driver version.

`test_DeletePrinterDriver_exp` and `test_DeletePrinterDriverEx_exp` wrap the delete RPCs. `test_DeletePrinterDriver` and `test_DeletePrinterDriverEx` add behavioral checks around them: deletion with environment `FOOBAR` must fail with `WERR_INVALID_ENVIRONMENT`, deletion with the real environment must succeed, subsequent enumeration should not find the driver, and a second delete must return `WERR_UNKNOWN_PRINTER_DRIVER`.

`test_PrinterDriver_args` is the central add/delete matrix dispatcher. It calls the level-specific add helper, skips deletion for level 1 and for non-Ex level 6/8 cases, opens a separate `winreg` pipe, checks driver registry state via `test_GetDriverInfo_winreg`, and then deletes with the matching normal or Ex delete helper.

## Driver File and Directory Flow

`fillup_printserver_info` opens the print server, obtains the remote server environment, closes the handle, then fetches the print driver directory for either the requested local environment or the discovered remote environment. This populates `d->remote.environment` and `d->remote.driver_directory`.

`driver_directory_dir` returns the final path component after the last backslash in a driver directory. `driver_directory_share` parses a UNC path to extract the SMB share name. `CREATE_PRINTER_DRIVER_PATH` builds a full remote path under a temporary upload directory.

`create_printer_driver_directory` optionally creates a per-test upload directory under the remote architecture directory. `upload_printer_driver_file` maps a possibly path-qualified driver file to a local file under `d->local.driver_directory`, opens the remote destination, streams local bytes in 64,512-byte chunks, and closes the remote handle. `upload_printer_driver` connects to the driver share, optionally creates the upload directory, and uploads driver, data, config, help, and dependent files.

`check_printer_driver_file` verifies a copied driver file in the versioned destination directory `<arch-dir>\<version>\<file>`. `check_printer_driver_files` applies that check to all files in `d->info8` and compares the result against `expect_exist`.

`remove_printer_driver_file` unlinks an uploaded source file from the driver share. `remove_printer_driver` removes each uploaded file, avoiding duplicate unlinks for config/dependent files that alias another file name.

## Driver Test Cases

`test_add_driver_arg` is the main test runner for one driver context. It fills remote server info, skips if local CUPS driver files are missing, uploads files, tests add/delete at levels 1, 2, 3, 4, 6, and 8 using bare file names, rewrites paths to full UNC driver-directory paths, repeats the level matrix, removes uploaded files, and returns the accumulated result. It skips levels 2 and 4 for Samba targets and level 8 for Windows Server 2003 targets.

`test_add_driver_ex_64`, `test_add_driver_ex_32`, `test_add_driver_64`, and `test_add_driver_32` create x64 and NT x86 driver contexts using `/usr/share/cups/drivers/x64` or `/usr/share/cups/drivers/i386`, driver files `pscript5.dll`, `cups6.ppd`, and `cupsui6.dll`, and select normal or Ex API behavior with different driver names.

`test_add_driver_adobe` and `test_add_driver_adobe_cupsaddsmb` are Samba3-only Windows 4.0 driver tests using Adobe-style driver files. The cupsaddsmb variant includes help, monitor, datatype, and a dependent file array.

`test_add_driver_timestamps` tests Ex driver date persistence twice: first with the current time converted to NT time and then with a one-second Unix timestamp converted to NT time.

`test_multiple_drivers` uploads one shared set of local files, registers three drivers with distinct names, deletes them one at a time, and asserts deleting one driver does not remove the others from enumeration.

`test_driver_copy_from_directory` builds a unique remote upload subdirectory from a GUID, sets `APD_COPY_NEW_FILES | APD_COPY_FROM_DIRECTORY | APD_RETURN_BLOCKING_STATUS_CODE`, adds a driver using full remote paths, deletes with `DPD_DELETE_ALL_FILES`, and verifies the versioned copied files no longer exist. x64 and x86 wrappers provide architecture-specific cases.

`test_del_driver_all_files` adds an Ex x64 driver with dependent files, deletes with `DPD_DELETE_ALL_FILES`, and verifies all copied driver files are gone.

`test_del_driver_unused_files` adds two x64 Ex drivers with overlapping files. It expects `DPD_DELETE_ALL_FILES` on the first driver to fail with `WERR_PRINTER_DRIVER_IN_USE`, then expects `DPD_DELETE_UNUSED_FILES` to delete only non-overlapping files. It confirms the second driver's files remain, deletes the second driver with `DPD_DELETE_ALL_FILES`, and confirms its files are gone.

`torture_rpc_spoolss_driver` registers the driver suite as an RPC interface tcase for `ndr_table_spoolss`, adding all normal, Ex, Adobe, timestamp, multiple-driver, copy-from-directory, and delete-file-semantics tests.

## State and Persistence Behavior

The tests intentionally create persistent server-side state: printers, print jobs, printer data values, published-printer attributes, driver registry entries, driver files in print$-style shares, and versioned driver files copied by the spooler. State is cleaned in fixture teardowns and per-driver test cleanup, but failures can leave server artifacts. The code mitigates this by using fixed torture names for predictable cleanup, GUID-named temporary upload directories for copy-from-directory tests, delete-after-add checks, purge-before-job-enum checks, and duplicate-file guards during manual source-file unlinking.

Printer handles and server handles are explicit `policy_handle` values that must be closed or invalidated by delete/close helpers. Driver file upload state is not tracked in an external manifest; it is reconstructed from `torture_driver_context` fields during removal and verification. Memory ownership is mainly `talloc`-scoped to `tctx` or per-driver contexts.

## Dependencies and Integration Points

This chunk integrates the Samba torture framework, DCE/RPC generated spoolss and winreg clients, NDR decoding, SMB client libraries, loadparm client options, command-line credentials, event contexts, and target-specific torture settings such as `samba3`, `samba4`, `w2k3`, and `host`.

It assumes a target server with spoolss enabled, available static printer share `print1` for the SMB2 spooling test, accessible print driver share derived from `GetPrinterDriverDirectory`, and local driver fixture files under `/usr/share/cups/drivers/...` for driver upload tests. Some tests are deliberately skipped for Samba or older Windows targets where the expected behavior differs or support is incomplete.

## Risks and Edge Cases

- The SMB2 spooling test documents a race between dynamically added printers and separate spoolss worker processes, so it hard-codes `TORTURE_PRINTER_STATIC1`.
- Many driver tests depend on local CUPS driver files. Missing files cause skips, reducing coverage silently unless the test environment tracks skips.
- Fixed driver names such as `torture_driver_add`, `torture_driver_ex`, and `torture_driver_deleter` can collide with leftovers from failed prior runs.
- Cleanup is best effort in some paths. Driver file removal warnings during fixture teardown may leave remote files or registry entries.
- `upload_printer_driver_file` logs read/write warnings and breaks its loop, but still proceeds to close and return success unless later assertions fail, so partial file uploads may produce add-driver failures farther downstream.
- Path-prefix assertions check that returned paths start with the driver directory, but they do not canonicalize case, separators, or equivalent UNC forms.
- Delete-file tests are sensitive to server-side reference counting for shared files. Incorrect overlap modeling or stale server state can change expected `WERR_PRINTER_DRIVER_IN_USE` and file-existence outcomes.
- Publish/unpublish checks allow pending states, reflecting asynchronous directory publishing behavior.

## Test Signals

Strong success signals are returned `WERROR` values, transport `NTSTATUS`, enumeration counts, exact job counts, post-delete enumeration misses, registry verification through a separate `winreg` pipe, driver path-prefix checks, driver timestamp/version equality, BIDI and GDI buffer-size responses, OS version equality between `GetPrinter` level 0 and `OSVersion` printer data, and SMB file existence checks after delete flags.

The main failure signals are `torture_assert*` failures, `torture_fail` for leaked deleted drivers or remote-file open failures, and skips for unsupported Samba/Windows target combinations or missing local driver directories. The chunk's suite registration exposes these signals through the Samba torture runner under `spoolss`, `spoolss.printer`, and `spoolss.driver`.
