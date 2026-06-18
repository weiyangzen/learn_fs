# Research: subset-b-010011

Grouped research for Samba VFS torture, winbind torture/service/idmap, oLschema2ldif utility, utility blackbox tests, and WREPL server sources.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/streams_xattr.c -->
# sources/user-network-fs/samba/source4/torture/vfs/streams_xattr.c

## Purpose

This file defines the `vfs.streams_xattr.streams-pwrite-hole` SMB2 torture test. It validates that the `vfs_streams_xattr` alternate data stream backend preserves sparse stream semantics: writing to the beginning and near the end of an ADS should expose zero-filled bytes in the unwritten hole when read back through SMB2.

## Important APIs, Types, and Functions

- `get_stream_handle()` creates the base test directory, base file, and named stream, returning an SMB2 handle for the stream.
- `read_stream()` wraps `smb2_read()` for an arbitrary stream offset and length.
- `test_streams_pwrite_hole()` is the single test body. It writes `WRITE_PAYLOAD` at offset `0` and at `ADS_OFF_TAIL`, reads `ADS_LEN` bytes, and checks payload placement plus zero fill.
- `torture_vfs_streams_xattr()` registers the suite and test under the VFS torture namespace.

## Control Flow

The test creates `smb2-testads`, opens `testdir/testfile:test_stream`, writes the canary string twice using `smb2_util_write()`, then reads the full 1024-byte ADS. It first asserts the read length is exactly `ADS_LEN`, then compares the two written regions and scans the gap byte by byte for `'\0'`. Cleanup frees the temporary talloc context, closes the stream handle if present, and removes the test tree with `smb2_deltree()`.

## State and Persistence Behavior

All state is remote SMB server state under `BASEDIR`. The test creates a directory, a file, and an ADS, then removes the tree at the end. No local files are persisted. Early `return false` paths after failed writes skip the common cleanup block, so a failed server write can leave the test tree behind.

## Dependencies and Integration Points

The file depends on the SMB2 torture helpers, SMB2 read/write calls, SMB2 testdir/testfile helpers, and the VFS torture registration in `vfs.c`. It is meaningful only against a share configured with streams support, typically `vfs_streams_xattr`.

## Risks and Edge Cases

The test relies on server behavior for sparse ADS reads and on `sizeof(WRITE_PAYLOAD)`, which includes the trailing NUL byte. Diagnostics on write failure print `sizeof(canary)`, where `canary` is a pointer, not the payload length; this affects reporting, not the write itself. Failed write paths bypass handle/tree cleanup.

## Test Signals

Pass signals are successful stream creation, exact 1024-byte readback, matching payload at offset `0` and offset `ADS_OFF_TAIL`, and all intervening bytes zero. Failure signals point to stream hole materialization, ADS length, xattr stream storage, or SMB2 read/write regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/streams_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/vfs.c -->
# sources/user-network-fs/samba/source4/torture/vfs/vfs.c

## Purpose

This file is the VFS torture module entry point. It registers VFS-related SMB torture suites, including fruit, acl_xattr, and streams_xattr, and provides a helper for tests that need two SMB2 tree connections to separate shares/namespaces.

## Important APIs, Types, and Functions

- `wrap_2ns_smb2_test()` opens the default SMB2 tree and a second tree from torture option `share2`, runs a two-tree test function, and frees connection state safely.
- `torture_suite_add_2ns_smb2_test()` constructs a `torture_test` that uses `wrap_2ns_smb2_test()`.
- `torture_vfs_init()` creates the top-level `vfs` suite and attaches all VFS sub-suites.

## Control Flow

Two-namespace tests are registered as a tcase with a custom wrapper. At runtime the wrapper opens the first tree with `torture_smb2_connection()`, steals it to a local talloc context so tests that close connections do not cause double-free, optionally opens the second tree via `torture_smb2_con_sopt()`, invokes the stored function pointer, and frees the wrapper context. Module initialization creates the `vfs` suite, adds child suites, adds the standalone fruit AFP info validator, registers the suite, and returns `NT_STATUS_OK`.

## State and Persistence Behavior

This file itself persists no data. It manages SMB2 connection lifetimes through talloc ownership and deliberately tolerates tests that close their own connections. Persistent state is created only by child tests.

## Dependencies and Integration Points

It integrates with the Samba torture framework, SMB2 helper layer, VFS suite constructors from `torture/vfs/proto.h`, and the module system through `torture_vfs_init()`. `torture/wscript_build` compiles it into the `TORTURE_VFS` smbtorture module.

## Risks and Edge Cases

`wrap_2ns_smb2_test()` proceeds even if the second tree open fails; individual two-tree tests must handle a NULL or unusable `tree2`. The manual `struct torture_test` allocation must keep fields in sync with torture framework expectations.

## Test Signals

The main signal is suite availability: VFS subtests appear under `vfs` and run with expected SMB2 connection setup. Failures usually surface as missing VFS tests, failed tree setup, or lifetime bugs when tests close connections themselves.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/struct_based.c -->
# sources/user-network-fs/samba/source4/torture/winbind/struct_based.c

## Purpose

This file implements `winbind.struct`, a torture suite for the legacy struct-based winbind client protocol. It sends `WINBINDD_*` operations through `wbcRequestResponse()` and validates interface versioning, ping, configuration identity, trusted-domain enumeration, domain-controller lookup, passwd enumeration, user/group listing, name/SID round trips, and invalid SID lookup behavior.

## Important APIs, Types, and Functions

- `DO_STRUCT_REQ_REP_EXT()` maps libwbclient errors into NSS-style statuses and enforces strict or warning-only expectations.
- `winbind_separator()`, `get_winbind_domain()`, `get_trusted_domains()`, `get_user_list()`, and `get_group_list()` are shared request/parse helpers.
- `torture_winbind_struct_interface_version()`, `ping()`, `info()`, `priv_pipe_dir()`, `netbios_name()`, `domain_name()`, and `check_machacc()` validate basic daemon metadata and machine account state.
- `torture_winbind_struct_list_trustdom()`, `domain_info()`, `getdcname()`, and `dsgetdcname()` exercise trust and DC discovery.
- `torture_winbind_struct_setpwent()`, `getpwent()`, and `endpwent()` exercise NSS passwd enumeration operations.
- `lookup_name_sid_list()` and `torture_winbind_struct_lookup_name_sid()` validate `LOOKUPNAME` and `LOOKUPSID` as inverses for listed users/groups and check invalid inputs.
- `torture_winbind_struct_init()` registers all tests.

## Control Flow

Most tests zero a `winbindd_request` and `winbindd_response`, issue one request via the macro, then assert fields or parse `extra_data`. Trust parsing expects newline-separated records in `NETBIOS\DNS\SID` form and verifies at least BUILTIN plus the local domain. User/group parsing consumes comma-separated extra data. Lookup tests enumerate known users/groups, split domain-qualified names using the configured separator or UPN fallback, perform name-to-SID and SID-to-name calls, then compare the reconstructed name case-insensitively. Some tests use a `strict mode` torture option: without strict mode, environment-sensitive failures become warnings.

## State and Persistence Behavior

The tests do not modify persistent domain state. They do exercise winbind daemon cached state, NSS enumeration cursor state (`SETPWENT`/`GETPWENT`/`ENDPWENT`), and machine-account verification. Response `extra_data.data` returned by winbind is freed with `SAFE_FREE()` in most parsing helpers.

