# subset-b-009892 Research

Grouped source research for selected Samba source3 utilities, smbstatus JSON/profile support, the retired SWAT stub, and winbind idmap core/backends. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbpasswd.c -->
# sources/user-network-fs/samba/source3/utils/smbpasswd.c

## Purpose

`sources/user-network-fs/samba/source3/utils/smbpasswd.c` implements the `smbpasswd` command-line tool. It changes SMB passwords locally through Samba passdb, remotely through password-change RPC, and, for root, performs administrative account operations such as add/delete/enable/disable users, machine or interdomain trust accounts, no-password state, and storing the LDAP admin password in `secrets.tdb`. The source was read as a complete 678-line file.

## Important APIs, Types, and Functions

Important entry points are `main`, `process_options`, `process_root`, `process_nonroot`, `password_change`, `prompt_for_new_password`, `store_ldap_admin_pw`, and `usage`. Global state includes `got_username`, `stdin_passwd_get`, `user_name`, `new_passwd`, `remote_machine`, and `ldap_secret`. The code uses local operation flags from `passwd_proto.h` such as `LOCAL_AM_ROOT`, `LOCAL_SET_PASSWORD`, `LOCAL_ADD_USER`, `LOCAL_DELETE_USER`, `LOCAL_DISABLE_USER`, `LOCAL_ENABLE_USER`, `LOCAL_TRUST_ACCOUNT`, `LOCAL_INTERDOM_ACCOUNT`, `LOCAL_SET_NO_PASSWORD`, and `LOCAL_SET_LDAP_ADMIN_PW`.

## Control Flow

`main` initializes memcache, locale, loadparm, and command-line parsing, rejects setuid-root execution, then dispatches to `process_root` when uid 0 or `process_nonroot` otherwise. `process_options` handles legacy getopt flags, loads the selected `smb.conf`, and sets local operation flags. Root mode initializes secrets/passdb, normalizes trust account names with a trailing `$`, prompts for generated or explicit passwords as needed, and calls `password_change`. Non-root mode restricts flags to password changes, infers the local username, allows `DOMAIN\user` parsing, uses localhost when no remote host is specified, prompts for old and new passwords, and performs a remote password change.

## State and Persistence Behavior

Local password changes mutate the configured passdb backend through `local_password_change`. Remote changes are sent to the target machine with `remote_password_change`. `-w` and `-W` store LDAP admin credentials in `secrets.tdb` via `secrets_store_ldap_pw`. The tool holds plaintext passwords in heap/fstring buffers only for the command lifetime and frees many of them on exit, but the source does not explicitly scrub every heap allocation after use.

## Dependencies and Integration Points

The utility integrates with Samba loadparm, passdb, secrets, local password utilities, remote password-change helpers, name resolution ordering, interface loading, and command-line contexts. It depends on `get_pass`, Unix passwd lookup, `initialize_password_db`, `get_global_sam_sid`, and `samba_cmdline`/loadparm helpers.

## Risks and Edge Cases

Option parsing is old-style and stateful; combinations such as local add/delete with remote operations are rejected only after parsing. Root-only operations are sensitive because they can change passdb entries or store LDAP secrets. Trust account name manipulation must avoid overflowing the fixed `fstring`. Non-root changes always go through a remote path, including localhost, so network/service availability affects local user workflows. Password handling is security-sensitive because values pass through process memory and optional stdin mode.

## Test Signals

Useful tests include CLI option matrix coverage, setuid-root rejection, root versus non-root flows, local passdb add/delete/enable/disable/no-password operations, remote password-change failures, trust-account `$` normalization, LDAP admin password storage with and without stdin prompting, and valgrind/sanitizer checks for prompt and error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbpasswd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbtree.c -->
# sources/user-network-fs/samba/source3/utils/smbtree.c

## Purpose

`sources/user-network-fs/samba/source3/utils/smbtree.c` implements the `smbtree` network-neighborhood browser. It enumerates workgroups, servers, and optionally shares through libsmbclient using `smb://` directory traversal. The source was read as a complete 299-line file.

## Important APIs, Types, and Functions

The executable has `main`, an auth callback `get_auth_data_with_context_fn`, enum `tree_level` (`LEV_WORKGROUP`, `LEV_SERVER`, `LEV_SHARE`), and global `level`. It configures `SMBCCTX`, uses libsmbclient function slots such as `Opendir`, `Readdir`, and `Closedir`, and consumes credentials from `samba_cmdline_get_creds`.

## Control Flow

`main` initializes locale, stdout buffering, Samba client command-line parsing, and popt options. `--domains` stops at workgroups, `--servers` stops at server listing, and the default includes shares. After building an `SMBCCTX`, it points the configuration at `smb.conf`, preserves the debug level, forces the protocol max/min option to `"NT1"`, installs the auth callback, and initializes the context. It opens `smb://`, prints workgroup names, recursively opens `smb://WORKGROUP/` for servers, and opens `smb://SERVER/` for shares.

## State and Persistence Behavior

