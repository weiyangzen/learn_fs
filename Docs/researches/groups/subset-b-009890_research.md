# Research: subset-b-009890

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.c -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth.c

## Purpose

`ntlm_auth.c` implements Samba's `ntlm_auth` command and stdio helper. It authenticates plaintext passwords, NTLM challenge/response blobs, Squid helper exchanges, NTLMSSP client/server handshakes, SPNEGO/GSS handshakes, and password-change helper requests. The file is both a command-line utility and a long-lived line-oriented protocol worker used by external programs.

## Important APIs, Types, and Functions

The central state is `struct ntlm_auth_state`, which preserves helper mode, client state, GENSEC/NTLMSSP state, requested feature strings, session-key state, and private protocol state across stdin lines. `stdio_helper_protocols[]` maps externally visible helper protocol names to handler functions. Public helpers exported through `ntlm_auth_proto.h` include `get_winbind_domain()`, `get_winbind_netbios_name()`, `get_challenge()`, `contact_winbind_auth_crap()`, and `get_pam_winbind_config()`.

Important internal paths include `check_plaintext_auth()` for `WINBINDD_PAM_AUTH`, `contact_winbind_auth_crap()` for `WINBINDD_PAM_AUTH_CRAP`, `contact_winbind_change_pswd_auth_crap()` for encrypted password changes, `make_auth4_context_ntlm_auth()` for GENSEC password checking, `ntlm_auth_prepare_gensec_client()` and `ntlm_auth_prepare_gensec_server()` for SPNEGO/NTLMSSP setup, and `manage_gensec_request()` for most token-based helper protocols.

## Control Flow

`main()` initializes Samba cmdline/loadparm state, parses options, derives domain/user defaults, opens a loadparm context, and then either starts a persistent helper stream or performs a one-shot authentication. Helper mode enters `squid_stream()`, which repeatedly calls `manage_squid_request()` to assemble one newline-delimited request up to `MAX_BUFFER_SIZE` and dispatch to the selected handler.

Basic helper requests split `user password`, optionally RFC1738-decode Squid 2.5 input, and call `check_plaintext_auth()`. GENSEC helpers accept prefixes such as `YR`, `TT`, `KK`, `AF`, `NA`, `PW`, `GK`, `GF`, and `SF`; they lazily create client or server GENSEC state, decode base64 tokens, call `gensec_update()`, squash authentication errors, and print Squid-compatible response codes. `NTLM_SERVER_1` and `NTLM_CHANGE_PASSWORD_1` accumulate key/value request lines in static variables until `.` commits the transaction, then reset the static request state.

## State and Persistence Behavior

The process holds option globals for username/domain/workstation/password, response blobs, membership requirements, cached/offline flags, and target SPN fields. Winbind details and generated challenges are cached in static variables. Long-lived helpers retain GENSEC state across lines. Authentication itself is delegated to winbind and does not persist local account data, except password-change requests forwarded to winbind can mutate account passwords. Sensitive plaintext and hashes are partially zeroed in some paths, but many values live in talloc allocations or static request variables until reset.

## Dependencies and Integration Points

The file integrates with libwbclient/winbindd private requests, GENSEC, NTLMSSP, SPNEGO, Kerberos PAC parsing when available, Samba credentials/loadparm/cmdline libraries, tiniparser for `pam_winbind.conf`, base64/hex utilities, GnuTLS ARCFOUR for password-change blob encryption, and diagnostics in `ntlm_auth_diagnostics.c`.

## Risks and Edge Cases

The helper protocols are external compatibility contracts; output prefixes and newline framing are fragile. Several helper transactions use static variables, which is acceptable for single-threaded stdin helpers but unsuitable for concurrent dispatch. `manage_ntlm_change_password_1_request()` has subtle blob-presence checks and a reset typo that assigns `old_nt_hash_enc` twice instead of clearing `old_lm_hash_enc`. Some request blob copies assume validated fixed lengths, while winbind auth caps or allocates large NTLMv2 responses. Password material moves through stdout prompts, talloc, static buffers, and GnuTLS state, so memory-lifetime review matters.

## Test Signals

Useful tests are Squid basic/NTLMSSP protocol transcripts, GSS-SPNEGO client/server token exchange tests, challenge/response one-shot auth with and without session-key requests, membership restriction tests using name and SID forms, offline/cached credential paths, FIPS/ARCFOUR password-change failures, and diagnostics mode against servers with and without LM support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.h -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth.h

## Purpose