## Dependencies and Integration Points

Dependencies include libwbclient internals, `winbind_struct_protocol.h`, `winbind_nss_config.h`, Samba security SID helpers, Netlogon constants, loadparm settings, and PAM error mapping. The suite is included by `torture/winbind/winbind.c` and built into `TORTURE_WINBIND`.

## Risks and Edge Cases

The tests are sensitive to configured workgroup, winbind separator, trusts, domain mode, and availability of users/groups. `get_group_list()` has a diagnostic string typo for zero entries, and `getpwent()` has Samba3-specific tolerance because some Samba3 deployments return success without an entry. Parsing assumes trust lines contain two backslashes and that BUILTIN is first. The `getdcname`/`dsgetdcname` tests may not exercise anything in small or non-AD environments unless strict mode is enabled.

## Test Signals

Strong pass signals are matching interface version, stable ping loop, correct separator/netbios/domain metadata, valid machine-account status, trust/domain-info SID consistency, non-empty and count-matched group lists, successful passwd enumeration when expected, reversible name/SID lookup for all listed principals, and `NSS_STATUS_NOTFOUND` for invalid lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/struct_based.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/winbind.c -->
# sources/user-network-fs/samba/source4/torture/winbind/winbind.c

## Purpose

This file is the winbind torture module entry point and contains Kerberos PAC comparison tests. It creates an in-process GENSEC client/server exchange, captures the PAC used to build session info, asks winbind to decode the same PAC, and compares winbind's `wbcAuthUserInfo` with Samba's internal Kerberos PAC decoder.

## Important APIs, Types, and Functions

- `struct pac_data` stores the PAC blob captured from the server session-info hook.
- `test_generate_session_info_pac()` decodes a PAC into `auth_user_info_dc`, sets authentication/session flags, calls `auth_generate_session_info()`, and saves the PAC in `auth_ctx->private_data`.
- `torture_decode_compare_pac()` calls `wbcAuthenticateUserEx()` with `WBC_AUTH_USER_LEVEL_PAC`, decodes the PAC internally with `kerberos_pac_logon_info()`, and compares scalar fields plus primary, group, extra, and resource SIDs.
- `torture_winbind_pac()` drives the GENSEC client/server update loop for GSSAPI, GSS-SPNEGO, or krb5.
- `torture_winbind_init()` registers struct, wbclient, and PAC sub-suites.

## Control Flow

The PAC test initializes machine server credentials, a minimal `auth4_context` with a custom PAC session-info callback, and GENSEC client/server contexts. The client uses command-line credentials; the server uses machine credentials. The chosen mechanism is started by SASL name or mechanism name, then client/server `gensec_update()` calls are alternated until authentication completes. After `gensec_session_info()`, the saved PAC blob is decoded by winbind and internally, and all important identity fields and SID ordering are checked.

## State and Persistence Behavior

No database or local file state is written. The test mutates in-memory authentication context state by storing `pac_data` under `auth_ctx->private_data` and stealing the PAC blob memory into it. It depends on live Kerberos credentials and winbind availability.

## Dependencies and Integration Points

The file depends on GENSEC, Kerberos PAC utilities, auth session-info generation, libwbclient PAC authentication, Samba command-line credentials, and loadparm GENSEC settings. It integrates with `torture_winbind_struct_init()` and `torture_wbclient()` in the top-level winbind suite.

## Risks and Edge Cases

The comparison assumes winbind and internal PAC decoding produce the same scalar fields, Unix-time conversions, and SID ordering. PACs without expected resource-group structures or environments without usable Kerberos credentials can fail before comparison. `wbcFreeMemory(info)` is called after success, but the `error` pointer from `wbcAuthenticateUserEx()` is not separately freed in this code path.

## Test Signals

Pass signals are successful GENSEC authentication for `GSSAPI`, `GSS-SPNEGO`, and `krb5`, successful winbind PAC authentication, successful internal PAC parsing, equal account/domain/time/counter fields, and exact SID sequence equivalence for account SID, primary group SID, domain groups, extra SIDs, and resource groups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/winbind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/wscript_build -->
# sources/user-network-fs/samba/source4/torture/winbind/wscript_build

## Purpose

This Waf build fragment defines the `TORTURE_WINBIND` internal smbtorture module.

## Important APIs, Types, and Functions

- `bld.SAMBA_MODULE('TORTURE_WINBIND', ...)` declares sources, generated prototype header, subsystem, init function, dependencies, and internal-module status.

## Control Flow

The fragment is executed during Samba's build configuration. It compiles `winbind.c`, `struct_based.c`, and the libwbclient test source into the `smbtorture` subsystem, generating `proto.h` and using `torture_winbind_init` as the module initializer.

## State and Persistence Behavior

It generates build artifacts only as part of the Waf build. It does not affect runtime state.

## Dependencies and Integration Points

Dependencies include `popt`, `wbclient`, `torture`, `PAM_ERRORS`, and `winbindd-lib`. The parent `source4/torture/wscript_build` recurses into this directory so the module becomes part of `smbtorture`.

## Risks and Edge Cases

If `winbindd-lib` or libwbclient tests change ABI or dependencies, this fragment must stay synchronized. The module is internal to smbtorture, not independently installed.

## Test Signals

Successful build should produce the `TORTURE_WINBIND` module with generated prototypes and visible `winbind` torture tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/wscript_build -->
# sources/user-network-fs/samba/source4/torture/wscript_build

## Purpose

This is the main Waf build script for Samba4 torture binaries and modules. It defines shared torture support, core smbtorture modules, subdirectory recursion, and standalone test tools such as `smbtorture`, `gentest`, `masktest`, and `locktest`.

## Important APIs, Types, and Functions

- `bld.SAMBA_SUBSYSTEM()` declares shared subsystems such as `TORTURE_UTIL`, `TORTURE_NDR`, `IREMOTEWINSPOOL_COMMON`, and `torturemain`.
- `bld.SAMBA_MODULE()` declares smbtorture modules including `TORTURE_BASIC`, `TORTURE_RAW`, `torture_rpc`, `TORTURE_RAP`, `TORTURE_AUTH`, `TORTURE_LDAP`, `TORTURE_NBT`, and `TORTURE_VFS`.
- `bld.RECURSE()` includes sub-builds for `smb2`, `winbind`, `libnetapi`, `libsmbclient`, `gpo`, `drs`, `dns`, `local`, and `krb5`.
- `bld.SAMBA_BINARY()` declares `smbtorture`, `gentest`, `masktest`, and `locktest`.

## Control Flow

The script computes Python embedded library names, builds utility subsystems, defines modules with source lists and dependency lists, conditionally adds NTVFS-specific spoolss notify sources, recurses into child directories, assembles `TORTURE_MODULES`, and links those modules into `torturemain` and `smbtorture`. Module declarations include `init_function` names that register suites at runtime.

## State and Persistence Behavior

This file controls build graph state and generated prototype headers. It has no runtime persistence, but changes affect which tests are compiled, linked, and available in `smbtorture`.

## Dependencies and Integration Points