The program has no durable state. Runtime state is the libsmbclient context, active directory handles, command-line credentials, and talloc strings for URLs/server names. Output is printed directly to stdout.

## Dependencies and Integration Points

It depends on libsmbclient, Samba cmdline credentials, `smb.conf`, NetBIOS name browsing, the srvsvc/RPC and namequery stack, and SMB1/NT1 browsing behavior. The error message explicitly documents that the utility does not work when NetBIOS name resolution is not configured and that SMB2/SMB3 browsing via WSD/LLMNR is not supported here.

## Risks and Edge Cases

The core behavior depends on SMB1/NetBIOS browsing, which is disabled in many modern environments. A failed nested `opendir` aborts the whole command rather than skipping only the failing workgroup/server. The auth callback silently returns if fixed-size output buffers are too small. Directory-entry storage can be overwritten by nested readdir calls, so the code copies server names before opening shares.

## Test Signals

Tests should cover option parsing levels, credential callback truncation behavior, empty/failed `smb://` root browsing, server/share enumeration with a mock or test libsmbclient server, and environments where NT1 browsing is disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status.c -->
# sources/user-network-fs/samba/source3/utils/status.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status.c` implements `smbstatus`, Samba's live status-reporting command. It reports active sessions, tree connections, open files/share modes, byte-range locks, notify registrations, and profiling information in either text or JSON mode. The source was read as a complete 1341-line file.

## Important APIs, Types, and Functions

Important functions include `main`, `prepare_sessionid`, `traverse_sessionid`, `prepare_connections`, `traverse_connections`, `prepare_share_mode`, `print_share_mode`, `prepare_brl`, `print_brl`, `prepare_notify`, `print_notify_rec`, `session_dialect_str`, crypto helpers `smbXsrv_is_encrypted`, `smbXsrv_is_partially_encrypted`, `smbXsrv_is_signed`, `smbXsrv_is_partially_signed`, and user filters `Ucrit_addUid`, `Ucrit_checkUid`, `Ucrit_addPid`, `Ucrit_checkPid`. It shares `struct traverse_state` and `enum crypto_degree` with `status.h`.

## Control Flow

`main` initializes Samba command-line parsing, default log level, security, optional Jansson root JSON, and root-only messaging context. It parses flags for process/share/lock/notify/profile/brief/numeric/json/fast/resolve-uids. Profile-only modes call `status_profile_dump` or `status_profile_rates`. Otherwise it traverses session records with `sessionid_traverse_read`, connection records with `connections_forall_read`, share-mode records with `share_entry_forall_read`, optional byte-range locks with `brl_forall`, and notify records with `notify_walk`.

## State and Persistence Behavior

The file reads persistent/live Samba databases but does not mutate them: session DB, connection TDB, `locking.tdb`, share-mode locks, leases DB, notifyd DB, messaging context, and profile shared memory. User filtering stores one uid and up to `SMB_MAXPIDS` matching server IDs in static globals so later share/lock views can be limited to the selected user's processes.

## Dependencies and Integration Points

It integrates with `session.h`, locking/share-mode APIs, `conn_tdb`, `serverid`, leases DB, notifyd, messaging, profile support, loadparm/cmdline contexts, and JSON/profile helper modules. JSON output calls `status_json.c`; when Jansson is absent, JSON is rejected at runtime.

## Risks and Edge Cases

The command requires real root and rejects setuid use. `--fast` disables process-existence checks, so stale records may appear. Unknown share deny modes and unknown crypto/signing ciphers can produce warnings or error status. User filtering has a hard `SMB_MAXPIDS` limit. Several traversal callbacks return errors only through integer status while the top-level flow often continues, so partial data or truncated lock lists are possible.

## Test Signals

Tests should exercise text and JSON output, root/setuid rejection, process-only/share-only/lock-only/brief combinations, stale process filtering versus `--fast`, user filtering, crypto/signing degree formatting, share-mode and lease display, byte-range lock traversal, notify output, and no-`locking.tdb` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status.h -->
# sources/user-network-fs/samba/source3/utils/status.h

## Purpose

`sources/user-network-fs/samba/source3/utils/status.h` defines the shared status traversal state and crypto classification enum used by `smbstatus`, JSON output, and profile output. The source was read as a complete 45-line file.

## Important APIs, Types, and Functions

The key type is `struct traverse_state`, with `json_output`, `first`, `resolve_uids`, and, under `HAVE_JANSSON`, `root_json`. The key enum is `enum crypto_degree` with `CRYPTO_DEGREE_NONE`, `CRYPTO_DEGREE_PARTIAL`, `CRYPTO_DEGREE_ANONYMOUS`, and `CRYPTO_DEGREE_FULL`.

## Control Flow

This header has no runtime control flow. It supplies the state object passed through `status.c` traversal callbacks and helper emitters.

## State and Persistence Behavior

The state is per-command runtime state. `first` controls text header emission, `json_output` selects JSON versus text emitters, `resolve_uids` controls UID name enrichment for open-file records, and `root_json` owns the top-level Jansson object while `smbstatus` runs.