`ntlm_auth.h` is the small public coordination header for the NTLM authentication utility. It includes the collected prototype header and exposes command option globals needed by the diagnostics translation unit.

## Important APIs, Types, and Functions

The header includes `utils/ntlm_auth_proto.h` and declares `extern const char *opt_username`, `opt_domain`, `opt_workstation`, and `opt_password`. These globals are defined in `ntlm_auth.c` and consumed by `ntlm_auth_diagnostics.c`.

## Control Flow

There is no runtime control flow in this header. Its compile-time role is to make the main utility's parsed option state visible to diagnostics helpers and to surface the helper function prototypes.

## State and Persistence Behavior

The declared globals carry process-wide authentication identity and password state. Because diagnostics reads them directly, diagnostics must be run after `main()` has parsed defaults and prompted or accepted a password. The state is not isolated per test.

## Dependencies and Integration Points

This header couples `ntlm_auth.c`, `ntlm_auth_diagnostics.c`, and `ntlm_auth_proto.h`. It also inherits all type requirements for `DATA_BLOB`, `NTSTATUS`, and `TALLOC_CTX` through included Samba headers.

## Risks and Edge Cases

The diagnostics code depends on mutable process-global option state rather than a parameter object. Any future attempt to run diagnostics independently, reentrantly, or in parallel would need to break this coupling. Since `opt_password` is an extern pointer, callers must also preserve its lifetime for the whole diagnostic pass.

## Test Signals

Compile coverage should ensure both `ntlm_auth.c` and `ntlm_auth_diagnostics.c` include this header cleanly. Behavioral coverage comes from running `ntlm_auth --diagnostics`, which proves the extern option handoff is initialized before diagnostics reads it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_diagnostics.c -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth_diagnostics.c

## Purpose

`ntlm_auth_diagnostics.c` is a diagnostic harness for the `ntlm_auth` utility. It synthesizes LM, NTLM, LMv2, NTLMv2, and plaintext-in-response-field authentication attempts, sends them through `contact_winbind_auth_crap()`, and verifies whether authentication and returned session keys match expectations.

## Important APIs, Types, and Functions

`enum ntlm_break` describes deliberate test mutations: no mutation, broken LM, broken NT, no LM, or no NT. `diagnose_ntlm_auth()` is the exported entry point. `test_lm_ntlm_broken()`, `test_ntlm_in_lm()`, `test_ntlm_in_both()`, `test_lmv2_ntlmv2_broken()`, and `test_plaintext()` perform the main protocol variants. `test_table[]` orders all diagnostic cases and marks tests that should only pass when LM support is expected.

## Control Flow

`diagnose_ntlm_auth()` iterates `test_table[]`, passes the caller's LANMAN expectation into each test, and fails the overall result if a required test fails or an LM-only test unexpectedly passes when LM support should be disabled. Each test builds a challenge with `get_challenge()`, derives responses and expected keys from the process-global username/domain/password, optionally corrupts or removes one response, calls winbind through `contact_winbind_auth_crap()`, and compares returned LM/user session keys to expected hashes or NTLMv2 session keys.

## State and Persistence Behavior

The diagnostics code does not persist account state. It consumes the process-global option values declared in `ntlm_auth.h` and uses talloc stack allocations for blobs. Authentication attempts may update winbind-side bad password counters or logs because deliberately corrupted responses are sent to the real authentication backend.

## Dependencies and Integration Points

It depends on Samba NTLM crypto helpers (`SMBencrypt`, `SMBNTencrypt`, `SMBNTLMv2encrypt`, `E_deshash`, `E_md4hash`, `SMBsesskeygen_ntv1`), `contact_winbind_auth_crap()` from `ntlm_auth.c`, winbind status flags, and debug/dump utilities. It also uses `get_winbind_netbios_name()` and `get_winbind_domain()` to build NTLMv2 target names.

## Risks and Edge Cases

Diagnostics are live authentication attempts, not offline unit tests. Broken-response cases can trigger account lockout policy or misleading audit noise. Expected LM-key behavior differs by server capability, so the `lanman_support_expected` input must match the environment. The plaintext diagnostic uses a zero challenge and `MSV1_0_CLEARTEXT_PASSWORD_ALLOWED`, so policy changes around cleartext auth will affect results.

## Test Signals

The file is itself a test signal for the wider authentication chain. Useful coverage includes running diagnostics with `--request-lm-key` against an LM-capable server, without it against Samba AD-style behavior, and under bad-password lockout policy in a controlled account to confirm broken cases do not accidentally pass.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_diagnostics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_proto.h -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth_proto.h

