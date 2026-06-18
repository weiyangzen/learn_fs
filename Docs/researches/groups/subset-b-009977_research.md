# Research Group subset-b-009977

This grouped report covers Samba NDR torture sources under `sources/user-network-fs/samba/source4/torture/ndr/`. Each section is bounded for reconciliation into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ntprinting.c -->
# sources/user-network-fs/samba/source4/torture/ndr/ntprinting.c

## Purpose

`ntprinting.c` is a Samba torture-suite fixture for validating NDR unmarshalling of the generated `ntprinting_printer` type. It embeds captured printer metadata blobs and checks that Samba decodes classic NT printing state, `DEVMODE` fields, private driver data, registry-like printer data entries, and DOS-codepage-sensitive strings.

## Important APIs, Types, and Functions

- Includes `torture/ndr/ndr.h`, `librpc/gen_ndr/ndr_ntprinting.h`, `torture/ndr/proto.h`, and `param/param.h`.
- `ntprinting_printer_data` is the main captured binary fixture for a Kyocera printer.
- `ntprinting_printer_data_latin1` is a second fixture aimed at non-ASCII printer metadata and codepage handling.
- `ntprinting_printer_check()` validates the decoded `struct ntprinting_printer`, especially `info`, `devmode`, `nt_dev_private`, `count`, and `printer_data[]`.
- `ntprinting_printer_latin1_check()` manually builds a `DATA_BLOB`, sets `dos charset` to `CP1252`, calls `reload_charcnv()`, and invokes `ndr_pull_struct_blob()` with `ndr_pull_ntprinting_printer`.
- `ndr_ntprinting_suite()` registers a simple Latin-1 conversion test and a generated pull test through `torture_suite_add_simple_test()` and `torture_suite_add_ndr_pull_test()`.

## Control Flow

The suite constructor creates the `ntprinting` suite, registers the explicit Latin-1 path first, then registers the normal NDR pull fixture. The normal fixture is handled by the torture NDR framework, which pulls `ntprinting_printer_data` using generated NDR code and calls `ntprinting_printer_check()`. The Latin-1 path is not a generated-test macro wrapper: it mutates loadparm character conversion state, prepares `r.info.string_flags = LIBNDR_FLAG_STR_ASCII`, pulls the blob, and asserts selected decoded strings.

`ntprinting_printer_check()` is assertion-heavy and mostly linear. It checks scalar printer info, server/printer/share/port/driver strings, `DEVMODE` dimensions and flags, the private driver data length, then all 11 `printer_data` entries by pointer marker, registry-style name, type, and data length.

## State and Persistence Behavior

The file has no persistent storage and performs no network or filesystem I/O. Runtime state is limited to static byte arrays, decoded structures allocated by the torture framework, and a temporary loadparm character-conversion configuration change in `ntprinting_printer_latin1_check()`. That function does not restore the previous charset before returning, so it relies on test-suite isolation or later tests being robust to the modified `lp_ctx`.

## Dependencies and Integration Points

The test depends on Samba generated NDR for `ntprinting`, the torture assertion framework, TALLOC/DATA_BLOB helpers, and loadparm character conversion helpers. It integrates into the broader NDR torture registry through `ndr_ntprinting_suite()`, whose name is used by the test runner. The fixture is tightly coupled to generated parser semantics for ASCII strings, embedded private driver blobs, and `DEVMODE` layout.

## Risks and Edge Cases

- The Latin-1 check mutates global-ish configuration on `tctx->lp_ctx`; missing restoration can make failures order-dependent if another test reuses the context.
- The main fixture validates many decoded fields but does not fully inspect raw private driver data contents, only its length.
- A disabled pull-validate test documents that pull-push validation was not working at the time, so round-trip encoding is not covered.
- Hard-coded captured data can become stale if IDL definitions intentionally change; failures will need triage between parser regression and fixture drift.

## Test Signals