It integrates almost every Samba4 torture subsystem with Waf, generated NDR bindings, RPC client libraries, Kerberos/auth libraries, SMB client libraries, process/service helpers, and Python embedding. The `TORTURE_VFS` stanza includes `vfs/vfs.c`, `fruit.c`, `acl_xattr.c`, and `streams_xattr.c`; `bld.RECURSE('winbind')` brings in the winbind torture module.

## Risks and Edge Cases

Large hand-maintained source/dependency lists can drift when files move or add new link dependencies. Conditional `enabled=bld.PYTHON_BUILD_IS_ENABLED()` affects test availability. The NTVFS conditional changes RPC module contents based on build config.

## Test Signals

Pass signals are successful Waf configure/build, generated prototype headers, linked `smbtorture`, and runtime visibility of all expected suites. Missing modules or unresolved symbols usually indicate stale source/dependency declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.c -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.c

## Purpose

This file implements the core `oLschema2ldif` converter. It reads OpenLDAP schema definitions, parses `attributetype` and `objectclass` records, and emits AD/LDB-compatible LDIF messages with schema attributes such as `attributeID`, `governsID`, `schemaIdGuid`, `attributeSyntax`, `oMSyntax`, `mustContain`, `mayContain`, and class category fields.

## Important APIs, Types, and Functions

- `check_braces()` detects complete schema records and malformed final closing braces.
- `skip_spaces()`, `add_multi_string()`, and `get_def_value()` support token parsing.
- `get_next_schema_token()` recognizes OpenLDAP schema keywords (`NAME`, `SUP`, `MUST`, `MAY`, `SYNTAX`, `DESC`, etc.) and returns `struct schema_token`.
- `process_entry()` converts one schema record into an `ldb_message`.
- `process_file()` streams input, skips comments/blank lines, accumulates complete records, calls `process_entry()`, writes LDIF via `ldb_ldif_write_file()`, and returns conversion counts/failures.

## Control Flow

`process_file()` reads one character at a time. It ignores `#` comments and blank lines, grows a talloc buffer as needed, and calls `check_braces()` whenever a newline is seen inside a record. Once a full record is found, `process_entry()` determines whether the entry is an attribute or object class, extracts the OID, creates a deterministic `schemaIdGuid` from SHA-256 of that OID, then walks schema tokens until `)`. Token handlers populate LDB attributes; syntax tokens are translated through `find_syntax_map_by_standard_oid()`. Successful messages are written as LDIF; failed records increment `failures`.

## State and Persistence Behavior

The converter stores no durable state except the output LDIF stream. All parse and LDB message memory is talloc-scoped. `process_entry()` steals successful messages to the caller context and frees failed temporary contexts. `process_file()` updates only the returned `struct schema_conv` counters.

## Dependencies and Integration Points

It depends on LDB message/LDIF APIs, DSDB schema syntax maps, GUID helpers, and GnuTLS SHA-256 hashing. It is used by `main.c` for the command-line tool and by `test.c` for cmocka parser regression tests.

## Risks and Edge Cases

The parser is intentionally narrow. It only supports the first `NAME` alias, treats unknown tokens as fatal, and has TODOs for equality/ordering/substr behavior. Unknown syntax OIDs lead to missing syntax fields and can make entries invalid. `check_braces()` enforces a space before a final closing brace. Parsing is hand-written and sensitive to quoting, multiline records, and malformed parentheses. The generated schema GUID is deterministic but not an AD-originated GUID.

## Test Signals

Useful signals are correct record/failure counts, emitted LDIF for valid attribute/objectclass inputs, deterministic `schemaIdGuid`, proper multi-value splitting for `$` lists, and failure on malformed tokens, unterminated values, missing names, or unsupported syntax mappings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.h -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.h

## Purpose

This header exposes the minimal public interface for the `oLschema2ldif` converter library.

## Important APIs, Types, and Functions

- `struct schema_conv` reports `count` and `failures` from a conversion run.
- `struct conv_options` carries the LDB context, base DN, input stream, and output stream.
- `process_file()` is the single exported conversion function.

## Control Flow

Consumers fill `conv_options`, call `process_file()`, and inspect the returned counters. The header itself contains no logic.

## State and Persistence Behavior

The caller owns the LDB context, base DN, and streams. Conversion state is owned by `process_file()` and its caller-provided talloc context.

## Dependencies and Integration Points

The header includes Samba `includes.h`, `ldb.h`, and DSDB/SAMDB headers because the converter uses LDB and schema syntax APIs. It is included by both `main.c` and `test.c`.

## Risks and Edge Cases

The API assumes valid, open `FILE *` handles and a valid `ldb_dn`. It exposes only aggregate counts, not structured parse errors or per-entry diagnostics.

## Test Signals

Build success and clean inclusion by the command-line tool and cmocka tests are the primary signals. Runtime callers should see accurate `count` and `failures` fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/main.c -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/main.c

## Purpose

This file implements the `oLschema2ldif` command-line tool. It parses options, opens input/output streams, initializes an LDB context and base DN, runs the converter library, and prints a conversion summary.

## Important APIs, Types, and Functions

- `usage()` prints help text and exits.
- `options` stores `--basedn`, `--input`, and `--output`.
- `main()` uses Samba popt helpers, `ldb_init()`, `ldb_dn_new()`, stream opening, `process_file()`, and cleanup.

## Control Flow

`main()` allocates a top-level talloc context, sets `LDB_URL=NONE`, builds a popt context, rejects invalid options, requires `--basedn`, initializes default stdin/stdout streams and an LDB context, validates the base DN, optionally opens input and output files, calls `process_file()`, closes streams, prints `"Converted %d records with %d failures"`, frees the popt context, and exits with status `0`.

## State and Persistence Behavior

The only persistent output is the optional LDIF output file. The tool also writes the summary to stdout even when stdout is the LDIF output stream, so callers redirecting LDIF to stdout get the summary appended after LDIF output.

## Dependencies and Integration Points

It depends on the converter library, Samba command-line/popt helpers, LDB DN parsing, and standard C file streams. The build script links it as `oLschema2ldif` with manpage `oLschema2ldif.1`.

## Risks and Edge Cases

The manpage synopsis omits the required `--basedn` option even though the program requires it. Error handling calls `usage()` and exits rather than returning distinct error codes. `fclose(copt.in)` and `fclose(copt.out)` are called even when they are stdin/stdout.

## Test Signals

Pass signals are option parsing, rejection of missing/malformed base DN, successful conversion from file or stdin, output file creation when requested, and accurate conversion summary counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/oLschema2ldif.1.xml -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/oLschema2ldif.1.xml

## Purpose

This DocBook XML file is the manual page source for `oLschema2ldif(1)`.

## Important APIs, Types, and Functions

- The document defines `refentry`, `refmeta`, `refnamediv`, synopsis, description, options, version, see-also, and author sections.
- It documents `-I input-file` and `-O output-file`.

## Control Flow

There is no executable flow. During the build, Samba's manpage tooling converts this XML into `oLschema2ldif.1`.

## State and Persistence Behavior

It affects installed/generated documentation only.

## Dependencies and Integration Points

The XML uses the DocBook V4.2 DTD and is referenced by `wscript_build` through `manpages='oLschema2ldif.1'`.

## Risks and Edge Cases

The synopsis and options do not document the `-b/--basedn` option that `main.c` requires. The purpose text says "LDAP schema's" and references the historical LDB site, so documentation may be stale relative to the current command behavior.