## Purpose

`ntlm_auth_proto.h` is the collected prototype header for `ntlm_auth.c` and `ntlm_auth_diagnostics.c`. It exposes the small cross-file API needed by diagnostics and any other utility code that links these helpers.

## Important APIs, Types, and Functions

The header declares winbind metadata helpers `get_winbind_domain()` and `get_winbind_netbios_name()`, challenge generation `get_challenge()`, challenge/response authentication `contact_winbind_auth_crap()`, diagnostics entry point `diagnose_ntlm_auth()`, and `get_pam_winbind_config()`.

## Control Flow

There is no runtime control flow. The declared functions participate in `ntlm_auth` command execution: `main()` calls diagnostics, diagnostics call challenge/auth helpers, and auth helper functions contact winbind.

## State and Persistence Behavior

Declared functions operate on process-global state in `ntlm_auth.c` for defaults, options, and cached winbind details. `contact_winbind_auth_crap()` may request session keys or Unix names and can allocate error strings and Unix-name strings for the caller.

## Dependencies and Integration Points

Consumers must include Samba base types for `DATA_BLOB`, `TALLOC_CTX`, and `NTSTATUS`. The interface is tightly coupled to winbind protocol flags, NTLM response blobs, and Samba memory ownership conventions.

## Risks and Edge Cases

Because this is a frozen generated-style prototype header, API drift can happen if function signatures change without updating it. `contact_winbind_auth_crap()` ownership semantics are easy to misuse: output strings are heap-allocated and must be freed by the caller, and optional session-key buffers must be valid when their flags are requested.

## Test Signals

Compile tests should catch signature drift. Runtime checks should exercise `contact_winbind_auth_crap()` with and without `WBFLAG_PAM_LMKEY`, `WBFLAG_PAM_USER_SESSION_KEY`, and `WBFLAG_PAM_UNIX_NAME` to verify optional outputs and ownership.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_proto.h -->
# sources/user-network-fs/samba/source3/utils/passwd_proto.h

## Purpose

`passwd_proto.h` is the collected prototype header for password prompting helpers used by Samba account-management utilities.

## Important APIs, Types, and Functions

It declares `char *get_pass(const char *prompt, bool stdin_get)`, implemented in `passwd_util.c`. The function returns a newly allocated password string read either from stdin or from the terminal prompt.

## Control Flow

This header has no runtime flow. It allows tools such as `pdbedit.c` to call the shared password input helper.

## State and Persistence Behavior

The declared function returns heap memory that callers own and should wipe before freeing when holding secrets. The stdin path in the implementation uses a static `fstring`, but callers receive an allocated duplicate.

## Dependencies and Integration Points

It depends on Samba's common boolean type and memory helpers through the including translation unit. The principal integration point is `pdbedit` user creation with `--password-from-stdin`.

## Risks and Edge Cases

The API does not encode whether the returned secret has been zeroed or whether the caller must zero it. Callers that forget to scrub the returned buffer leave password material in process memory.

## Test Signals

Compile coverage through `pdbedit.c` validates the prototype. Functional checks should cover terminal prompt mode, stdin mode, EOF on stdin, and caller-side password mismatch handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_util.c -->
# sources/user-network-fs/samba/source3/utils/passwd_util.c

## Purpose

`passwd_util.c` provides the shared password-reading helper used by passdb editing tools. It supports interactive terminal prompting and script-friendly stdin input.

## Important APIs, Types, and Functions

`stdin_new_passwd()` reads one line from stdin into a static `fstring`, strips a trailing newline, and returns the static buffer. `get_pass()` selects stdin or `samba_getpass()`, then returns an `smb_xstrdup()` copy of the password.

## Control Flow

Callers pass a prompt and `stdin_get`. In stdin mode the helper reads exactly one newline-terminated password line. In interactive mode it calls `samba_getpass(prompt, pwd, sizeof(pwd), false, false)`. On read failure it returns `NULL`; otherwise it duplicates the captured password and returns ownership to the caller.

## State and Persistence Behavior

The stdin helper uses a static buffer and clears it before each read. The interactive path uses a local stack buffer. Both paths duplicate the password to heap memory; scrubbing that returned copy is the caller's responsibility. No persistent account state is changed here.

## Dependencies and Integration Points

It includes `passwd_proto.h` and relies on Samba `fstring`, `ZERO_ARRAY`, `samba_getpass()`, and `smb_xstrdup()`. `pdbedit.c` uses it while adding users and comparing repeated password entries.