Strong signals include exact scalar/string assertions, 11 printer-data entry checks, private-driver length validation, and a targeted codepage conversion test. Weaker signals are the disabled pull-validate path and partial inspection of opaque private driver data. A relevant validation command would be the Samba NDR torture suite filtered to `ntprinting`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/ntprinting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/odj.c -->
# sources/user-network-fs/samba/source4/torture/ndr/odj.c

## Purpose

`odj.c` is a fixture for Windows Offline Domain Join provisioning data. It verifies that the generated ODJ NDR parser can pull a captured `ODJ_PROVISION_DATA_serialized_ptr` blob without error.

## Important APIs, Types, and Functions

- Includes `torture/ndr/ndr.h`, `librpc/gen_ndr/ndr_ODJ.h`, and `torture/ndr/proto.h`.
- `ODJ_PROVISION_DATA_data` embeds one serialized offline-join provisioning sample containing nested ODJ structures, Unicode strings, GUIDs, SID data, domain/controller names, and provisioning metadata.
- `ODJ_PROVISION_DATA_check()` receives `struct ODJ_PROVISION_DATA_serialized_ptr *` and currently returns `true` without semantic assertions.
- `ndr_ODJ_suite()` creates suite `ODJ` and registers one `torture_suite_add_ndr_pull_test()` for `ODJ_PROVISION_DATA_serialized_ptr`.

## Control Flow

The torture runner calls `ndr_ODJ_suite()`, which registers the static blob with the generated NDR pull framework. The framework decodes the blob into `ODJ_PROVISION_DATA_serialized_ptr` and then invokes `ODJ_PROVISION_DATA_check()`. Since the callback is a no-op success, the effective test result is pass/fail on parser acceptance and memory-safe traversal rather than field-level correctness.

## State and Persistence Behavior

There is no persistent state, no external I/O, and no mutable global state. All input is static in the binary, and decoded state is owned by the torture framework/TALLOC context.

## Dependencies and Integration Points

This file depends on generated ODJ NDR headers and the generic NDR torture helpers. It integrates with Samba's NDR test registry through `ndr_ODJ_suite()` and exercises the ODJ IDL-generated pull code rather than any live domain-join service.

## Risks and Edge Cases

- The check callback does not assert decoded domain names, SIDs, GUIDs, counts, pointer presence, or nested provisioning items. A parser could map fields incorrectly and still pass if it consumes the blob successfully.
- The fixture is a single captured example, so alternate ODJ versions, absent sections, malformed lengths, and error paths are not covered here.
- Because the data includes pointer-heavy serialized structures, changes in conformant-array or pointer semantics may produce broad failures that are hard to localize without additional assertions.

## Test Signals

The main signal is that `ODJ_PROVISION_DATA_serialized_ptr` can be unmarshalled from a realistic captured blob. Semantic test strength is low because `ODJ_PROVISION_DATA_check()` is empty. Future improvements should assert top-level counts, domain/computer strings, SID/GUID fields, and selected nested buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/odj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/samr.c -->
# sources/user-network-fs/samba/source4/torture/ndr/samr.c

## Purpose