## Dependencies and Integration Points

When Jansson is available the header includes `<jansson.h>`, `audit_logging.h`, and `auth/common_auth.h` so `struct json_object` is visible. It is included by `status.c`, `status_json.h`, and `status_profile.h`.

## Risks and Edge Cases

Because JSON fields are conditionally compiled, all users must be built with consistent `HAVE_JANSSON` settings. The enum ordering is used as a classification contract between `status.c` and JSON/text formatters.

## Test Signals

Compile tests should cover both Jansson and non-Jansson builds, plus text and JSON traversal paths that rely on the same state object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_json.c -->
# sources/user-network-fs/samba/source3/utils/status_json.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_json.c` implements JSON emitters for `smbstatus`. It converts sessions, tree connections, open files, byte-range locks, notify records, profile counters, server IDs, access masks, share modes, oplocks, leases, crypto state, and timestamps into the `state->root_json` object. The source was read as a complete 1446-line file.

## Important APIs, Types, and Functions

Public functions are `add_general_information_to_json`, `add_section_to_json`, `add_profile_item_to_json`, `add_profile_persvc_item_to_json`, `traverse_connections_json`, `traverse_sessionid_json`, `print_share_mode_json`, `print_brl_json`, and `print_notify_rec_json`. Important helpers include `add_server_id_to_json`, `map_mask_to_json`, `add_nested_item_to_json`, `add_crypto_to_json`, channel emitters, access/caching/oplock/lease/sharemode emitters, `lease_key_to_str`, `add_open_to_json`, `add_fileid_to_json`, and `add_lock_to_json`.

## Control Flow

`smbstatus` creates `root_json`, calls `add_general_information_to_json`, adds empty sections before each traversal, and each callback updates the relevant section object. Sessions are keyed by session id and include channels. Tcons are keyed by tree-connect id. Open files are keyed by service path plus filename and contain nested `opens` keyed by server id/share file id. Byte-range locks are keyed by share path plus filename and contain a `locks` array. Notify records are keyed by server id.

## State and Persistence Behavior

The file only mutates the in-memory JSON tree. It uses talloc stack frames for temporary strings and frees temporary JSON objects on failure. It reads fields supplied by `status.c`, including live session globals, connection data, share-mode entries, lease state, and notify instances.

## Dependencies and Integration Points

It depends on Jansson through Samba's `audit_logging` JSON wrappers, `smbprofile`, `conn_tdb`, `session`, generated NDR structs, security/open-file constants, server ID utilities, time conversion, and `status.h`. It is selected in `wscript_build` only when `HAVE_JANSSON` is configured.

## Risks and Edge Cases

`map_mask_to_json` asserts that all bits are known, so new access/oplock/share/lease bits can crash debug/assert builds until the tables are updated. Several section updates rely on `json_get_object` behavior for missing keys after `add_section_to_json`; calling emitters without preparation can fail. Path-based JSON keys can collide for repeated names or unusual path normalization. The JSON object update pattern is verbose and error-prone if future helpers forget to free invalid objects.

## Test Signals

Tests should compare JSON schema for sessions, tcons, opens, locks, notify records, profile sections, UID resolution on/off, lease and oplock combinations, unknown/expanded mask bits, no data sections, and builds with and without Jansson.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_json.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_json.h -->
# sources/user-network-fs/samba/source3/utils/status_json.h

## Purpose

`sources/user-network-fs/samba/source3/utils/status_json.h` declares the JSON output interface used by `smbstatus` and profile dumping. The source was read as a complete 84-line file.

## Important APIs, Types, and Functions

It declares section/general/profile helpers plus traversal emitters for connections, sessions, share modes, byte-range locks, and notify records. Parameters expose the data contracts from `conn_tdb`, `sessionid`, `share_mode_data`, `share_mode_entry`, `file_id`, `server_id`, `notify_instance`, `brl_flavour`, and `enum crypto_degree`.

## Control Flow

The header has no executable flow. `status.c` calls `add_section_to_json` before traversals and calls the typed JSON functions from callbacks. `status_profile.c` calls profile item helpers when `state->json_output` is true.

## State and Persistence Behavior

All functions mutate the in-memory `struct traverse_state` root JSON object and do not own persistent storage.

## Dependencies and Integration Points

It includes `status.h` and notifyd DB declarations. The implementations are either the real Jansson-backed `status_json.c` or no-op fallbacks in `status_json_dummy.c`, selected by the build.

## Risks and Edge Cases

The header is compiled even for non-Jansson builds, so declarations must remain compatible with dummy implementations. Any signature change must be synchronized with `status.c`, `status_profile.c`, `status_json.c`, and `status_json_dummy.c`.

## Test Signals

Compile coverage for both implementation variants and integration tests for `smbstatus --json` are the primary signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_json.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_json_dummy.c -->
# sources/user-network-fs/samba/source3/utils/status_json_dummy.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_json_dummy.c` provides no-op implementations of the `status_json.h` interface when Samba is built without Jansson JSON support. The source was read as a complete 111-line file.