## Risks and Edge Cases

The stdin path truncates input to the `fstring` size and accepts a line without a trailing newline. Because returned memory is a normal duplicate, callers must explicitly zero it. The helper does not enforce password policy; policy is applied later by account-management functions.

## Test Signals

Tests should cover stdin EOF, long stdin lines, interactive getpass failure, password strings with and without trailing newline, and caller cleanup paths that wipe both password copies after mismatch or success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/pdbedit.c -->
# sources/user-network-fs/samba/source3/utils/pdbedit.c

## Purpose

`pdbedit.c` implements Samba's passdb editing command-line utility. It lists, creates, modifies, deletes, imports, exports, repairs, and policy-edits passdb user and machine accounts.

## Important APIs, Types, and Functions

The file is organized around command bitmasks such as `BIT_LIST`, `BIT_CREATE`, `BIT_MODIFY`, `BIT_DELETE`, `BIT_IMPORT`, and `BIT_ACCPOLICY`. Key functions are `print_sam_info()`, `print_user_info()`, `print_users_list()`, `fix_users_list()`, `set_user_info()`, `set_machine_info()`, `new_user()`, `new_machine()`, `delete_user_entry()`, `delete_machine_entry()`, `export_database()`, `export_groups()`, `export_account_policies()`, and `reinit_account_policies()`. `get_sid_from_cli_string()` accepts full SIDs or RIDs.

## Control Flow

`main()` initializes Samba cmdline and passdb state, parses options, builds `setparms`, optionally overrides the passdb backend via loadparm, initializes the password DB, then validates compatible option groups. Account-policy operations are handled early. Import/export constructs source and destination `pdb_methods` backends. Legacy-compatible cases promote a lone user argument into list mode and promote user field options into modify mode. Create, delete, and modify branches dispatch to user or machine variants.

## State and Persistence Behavior

This utility directly mutates passdb backends: it can add accounts, set passwords, update SIDs, update account flags, reset bad-password counters, reset logon hours, set kickoff time, set NT hashes and password history, delete users or machine accounts, migrate accounts/groups/policies, and reset policy defaults. Passwords read for new users are scrubbed before free. Backend override changes process loadparm state.

## Dependencies and Integration Points

It integrates with Samba passdb (`pdb_*`, `struct samu`, `pdb_methods`), SAMR display entries, account-policy helpers, local password change logic, cmdline/loadparm, SID utilities, and `get_pass()` from `passwd_util.c`.

## Risks and Edge Cases

The option compatibility mask is dense and easy to break when adding flags. Some error paths return without freeing temporary `samu` allocations, but process exit usually follows. Setting `--set-nt-hash` bypasses plaintext password policy and requires valid 32-hex-character input. Machine names are normalized to lowercase and `$`-suffixed, which can surprise callers. Import/export updates existing destination users by name, so a backend migration can overwrite attributes.

## Test Signals

Useful tests include list formats with verbose and smbpasswd-style output, create/delete/modify user and machine accounts, stdin password mismatch, SID-as-RID parsing, account-control validation, policy get/set/reset, import/export between temporary passdb backends, force-initialized password repair, and direct NT-hash setting with password-history verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/pdbedit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/profiles.c -->
# sources/user-network-fs/samba/source3/utils/profiles.c

## Purpose

`profiles.c` rewrites a Windows registry hive/profile file into a new `.new` file, optionally replacing one SID with another inside registry security descriptors. It is used for profile migration or ownership remapping.

## Important APIs, Types, and Functions

Global `old_sid`, `new_sid`, `change`, `new_val`, and `opt_verbose` hold command state. `verbose_output()` conditionally prints details. `swap_sid_in_acl()` replaces matching owner, group, and DACL trustee SIDs in a `security_descriptor`. `copy_registry_tree()` recursively copies keys, values, subkeys, and security descriptors from one `REGF_FILE` to another.

## Control Flow

`main()` parses `--change-sid`, `--new-sid`, and `--verbose`, requires both SID options if either is supplied, opens the original profile read-only, creates `<profilefile>.new`, fetches the root key, and calls `copy_registry_tree()`. The recursive copy duplicates the source security descriptor, performs SID replacement, collects values into a `regval_ctr`, collects subkey names into a `regsubkey_ctr`, writes the key into the output file, then recurses into each fetched subkey.

## State and Persistence Behavior