`samr.c` validates NDR parsing for selected SAMR RPC request and response payloads. It embeds captured wire blobs for connection, domain, user, password, and handle operations, with one detailed semantic check for a password-change rejection response.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_samr.h` and the generic torture NDR helpers.
- Static fixtures cover `samr_Connect5`, `samr_OpenDomain`, `samr_LookupNames`, `samr_OpenUser`, `samr_QueryUserInfo`, `samr_SetUserInfo`, `samr_SetUserInfo2`, `samr_GetUserPwInfo`, `samr_Close`, and `samr_ChangePasswordUser3`.
- `samr_changepassworduser3_w2k8r2_out_check()` validates `samr_DomInfo1`, `userPwdChangeFailureInformation`, and the final `NT_STATUS_PASSWORD_RESTRICTION`.
- `ndr_samr_suite()` registers input-only, output-only, and input/output pull tests using `torture_suite_add_ndr_pull_fn_test()` and `torture_suite_add_ndr_pull_io_test()`.

## Control Flow

The suite constructor registers each captured blob against its generated SAMR operation type and NDR direction. Most registered tests pass `NULL` as the semantic callback, so they check successful decoding only. `samr_QueryUserInfo` also has an input/output registration to validate combined call semantics. For `samr_ChangePasswordUser3`, the W2K request is decoded, a W2K response fixture is disabled, and the W2K8R2 rejection response is decoded with a callback that validates password policy fields and rejection reason.

## State and Persistence Behavior

The source is stateless apart from static fixtures. It does not contact SAMR, mutate account state, store handles, or persist results. Policy handles, SIDs, encrypted password buffers, and status codes are represented only as captured bytes decoded into generated structs.

## Dependencies and Integration Points

The file integrates generated SAMR NDR parsers with the NDR torture suite. It depends on SAMR constants such as `DOMAIN_PASSWORD_COMPLEX`, `SAM_PWD_CHANGE_NOT_COMPLEX`, and NTSTATUS comparison helpers. It exercises client/server marshalling contracts, not SAM database implementation logic.

## Risks and Edge Cases

- Most operations only verify that decoding succeeds; they do not assert handle UUIDs, access masks, RIDs, encrypted buffer sizes, or status values.
- The disabled W2K `ChangePasswordUser3` response notes a known parser failure or unsupported shape, leaving historical compatibility uncovered.
- Large encrypted payload fixtures are opaque; corruption inside fixed-size password buffers may not be detected unless parser length handling fails.
- Changes to SAMR IDL unions or password-info layouts can break these fixtures, but sparse assertions may not localize the changed field.

## Test Signals

The suite provides broad parser smoke coverage over common SAMR operations and one strong semantic check for password-policy rejection details. It is best interpreted as NDR compatibility coverage for captured traffic, with limited business-logic validation. Relevant signals are successful NDR pull of all registered blobs and exact assertions in `samr_changepassworduser3_w2k8r2_out_check()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/spoolss.c -->
# sources/user-network-fs/samba/source4/torture/ndr/spoolss.c

## Purpose

`spoolss.c` is a large NDR torture fixture for Samba's print-spooler RPC IDL. It decodes captured `spoolss` and `winspool_Async*` request/response blobs for printer open/close/query/data/driver/key/form/notification/job/property operations, including classic NDR and NDR64 paths.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_spoolss.h` through the generated torture interfaces, plus generic torture helpers and printing/security-related generated types.
- Static fixtures cover `OpenPrinterEx`, `ClosePrinter`, `GetPrinter`, `GetPrinterData`, `ReplyOpenPrinter`, `ReplyClosePrinter`, `RemoteFindFirstPrinterChangeNotifyEx`, `RouterRefreshPrinterChangeNotify`, `EnumForms`, `EnumPrinterDataEx`, `EnumPrinterKey`, `FindClosePrinterNotify`, `GetPrinterDriverDirectory`, `AddPrinterDriverEx`, `GetPrinterDriver2`, `SetPrinter`, `GetCorePrinterDrivers`, and `SetJobNamedProperty`.
- Async equivalents are registered for many operations: `winspool_AsyncOpenPrinter`, `AsyncClosePrinter`, `AsyncGetPrinter`, `AsyncGetPrinterData`, `AsyncEnumForms`, `AsyncEnumPrinterDataEx`, `AsyncEnumPrinterKey`, `AsyncGetPrinterDriverDirectory`, `AsyncAddPrinterDriver`, `AsyncGetPrinterDriver`, `AsyncSetPrinter`, `AsyncGetCorePrinterDrivers`, and `AsyncSetJobNamedProperty`.
- `getprinterdriver2_in_check()` asserts architecture, info level, offered buffer size, and client version values.
- `getprinterdriver2_out_check()` deeply validates a level-6 Ricoh x64 driver response, paths, dependent files, version fields, manufacturer/provider metadata, needed size, server version outputs, and `WERR_OK`.
- `setjobnamedproperty_req_check()` validates job id and `SPLFILE_CONTENT_TYPE_*` named-property decoding.
- `setprinter_level_3_xpsp3_req_check()` validates a policy handle GUID, level-3 info, empty devmode, and security descriptor container details.
- `ndr_spoolss_suite()` registers dozens of pull and pull-IO tests, including `LIBNDR_FLAG_NDR64` variants.