## Important APIs, Types, and Functions

It defines every JSON interface function: `add_section_to_json`, `add_general_information_to_json`, profile item helpers, connection/session traversal JSON hooks, share-mode and byte-range-lock JSON printers, and `print_notify_rec_json`.

## Control Flow

Every function immediately returns success-like values (`0` for integer functions and `0`/false for the bool notify function). In normal non-Jansson runtime, `status.c` rejects `--json` before these emitters are used, so the dummy module mainly satisfies link-time references.

## State and Persistence Behavior

No state is read or written. Parameters are ignored, and no JSON tree exists in `struct traverse_state` for non-Jansson builds.

## Dependencies and Integration Points

The file includes the same broad Samba status/open-file/security headers needed for signature compatibility. `wscript_build` chooses this file instead of `status_json.c` when `HAVE_JANSSON` is not configured.

## Risks and Edge Cases

If future code calls JSON emitters without first rejecting JSON mode in non-Jansson builds, these no-ops could make the command appear to succeed while emitting no structured content. Signature drift against the real implementation would cause build failures.

## Test Signals

Build tests without Jansson should link `smbstatus`, and runtime tests should verify `smbstatus --json` reports JSON support unavailable rather than silently producing empty output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_json_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_profile.c -->
# sources/user-network-fs/samba/source3/utils/status_profile.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_profile.c` implements `smbstatus` profile dumping and profile rate display when Samba is built with profiling support. It prints raw profile counters, JSON profile counters, per-service profile sections, and a continuous one-second rate view. The source was read as a complete 511-line file.

## Important APIs, Types, and Functions

Public functions are `status_profile_dump` and `status_profile_rates`. Helpers include `profile_separator`, `print_buckets`, `status_profile_dump_persvc_stats`, `status_profile_dump_persvc_cb`, `status_profile_dump_persvc`, rate printers for count/basic/bytes/iobytes stats, and `print_count_samples`. The implementation relies heavily on `SMBPROFILE_STATS_ALL_SECTIONS` macro expansion.

## Control Flow

`status_profile_dump` initializes profile shared memory with `profile_setup`, collects a `profile_stats` snapshot, and expands profile macros to print each counter or add JSON fields. In JSON mode it also collects per-service stats with `smbprofile_persvc_collect`. `status_profile_rates` initializes profiling, collects alternating samples, computes deltas once per second, prints active rates, swaps sample buffers, and sleeps until the next sample.

## State and Persistence Behavior

It reads profiling shared memory but does not persist data. Rate mode keeps static two-element `sample_data` and `sample_time` buffers for delta calculations and runs indefinitely until interrupted.

## Dependencies and Integration Points

It depends on `smbprofile.h`, `status_profile.h`, `conn_tdb`, generated open-files types, and `status_json.h`. `status.c` dispatches to it for `-P` and `-R`; `wscript_build` selects this file only when `WITH_PROFILE` is enabled.

## Risks and Edge Cases

The macro-based counter expansion must stay synchronized with `smbprofile` structures. Rate conversion divides by elapsed seconds after converting microseconds, so unusually short or skewed intervals can produce zero or misleading rates; the code guards only zero microsecond deltas. Rate mode is intentionally infinite. JSON profile output depends on the JSON section hierarchy already being valid.

## Test Signals

Tests should cover text and JSON dumps, no-profile-memory failure, per-service profile collection, rate output with synthetic sample deltas, verbose delay logging, and build selection with `WITH_PROFILE` on/off.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_profile.h -->
# sources/user-network-fs/samba/source3/utils/status_profile.h

## Purpose

`sources/user-network-fs/samba/source3/utils/status_profile.h` declares the profile reporting interface used by `smbstatus`. The source was read as a complete 30-line file.

## Important APIs, Types, and Functions

It declares `status_profile_dump(bool be_verbose, struct traverse_state *state)` and `status_profile_rates(bool be_verbose)`.

## Control Flow

The header has no runtime flow. `status.c` calls these functions when `--profile` or `--profile-rates` is selected.

## State and Persistence Behavior

The dump function receives the shared `traverse_state` so it can emit either text or JSON profile output. Rate mode has no caller-supplied state beyond verbosity.

## Dependencies and Integration Points

It includes `replace.h` and `status.h`, tying the profile API to the `smbstatus` output mode state. Implementations are selected between `status_profile.c` and `status_profile_dummy.c`.

## Risks and Edge Cases

Any signature change requires coordinated updates in the real implementation, dummy implementation, and `status.c`. JSON behavior depends on `struct traverse_state` remaining the shared output contract.

## Test Signals

Compile tests for both profile-enabled and profile-disabled builds plus `smbstatus -P`/`-R` smoke tests cover this header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_profile_dummy.c -->
# sources/user-network-fs/samba/source3/utils/status_profile_dummy.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_profile_dummy.c` provides profile API fallbacks when Samba is built without profiling support. The source was read as a complete 35-line file.

