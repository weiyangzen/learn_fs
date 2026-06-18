# subset-b-009974 research

Grouped research for Samba `source4/torture/ndr` fixtures covering BackupKey, Cabinet, charset, Cluster API property lists, and DCE/RPC packet NDR behavior. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/backupkey.c -->
# sources/user-network-fs/samba/source4/torture/ndr/backupkey.c

## Purpose
`backupkey.c` adds a focused Samba torture NDR test for the BackupKey RPC data type `bkrp_exported_RSA_key_pair`. It embeds one captured NDR byte stream, `exported_rsa_ndr`, representing an exported RSA key pair and certificate-like payload, then verifies that Samba's generated BackupKey NDR pull and push routines can parse and re-emit the structure without changing the encoded bytes.

## Important APIs, types, and functions
- `exported_rsa_ndr` is the static binary fixture. The data starts with BackupKey/RSA metadata and includes a large RSA public/private key and X.509-style certificate material.
- `ndr_backupkey_suite(TALLOC_CTX *ctx)` is the exported suite factory consumed by the parent NDR torture suite.
- `torture_suite_create(ctx, "backupkey")` creates the child suite.
- `torture_suite_add_ndr_pull_validate_test(..., bkrp_exported_RSA_key_pair, exported_rsa_ndr, NULL)` registers a pull-and-push validation test using generated functions from `librpc/gen_ndr/ndr_backupkey.h`.

## Control flow
At test-suite construction time, the file creates a `backupkey` suite and registers one generated NDR validation case. The torture helper pulls `exported_rsa_ndr` into `struct bkrp_exported_RSA_key_pair`, optionally prints it through the generated printer, pushes it back through `ndr_push_bkrp_exported_RSA_key_pair`, and compares the result against the original fixture. No custom check callback is supplied, so the behavioral assertion is round-trip fidelity rather than semantic field-by-field validation.

## State and persistence behavior
The file has no mutable process state and no external persistence. The only state is the compile-time `static const` byte array and the transient talloc-backed objects allocated by the shared NDR torture harness when the suite runs.

## Dependencies and integration points
The file depends on Samba's common includes, `torture/ndr/ndr.h` for NDR torture registration macros, generated BackupKey NDR declarations from `ndr_backupkey.h`, and `torture/ndr/proto.h` for suite prototypes. It is integrated into the overall NDR suite by `source4/torture/ndr/ndr.c`, which adds `ndr_backupkey_suite(suite)` under the larger `ndr` test family.

## Risks and edge cases
- Because the custom check callback is `NULL`, regressions that decode to semantically wrong in-memory fields but happen to push back to identical bytes may not be caught.
- The fixture is large cryptographic material; accidental byte edits are hard to review manually and would change test meaning.
- The test covers one exported RSA key pair shape only. It does not exercise malformed BackupKey data, alternate key sizes, or failure paths.
- Round-trip validation is sensitive to intentional encoder canonicalization changes; generated NDR push behavior must preserve this fixture exactly.

## Test signals
The test signal is a successful `backupkey` NDR torture subtest. It proves generated pull/push support for `bkrp_exported_RSA_key_pair` can consume this captured Windows-style BackupKey RSA export and reproduce the same NDR stream.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/backupkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/cabinet.c -->
# sources/user-network-fs/samba/source4/torture/ndr/cabinet.c

## Purpose
`cabinet.c` tests Samba's generated NDR parser for Microsoft Cabinet (`cab_file`) structures. It embeds three complete CAB fixtures: an uncompressed cabinet containing a 32 KiB file of `A` bytes, an MSZIP-compressed version of the same logical file, and an LZX-compressed version. The tests verify header fields, folder/file metadata, data block sizes and checksums, and decompressed content where the implementation supports it.