## Control Flow

The suite constructor is a long linear registration table. For each captured operation, it registers request, response, or paired request/response blobs with the generated NDR pull framework. Many operations are registered twice: once for synchronous `spoolss_*` and once for equivalent async `winspool_Async*` forms. The NDR64 cases use `torture_suite_add_ndr_pull_fn_test_flags()` to force `LIBNDR_FLAG_NDR64`.

Most tests rely on successful decode as the assertion. A smaller set invokes explicit callbacks for high-value structures: `GetPrinterDriver2`, `SetJobNamedProperty`, and an XP SP3-style `SetPrinter` level-3 security descriptor. Combined IO tests validate direction-sensitive request/response parsing for buffer-size negotiation and result handling.

## State and Persistence Behavior

The file has no live spooler state. Handles, printer names, driver paths, form data, registry-key names, security descriptors, and job properties are static captured wire representations. No printer configuration is changed and no files are read from print shares. Decoded state lives only for the duration of each torture test.

## Dependencies and Integration Points

This is an integration point between Samba's generated spoolss/winspool NDR parsers and the torture test harness. It also indirectly depends on generated constants for driver versions, property names, RPC property value types, security descriptor fields, WERROR helpers, GUID parsing, and NDR64 support. Because the same blobs are registered against sync and async RPC shapes, it helps detect divergence between related IDL definitions.

## Risks and Edge Cases

- The file is fixture-heavy; many registered tests have `NULL` callbacks and only prove that parsing completes.
- Some complex data, such as printer data blobs, driver private data, and security ACL contents, is only partially validated.
- Hard-coded server/printer names, UNC paths, driver versions, and GUIDs encode historical Windows behavior. Intentional IDL normalization can cause noisy fixture failures.
- NDR64 coverage is valuable but narrow: it covers selected open, set, and core-driver requests, not every response or error variant.
- The large source size and many byte arrays make maintenance error-prone; adding or editing fixtures without semantic callbacks can reduce regression value.

## Test Signals

Strongest signals are the explicit checks for `GetPrinterDriver2` level 6, named job property decoding, XP SP3 `SetPrinter` security descriptor parsing, paired IO tests for buffer negotiation, and dual sync/async registrations. Weaker signals are decode-only fixtures. The relevant validation surface is the Samba NDR torture suite filtered to `spoolss`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/spoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/string.c -->
# sources/user-network-fs/samba/source4/torture/ndr/string.c

## Purpose

`string.c` tests low-level NDR string push/pull behavior across ASCII, UTF-8, raw 8-bit, null-terminated, non-terminated, and charset-conversion scenarios. Unlike the other files in this group, it exercises generic NDR string primitives directly rather than generated RPC operation fixtures.

## Important APIs, Types, and Functions

- Includes `torture/ndr/ndr.h`, `torture/ndr/proto.h`, `../lib/util/dlinklist.h`, and `param/param.h`.
- Static string fixtures are `ascii`, `latin1`, and `utf8`, with byte arrays used to avoid source-encoding dependence.
- Flag aliases include `fl_ascii_null`, `fl_ascii_noterm`, `fl_utf8_null`, and `fl_raw8_null`.
- `test_ndr_push_string()` creates an `ndr_push`, sets string flags, calls `ndr_push_string()`, checks the expected `ndr_err_code`, output offset, data pointer, and byte comparison behavior.
- `test_ndr_pull_string()` creates a `DATA_BLOB` with `data_blob_string_const()`, initializes `ndr_pull`, calls `ndr_pull_string()`, and checks expected status/result comparison.
- `torture_ndr_string()` runs the push/pull matrix and temporarily changes `dos charset` between `ASCII`, `CP850`, and the saved original.
- `ndr_string_suite()` registers a simple test named `ndr_string` and sets a description.

## Control Flow