## Important APIs, Types, and Functions

It defines `status_profile_dump` and `status_profile_rates`, matching `status_profile.h`.

## Control Flow

Both functions print `Profile data unavailable` to stderr and return `true`. This lets `smbstatus -P` or `-R` link and finish without profile support, though no profile data is shown.

## State and Persistence Behavior

No state is read or written. Arguments are ignored apart from signature compatibility.

## Dependencies and Integration Points

The file includes `smbprofile.h` and `status_profile.h` for ABI compatibility. `wscript_build` selects it when `WITH_PROFILE` is not configured.

## Risks and Edge Cases

Returning success after printing an unavailable message can make automation think a profile command succeeded. If stricter semantics are desired, the caller or dummy implementation would need to return failure.

## Test Signals

Profile-disabled builds should link `smbstatus`, and `smbstatus -P`/`-R` should print the unavailable message without crashing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/status_profile_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/testparm.c -->
# sources/user-network-fs/samba/source3/utils/testparm.c

## Purpose

`sources/user-network-fs/samba/source3/utils/testparm.c` implements `testparm`, the Samba configuration syntax and logic checker. It loads `smb.conf`, reports global and per-share configuration problems, can dump full or filtered configuration, can list all parameters, and can test host allow/deny access decisions. The source was read as a complete 1231-line file.

## Important APIs, Types, and Functions

Key functions are `main`, `do_global_checks`, `do_per_share_checks`, `do_idmap_check`, `lp_scan_idmap_found_domain`, `idmap_config_int`, `pw2kt_check_line`, `pw2kt_validate_spn_spec`, and `directory_exist_stat`. Local structs `idmap_config` and `idmap_domains` hold discovered idmap backend/range data.

## Control Flow

`main` initializes cmdline/loadparm, parses options such as `--suppress-prompt`, `--verbose`, `--skip-logic-checks`, `--show-all-parameters`, `--parameter-name`, and `--section-name`, loads the selected config with registry shares, reports weak crypto state, runs global/per-share checks unless skipped, and dumps configuration or host access decisions. `do_global_checks` performs hard-coded warnings/errors for security modes, WINS settings, directories, socket options, password sync, idmap, crypto hardening, keytab sync, and mixed quoting warnings. `do_per_share_checks` validates hosts allow/deny lists, oplock settings, DOS attribute masks, print command quirks, and mixed `vfs_fruit` usage.

## State and Persistence Behavior

The tool reads configuration and filesystem metadata but does not persist changes. It uses talloc for temporary idmap and parsing data, and writes diagnostics to stderr and config dumps to stdout.

## Dependencies and Integration Points

It integrates with Samba loadparm, registry shares, host access checks, GnuTLS helper state, regex scanning of parametric options, filesystem stat wrappers, Kerberos/keytab configuration, PAM/systemd-userdb build options, and Samba's parameter dump APIs.

## Risks and Edge Cases

The logic checks encode security policy assumptions and version-specific warnings, so stale checks can create noisy or missing diagnostics. Idmap scanning caps the temporary discovered-domain array at 32 entries. Some loops scan service numbers from 0 to 999, depending on `VALID_SNUM`. Mixed quoting warnings reference CVE-driven substitution behavior and must stay aligned with actual substitution semantics.

## Test Signals

Tests should cover valid and invalid smb.conf loading, filtered parameter/section dumps, host allow/deny checks, idmap range overlap and autorid range-size checks, ADS/domain security requirements, directory permission warnings, password sync validation, crypto hardening warnings, `sync machine password to keytab` parser cases, and per-share VFS/printing/oplock validations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/testparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/wscript_build -->
# sources/user-network-fs/samba/source3/utils/wscript_build

## Purpose

`sources/user-network-fs/samba/source3/utils/wscript_build` is the Waf build manifest for many Samba source3 utility binaries and utility subsystems. It declares sources, dependencies, install behavior, feature gates, and conditional source composition for tools such as `smbpasswd`, `smbtree`, `testparm`, `smbstatus`, `net`, `mdsearch`, and `wspsearch`. The source was read as a complete 373-line file.

## Important APIs, Types, and Functions

The file uses build DSL calls including `bld.SAMBA3_SUBSYSTEM`, `bld.SAMBA3_BINARY`, `bld.SAMBA_BINARY`, `bld.SAMBA3_PYTHON`, `bld.CONFIG_GET`, and `bld.CONFIG_SET`. Important local build variable `smbstatus_source` conditionally appends `status_profile.c` or `status_profile_dummy.c`, and `status_json.c` or `status_json_dummy.c`.

## Control Flow

At Waf configure/build time, the script registers subsystems first, then many binaries with multiline dependency lists. Conditional build gates enable `samba-regedit`, `mvxattr`, `smb_prometheus_endpoint`, and `wspsearch` only under corresponding environment/config flags. `smbstatus` source list is assembled based on `WITH_PROFILE` and `HAVE_JANSSON`.