## Test Signals

Build-time validation of DocBook/manpage generation and user-facing consistency with `oLschema2ldif --help` are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/oLschema2ldif.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/test.c -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/test.c

## Purpose

This file contains cmocka regression tests for malformed or unsupported OpenLDAP schema inputs handled by the `oLschema2ldif` library.

## Important APIs, Types, and Functions

- `setup_context()` and `teardown_context()` allocate/free a small talloc test context.
- `process_data_blob()` wraps an in-memory input blob with `fmemopen()`, writes output to `/dev/null`, creates an LDB context/base DN, and calls `process_file()`.
- Tests cover unknown syntax OID, unterminated quoted token value, unterminated `MUST`, `MAY`, and `SUP` values, unknown tokens, and missing `NAME`.
- `main()` registers tests with cmocka and emits subunit output.

## Control Flow

Each test constructs one schema definition blob, invokes `process_data_blob()`, then asserts `ret.count == 1` and `ret.failures == 1`. The helper closes the in-memory input and `/dev/null` output after conversion.

## State and Persistence Behavior

No durable state is written. `/dev/null` receives generated LDIF if conversion unexpectedly succeeds. All allocations are under the test talloc context and are freed in teardown.

## Dependencies and Integration Points

The tests depend on cmocka, `fmemopen()`, LDB, Samba talloc/includes, and `oLschema2ldif-lib`. The build enables `test_oLschema2ldif` only when `HAVE_FMEMOPEN` is set.

## Risks and Edge Cases

The tests cover negative parse paths but not successful conversion output. They assert only aggregate counts, so they do not validate diagnostics or partially emitted LDIF content. They rely on `/dev/null`, which is Unix-specific but suitable for Samba's build targets.

## Test Signals

The expected signal is every malformed fixture being counted as one attempted record with one failure. A success count without failure would indicate the parser accepted malformed or unsupported schema input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/wscript_build -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/wscript_build

## Purpose

This Waf fragment builds the `oLschema2ldif` converter library, command-line binary, and local cmocka test binary.

## Important APIs, Types, and Functions

- `bld.SAMBA_SUBSYSTEM('oLschema2ldif-lib', source='lib.c', deps='samdb')`
- `bld.SAMBA_BINARY('oLschema2ldif', source='main.c', manpages='oLschema2ldif.1', deps='oLschema2ldif-lib cmdline')`
- `bld.SAMBA_BINARY('test_oLschema2ldif', source='test.c', deps='cmocka oLschema2ldif-lib', enabled=bld.CONFIG_SET('HAVE_FMEMOPEN'), install=False)`

## Control Flow

During build configuration, Waf declares the library first, then the installed utility, then the non-installed test binary conditional on `fmemopen()` support.

## State and Persistence Behavior

It affects build outputs and installed binaries/manpages. It has no runtime persistence.

## Dependencies and Integration Points

The converter library links against `samdb`; the CLI links against `cmdline`; the test links against cmocka. The test binary is local/non-installed.

## Risks and Edge Cases

Test coverage is absent on platforms without `fmemopen()`. Dependency drift in `lib.c` can require this fragment to add more explicit libraries.

## Test Signals

Successful build should produce `oLschema2ldif`, `oLschema2ldif.1`, and, where supported, `test_oLschema2ldif`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_nmblookup.sh -->
# sources/user-network-fs/samba/source4/utils/tests/test_nmblookup.sh

## Purpose

This shell script runs blackbox `nmblookup` tests against a Samba test environment, checking direct server-IP lookups and ordinary NetBIOS name lookups for server name, NetBIOS name, and NetBIOS alias.

## Important APIs, Types, and Functions

- Positional arguments provide `NETBIOSNAME`, `NETBIOSALIAS`, `SERVER`, `SERVER_IP`, `nmblookup`, and trailing torture options.
- `testit()` prints subtest status, runs a command, increments `failed` on nonzero exit, and returns the command status.

## Control Flow

The script shifts the first five arguments, stores remaining options, runs six `testit` calls, and exits with the accumulated failure count.

## State and Persistence Behavior

No files are written. The only state is the `failed` counter and subprocess exit codes.

## Dependencies and Integration Points

It depends on `/bin/sh`, `expr`, an executable `nmblookup`, and a test environment where the supplied server and aliases are resolvable by WINS/NetBIOS.

## Risks and Edge Cases

Arguments are mostly unquoted in command execution, so spaces or shell metacharacters in names/options would break execution. The failure count is used directly as the exit code.

## Test Signals

Pass signal is exit `0` after all six lookup commands succeed. Any failed lookup increments the exit status and identifies the failing subtest in stdout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_nmblookup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_samba_tool.sh -->
# sources/user-network-fs/samba/source4/utils/tests/test_samba_tool.sh

## Purpose

This shell script runs blackbox tests for `samba-tool` and machine-account `smbclient` login behavior in a Samba test environment.

## Important APIs, Types, and Functions

- Positional arguments provide server, server IP, username, password, domain, and `smbclient`.
- Environment variables `BINDIR`, `VALGRIND`, `PYTHON`, and `CONFIGURATION` control command locations/wrappers.
- `testit()` runs commands and accumulates failures.

## Control Flow

After argument setup, it derives `$samba_tool` from `$BINDIR/samba-tool`, runs machine-pass `smbclient` login without explicit Kerberos, machine-pass login with `-k`, `samba-tool time`, `domain level show`, `domain info`, and `fsmo show`, then exits with the failure count.

## State and Persistence Behavior

No local files are written by the script. The commands query live Samba services and may use credentials, machine account secrets, and configuration paths provided by the environment.

## Dependencies and Integration Points

It integrates the Python `samba-tool` command, `smbclient`, Samba test configuration, and optional valgrind wrapping. The script expects `$BINDIR` and `$CONFIGURATION` to be set by the test harness.

## Risks and Edge Cases

Commands and many variables are unquoted in command position. The script uses older `smbclient -k` Kerberos syntax, while other tests use `--use-kerberos`. `domain level show` and `fsmo show` do not pass explicit credentials in this script, relying on configuration/environment defaults.

## Test Signals

Pass signal is successful machine-pass SMB access in both auth modes and successful `samba-tool` time/domain/FSMO queries. Failures point to credentials, Kerberos, tool discovery, domain controller reachability, or Samba-tool regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_samba_tool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_smbclient.sh -->
# sources/user-network-fs/samba/source4/utils/tests/test_smbclient.sh

## Purpose

This shell script blackbox-tests `smbclient` machine-account authentication to the `tmp` share with Kerberos disabled and required.

## Important APIs, Types, and Functions

- Positional arguments supply server, server IP, username, password, domain, and `smbclient`; only server and smbclient are used.
- `testit()` runs a subcommand, prints success/failure, and increments `failed`.

## Control Flow

The script runs two `smbclient -c 'ls' //$SERVER/tmp --machine-pass` commands: one with `--use-kerberos=disabled`, one with `--use-kerberos=required`. It exits with the number of failed subtests.

## State and Persistence Behavior

No files are written. The test reads the remote `tmp` share directory and uses the local machine account secret through Samba configuration.

## Dependencies and Integration Points

It depends on the test harness setting `CONFIGURATION` and optional `VALGRIND`, a usable `smbclient`, and a server exposing `tmp` to the machine account.