## Important APIs, types, and functions
- `cab_file_plain_data` is a large static fixture for a `MSCF` cabinet with `CF_COMPRESS_NONE`. Most of the file's 4,335 lines are the 32 KiB literal `A` payload in this array.
- `cab_file_MSZIP_data` is a compact fixture for the same 32 KiB logical file using `CF_COMPRESS_MSZIP`.
- `cab_file_LZX_data` is a compact fixture for the same logical file using LZX compression; the code currently checks metadata but leaves decompressed payload validation disabled.
- `cab_file_plain_check`, `cab_file_MSZIP_check`, and `cab_file_LZX_check` validate the parsed `struct cab_file` fields.
- `ndr_cabinet_suite(TALLOC_CTX *ctx)` registers the cabinet subtests through `torture_suite_add_ndr_pull_test` and one plain round-trip validation via `torture_suite_add_ndr_pull_validate_test`.

## Control flow
The suite registers three pull-only tests, one for each fixture. The shared NDR harness pulls the fixture into `struct cab_file` using generated functions from `librpc/gen_ndr/ndr_cab.h`, then invokes the corresponding check function. The check functions assert the `MSCF` signature, cabinet size, file-table offset, version, folder count, file count, flags, set/cabinet identifiers, folder data offset, number of data blocks, compression type, file size, file offset, folder index, DOS date/time, attributes, filename, data-block checksum, compressed byte count, and uncompressed byte count. For plain and MSZIP fixtures, they allocate a `DATA_BLOB` of 0x8000 bytes, fill it with `A`, and compare it to `r->cfdata[0].ab`. For LZX, the equivalent payload comparison is inside `#if 0` because LZX decompression support is not enabled.

The suite also registers a pull/push validation for the plain fixture. The MSZIP validate test is intentionally commented out because zlib can produce a different but equivalent compressed stream, making byte-for-byte round-trip validation unsuitable for that fixture.

## State and persistence behavior
There is no persistent state. Static fixture arrays are read-only. Check functions allocate temporary `DATA_BLOB` objects using Samba allocation helpers, fill them with deterministic content, compare them, and free them before returning.

## Dependencies and integration points
The file depends on the generic Samba torture/NDR harness, generated Cabinet NDR declarations in `ndr_cab.h`, and constants such as `CF_COMPRESS_NONE` and `CF_COMPRESS_MSZIP`. It is added to the parent NDR test suite by `ndr.c` through `ndr_cabinet_suite(suite)`. The implementation under test is the generated `ndr_pull_cab_file`/`ndr_push_cab_file` path and any Cabinet decompression support it invokes for `cfdata[0].ab`.

## Risks and edge cases
- The enormous plain fixture makes reviews noisy and increases the chance of accidental fixture corruption.
- LZX content validation is explicitly disabled, so the LZX test currently proves header/data-block parsing but not successful decompression.
- MSZIP push validation is disabled because compression output is not byte-stable across zlib behavior; this is intentional but leaves round-trip coverage weaker for compressed cabinets.
- The tests cover a simple one-folder, one-file cabinet only. Multi-folder, multi-file, continuation cabinet, reserved-area, and malformed checksum paths are not represented.
- The LZX check uses the numeric value `4611` for `typeCompress` rather than a named constant, which is less self-documenting and can hide enum/bitfield intent.

## Test signals
Passing tests demonstrate that Samba parses basic CAB headers, CFFOLDER/CFFILE tables, CFDATA metadata, uncompressed data, and MSZIP decompressed data for a deterministic 32 KiB payload. The plain validation subtest additionally proves byte-for-byte pull/push stability for an uncompressed cabinet.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/cabinet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/charset.c -->
# sources/user-network-fs/samba/source4/torture/ndr/charset.c

## Purpose
`charset.c` is a small NDR torture unit for charset push helpers. It verifies how `ndr_push_charset` and `ndr_push_charset_to_null` handle `NULL`, empty, and ordinary strings when encoding UTF-16LE scalar data into an NDR push context.

## Important APIs, types, and functions
- `test_ndr_push_charset(struct torture_context *tctx)` tests `ndr_push_charset(ndr, NDR_SCALARS, str, 256, 2, CH_UTF16LE)`.
- `test_ndr_push_charset_to_null(struct torture_context *tctx)` tests `ndr_push_charset_to_null` with the same bounds and charset.
- `ndr_charset_suite(TALLOC_CTX *ctx)` creates the `charset` suite, sets a descriptive label, and registers `push` and `push_to_null` simple tests.
- The fixture values are `NULL`, `""`, and `"test"`.