`torture_ndr_string()` saves the current DOS charset, runs push tests for valid ASCII, empty strings, UTF-8, raw8, Latin-1 raw8, and invalid ASCII conversions, then runs pull tests for valid ASCII/UTF-8/raw8 cases. It then forces `dos charset=ASCII` and expects Latin-1/UTF-8 under ASCII flags to fail with `NDR_ERR_CHARCNV`. Next it forces `dos charset=CP850` and expects success but string mismatch for the same malformed input combinations. Finally it restores the saved charset and reloads conversion tables.

The helper functions centralize allocation, flag setup, NDR primitive calls, expected-error checking, and comparison semantics. They free their temporary TALLOC contexts before returning.

## State and Persistence Behavior

There is no persistent state, but the test intentionally mutates `torture->lp_ctx` global parameters and reloads character conversion state. It preserves and restores the original `dos charset`, so state leakage risk is lower than in similar code that does not restore. Temporary NDR buffers are TALLOC-owned and freed in each helper.

## Dependencies and Integration Points

The file exercises the generic libndr string implementation and Samba's character conversion layer. It depends on loadparm mutation (`lpcfg_do_global_parameter()`), `reload_charcnv()`, NDR push/pull initialization helpers, and torture assertion macros. It provides regression coverage for callers throughout Samba that rely on `LIBNDR_FLAG_STR_*` semantics.

## Risks and Edge Cases

- Expected behavior depends on charset conversion tables and runtime loadparm behavior; environment or library changes can alter success/failure modes.
- The tests compare byte/string equality for simple cases but do not exhaustively validate UTF-16 or conformant-varying string encodings.
- `test_ndr_push_string()` uses `strlen()` to compute expected offsets, so it is intentionally scoped to single-byte output modes covered by the selected flags.
- A failure before restoration could leave the test context charset changed unless the torture framework tears it down.

## Test Signals

This file has strong unit-style signals: explicit expected `NDR_ERR_SUCCESS` and `NDR_ERR_CHARCNV`, output length checks, null/non-null output checks, and equality/mismatch checks under multiple string flag combinations. It is the most direct regression test in this group for character conversion behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/svcctl.c -->
# sources/user-network-fs/samba/source4/torture/ndr/svcctl.c

## Purpose