## Risks and Edge Cases

Unused positional variables are accepted for harness consistency. Variables are unquoted in command execution, so unusual server names or configuration strings can break the shell command.

## Test Signals

Exit `0` means both non-Kerberos and required-Kerberos machine-pass SMB sessions listed the share successfully. Nonzero exit identifies one or both authentication modes as broken.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_smbclient.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.c -->
# sources/user-network-fs/samba/source4/winbind/idmap.c

## Purpose

This file implements Samba4 AD DC SID/unixid mapping. It maps Unix UIDs/GIDs to SIDs and SIDs to Unix IDs using RFC2307 attributes in `sam.ldb` when configured, existing mappings in `idmap.ldb`, Unix local SIDs (`S-1-22-*`), and transactional allocation of new idmap entries.

## Important APIs, Types, and Functions

- `idmap_get_bounds()` reads `lowerBound` and `upperBound` from `CN=CONFIG` in `idmap.ldb`.
- `idmap_msg_add_dom_sid()` and `idmap_msg_get_dom_sid()` marshal/unmarshal `dom_sid` values through NDR blobs in LDB messages.
- `idmap_init()` opens `idmap.ldb` and `sam.ldb` with the system session.
- `idmap_xid_to_sid()` maps one `struct unixid` to a SID.
- `idmap_sid_to_xid()` maps one SID to a `struct unixid`, allocating a new idmap entry when needed.
- `idmap_xids_to_sids()` and `idmap_sids_to_xids()` batch arrays of `struct id_map` and set per-entry `ID_MAPPED`/`ID_UNMAPPED`.

## Control Flow

Initialization connects to `idmap.ldb` and `sam.ldb`. UID/GID-to-SID first optionally searches `sam.ldb` for matching `uidNumber`/`gidNumber` when `idmap_ldb:use rfc2307 = true`. If absent, it searches `idmap.ldb` for a compatible `xidNumber` and type. If still absent, local Unix users/groups are represented as calculated `S-1-22-1/2` SIDs without writing an idmap entry.

SID-to-xID first handles local Unix user/group SID namespaces by splitting the RID. It then optionally checks `sam.ldb` RFC2307 attributes. If no existing `sidMap` entry exists in `idmap.ldb`, it starts an LDB transaction, rechecks for races, reads bounds and the high-water mark from `CN=CONFIG`, increments the high-water mark, creates `CN=<sid>` with `objectClass=sidMap`, `objectSid`, `xidNumber`, `type=ID_TYPE_BOTH`, commits, and returns the allocated ID. Batch wrappers retry once on `NT_STATUS_RETRY`.

## State and Persistence Behavior

This file reads persistent `sam.ldb` and reads/writes persistent `idmap.ldb`. New SID-to-xID mappings advance the `xidNumber` high-water mark under `CN=CONFIG` and add a durable `sidMap` record. Transactions protect high-water mark plus mapping creation. Local Unix SID calculations and RFC2307 matches do not write new idmap records.

## Dependencies and Integration Points

Dependencies include LDB, `ldb_wrap_connect`, SAMDB search helpers, NDR SID encoding, LDAP SID encoding, loadparm parameters, Unix SID helpers, DSDB account-type constants, and generated idmap types from `librpc/gen_ndr/idmap.h`. The build exposes this as the `IDMAP` subsystem.

## Risks and Edge Cases

Duplicate RFC2307 matches return `NT_STATUS_NONE_MAPPED`. `idmap_get_bounds()` and allocator correctness depend on a valid `CN=CONFIG`. Allocations return `NT_STATUS_RETRY` if another writer adds the mapping between the initial and transactional lookup. The high-water mark check uses `hwm > high`, so `hwm == high` is still allocated and increments past high. UID/GID-to-SID fallback creates `S-1-22` SIDs without checking whether those UIDs/GIDs exist locally.

## Test Signals

Signals include correct RFC2307 lookup from `sam.ldb`, stable lookup of existing `sidMap` records, transactional allocation of new mappings within bounds, accurate type propagation (`UID`, `GID`, `BOTH`), per-entry batch statuses, `STATUS_SOME_UNMAPPED` for partial failures, and durable idmap entries visible in `idmap.ldb`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.h -->
# sources/user-network-fs/samba/source4/winbind/idmap.h

## Purpose

This header defines the Samba4 winbind idmap context and exposes generated idmap prototypes.

## Important APIs, Types, and Functions

- `struct idmap_context` contains `lp_ctx`, `ldb_ctx` for `idmap.ldb`, and `samdb` for `sam.ldb`.
- It forward-declares `struct tevent_context`.
- It includes `winbind/idmap_proto.h`, generated from `idmap.c`.

## Control Flow

No executable flow exists. Callers include this header, initialize `idmap_context` with `idmap_init()`, and use generated prototypes for mapping functions.

## State and Persistence Behavior

The context holds handles to persistent databases but does not itself manage persistence beyond talloc lifetime. Freeing the context closes associated LDB handles.

## Dependencies and Integration Points

It includes generated ID mapping types from `librpc/gen_ndr/idmap.h` and is used by Samba4 winbind/idmap consumers.

## Risks and Edge Cases

The structure exposes database internals directly, so callers can bypass intended mapping APIs if they include this header. Generated prototype availability depends on the Waf `autoproto` step.

## Test Signals

Build success for idmap consumers and correct generation of `idmap_proto.h` are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/winbindd.c -->
# sources/user-network-fs/samba/source4/winbind/winbindd.c

## Purpose

This file registers a Samba4 server service that runs the Samba3 `winbindd` daemon as a managed child process inside the Samba4 task framework.

## Important APIs, Types, and Functions

- `winbindd_done()` handles child process completion from `samba_runcmd_recv()` and terminates the service task.
- `winbindd_task_init()` constructs the `winbindd` command line and starts it with `samba_runcmd_send()`.
- `server_service_winbindd_init()` registers service names `winbindd` and `winbind`.

## Control Flow

At service initialization, Samba registers `winbindd`/`winbind` with service details that inhibit fork-on-accept and prefork. When the task starts, it sets the process title, builds the path `${dyn_SBINDIR}/winbindd`, adds a `--configfile` option only for non-default config paths, then runs winbindd with `-D`, `--foreground`, and `server role check:inhibit=yes`. A callback is attached so any normal or abnormal child exit terminates the parent task.

## State and Persistence Behavior

This file creates a child process and supervises its lifetime. It does not directly write databases or files, but child winbindd will use Samba runtime directories, winbind caches, and configuration. The parent service terminates when the child exits.

## Dependencies and Integration Points

It depends on Samba service/task registration, process model details, `UTIL_RUNCMD`, dynconfig paths, debug output settings, and winbind client headers. The Waf build registers it as `service_winbindd` in the `service` subsystem.

## Risks and Edge Cases

If `dyn_SBINDIR/winbindd` is missing or fails quickly, the service terminates. `winbindd_done()` logs `sys_errno` as an exit status, which may be imprecise depending on `samba_runcmd_recv()` semantics. Empty `config_file` is still passed as an argument position, relying on runcmd handling.

## Test Signals

Pass signals are successful service registration under both names, child winbindd startup, continued foreground operation, and task termination when the child exits or fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/winbindd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/wscript_build -->
# sources/user-network-fs/samba/source4/winbind/wscript_build