## Control flow
Each test allocates a zeroed `struct ndr_push` from the torture context and loops over the three string inputs. `test_ndr_push_charset` expects `NDR_ERR_INVALID_POINTER` only for the `NULL` input and `NDR_ERR_SUCCESS` for empty and non-empty strings. `test_ndr_push_charset_to_null` expects success for all three inputs, documenting that the `_to_null` variant tolerates `NULL`. Assertions use `torture_assert_ndr_err_equal` and `torture_assert_ndr_success`.

## State and persistence behavior
There is no persistent state. The only mutable object is the temporary `struct ndr_push` allocated under `tctx`. The same push context is reused across loop iterations, so the test also implicitly tolerates appending multiple charset encodings into a single push buffer.

## Dependencies and integration points
The file depends on `torture/ndr/ndr.h`, Samba's NDR push implementation, charset constant `CH_UTF16LE`, `ARRAY_SIZE`, and the torture assertion macros. It is linked into the overall NDR suite by `ndr.c` through `ndr_charset_suite(suite)`.

## Risks and edge cases
- The test checks return codes only; it does not inspect the encoded bytes, buffer length, terminator placement, or alignment.
- A single allocation of `struct ndr_push` is made without explicitly initializing all normal push fields beyond zeroing, so the test is narrowly tied to helper behavior that tolerates this setup.
- Only UTF-16LE with element size 2 and max length 256 is covered.
- Reusing one push context means a failure may depend on prior loop iterations if helper state handling changes.

## Test signals
The `push` subtest signals that the raw charset pusher rejects `NULL` and accepts `""`/`"test"`. The `push_to_null` subtest signals that the null-tolerant wrapper accepts all three inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/charset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/clusapi.c -->
# sources/user-network-fs/samba/source4/torture/ndr/clusapi.c

## Purpose
`clusapi.c` validates NDR parsing and round-trip encoding of Windows Cluster API property lists. It embeds two `clusapi_PROPERTY_LIST` byte streams and verifies that Samba decodes property counts, property names, syntaxes, sizes, value buffers, padding, and end markers exactly.

## Important APIs, types, and functions
- `clusapi_PROPERTY_LIST_data` is a six-property fixture with quorum and cluster storage settings: `FixQuorum`, `PreventQuorum`, `IgnorePersistentStateOnStartup`, `SharedVolumesRoot`, `WitnessDynamicWeight`, and `AdminAccessPoint`.
- `clusapi_PROPERTY_LIST_check` validates the first fixture, including DWORD blobs for zero/one values and an SZ value decoded as `C:\ClusterStorage`.
- `clusapi_PROPERTY_LIST_data2` is a twelve-property node/version fixture containing `NodeName`, version/build fields, `CSDVersion`, `NodeInstanceID`, drain fields, `DynamicWeight`, and `NeedsPreventQuorum`.
- `clusapi_PROPERTY_LIST_check2` validates the second fixture, including empty strings, GUID-like strings, DWORDs, and nonzero padding lengths.
- `ndr_clusapi_suite(TALLOC_CTX *ctx)` registers both fixtures as pull/push validation tests for `clusapi_PROPERTY_LIST`.

## Control flow
The suite creates a `clusapi` child suite and adds two `torture_suite_add_ndr_pull_validate_test` cases. For each fixture, the shared NDR harness pulls bytes into `struct clusapi_PROPERTY_LIST`, calls the relevant checker, pushes the structure back out, and validates byte stability. The checkers create expected four-byte `DATA_BLOB` values for DWORD zero, one, and selected version constants using `SIVAL`; they compare raw buffers with `torture_assert_data_blob_equal`. For string property values, they call `pull_reg_sz` to convert registry-style UTF-16LE `REG_SZ` buffers into C strings before comparing.

## State and persistence behavior
The file has no durable state. Static fixtures are immutable. Checkers allocate short temporary `DATA_BLOB` objects and release them with `data_blob_free`; decoded strings are talloc-owned by the torture context through `pull_reg_sz`.