The original hive is read-only. The output hive is created with owner read/write permissions and truncated if already present. SID replacement only affects copied security descriptors in the new file. Values and subkey structure are preserved, with value data sizes masked by `~VK_DATA_IN_OFFSET`.

## Dependencies and Integration Points

It depends on Samba registry file I/O (`regfio`), registry object containers, security descriptor/SID utilities, filesystem flags, and Samba cmdline initialization. It does not use the live Samba registry service.

## Risks and Edge Cases

`swap_sid_in_acl()` assumes `sd->owner_sid`, `sd->group_sid`, and `sd->dacl` are non-NULL; malformed descriptors can crash despite a top-level `sec_desc` NULL check. SACL rewrite is disabled. The code always calls `swap_sid_in_acl()` even when SID options were not supplied, relying on zero-initialized globals. Output naming is fixed to `.new` and may overwrite an existing file.

## Test Signals

Tests should use small REGF fixtures with owner/group/DACL SID matches, no matches, nested keys, values with inline data, NULL or missing ACL components, missing root keys, and invalid SID command arguments. A binary comparison of key/value structure plus descriptor SID changes is the main validation signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/profiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.c -->
# sources/user-network-fs/samba/source3/utils/py_net.c

## Purpose

`py_net.c` implements the `net_s3` Python extension module and exposes a `Net` object for Samba3-style domain join and leave operations.

## Important APIs, Types, and Functions

The Python type is `py_net_Type`, with C backing struct `py_net_Object` from `py_net.h`. Methods are `join_member()` and `leave()`. `check_ads_config()` validates member-server role, NetBIOS name length, and ADS realm configuration. `net_obj_new()` converts Python credentials and loadparm objects into Samba C pointers and stores an optional server address.

## Control Flow

Python constructs `net_s3.Net(creds, lp=None, server=None)`. `join_member()` allocates a `libnet_JoinCtx`, parses optional host/account/OS/password/debug/DNS flags, validates config unless the config backend is registry-backed, fills join flags and admin credentials, tries DNS-domain join first, retries NetBIOS-domain join on DC-not-found, optionally performs DNS updates, and returns `(domain_sid, dns_domain_name)`. `leave()` allocates `libnet_UnjoinCtx`, requires a realm, parses `keepAccount` and `debug`, requests account delete or disable semantics, calls `libnet_Unjoin()`, and returns a Python boolean.

## State and Persistence Behavior

Join and leave are persistent domain membership operations. They can create, delete, or disable machine accounts; modify local Samba configuration when registry-backed config is active; update secrets; and attempt DNS updates. The `Net` object owns a talloc frame, credentials pointer, loadparm context, server address pointer, and tevent context.

## Dependencies and Integration Points

It integrates Python C API, pytalloc/pyparam/pycredentials, Samba credentials, loadparm, `libnet_Join`, `libnet_Unjoin`, DNS update helper `net_ads_join_dns_updates()`, cmdline messaging, SID formatting, and dynamic config paths.

## Risks and Edge Cases

`net_obj_new()` stores `server_address` directly from Python argument parsing; object lifetime should be checked if Python frees or mutates the source object. Several allocation-error paths return without freeing the temporary context. Join treats DNS update failure as non-fatal after successful join, which callers must understand. `leave()` returns `False` after setting a Python exception on unjoin failure, an unusual combination for Python callers.

## Test Signals

Tests should cover constructor type validation, invalid ADS/member configuration, successful join return tuple, DC-not-found fallback to workgroup NetBIOS name, `noDnsUpdates`, registry versus file-backed config behavior, leave with and without `keepAccount`, and Python exception state on join/leave failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.h -->
# sources/user-network-fs/samba/source3/utils/py_net.h

## Purpose

`py_net.h` defines the C structure backing the `net_s3.Net` Python object.

## Important APIs, Types, and Functions

`py_net_Object` embeds `PyObject_HEAD` and stores `TALLOC_CTX *mem_ctx`, `struct cli_credentials *creds`, `struct loadparm_context *lp_ctx`, `const char *server_address`, and `struct tevent_context *ev`.

## Control Flow

There is no executable logic in the header. `py_net.c` allocates this structure in `net_obj_new()`, reads it in Python method implementations, and frees `mem_ctx` in `py_net_dealloc()`.

## State and Persistence Behavior

The object captures the state required for domain join/leave calls: credentials, configuration, optional target server, and event context. Domain membership persistence is performed by methods using these fields, not by the header itself.

## Dependencies and Integration Points