## Purpose

This Waf build fragment declares the Samba4 winbind service wrapper and the ID mapping subsystem.

## Important APIs, Types, and Functions

- `bld.SAMBA_MODULE('service_winbindd', ...)` builds `winbindd.c` as a service module with `server_service_winbindd_init`.
- `bld.SAMBA_SUBSYSTEM('IDMAP', ...)` builds `idmap.c` with generated `idmap_proto.h`.

## Control Flow

Waf processes the service module declaration, then the `IDMAP` subsystem declaration. The service module is not internal, while IDMAP exposes public dependencies on `samdb-common` and `ldbsamba`.

## State and Persistence Behavior

This file affects build artifacts only. Runtime state is created by the compiled service and idmap code.

## Dependencies and Integration Points

`service_winbindd` depends on `process_model` and `UTIL_RUNCMD`; `IDMAP` depends publicly on SAMDB/LDB support. Other build files link against these targets.

## Risks and Edge Cases

Dependency drift in `idmap.c` can require updates here. The service module relies on the runtime presence of the separate `winbindd` daemon binary.

## Test Signals

Build success should generate the service module and `IDMAP` subsystem with prototypes. Runtime service registration validates `service_winbindd`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_apply_records.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_apply_records.c

## Purpose

This file applies WINS replication records received from a partner to the local WINS database. It implements the WREPL conflict-resolution matrix for unique, normal group, special group, and multi-homed names across owned and replica records, including replacement, propagation, challenge, release-demand, and merge actions.

## Important APIs, Types, and Functions

- `enum _R_ACTION` represents the selected action: replace, not replace, propagate, challenge, release demand, or special-group merge.
- Address-list helpers compare old `winsdb_record` addresses with incoming `wrepl_name` addresses.
- `replace_*_replica_vs_X_replica()` and `replace_*_owned_vs_X_replica()` encode the conflict matrix.
- `r_do_add()`, `r_do_replace()`, `r_not_replace()`, `r_do_propagate()`, `r_do_mhomed_merge()`, `r_do_challenge()`, `r_do_release_demand()`, and `r_do_sgroup_merge()` execute selected actions.
- `wreplsrv_apply_one_record()` chooses an action for one incoming record.
- `wreplsrv_apply_records()` applies a batch and updates the local owner table.

## Control Flow

For each incoming `wrepl_name`, `wreplsrv_apply_one_record()` truncates overlong scopes to Windows-compatible length, looks up the local record, and adds a new record if absent. If present, it classifies the conflict as same owner, replica-vs-replica, or local-owned-vs-replica. Static records get special protection/propagation handling. Otherwise, type-specific matrix functions select an action. The action dispatcher modifies the WINS DB, starts an async challenge through the local `nbt_server` IRPC interface, sends release demands, or merges address lists.

After the batch, `wreplsrv_apply_records()` updates `service->table` with the remote owner max version using `wreplsrv_add_table()`.

## State and Persistence Behavior

The file persists changes in `winsdb`: adds records, replaces records, allocates new version IDs, takes ownership, deletes/updates address lists through modifications, and updates owner-table state. Challenge and release-demand operations are asynchronous IRPC calls to `nbt_server`; their states are talloc-stealed to the partner/service until completion.

## Dependencies and Integration Points

It depends on WREPL NDR types, WINS DB record APIs, NBT name utilities, IRPC bindings to `nbtd_proxy_wins_challenge` and `nbtd_proxy_wins_release_demand`, tevent, loadparm option `wreplsrv:propagate name releases`, and partner/service structures from `wrepl_server.h`. It is called by outbound pull cycles after receiving name batches.

## Risks and Edge Cases

The conflict matrix is large and maintenance-sensitive. Some action names/comments contain typos but not behavior changes. Asynchronous challenge/release-demand results are mostly best-effort, so failures may leave temporary inconsistencies. `r_do_release_demand()` keeps a reference to the old address list before replacement; lifetime correctness depends on talloc ownership. Special-group merge behavior can intentionally diverge from Windows when `propagate name releases` is enabled. Scope truncation mutates incoming names before DB lookup.

## Test Signals

Signals include correct WINS DB state after all matrix cases, allocated versions when local ownership/propagation is required, release demands after replacing local unique/mhomed records with group/sgroup records, successful mhomed/sgroup merges, and updated owner-table max versions after a batch. WREPL/NBT torture tests should catch regressions in conflict outcomes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_apply_records.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_call.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_call.c

## Purpose

This file handles decoded inbound WINS Replication protocol calls. It manages association start/stop, validates association contexts, authorizes partner direction, serves owner-table and name-send requests, reacts to update/inform messages, and constructs reply packets.

## Important APIs, Types, and Functions

- `wreplsrv_in_start_association()` and `wreplsrv_in_stop_association()` maintain association context state.
- `wreplsrv_in_table_query()` fills a local WREPL owner table reply.
- `wreplsrv_record2wins_name()` converts `winsdb_record` to `wrepl_wins_name`.
- `wreplsrv_in_send_request()` queries `winsdb` for active/tombstone records in a version range and returns sorted names.
- `wreplsrv_in_update()` donates the accepted stream to an outbound pull cycle.
- `wreplsrv_in_inform()` triggers an outbound pull based on a partner-supplied table.
- `wreplsrv_in_replication()` dispatches replication commands and enforces partner type flags.
- `wreplsrv_in_call()` is the top-level dispatcher.

## Control Flow

The dispatcher rejects invalid message types, handles initial invalid-association behavior, and appends standard opcode bits plus peer association context on successful replies. Replication commands first validate association bits when present, then lazily resolve the remote peer as a configured partner by IPv4 address. Non-partners or partners using the wrong push/pull direction receive stop-association behavior.

Table queries call `wreplsrv_fill_wrepl_table()`. Send requests normalize max version `0` to `UINT64_MAX`, validate ranges, search the WINS LDB for records owned by the requested owner and in active/tombstone states, parse records, skip records that became expired during parsing, sort by version ID, and return them. Update messages convert the inbound connection into a client-side `wreplsrv_out_connection` and start `wreplsrv_pull_cycle_send()` on the same stream.

## State and Persistence Behavior

Association state is held on `wreplconn->assoc_ctx`. Send requests are read-only against `winsdb`, but parsing can observe time-based state changes. Update/inform can initiate outbound pull cycles that later mutate the local WINS DB. The update path steals table partner arrays and donates stream ownership.

## Dependencies and Integration Points

Dependencies include WREPL client/server helpers, WINS DB APIs, LDB searches, owner-table helpers, `wreplsrv_pull_cycle_send()`, `wreplsrv_out_partner_pull()`, and Samba talloc/tevent infrastructure. It is called from `wrepl_in_connection.c` after packet decoding.

## Risks and Edge Cases

Version compatibility code intentionally ignores start-association version fields for NT4 compatibility. Returning `ERROR_INVALID_PARAMETER` is used as "ignore/no reply" behavior in several paths. Partner type enforcement is critical; misconfiguration blocks replication. The update path frees the send queue and donates the stream, so later inbound connection handling must stop using it.

## Test Signals

Signals include correct association replies, stop behavior, empty replies for unknown owners or invalid ranges, sorted send replies, rejection of non-partners/wrong-direction partners, successful pull-cycle handoff on update, and no reply for inform messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_connection.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_connection.c