## State and Persistence Behavior

The file does not own runtime state. It affects build graph state by registering targets, dependency edges, install paths, and source selections.

## Dependencies and Integration Points

It connects utility source files to Samba libraries such as `smbconf`, `CMDLINE_S3`, `cmdline_contexts`, `pdb`, `PASSWD_UTIL`, `PASSCHANGE`, `smbclient`, `msrpc3`, `LOCKING`, `PROFILE`, `CONN_TDB`, `jansson`, `common_auth`, WSP libraries, and Python embedding libraries.

## Risks and Edge Cases

Dependency omissions surface as link or runtime feature failures. Conditional dummy/real source selection for `smbstatus` must match C preprocessor expectations around Jansson/profile support. Feature-gated tools like `wspsearch` can silently disappear from builds when environment flags are false.

## Test Signals

Build matrix tests should cover profile on/off, Jansson on/off, WSP enabled/disabled, optional regedit/mvxattr/prometheus settings, and link-time coverage for each declared binary.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/wspsearch.c -->
# sources/user-network-fs/samba/source3/utils/wspsearch.c

## Purpose

`sources/user-network-fs/samba/source3/utils/wspsearch.c` implements a command-line Windows Search Protocol client for querying a remote server's WSP service over IPC/RPC. It builds default or custom WSP SQL queries, binds result columns, polls result counts, retrieves rows, and prints result values. The source was read as a complete 847-line file.

## Important APIs, Types, and Functions

Important functions are `main`, `wsp_connect`, `create_query`, `create_bindings`, `create_querystatusex`, `create_getrows`, `print_rowsreturned`, `is_valid_kind`, and `build_default_sql`. It uses WSP request/response structs, `wsp_client_ctx`, `wsp_cpmsetbindingsin`, `t_select_stmt`, `DATA_BLOB`, and DCERPC binding handles.

## Control Flow

`main` parses `--limit`, `--search`, `--kind`, `--query`, Samba connection, and credential options. It parses `//server/share`, builds default SQL with `Scope`, kind, and phrase clauses unless a custom query is supplied, parses SQL with `get_wsp_sql_tree`, ensures a default `System.ItemUrl` column, connects to `IPC$`, creates a WSP client, sends CPMConnectIn, creates a query, sets bindings, asks query status for result count, then loops `CPMGetRows` requests until rows are exhausted or the requested limit is reached.

## State and Persistence Behavior

The tool maintains only runtime RPC/client state: SMB connection, WSP pipe context, cursor, bindings, row buffers, and talloc contexts. It does not persist query state locally; server-side WSP cursor state exists for the connection lifetime.

## Dependencies and Integration Points

It depends on Samba client cmdline/credentials, `cli_full_connection_creds`, SMB transport parsing, WSP utility/client libraries, SQL/AQS parsing, generated NDR WSP types, DCERPC timeout handling, and talloc/tevent contexts. `wscript_build` enables it only when `bld.env.with_wsp` is true.

## Risks and Edge Cases

Argument parsing assumes `//server/share` syntax and mutates the path in place. Default query construction uses string interpolation, so quote/escaping behavior for phrase/location is important. `is_valid_kind` returns `NULL` on allocation failure despite bool return type. Row retrieval uses fixed initial batch size and magic bookmark/offset constants; incorrect 32/64-bit negotiation affects row decoding. Some popt errors are not explicitly checked because the loop body is empty.

## Test Signals

Tests should cover default SQL construction, invalid kind rejection, custom query path, missing share handling, SQL parse failures, mocked WSP request/response sequences, 32-bit and 64-bit row extraction, zero-result handling, limit enforcement, and network/RPC failure diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/wspsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/web/swat.c -->
# sources/user-network-fs/samba/source3/web/swat.c

## Purpose

`sources/user-network-fs/samba/source3/web/swat.c` is a retired Samba Web Administration Tool placeholder. It contains only copyright/license text and an ASCII memorial comment noting SWAT's retirement. The source was read as a complete 58-line file.

## Important APIs, Types, and Functions

There are no includes, declarations, functions, types, or executable APIs in this file.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The file owns no state and performs no persistence.

## Dependencies and Integration Points

There are no direct dependencies. Its presence may preserve historical source tree layout or references to the removed SWAT component.

## Risks and Edge Cases

The main risk is build-system or packaging code accidentally treating this as an active implementation. Otherwise it is inert.

## Test Signals