The struct ties the Python API to Samba talloc, credentials, loadparm, and tevent libraries. It must remain consistent with `py_net_Type.tp_basicsize`.

## Risks and Edge Cases

Ownership of `creds`, `lp_ctx`, and `server_address` is implicit. Any future change to retain borrowed Python data must ensure the C object keeps a valid reference or talloc-owned copy. Adding fields requires care around deallocation and initialization failures.

## Test Signals

Constructor/destructor tests for `net_s3.Net` are the key signal. Leak checks should verify `mem_ctx` and `ev` are released, and method tests should confirm the stored credentials and loadparm context are used for join/leave calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.c -->
# sources/user-network-fs/samba/source3/utils/regedit.c

## Purpose

`regedit.c` implements Samba's ncurses-based registry editor. It displays registry keys in a tree pane, values in a value pane, supports key/value creation, editing, deletion, search, refresh, resize handling, and opens the Samba3 registry backend.

## Important APIs, Types, and Functions

`struct regedit` holds the registry context, ncurses windows, tree view, value list, current input pane, and active search options. Major helpers are `show_path()`, `print_heading()`, `load_values()`, `add_reg_key()`, `regedit_search()`, `handle_tree_input()`, `handle_value_input()`, `handle_main_input()`, `regedit_getch()`, `display_window()`, and `main()`.

## Control Flow

`main()` initializes Samba cmdline state, disables logging noise, burns credentials from argv, opens the Samba3 registry through `reg_open_samba3()`, and calls `display_window()`. The UI initializes curses, colors, the root tree, key/value panes, and a global `regedit_main` used by `regedit_getch()`. The main loop reads keys until `q`, dispatches global commands first, then routes input to either the tree or value pane. Tree input navigates, loads children, ascends, creates keys/subkeys, and deletes keys after confirmation. Value input navigates, edits or creates values through dialog helpers, and deletes values after confirmation.

## State and Persistence Behavior

Registry mutations are persistent through `reg_key_add_name()`, `reg_key_del()`, `reg_val_set()` in dialog code, and `reg_del_value()`. UI state includes selected tree node, selected value item, cached tree children, value-list contents, active search query/options, and current focus pane. Refresh reopens the tree path from the registry context.

## Dependencies and Integration Points

It depends on ncurses/menu/panel, `regedit_treeview`, `regedit_valuelist`, `regedit_dialog`, Samba registry APIs, Samba cmdline credentials, loadparm, and the Samba3 wrapper declared in `regedit.h`.

## Risks and Edge Cases

The UI uses global `regedit_main`, making nested or concurrent editor instances unsafe. Many paths rely on `SMB_ASSERT()` after allocation or tree assumptions. Delete and edit operations reopen keys to refresh caches, but error handling for delete value ignores the returned `WERROR`. Search temporarily loads value lists for other keys and must restore visible state carefully. Small terminals can expose layout assumptions despite resize handling.

## Test Signals

Manual or scripted curses tests should cover navigation, resize, refresh, create/delete key, create/edit/delete each supported value type, binary edit mode, recursive and non-recursive search, case-sensitive search, and failure injection from registry wrappers. Terminal smoke tests on very small dimensions are useful.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.h -->
# sources/user-network-fs/samba/source3/utils/regedit.h

## Purpose

`regedit.h` declares the registry wrapper API and shared search/UI constants used by the Samba registry editor implementation.

## Important APIs, Types, and Functions

It declares `struct samba3_registry_key` as a wrapper around `struct registry_key *`, wrapper functions for opening hives/keys, enumerating values and subkeys, creating/deleting keys, deleting/setting/querying values, querying key metadata, initializing the registry, and opening a Samba3 registry context. It also declares `regedit_getch()`, `regedit_search_match_fn_t`, `struct regedit_search_opts`, and color-pair constants.

## Control Flow

The header has no runtime flow. `regedit.c` uses `reg_open_samba3()` to acquire a registry context and `regedit_dialog.c`/other UI modules call `regedit_getch()` for resize-aware input.

## State and Persistence Behavior

The wrapper functions declared here can mutate persistent registry state via create/delete/set operations. `regedit_search_opts` persists the active query and flags while the editor is running.

## Dependencies and Integration Points

It couples the curses UI modules to the Samba registry backend and wrapper implementation files such as `regedit_wrap.c` and `regedit_samba3.c`. It forward-declares registry and security types to limit include weight.

## Risks and Edge Cases