## Purpose

This file implements the inbound WINS Replication TCP server connection layer. It accepts port 42 connections, converts sockets to tstream contexts, reads length-prefixed WREPL PDUs, dispatches decoded calls, writes replies through a queue, supports stream handoff/merge, and binds listening sockets.

## Important APIs, Types, and Functions

- `wreplsrv_terminate_in_connection()` terminates a stream connection with a reason.
- `wreplsrv_process()` decodes a `wrepl_packet`, calls `wreplsrv_in_call()`, and encodes a reply.
- `wreplsrv_accept()` initializes a new inbound connection.
- `wreplsrv_call_loop()` receives one PDU, processes it, queues any reply, and schedules the next read.
- `wreplsrv_call_writev_done()` handles queued write completion and terminate-after-send behavior.
- `wreplsrv_in_connection_merge()` turns an existing outbound stream into an inbound server connection.
- `wreplsrv_setup_sockets()` binds WREPL server sockets on IPv4 interfaces or `0.0.0.0`.

## Control Flow

On accept, the code creates `wreplsrv_in_connection`, a send queue, removes the old file descriptor event, wraps the existing socket in `tstream`, marks the socket no-close, validates IPv4 peer address, resolves the partner, registers an IRPC name, and starts `tstream_read_pdu_blob_send()` with a 4-byte length header. Each completed read creates a call, strips the length header, dispatches the call, writes a reply if one exists, and schedules the next read unless the stream was handed off. Write completion frees the call or terminates when requested.

`wreplsrv_in_connection_merge()` performs similar setup for a stream split from an outbound client connection, preserving peer association context. Socket setup binds per configured IPv4 interface when bind-interfaces-only is set, otherwise all IPv4 addresses.

## State and Persistence Behavior

This file owns transient connection, queue, tstream, and call state. It does not persist WINS data directly; persistence is delegated to call handlers. Stream ownership can move between inbound and outbound roles during WREPL update flows.

## Dependencies and Integration Points

It depends on Samba stream server APIs, socket/tstream helpers, process model, IRPC naming, WREPL NDR encoding, network interface helpers, and `wreplsrv_in_call()`. It integrates with service startup through `wreplsrv_setup_sockets()`.

## Risks and Edge Cases

Only IPv4 peers are accepted. Invalid packets are silently ignored to match Windows behavior. Raw stream callbacks `recv_handler` and `send_handler` should never trigger after tstream conversion; if they do, the connection is terminated. Handoff paths must ensure no further reads/writes use a donated stream.

## Test Signals

Signals include successful socket binding, accepted IPv4 partner connections, correct decode/encode of length-prefixed WREPL PDUs, stable read loop after replies, ignored invalid packets, terminate-after-send stop association, and successful merge of update-triggered streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_in_connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.c

## Purpose

This file provides asynchronous outbound WREPL helper state machines: connect/associate to partners, pull owner tables, pull changed names, run a full pull cycle applying records, and notify partners through update/inform push messages.

## Important APIs, Types, and Functions

- `wreplsrv_out_connect_send/recv()` connects to a partner, performs WREPL association, and caches push/pull connections where appropriate.
- `wreplsrv_pull_table_send/recv()` obtains a remote owner table or uses an inform-supplied table.
- `wreplsrv_pull_names_send/recv()` requests names for one owner/version range.
- `wreplsrv_pull_cycle_send/recv()` coordinates table update, per-owner name pulls, `wreplsrv_apply_records()`, and optional association stop.
- `wreplsrv_push_notify_send/recv()` sends WREPL update/inform notifications and handles update stream role reversal.

## Control Flow

Every operation is represented by a `composite_context` plus a private stage enum. Connect starts `wrepl_connect_send()`, then `wrepl_associate_send()`, stores peer association context/version, and optionally caches the connection in `partner->push.wreplconn` or `partner->pull.wreplconn`. Pull table either returns the supplied inform table immediately or connects and sends a table query. Pull cycle updates `partner->pull.table`, then walks owners whose remote max version is newer than local, pulls names with `min_version = local + 1`, applies records, and repeats. If the cycle was initiated on an already-donated stream, it sends association stop at the end.

Push notify chooses inform/update command based on `inform` and `propagate` flags, falls back from inform to update for old peers, fills the local table, sends the request, and for update messages splits the client socket stream and merges it into an inbound server connection for the peer's send requests.

## State and Persistence Behavior

The helpers maintain cached outbound connections on partners, association context fields, partner pull tables, pending composite requests, and pulled name batches. Persistent WINS DB changes happen through `wreplsrv_apply_records()`. Push update can transfer stream ownership to an inbound connection and free the outbound connection.

## Dependencies and Integration Points

Dependencies include WREPL client functions, composite/tevent async APIs, WINS DB and WREPL table helpers, address selection via `wrepl_best_ip()`, `wreplsrv_in_connection_merge()`, and the record application layer. It is used by inbound update handling and by periodic pull/push schedulers.

## Risks and Edge Cases

Connection caching must discard disconnected cached sockets. Pull cycle compares owner max versions and skips local/self owners; stale tables can miss changes until refreshed. The TODO notes record application may need async handling because conflict resolution can trigger network access. Update/inform fallback depends on peer major version. Stream split/merge errors can leave push updates incomplete.

## Test Signals

Signals include successful connection association, correct connection caching, accurate remote table ingestion, pulls only for owners with newer versions, successful record application and owner-table updates, association stop on donated streams, inform/update fallback for older peers, and conversion from outbound update to inbound server role.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.h -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.h

## Purpose

This header declares the small I/O structures shared by outbound WREPL helper APIs.

## Important APIs, Types, and Functions

- `struct wreplsrv_pull_cycle_io` carries a partner, optional owner table, and optional existing outbound connection for a pull cycle.
- `struct wreplsrv_push_notify_io` carries a partner plus flags selecting inform/update and propagation behavior.

## Control Flow

The header contains no functions. Callers populate these structures and pass them to helper functions declared elsewhere/generated from `wrepl_out_helpers.c`.

## State and Persistence Behavior

The structures reference partner, owner arrays, and optional connection state owned by callers or talloc parents. They do not persist state themselves.

## Dependencies and Integration Points

It is included by WREPL outbound/inbound scheduler code that starts pull cycles and push notifications.

## Risks and Edge Cases

Ownership of `owners` and `wreplconn` is transferred or stolen in helper implementations, so callers must follow the expected talloc lifetime rules.

## Test Signals

Correct compilation and successful async pull/push flows validate the structure contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_pull.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_pull.c

## Purpose

This file schedules and supervises outbound WREPL pull cycles for configured pull partners.

## Important APIs, Types, and Functions

- `wreplsrv_out_pull_reschedule()` sets `partner->pull.next_run` and requests a service periodic wakeup.
- `wreplsrv_pull_handler_creq()` handles pull-cycle completion, retry, backoff, and cleanup.
- `wreplsrv_out_partner_pull()` starts a pull cycle for a partner, optionally using an inform-supplied owner table.
- `wreplsrv_out_pull_run()` scans all partners and starts due pull cycles.

## Control Flow