`svcctl.c` validates NDR parsing for the Service Control Manager `ChangeServiceConfigW` request and response. It focuses on a captured request that changes service type/start/error-control fields while leaving optional strings and dependency/password fields null.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_svcctl.h`, `torture/ndr/ndr.h`, `torture/ndr/proto.h`, and `param/param.h`.
- `svcctl_ChangeServiceConfigW_req_data` is the request fixture.
- `svcctl_ChangeServiceConfigW_req_check()` builds an expected `policy_handle` UUID with `GUID_from_string()`, then asserts handle UUID, service type, `SVCCTL_AUTO_START`, `SVCCTL_SVC_ERROR_NORMAL`, null optional strings, null `tag_id`, and zero dependency/password sizes.
- `svcctl_ChangeServiceConfigW_rep_data` is the response fixture.
- `svcctl_ChangeServiceConfigW_rep_check()` asserts null output `tag_id` and `WERR_OK`.
- `ndr_svcctl_suite()` registers request and response pull tests for `svcctl_ChangeServiceConfigW`.

## Control Flow

The suite constructor creates suite `svcctl`, registers the request blob as `NDR_IN` with the request check callback, then registers the response blob as `NDR_OUT` with the response check callback. The request callback is linear and covers every decoded input field present in the call shape. The response callback covers the output pointer and result status.

## State and Persistence Behavior

No service is contacted or modified. The service handle and configuration fields are static captured wire data. Decoded objects are transient inside the torture framework.

## Dependencies and Integration Points

This test integrates the generated SVCCTL NDR parser with Samba's NDR torture harness. It depends on GUID parsing, service-control constants, WERROR assertions, and generated `struct svcctl_ChangeServiceConfigW` direction-specific members.

## Risks and Edge Cases

- Coverage is limited to one operation and one shape of optional-field usage.
- It validates null optional fields well, but does not cover non-null binary path, dependencies multi-string handling, password buffers, display names, or failure statuses.
- `GUID_from_string()` return status is not asserted before using the UUID, although the literal is fixed and expected to parse.

## Test Signals

This file gives a strong semantic signal for one `ChangeServiceConfigW` request/response pair: field-level assertions cover handle identity, enum values, null pointers, size fields, and success status. It is narrow but precise.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/svcctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/winreg.c -->
# sources/user-network-fs/samba/source4/torture/ndr/winreg.c

## Purpose

`winreg.c` is a broad NDR torture fixture for Windows Remote Registry RPC operations. It decodes captured request/response blobs for key open/close/create/delete/flush/query/enumeration/notification APIs and asserts selected handle, string, buffer, metadata, and result-code fields.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_winreg.h`, `librpc/gen_ndr/ndr_security.h`, `libcli/security/security.h`, and generic NDR torture helpers.
- Fixtures cover `winreg_CloseKey`, `OpenHKLM`, `CreateKey`, `EnumValue`, `QueryValue`, `QueryMultipleValues`, `QueryMultipleValues2`, `FlushKey`, `OpenKey`, `DeleteKey`, `GetVersion`, `QueryInfoKey`, `NotifyChangeKeyValue`, and `EnumKey`.
- Disabled fixtures/checks exist for `QueryInfoKey` output and `GetKeySecurity` input/output.
- Check callbacks validate details such as policy-handle presence/type, `OpenHKLM` system/access mask, key name `spottyfoot`, value name `HOMEPATH`, value name `TEMP`, type/size/length pointers, `WERR_INVALID_PARAMETER`, `WERR_FILE_NOT_FOUND`, `WERR_MORE_DATA`, version `5`, notify flags, and enum-key metadata.
- `ndr_winreg_suite()` registers the fixtures with `torture_suite_add_ndr_pull_fn_test()` or `torture_suite_add_ndr_pull_io_test()`.

## Control Flow

The suite constructor is a linear registration table. Each operation gets one or more direction-specific tests. Simple request/response cases use separate `NDR_IN` and `NDR_OUT` registrations; buffer-negotiating calls such as `QueryMultipleValues` and `QueryMultipleValues2` use pull-IO tests pairing request and response fixtures. Some fixtures are registered with `NULL` callbacks when decode-only coverage is intended, such as one alternate `EnumValue` input.

Callbacks are operation-specific and generally validate the highest-value decoded fields without trying to model registry semantics. Several comments mark known gaps such as unchecked parent handles, output buffers, or last-change timestamps.

## State and Persistence Behavior

The file does not access a live registry and does not persist any key/value changes. All registry handles, names, classes, data buffers, security descriptors, and result codes are captured byte arrays. Decoded state is transient and owned by the torture runner.

## Dependencies and Integration Points

This file integrates generated winreg NDR types with the torture framework and security helpers. It depends on WERROR constants, GUID-zero checks, registry string containers, buffer-size pointer semantics, and generated request/response unions. It is a compatibility layer test for Samba's remote-registry marshalling contract, not the registry server implementation.

## Risks and Edge Cases

- Some important semantic fields are explicitly marked `FIXME`, including parent handles, some output buffers, and timestamps.
- `QueryInfoKey` output and `GetKeySecurity` tests are disabled, so security descriptor and key-info response coverage is incomplete.
- Several tests assert pointer presence and sizes but not the full pointed-to buffer content.
- Captured pointer-looking values and historical Windows layouts can be brittle if generated IDL alignment or pointer policy changes.

## Test Signals

The suite provides good breadth across remote-registry NDR operations and moderate semantic depth for key names, value names, buffer sizing, and result codes. Stronger signals come from `EnumValue`, `QueryValue`, `QueryMultipleValues`, `OpenKey`, `DeleteKey`, `NotifyChangeKeyValue`, and `EnumKey` callbacks. Weaker areas are disabled security/key-info responses and callbacks that intentionally leave handle/buffer validation as future work.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/winreg.c -->