The API mixes read-only wrappers and mutating wrappers in one header, so consumers must be careful about which functions persist changes. `regedit_search_opts.query` ownership is managed by dialog code and can be replaced during searches. The wrapper type hides only one pointer, so backend abstraction is intentionally thin.

## Test Signals

Compile coverage across `regedit.c`, dialog, tree, value-list, wrapper, and Samba3 backend files validates declarations. Integration tests should verify each wrapper maps correctly to registry operations and that search options survive repeated search dialogs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.c -->
# sources/user-network-fs/samba/source3/utils/regedit_dialog.c

## Purpose

`regedit_dialog.c` implements the reusable ncurses dialog framework for `regedit`, plus higher-level dialogs for input prompts, notices, value editing, type selection, and search options.

## Important APIs, Types, and Functions

The core framework uses `struct dialog`, `struct dialog_section`, and `struct dialog_section_ops`. Section implementations include labels, horizontal separators, text fields, hex editors, buttons, and option checkboxes. Public constructors and helpers include `dialog_new()`, `dialog_create()`, `dialog_modal_loop()`, `dialog_input*()`, `dialog_notice()`, `dialog_edit_value()`, `dialog_select_type()`, and `dialog_search_input()`.

## Control Flow

Callers build a dialog by appending sections, then `dialog_create()` computes size, creates pad/window/panel, creates section subpads, and focuses the first focusable section. `dialog_modal_loop()` repeatedly shows the dialog, updates panels, reads input via `regedit_getch()`, and lets `dialog_handle_input()` route keys to the current section or dialog submit callback. High-level input dialogs validate numeric or string entries. Value-edit dialogs select an editor mode based on registry type or forced binary mode, prefill current data, validate/serialize input, and call `reg_val_set()`.

## State and Persistence Behavior

Dialog state is talloc-owned and destroyed with the dialog. Text-field state lives in ncurses `FIELD`/`FORM` objects; hex data lives in a `struct hexedit`. `dialog_edit_value()` can persistently create or update registry values. Search dialogs update the caller's `regedit_search_opts`, freeing and replacing the query string.

## Dependencies and Integration Points

The file integrates ncurses panels, menus, and forms; `regedit_getch()` for resize-aware input; `regedit_hexedit`; `regedit_valuelist` value items; registry serialization helpers such as `push_reg_sz`, `pull_reg_multi_sz`, and `regtype_by_string`; and Samba registry write API `reg_val_set()`.

## Risks and Edge Cases

Focus traversal loops until a section accepts focus, so dialogs with no focusable section would loop. `dialog_destroy()` assumes `head_section` is non-NULL. `text_field_on_input()` increments length for all default input, including control keys not specially handled. `dialog_input_internal()` sets `*req.out.out_str = NULL` even for numeric output via a union, which is harmless for pointer-sized storage only if callers pass valid output storage. Binary value editing can grow buffers interactively and must handle allocation failure.

## Test Signals

Tests should cover dialog resize, focus traversal, tab/backtab, numeric validation, cancel paths, duplicate or blank value names, REG_DWORD range validation, REG_SZ/EXPAND_SZ/MULTI_SZ serialization, forced binary editing, buffer resize, search option validation, and memory cleanup under valgrind or sanitizer-enabled curses tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.h -->
# sources/user-network-fs/samba/source3/utils/regedit_dialog.h

## Purpose

`regedit_dialog.h` declares the dialog framework and high-level registry editor dialog API used by `regedit.c`.

## Important APIs, Types, and Functions

It defines `struct dialog`, `struct dialog_section`, `struct dialog_section_ops`, `enum dialog_action`, `enum section_justify`, button and option specs, and `enum dialog_type`. It declares section constructors for labels, separators, text fields, hex editors, buttons, and options; modal lifecycle functions; input/notice helpers; registry value edit/type selection dialogs; and search input.

## Control Flow

Consumers create a dialog, append sections, call `dialog_create()`, then run `dialog_modal_loop()` or use high-level wrappers such as `dialog_input()` and `dialog_edit_value()`. Section operation callbacks define how the modal input loop reacts to keys.

## State and Persistence Behavior

The public structs expose dialog internals: windows, panels, circular section list pointers, current focus, submit callback, and per-section ncurses windows. High-level edit functions can mutate registry values through the implementation.

## Dependencies and Integration Points

The header includes ncurses, panel, and menu headers, and forward-declares registry/value/search types. It is shared by the main editor, dialog implementation, and hex/value-list integration.

## Risks and Edge Cases