Only source inventory/build exclusion checks are relevant; no runtime tests apply.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/web/swat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap.c` implements the winbind idmap backend registry, idmap domain initialization/selection, configuration accessors, allocator wrappers, and Unix-ID-to-SID dispatch. It is the central glue between winbind callers and pluggable idmap modules. The source was read as a complete 632-line file.

## Important APIs, Types, and Functions

Important functions are `lp_scan_idmap_domains`, `idmap_init`, `smb_register_idmap`, `idmap_find_domain`, `idmap_find_domain_with_sid`, `idmap_close`, `idmap_allocate_uid`, `idmap_allocate_gid`, `idmap_backend_unixids_to_sids`, and config helpers `idmap_config_const_string`, `idmap_config_bool`, `idmap_config_int`, `idmap_config_string_list`, `domain_has_idmap_config`. Important static state includes backend list `backends`, `default_idmap_domain`, `passdb_idmap_domain`, `idmap_domains`, and `num_domains`.

## Control Flow

Backends register with `smb_register_idmap`. `idmap_init` runs static backend initialization once, creates the default `*` domain unless passdb owns everything else, creates a passdb domain for the local SAM, allocates the named-domain list, and scans parametric `idmap config DOMAIN : backend` settings. Domain creation loads/probes the requested backend, parses range/read-only options, and calls backend `init`.

## State and Persistence Behavior

This file owns process-global in-memory registry/domain state. It reads idmap configuration from loadparm but does not persist mappings itself; persistence is delegated to backend methods.

## Dependencies and Integration Points

It integrates with static idmap module declarations, dynamic module probing, passdb SID ownership, Samba loadparm parametric options, winbind offline state, and backend method tables (`init`, `allocate_id`, `unixids_to_sids`, `sids_to_unixids`). `idmap_find_domain_with_sid` routes passdb-owned SIDs to the passdb backend.

## Risks and Edge Cases

Initialization is guarded by a static bool and uses globals, so lifecycle and reinitialization must be careful. Range parsing accepts missing/invalid ranges only when `check_range` is false. `domain_has_idmap_config` checks initialized domains and loadparm fallback. Backend registration rejects version mismatch and duplicate names; missing modules fail domain creation. `idmap_close` frees domains but does not reset the static initialized flag.

## Test Signals

Tests should cover backend registration version/name validation, default/passdb/named domain selection, dynamic module probing failures, range parsing, read-only option handling, domain scanning, passdb SID routing, allocator wrappers, and close/reinitialize behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_ad.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_ad.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap_ad.c` implements the `idmap_ad` backend, mapping between Active Directory SIDs and Unix UID/GID values stored in RFC2307/SFU schema attributes. It also optionally enriches winbind user info with Unix primary group and NSS fields from AD. The source was read as a complete 1308-line file.

## Important APIs, Types, and Functions

Key types are `struct idmap_ad_context` and `struct idmap_ad_schema_names`. Important functions include `idmap_ad_init`, `idmap_ad_initialize`, `idmap_ad_get_context`, `idmap_ad_context_create`, `idmap_ad_get_tldap_ctx`, `get_posix_schema_names`, `get_attrnames_by_oids`, `idmap_ad_dn_filter`, `idmap_ad_query_user_retry`, `idmap_ad_unixids_to_sids_retry`, and `idmap_ad_sids_to_unixids_retry`.

## Control Flow

Initialization registers `ad_methods` and the AD NSS plugins. Context creation resolves a DC from gencache, creates private krb5 config, opens LDAP or LDAPS/StartTLS according to `client ldap sasl wrapping`, binds with machine trust credentials, fetches RootDSE, discovers schema attribute names by OID, loads options such as `unix_primary_group`, `unix_nss_info`, `ldap_timeout`, `allow ous`, and `deny ous`, and caches the context in the idmap domain. Mapping functions build LDAP OR filters for requested IDs or SIDs, search under the default naming context, filter returned DNs, infer UID/GID from `sAMAccountType`, and set `id_map` statuses.

## State and Persistence Behavior

The backend keeps a cached LDAP context, schema names, default naming context, OU filters, and options in `dom->private_data`. It reads AD state but does not write AD or local mapping databases. On LDAP server-down/timeout statuses, retry wrappers free cached private data and return `NT_STATUS_HOST_UNREACHABLE` so callers can retry later with a fresh connection.

## Dependencies and Integration Points

It depends on winbind domain/DC discovery, DNS/name resolution, Kerberos private config, trust credentials, tldap, TLS/gensec bind, loadparm, generated netlogon/ADS types, LDAP schema OIDs, LDB DN comparison, global event context, and idmap/NSS plugin registration.

## Risks and Edge Cases

LDAP filter construction must escape encoded SIDs and numeric attributes correctly. AD schema mode must match the directory; missing OID lookups fail context creation. OU allow/deny filters can silently exclude valid objects. The backend refuses use on AD DC builds. Network, TLS, and credential failures are common operational edges. Mapping type inference from `sAMAccountType` must match AD semantics.

## Test Signals