`wreplsrv_out_pull_run()` iterates partners, skipping non-pull partners, disabled intervals, and partners whose next run has not expired. Due partners are immediately rescheduled for their normal interval and `wreplsrv_out_partner_pull()` is invoked. A partner with an in-progress pull is skipped. Completion resets error count on success. The first failure triggers an immediate retry using the old owner table; later failures schedule increasing retry intervals capped at the normal pull interval.

## State and Persistence Behavior

State is stored in `partner->pull`: `next_run`, `creq`, `cycle_io`, `last_status`, and `error_count`. Persistent WINS state is changed indirectly by the pull cycle's record application.

## Dependencies and Integration Points

It depends on `wreplsrv_pull_cycle_send/recv()`, service periodic scheduling, WREPL partner configuration, and `wrepl_table` data supplied by inbound inform messages.

## Risks and Edge Cases

If allocation fails, the pull request is logged and ignored. A stuck `partner->pull.creq` prevents new pulls. Retry uses the previous `cycle_io` owner array, so lifetime transfer must remain correct.

## Test Signals

Signals include due partner detection, no duplicate pulls while one is active, successful error reset after success, immediate first retry on failure, increasing retry schedule after repeated failures, and eventual WINS DB convergence after pull cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_pull.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_push.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_push.c

## Purpose

This file schedules and supervises outbound WREPL push notifications to configured push partners when local WINS version changes exceed a configured threshold.

## Important APIs, Types, and Functions

- `wreplsrv_out_partner_push()` starts one push notification for a partner.
- `wreplsrv_push_handler_creq()` handles completion, one retry, error counting, and cleanup.
- `wreplsrv_calc_change_count()` tracks per-partner maxVersion deltas with overflow protection.
- `wreplsrv_out_push_run()` scans partners and starts eligible push notifications.

## Control Flow

`wreplsrv_out_push_run()` reads the current max WINS DB version, iterates push partners, skips disabled push thresholds, calculates the version delta since the last check, and starts a push if the delta reaches the configured `change_count`. Each push uses `wreplsrv_push_notify_send()`, with inform/update selected from partner configuration. Completion resets error count on success; the first failure retries once, later failures give up until a later trigger.

## State and Persistence Behavior

The file updates `partner->push.maxVersionID`, `creq`, `notify_io`, `last_status`, and `error_count`. It does not directly persist WINS records; it reacts to persistent WINS DB version changes and notifies peers.

## Dependencies and Integration Points

It depends on `winsdb_get_maxVersion()`, outbound push notify helpers, WREPL partner configuration, and periodic scheduling through `wrepl_periodic.c`.

## Risks and Edge Cases

`wreplsrv_calc_change_count()` updates `maxVersionID` even when the threshold is not reached, so it measures changes since the last scan, not since the last successful push. A running push suppresses additional push attempts. Repeated failures are only retried once immediately.

## Test Signals

Signals include push notifications when version deltas cross thresholds, no notification below threshold, no duplicate in-progress notifications, one retry after a failure, and reset error count after success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_push.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_periodic.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_periodic.c

## Purpose

This file coordinates periodic WREPL maintenance. Each timer tick reloads partners, runs WINS scavenging, starts due pulls, and sends due push notifications.

## Important APIs, Types, and Functions

- `wreplsrv_periodic_run()` performs the ordered maintenance steps.
- `wreplsrv_periodic_handler_te()` handles tevent timer expiration.
- `wreplsrv_periodic_schedule()` schedules or reschedules the next timer.
- `wreplsrv_setup_periodic()` schedules the first tick.

## Control Flow

The timer callback clears the current timer pointer, schedules the next normal periodic tick, then calls `wreplsrv_periodic_run()`. Scheduling coerces zero intervals to one second, adds a 5000 microsecond offset, and avoids replacing an existing timer if the new requested time is later than the current next event. It frees the old timer only after creating the new one.

## State and Persistence Behavior

Timer state is held in `service->periodic.te` and `service->periodic.next_event`. Persistent WINS DB effects occur through called scavenging and replication functions.

## Dependencies and Integration Points

It depends on tevent timers, task service termination, partner loading, scavenging, outbound pull, and outbound push modules.

## Risks and Edge Cases

Because partner reload occurs before each maintenance pass, configuration/database errors can prevent scavenging and replication. A scheduling failure terminates the task. Maintenance errors are logged but do not stop future timer scheduling.

## Test Signals

Signals include initial timer creation, no tight loop on zero intervals, partner reload before replication, scavenging/pull/push invocation in order, and earlier reschedules replacing later timers when retries need quicker wakeups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_periodic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_scavenging.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_scavenging.c

## Purpose

This file scavenges expired WINS records for the WREPL server. It transitions owned records through active/released/tombstone/deleted states, cleans non-active replica records, verifies expired active replica records with the owning WINS server, and schedules future scavenging.

## Important APIs, Types, and Functions

- `wreplsrv_owner_filter()` builds LDB filters for local owner versus remote owners, treating `0.0.0.0` as local-owned only.
- `wreplsrv_scavenging_owned_records()` handles expired local-owned records.
- `wreplsrv_scavenging_replica_non_active_records()` handles expired released/tombstone replica records.
- `wreplsrv_scavenging_replica_active_records()` starts async verification for expired active replica records.
- `verify_handler()` processes challenge results and modifies/deletes/skips records.
- `wreplsrv_scavenging_run()` gates scheduling, first-run skip, and the three scavenging passes.

## Control Flow

`wreplsrv_scavenging_run()` returns early until `next_run` expires, schedules the next run, skips actual scavenging on the first startup call, and prevents reentry with `service->scavenging.processing`. Owned scavenging searches expired local-owner records. Static active records are refreshed; normal active records become released, or special groups with propagation enabled may remain active/tombstone depending on replica addresses; released records become tombstones; tombstones are deleted only after `tombstone_extra_timeout` since startup.

Replica non-active scavenging transitions released replicas to tombstones and later deletes tombstones. Replica active scavenging asks the owning WINS server through `nbtd_proxy_wins_challenge`; missing records are deleted, matching records are refreshed, and different address replies tombstone the record with local ownership/version allocation.

## State and Persistence Behavior

The file modifies persistent `winsdb` records: state, expiration times, address expiration times, ownership, allocated version IDs, and deletions. It updates `service->scavenging.next_run` and `processing`. Active replica verification is asynchronous and keeps `verify_state` alive under the service until callbacks complete.

## Dependencies and Integration Points

Dependencies include WINS DB LDB searches and record APIs, WREPL state/type constants, tevent/IRPC calls to `nbt_server`, time helpers, service config intervals, and loadparm option `wreplsrv:propagate name releases`. Periodic scheduling calls this module before pull/push replication.

## Risks and Edge Cases

The owned-record loop reuses loop variable `i` inside the special-group address scan, which can disturb the outer result iteration. Verification uses a simplified WINS name challenge rather than a full Windows-style WREPL/DCERPC verification. Async verification errors generally skip changes, allowing stale replicas to remain until a later pass. First-run scavenging intentionally skips to avoid aggressive startup deletion.

## Test Signals

Signals include correct time-gated execution, active-to-released/tombstone transitions, delayed tombstone deletion after startup extra timeout, static record refresh, propagated special-group behavior when enabled, replica verification refresh/delete/tombstone outcomes, and no concurrent scavenging reentry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_scavenging.c -->