Because structs are public, other files can mutate internal pointers and break lifecycle assumptions. Callback contracts require callers to return `true` to close a submitted dialog and `false` to keep it open, which is easy to invert. Dialog dimensions are integer fields and negative widths have special meaning for expansion.

## Test Signals

Compile coverage plus UI integration tests should verify every declared constructor and high-level helper. ABI-sensitive checks should ensure public struct changes are reflected in all users and that callback semantics remain consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.c -->
# sources/user-network-fs/samba/source3/utils/regedit_hexedit.c

## Purpose

`regedit_hexedit.c` implements an ncurses hex editor widget used by registry value dialogs to view and edit binary data.

## Important APIs, Types, and Functions

`struct hexedit` tracks scroll offset, logical length, allocation size, cursor position, byte/nibble offsets, data buffer, and target window. Public functions are `hexedit_new()`, `hexedit_set_buf()`, `hexedit_get_buf()`, `hexedit_get_buf_len()`, `hexedit_set_cursor()`, `hexedit_refresh()`, `hexedit_driver()`, and `hexedit_resize_buffer()`. Internal helpers handle cursor movement, hex column mapping, editing, deletion, and scrolling.

## Control Flow

The widget renders 8 bytes per line as offset, two groups of hex bytes, and ASCII. `hexedit_driver()` maps abstract movement/delete commands or printable input to cursor movement and edit operations. Hex-column editing accepts only hex digits and updates one nibble at a time; ASCII-column editing writes the byte directly. Editing at `cursor_offset == len` grows the buffer by one. Backspace and delete remove bytes using `memmove()`.

## State and Persistence Behavior

All edited data is stored in the talloc-owned `data` buffer. Resizing can grow allocation exponentially, zero-fill new bytes, shrink logical length, or reset the cursor if it would move past the new end. The widget itself does not persist registry data; callers retrieve the buffer and write it through registry APIs.

## Dependencies and Integration Points

It depends on ncurses `WINDOW`, Samba `WERROR`, talloc allocation, and constants from `regedit_hexedit.h`. `regedit_dialog.c` wraps it as a dialog section and exposes resize/get/set operations to value editing.

## Risks and Edge Cases

`hexedit_set_buf()` allocates a zero-length array when size is zero; allocator behavior should be verified. Cursor math around line ends, ASCII/hex transitions, and deletion at boundaries is subtle. Page-up/page-down commands are defined but not implemented. `do_edit()` refreshes the whole widget after each edit, which is simple but can flicker on slow terminals.

## Test Signals

Widget tests should cover hex and ASCII entry, nibble replacement, append-at-end, backspace/delete at start/end/middle, shrink/grow resize, cursor movement across the gap between hex groups and ASCII, scrolling beyond one screen, zero-length buffers, and unimplemented page keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.h -->
# sources/user-network-fs/samba/source3/utils/regedit_hexedit.h

## Purpose

`regedit_hexedit.h` declares the public interface and key constants for the ncurses hex editor widget used by registry dialogs.

## Important APIs, Types, and Functions

It defines abstract driver key constants such as `HE_CURSOR_UP`, `HE_CURSOR_DOWN`, `HE_BACKSPACE`, and `HE_DELETE`, sets `LINE_WIDTH` to 44, forward-declares `struct hexedit`, and declares buffer lifecycle, rendering, cursor, driver, and resize functions.

## Control Flow

Callers create a widget with `hexedit_new()`, set or replace the buffer with `hexedit_set_buf()`, render with `hexedit_refresh()`, route key events through `hexedit_driver()`, update the visible cursor with `hexedit_set_cursor()`, and retrieve the edited buffer before persisting it.

## State and Persistence Behavior

The widget owns an editable in-memory copy of binary data. Persistence is intentionally external: `regedit_dialog.c` reads the buffer and calls registry write helpers when the user submits a dialog.

## Dependencies and Integration Points

It includes ncurses for `WINDOW` and relies on Samba/talloc types from including translation units. The abstract key constants decouple dialog key handling from internal cursor logic.

## Risks and Edge Cases

The fixed `LINE_WIDTH` must stay consistent with the renderer's offset/hex/ASCII columns. Adding driver commands requires implementation in `hexedit_driver()`, not just new constants. Callers must not retain the returned buffer after freeing the widget.

## Test Signals

Compile coverage through `regedit_dialog.c` validates the interface. Runtime tests should verify the widget can be embedded in a curses subwindow, edited via abstract keys, resized, and harvested into a registry value blob without stale pointers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.h -->