Tests should cover schema-mode OID resolution, LDAP bind/TLS modes, allow/deny OU filtering, UID/GID-to-SID batch mapping, SID-to-UID/GID mapping, timeout/server-down cache reset, `unix_primary_group` and `unix_nss_info` enrichment, AD DC rejection, and registration of both idmap and NSS methods.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_ad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_ad_nss.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_ad_nss.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap_ad_nss.c` implements NSS-info plugins that map between AD account names and POSIX aliases using SFU, SFU20, or RFC2307 schema attributes. The source was read as a complete 416-line file.

## Important APIs, Types, and Functions

Important functions are `idmap_ad_nss_init`, `nss_ad_generic_init`, `nss_sfu_init`, `nss_sfu20_init`, `nss_rfc2307_init`, `nss_ad_map_to_alias`, `nss_ad_map_from_alias`, `ad_idmap_cached_connection`, and `ad_map_type_string`. It defines a local `struct idmap_ad_context` with ADS connection, `posix_schema`, and map type.

## Control Flow

Plugin initialization registers three `nss_info_methods` tables under names `rfc2307`, `sfu`, and `sfu20`. Each init function creates or reuses an `idmap_domain` in the NSS domain entry and sets the desired POSIX mapping type. Alias mapping obtains a cached ADS connection, loads schema details if needed, searches by `sAMAccountName` to read the POSIX uid alias, or searches by POSIX uid alias to return `WORKGROUP\samAccountName`.

## State and Persistence Behavior

The plugin caches ADS connection/schema state in the NSS domain entry. It reads LDAP/AD attributes only and does not persist mappings. It refuses online lookups when winbind is in offline-logon state.

## Dependencies and Integration Points

It depends on ADS cached connections, `ads_check_posix_schema_mapping`, ADS LDAP search helpers, Samba idmap offline state, `nss_info` plugin registration, loadparm workgroup, and AD schema definitions from `libads/ldap_schema.h`.

## Risks and Edge Cases

The parameter validation in `nss_ad_map_to_alias` checks `!*alias`, which assumes the caller passes a non-null pointer with current content semantics; this is easy to misuse. LDAP filters interpolate names/aliases and need correct escaping behavior from callers or ADS helpers. Offline mode returns `NT_STATUS_FILE_IS_OFFLINE`. Schema absence returns object path/name errors.

## Test Signals

Tests should cover all three plugin registrations, map-type override warnings, offline behavior, missing schema, successful name-to-alias and alias-to-name LDAP searches, no-result handling, and invalid parameter cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_ad_nss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_autorid.c -->
# sources/user-network-fs/samba/source3/winbindd/idmap_autorid.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap_autorid.c` implements the `autorid` idmap backend. It algorithmically maps domain SID/RID ranges to Unix IDs while automatically allocating numeric ranges per domain and preserving special allocation-pool mappings in `autorid.tdb`. The source was read as a complete 945-line file.

## Important APIs, Types, and Functions

Key functions include `idmap_autorid_init`, `idmap_autorid_initialize`, `idmap_autorid_allocate_id`, `idmap_autorid_unixids_to_sids`, `idmap_autorid_sids_to_unixids`, `idmap_autorid_id_to_sid`, `idmap_autorid_sid_to_id`, `idmap_autorid_sid_to_id_alloc`, `idmap_autorid_sid_to_id_special`, `idmap_autorid_preallocate_wellknown`, and `idmap_autorid_initialize_action`. Important globals are `autorid_db` and `ignore_builtin`; `IDMAP_AUTORID_ALLOC_RESERVED` reserves high IDs in the allocation range.

## Control Flow

Initialization only accepts the default `*` idmap domain, builds an `idmap_tdb_common_context`, reads `rangesize` and `ignore builtin`, computes `maxranges`, opens `state_path("autorid.tdb")`, initializes HWMs/config in a transaction, and preallocates well-known group SIDs. SID-to-ID mapping splits the RID, derives domain range index, finds or allocates an autorid range, and computes `id = reduced_rid + range_low_id`. ID-to-SID mapping reverses the calculation by looking up the stored range-number-to-domain record. Well-known/allocated SIDs use the tdb-common allocation pool.

## State and Persistence Behavior

Persistent state lives in `autorid.tdb`: domain/range assignments, configuration, high-water marks, and explicit allocation-pool mappings. The backend writes new ranges and mappings unless `dom->read_only` is true. Runtime state is the shared DB context and global config under `dom->private_data`.

## Dependencies and Integration Points

It depends on `idmap_autorid_tdb` helpers, `idmap_tdb_common`, winbind domain knowledge, samlogon cache, machine SID/passdb checks, SID utility helpers, and the idmap backend registration API.

## Risks and Edge Cases

Incorrect `rangesize` or idmap range configuration can exhaust ranges or fail initialization; at least two ranges are required. Unknown domains are not allocated unless validated by local/builtin/own-domain checks, existing range zero, caller type hints, or samlogon cache. Read-only mode suppresses allocation. ID boundary checks must avoid off-by-one errors near max range. Special SID allocation scans only the reserved top 500 IDs.

## Test Signals

Tests should cover initialization constraints, range-size math, persistence in `autorid.tdb`, SID-to-ID and ID-to-SID round trips across multiple domain range indexes, read-only behavior, unknown-domain `ID_REQUIRE_TYPE`, builtin ignore mode, allocation-pool mappings, well-known preallocation, and database corruption/invalid-record handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/idmap_autorid.c -->