## Dependencies and integration points
Dependencies include generated Cluster API NDR declarations from `librpc/gen_ndr/ndr_clusapi.h`, registry string conversion from `libcli/registry/util_reg.h`, Samba `DATA_BLOB` helpers, `SIVAL`, and NDR torture macros. The parent `ndr.c` test suite integrates this file through `ndr_clusapi_suite(suite)`.

## Risks and edge cases
- The tests assume fixed property ordering and exact byte layout. That is useful for NDR compatibility but does not cover unordered lookup behavior.
- The check functions are long and repetitive; copy/paste mistakes in expected sizes, property indexes, or assertion labels could reduce diagnostic quality.
- Coverage is limited to list-value DWORD and SZ syntaxes represented by the fixtures; other Cluster property syntaxes and malformed lists are not tested here.
- The validators rely on `pull_reg_sz` for string interpretation, so a failure could come from either Cluster API NDR parsing or registry string conversion.

## Test signals
Passing tests show that Samba can decode and byte-stably re-encode real-world Cluster API property lists with mixed DWORD and UTF-16LE string values, including DWORD buffers, padding fields, and `CLUSPROP_SYNTAX_ENDMARK` handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/clusapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/dcerpc.c -->
# sources/user-network-fs/samba/source4/torture/ndr/dcerpc.c

## Purpose
`dcerpc.c` adds regression coverage for DCE/RPC connection-oriented packet NDR parsing, specifically minimal `CO_CANCEL` and `ORPHANED` packet types. It verifies that Samba's `ncacn_packet` decoder selects the correct union arm and preserves header flags, data representation, fragment lengths, call IDs, and empty authentication trailers.

## Important APIs, types, and functions
- `ncacn_packet_co_cancel_data` is a 16-byte little-endian DCE/RPC packet with `ptype` `DCERPC_PKT_CO_CANCEL`, flags `LAST | PENDING_CANCEL_OR_HDR_SIGNING`, fragment length 16, auth length 0, and call ID 1.
- `ncacn_packet_co_cancel_check` validates the decoded `struct ncacn_packet` and its `u.co_cancel.auth_info`.
- `ncacn_packet_orphaned_data` is a 16-byte packet with `ptype` `DCERPC_PKT_ORPHANED`, flags `FIRST | LAST`, fragment length 16, auth length 0, and call ID 8.
- `ncacn_packet_orphaned_check` validates the decoded `u.orphaned.auth_info`.
- `ndr_dcerpc_suite(TALLOC_CTX *ctx)` creates a parent `dcerpc` suite and nested `co_cancel` and `orphaned` suites.

## Control flow
The suite factory creates nested suites for the two packet types, attaches them to the parent, and registers one `torture_suite_add_ndr_pull_validate_test` for each. The shared NDR harness decodes the byte array through generated `ndr_pull_ncacn_packet`, calls the packet-specific checker, then pushes the structure back out and compares to the original input. The checkers assert each fixed header field and ensure that the selected union arm has an empty `DATA_BLOB` authentication field.

## State and persistence behavior
There is no persistent state. The file contains two immutable 16-byte fixtures and allocates only transient suite/test objects under the supplied talloc context.

## Dependencies and integration points
The file depends on generated DCE/RPC NDR declarations from `librpc/gen_ndr/ndr_dcerpc.h`, DCE/RPC constants such as `DCERPC_PKT_CO_CANCEL`, `DCERPC_PKT_ORPHANED`, `DCERPC_PFC_FLAG_*`, and `DCERPC_DREP_LE`, plus the generic NDR torture helpers. The parent NDR runner includes it via `ndr_dcerpc_suite(suite)`.

## Risks and edge cases
- Only minimal packets with no auth data and no body beyond the common header are covered.
- The comments above each fixture document expected parse output; if fixture bytes are updated without comment updates, the documentation can drift.
- These tests are precise for union dispatch and flag decoding but do not cover bind, request, response, fault, or authenticated packet paths.
- The `CO_CANCEL` flag expectation intentionally excludes `FIRST` even though comments list individual flag meanings; this protects a subtle flag combination but could be misread during maintenance.

## Test signals
Passing subtests demonstrate correct `ncacn_packet` handling for the `co_cancel` and `orphaned` union cases and byte-stable round trips for minimal DCE/RPC packet headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/dcerpc.c -->
