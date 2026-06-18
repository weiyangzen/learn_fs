# Research Report: subset-b-009802

Grouped research for the exact source files in work item `subset-b-009802`. Each section preserves the source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/test-utils.sh -->
# sources/user-network-fs/s3fs-fuse/test/test-utils.sh

## Purpose
This Bash helper library supports the s3fs-fuse integration test suite. It centralizes test constants, portable command selection, file/xattr helpers, suite execution, S3 HTTP helpers, mount-process inspection, OS timing waits, and workaround wrappers for platform-specific behavior.

## Important APIs, Types, and Functions
The file exports shell variables such as `TEST_TEXT`, `TEST_TEXT_FILE`, `TEST_DIR`, `BIG_FILE_BLOCK_SIZE`, `BIG_FILE_LENGTH`, `STAT_BIN`, `STDBUF_BIN`, `TRUNCATE_BIN`, and `SHA256SUM_BIN`. The xattr wrappers are `find_xattr`, `get_xattr`, `set_xattr`, and `del_xattr`, switching between macOS `xattr` and Linux `getfattr`/`setfattr`. Metadata helpers include `get_inode`, `get_size`, `get_ctime`, `get_mtime`, `get_atime`, `get_permissions`, `get_user_and_group`, and `check_file_size`.

Test lifecycle helpers include `mk_test_file`, `rm_test_file`, `mk_test_dir`, `rm_test_dir`, `cd_run_dir`, `clean_run_dir`, `init_suite`, `add_tests`, `report_pass`, `report_fail`, `describe`, and `run_suite`. S3 helpers include `s3_head`, `s3_mb`, `s3_cp`, and `check_content_type`; process and platform helpers include `wait_for_port`, `s3fs_args`, `wait_ostype`, and `cp_avoid_xattr_err`.

## Control Flow
Top-level initialization enables `errexit` and `pipefail`, sets locale to `en_US.UTF-8`, selects GNU command names on Darwin, and adjusts `STAT_BIN` if the installed stat supports cache-bypass flags. `run_suite` creates a unique run directory below `TEST_BUCKET_MOUNT_POINT_1`, iterates over `TEST_LIST`, rewrites per-test filenames with a sequential suffix, runs each test in a subshell with `errexit`, records pass/fail state, cleans the run directory, prints a summary, and returns failure if any test failed.

## State and Persistence
State is mostly shell-global: test lists, pass/fail arrays, mutable filename variables, S3 credentials inherited from the environment, and the current working directory. The script creates and deletes files/directories in the mounted bucket, creates temporary header/body files with `mktemp`, and performs real HTTP operations against the configured S3 endpoint. No long-lived local database is used.

## Dependencies and Integration Points
The helpers integrate with FUSE-mounted s3fs paths, curl AWS SigV4 support, S3Proxy or compatible S3 endpoints, GNU coreutils on macOS, filesystem xattr tools, `df`, `ps`, and test binaries/scripts that source this file. `s3_cp` deliberately defaults `Content-Type: application/octet-stream` unless a caller supplies one.

## Risks and Test Signals
Risks include destructive `rm -rf` in `clean_run_dir`, command behavior differences between Linux and macOS, locale availability, credential leakage through curl/process environments, direct `/dev/tcp` probing, and fragile parsing of HTTP headers and `df` output. Strong test signals are full suite pass/fail summaries, `check_file_size` comparing metadata and data length, `check_content_type` using S3 HEAD, xattr round-trips, and platform CI coverage for Linux/macOS branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/test-utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/truncate_read_file.cc -->
# sources/user-network-fs/s3fs-fuse/test/truncate_read_file.cc

## Purpose
This small test utility exercises a race-sensitive s3fs behavior: it truncates a file, reads the same path from a child command before the truncating descriptor is closed, and leaves final file-size validation to the caller.

## Important APIs, Types, and Functions
The only public entry point is `main(int argc, const char *argv[])`. It uses POSIX `open`, `ftruncate`, and `close`, C library `strtoull`, `snprintf`, `system`, and standard error reporting with `fprintf`.

## Control Flow
The program requires exactly two arguments: file path and truncate size in bytes. It opens the file read/write, converts the size with `strtoull`, calls `ftruncate(fd, size)`, executes `cat <path> >/dev/null 2>&1` through `system`, then closes the descriptor so s3fs flush behavior occurs after the intervening read. Any failure prints an error and exits nonzero.

## State and Persistence
Persistent state is the target file content and size. The open file descriptor intentionally remains live while the child `cat` process reads the file, so the test observes filesystem behavior before close/flush completes.

## Dependencies and Integration Points
It depends on a POSIX-like environment, a shell for `system`, and `cat`. In the s3fs test suite it is expected to run against a mounted s3fs file path, with the surrounding shell test checking size and contents afterward.

## Risks and Test Signals
The shell command is built by string interpolation and does not quote or escape the path, so spaces or shell metacharacters in test paths can break the utility or become command-injection hazards. `strtoull` errors and trailing garbage are not validated. Test signals are nonzero exits for open/truncate/read failures and caller-side size checks that prove truncate/read/flush ordering is correct.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/truncate_read_file.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/write_multiblock.cc -->
# sources/user-network-fs/s3fs-fuse/test/write_multiblock.cc

## Purpose
This C++ test helper writes randomly generated data into one or more files at one or more explicit offset/size ranges. It is designed to exercise sparse, overlapping, or multipart write behavior in s3fs-fuse.

## Important APIs, Types, and Functions
`write_block_part` stores `off_t start` and `off_t size`. `wbpart_list_t` is a `std::vector<write_block_part>` and `strlist_t` is a `std::list<std::string>`. `create_random_data` fills a heap buffer from `/dev/urandom`. `cvt_string_to_number`, `parse_string`, `parse_write_blocks`, and `parse_arguments` implement command parsing for repeated `-f` and `-p` options. `main` opens/creates each file and issues `pwrite` calls.

## Control Flow
Arguments must include at least one `-f <file>` and one `-p <start:size[,start:size...]>`. Parsing records all files and blocks while tracking the maximum block size. The program allocates one random buffer of that maximum size, then for each file validates an existing path is regular or creates it, and writes each block with retry-on-interrupt/EAGAIN loops using `pwrite` at `start + writepos`.

## State and Persistence
Persistent state is the set of target files and their byte ranges. The same random data buffer is reused across all files and all blocks, so equal offsets/sizes across files receive identical data for the same prefix. It does not fsync; persistence visibility relies on close and filesystem behavior.

## Dependencies and Integration Points
It depends on POSIX file APIs, `/dev/urandom`, and getopt. It integrates with shell tests that prepare file paths on an s3fs mount and verify resulting size/content/hash behavior externally.

## Risks and Test Signals
`create_random_data` can return null but `main` does not explicitly check before using the buffer. Negative or zero sizes are rejected, but very large `off_t` values can stress allocation or `pwrite`. Existing non-regular files are rejected. Test signals include nonzero exits for parse/open/write failures and subsequent caller checks for file size, sparse block behavior, multipart upload results, and consistency across files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/write_multiblock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth.c -->
# sources/user-network-fs/samba/source3/auth/auth.c

## Purpose
This file is the source3 NTLM authentication dispatcher. It registers auth backends, creates role-specific `auth_context` method chains, manages NTLM challenges, and runs user-supplied credentials through the configured backend list.

## Important APIs, Types, and Functions
The backend registry is the static `auth_backends` list of `auth_init_function_entry`. Public functions include `smb_register_auth`, `auth_get_ntlm_challenge`, `auth_check_ntlm_password`, `make_auth3_context_for_ntlm`, `make_auth3_context_for_netlogon`, `make_auth3_context_for_winbind`, and `auth3_context_set_challenge`. Internal helpers include `check_domain_match`, `make_auth_context`, `load_auth_module`, `make_auth_context_text_list`, and `make_auth_context_specific`.

## Control Flow
Backends register by name and interface version. Context creation chooses a method string from `lp_server_role()` and settings such as `lp_encrypt_passwords()`, then loads static/probed modules and links them into `auth_method_list`. During authentication, `auth_check_ntlm_password` validates the challenge, enforces trusted-domain policy, iterates methods until one returns something other than `NT_STATUS_NOT_IMPLEMENTED`, optionally performs a PAM account check, logs authentication events, and returns `auth_serversupplied_info`.

## State and Persistence
Process-local state includes the global backend registry, per-context challenge blob, `challenge_set_by`, `start_time`, method private data, and `for_netlogon`. Persistent external state is not written here, but called backends may update passdb and PAM/account state. The context destructor frees each method's private data.

## Dependencies and Integration Points
The dispatcher depends on loadparm configuration, dynamic Samba module probing, messaging for audit events, tsocket remote addresses, PAM account checks, and backend modules such as anonymous, SAM, winbind, samba4, and unix. It bridges to source4/GENSEC through method hooks selected from the first method that exposes them.

## Risks and Test Signals
Risks include wrong role-to-method selection, challenge length mismatches, module registration collisions, unexpected non-authoritative fallback, and PAM/account check failures after password success. Test signals include authentication event logs, role-specific auth method ordering, trusted-domain denial, `NT_STATUS_NOT_IMPLEMENTED` fallback behavior, guest/non-guest success logging, and failure authoritative flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_builtin.c -->
# sources/user-network-fs/samba/source3/auth/auth_builtin.c

## Purpose
This file provides built-in auth modules that do not require external identity stores. The main production module is `anonymous`, which accepts empty anonymous credentials and constructs anonymous server info.

## Important APIs, Types, and Functions
`check_anonymous_security` implements the module. `auth_init_anonymous` creates an `auth_methods` record named `anonymous`. Under `DEVELOPER`, `check_name_to_ntstatus_security` and `auth_init_name_to_ntstatus` expose a testing backend that maps usernames to NTSTATUS values. `auth_builtin_init` registers available built-ins.

## Control Flow
The anonymous checker only handles empty mapped account names. It rejects non-empty plaintext, non-null hashes, non-empty NT responses, and LM responses other than empty or single NUL by returning `NT_STATUS_NOT_IMPLEMENTED`, allowing later modules to try. If the input is genuinely anonymous, it calls `make_server_info_anonymous`.

## State and Persistence
No persistent state is stored. Anonymous server-info construction depends on cached anonymous/guest session state initialized elsewhere in `auth_util.c`.

## Dependencies and Integration Points
The file depends on `auth.h`, string helpers, the auth backend registration API in `auth.c`, and server-info constructors. It is normally first in the auth chain so anonymous handling is centralized before SAM or winbind.

## Risks and Test Signals
The critical risk is classifying credential blobs correctly: a malformed but non-empty response must not become anonymous. Tests should cover empty username with empty plaintext/hash/response combinations, non-empty username fallback, developer-only NTSTATUS mapping, and behavior when anonymous cached session info has not been initialized.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_builtin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_generic.c -->
# sources/user-network-fs/samba/source3/auth/auth_generic.c

## Purpose
This file adapts source3 authentication to the source4 `auth4_context` and GENSEC server interfaces. It prepares NTLMSSP/SPNEGO/Kerberos/SCHANNEL authentication and converts successful password or PAC validation into `auth_session_info`.

## Important APIs, Types, and Functions
Key functions are `make_auth4_context`, `auth_generic_prepare`, and `auth_check_password_session_info`. Internal PAC/Kerberos helpers are `generate_pac_session_info`, `generate_krb5_session_info`, `auth3_generate_session_info_pac`, and `make_auth4_context_s3`.

## Control Flow
For Kerberos PACs, domain-member/DC roles send the PAC to winbind through `wbcAuthenticateUserEx` and build server/session info from the returned identity. Standalone mode parses a minimal PAC, rejects full logon-info PACs, maps the Kerberos principal to a local user, and calls `make_session_info_krb5`. `auth_generic_prepare` either delegates to a backend-provided `prepare_gensec` hook or builds source3 GENSEC settings, orders Kerberos before NTLMSSP, adds SPNEGO/SCHANNEL/local-system mechanisms, sets anonymous server credentials, then attaches remote/local addresses and service description.

## State and Persistence
The code allocates short-lived talloc frames and moves resulting contexts to caller ownership. It may prime winbind/netsamlogon caches through PAC authentication. It sets current user substitution state and reloads shares after successful PAC or NTLM auth so `%U`-dependent configuration reflects the authenticated user.

## Dependencies and Integration Points
Dependencies include GENSEC, Kerberos/PAC NDR structures, winbind client APIs, loadparm, credentials, tsocket, PAM account checking, and source3 auth3 functions from `auth_ntlmssp.c`. It is the key integration layer used by SMB, RPC, and other services needing generic security negotiation.

## Risks and Test Signals
Risks include winbind unavailability, incorrect role-specific PAC handling, missing DNS names, GENSEC backend ordering regressions, and session-info mismatches between Kerberos and NTLM paths. Test signals include Kerberos PAC validation, standalone MIT realm mapping, NTLMSSP negotiation, SPNEGO fallback, SCHANNEL/local-system behavior, PAM account denial after PAC validation, and authorization audit events from `auth_check_password_session_info`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_ntlmssp.c -->
# sources/user-network-fs/samba/source3/auth/auth_ntlmssp.c

## Purpose
This file supplies the source3 implementations of the auth4 hooks used by NTLMSSP and other GENSEC modules: challenge get/set, asynchronous password checking, and session-info generation.

## Important APIs, Types, and Functions
Public functions are `auth3_generate_session_info`, `auth3_get_challenge`, `auth3_set_challenge`, `auth3_check_password_send`, and `auth3_check_password_recv`. The request state type `auth3_check_password_state` stores `authoritative`, `server_info`, and NT/LM session keys.

## Control Flow
`auth3_generate_session_info` handles two input shapes: `auth_user_info_dc` for SCHANNEL/local-system or anonymous tokens, and `auth_serversupplied_info` for normal auth3 password results. `auth3_check_password_send` maps the supplied user info, calls `auth_check_ntlm_password`, maps selected failures to guest server info, sets current user substitution state, reloads shares, extracts NT and LM session keys out of `server_info`, and completes a tevent request. `recv` moves the server info and keys to caller ownership.

## State and Persistence
State lives in the tevent request and the underlying `auth_context` stored in `auth4_context->private_data`. Successful logons alter process-global current user substitution state and trigger `lp_load_with_shares`. Session-key blobs are moved out of server info so the NTLMSSP layer can choose final key handling.

## Dependencies and Integration Points
The file depends on source3 auth dispatch, user mapping, tevent request helpers, local token creation, guest mapping policy, loadparm share reloads, and security token constants for system/anonymous SIDs.

## Risks and Test Signals
Risks include incorrect user remapping propagation, guest mapping on the wrong status, losing session keys through ownership mistakes, and share reload behavior depending on sanitized user names. Tests should cover normal NTLMSSP success, bad-user/bad-password guest mapping, authoritative flag handling, system/anonymous SCHANNEL generation, and key extraction lengths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_ntlmssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_sam.c -->
# sources/user-network-fs/samba/source3/auth/auth_sam.c

## Purpose
This file registers and implements SAM/passdb-backed auth modules. It decides whether a credential belongs to the local SAM/domain for the current server role, then delegates actual password and account validation to `check_sam_security`.

## Important APIs, Types, and Functions
Modules are `sam`, `sam_ignoredomain`, and `sam_netlogon3`. Their check functions are `auth_samstrict_auth`, `auth_sam_ignoredomain_auth`, and `auth_sam_netlogon3_auth`; init functions allocate `auth_methods` records. `auth_sam_init` registers all three.

## Control Flow
`sam_ignoredomain` accepts any non-empty mapped account and ignores domain qualification. `sam` normalizes empty or `.` domains to the local NetBIOS name, rejects UPN-style users on domain members so they can go to the DC, verifies local-name/workgroup ownership based on role, and handles IPA DNS forest matching for DCs. `sam_netlogon3` is restricted to DC roles and only handles the local workgroup or matching IPA forest. All successful ownership checks call `check_sam_security`.

## State and Persistence
This file itself stores no persistent state. It reads server role, workgroup, NetBIOS names, and passdb domain info, while `check_sam_security` may mutate bad-password counters and server-info state.

## Dependencies and Integration Points
It depends on loadparm role/config functions, passdb domain metadata, name comparison helpers, and the shared auth backend registry. It is placed in method chains after anonymous and before or around winbind depending on role.

## Risks and Test Signals
Risks include accepting a domain the local SAM should not service, rejecting valid IPA forest-domain aliases, incorrect fallback to winbind, and fatal exit if `auth_sam` is configured under an AD DC without the inhibit parameter. Tests should cover standalone, domain member, PDC/BDC/IPA DC, UPN users, empty domains, DNS forest matching, and `sam_netlogon3` role enforcement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_samba4.c -->
# sources/user-network-fs/samba/source3/auth/auth_samba4.c

## Purpose
This file implements the `samba4` auth backend used to redirect source3 authentication and GENSEC setup into the source4 authentication stack, especially for AD DC behavior.

## Important APIs, Types, and Functions
Important functions include `new_server_id_task`, `free_task_id`, `check_samba4_security`, `prepare_gensec`, `make_auth4_context_s4`, `auth_init_samba4`, and `auth_samba4_init`. The static `task_id_tree` allocates unique task IDs for messaging identities.

## Control Flow
`check_samba4_security` builds an auth4 context through source4, sets the source3 challenge, calls `auth_check_password`, converts `auth_user_info_dc` to SamInfo3, and returns either raw info3/no-authz server info or full server info. `prepare_gensec` initializes source4 loadparm, event, messaging, server credentials, and GENSEC server context, then requests session-key and Unix-token features. `make_auth4_context_s4` creates a source4 auth context, optionally using forced methods from the module parameter.

## State and Persistence
Persistent in-process state is the static IDR tree of allocated task IDs. Returned `server_id` objects remove their IDs through a talloc destructor. The backend also stores optional `forced_samba4_methods` on the auth context. No disk persistence is performed here.

## Dependencies and Integration Points
Dependencies include source4 auth, source4 events/messaging, GENSEC, credentials, loadparm, Samba server IDs, and auth SAM reply conversion. This module provides auth, `prepare_gensec`, and `make_auth4_context` hooks so the generic source3 path delegates deeply into source4.

## Risks and Test Signals
Risks include task ID leaks, messaging context setup failures, inconsistent token generation between SMB and LDAP if hooks diverge, and incorrect handling of non-authoritative `NO_SUCH_USER` fallback. Tests should cover AD DC NTLM, NTLMSSP and Kerberos via source4 GENSEC, forced method parameters such as `samba4:sam`, pdbtest coverage for SamLogon-style output, and repeated context creation/destruction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_samba4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_unix.c -->
# sources/user-network-fs/samba/source3/auth/auth_unix.c

## Purpose
This file implements the `unix` auth backend for plaintext username/password checks against the host password database or PAM. It is used when encrypted SMB passwords are disabled or plaintext Unix auth is explicitly part of the method chain.

## Important APIs, Types, and Functions
The main checker is `check_unix_security`; `auth_init_unix` creates an `auth_methods` record and `auth_unix_init` registers it.

## Control Flow
The checker extracts an IP remote host string from the supplied tsocket address, becomes root, looks up the mapped account with `Get_Pwnam_alloc`, calls `pass_check` with the plaintext password and remote host, then drops root. On success it converts the passwd record into `auth_serversupplied_info` using `make_server_info_pw`; if the passwd record is missing it returns `NO_SUCH_USER`.

## State and Persistence
No file-local persistent state is kept. It reads OS account/shadow/PAM state through `pass_check` and returns server info with Unix UID/GID from the passwd record.

## Dependencies and Integration Points
Dependencies include system passwd APIs, PAM or crypt-based password checking, tsocket remote addresses, privilege elevation helpers, and server-info conversion. It integrates with the auth chain selected for standalone plaintext mode.

## Risks and Test Signals
Risks include plaintext-only semantics, character-set assumptions documented in the code, incorrect root privilege boundaries, and inconsistency between the passwd record used for checking and server-info creation. Tests should cover valid/invalid plaintext logons, null password policy, PAM-enabled and non-PAM builds, missing users, and remote-host propagation to PAM.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_util.c -->
# sources/user-network-fs/samba/source3/auth/auth_util.c

## Purpose
This large utility file constructs user-supplied auth structures, creates local security/session tokens, builds and caches guest/anonymous/system session info, maps domain logon data to local Unix accounts, and provides guest mapping and session-key helpers.

## Important APIs, Types, and Functions
Input constructors include `make_user_info_map`, `make_user_info_netlogon_network`, `make_user_info_netlogon_interactive`, `make_user_info_for_reply`, `make_user_info_for_reply_enc`, and `make_user_info_guest`. Token/session functions include `create_local_token`, `auth3_user_info_dc_add_hints`, internal `auth3_session_info_create`, `make_session_info_from_username`, `init_guest_session_info`, `reinit_guest_session_info`, `init_system_session_info`, `make_server_info_guest`, `make_session_info_guest`, `make_server_info_anonymous`, `make_session_info_anonymous`, `make_session_info_system`, and `get_session_info_system`. Account mapping helpers include `_smb_create_user`, `check_account`, `smb_getpwnam`, `make_server_info_info3`, `make_server_info_wbcAuthUserInfo`, `is_trusted_domain`, `do_map_to_guest_server_info`, and `session_extract_session_key`.

## Control Flow
User-info constructors normalize or map SMB names, package LM/NT responses or plaintext, reject raw NTLMv2 when disabled, and set flags/logon parameters. `create_local_token` verifies the domain is allowed, reuses cached session info when present, otherwise builds Unix and NT tokens from server info, resolves SIDs to gids, adds Unix user/group SIDs, logs the token, and assigns a unique session GUID. `auth3_session_info_create` performs similar construction from source4 `auth_user_info_dc`, honoring S-1-5-88 Unix hint SIDs for uid/gid/name/translation behavior. Server-info conversion maps domain/user names to passwd records, can fall back from SID to UID, applies `min domain uid`, and handles `map to guest`.

## State and Persistence
Static cached pointers `guest_info`, `anonymous_info`, `guest_server_info`, and `system_info` persist for the process. External state can be changed by `_smb_create_user` running the configured add-user script and by winbind/passdb lookups. Token creation reads idmap, passwd, group, and configuration state but stores resulting tokens in talloc-owned session structures.

## Dependencies and Integration Points
The file integrates with passdb, winbind, id mapping, Unix passwd/group APIs, loadparm substitutions, token utilities, Netlogon SamInfo structures, PAM/account policy indirectly, and source4 auth info. It is used by nearly every backend to move from credentials to usable server/session identity.

## Risks and Test Signals
Risks include executing administrator-configured scripts with substituted usernames, domain firewall bypass mistakes, stale cached guest/system info after configuration changes, SID-to-UID mapping failures, ownership mistakes around cached session info, and guest mapping policy surprises. Test signals include guest/anonymous/system initialization, `map to guest` modes, domain UID minimum enforcement, winbind default-domain behavior, S-1-5-88 hint handling, SID/gid round-trips, token debug output, and session-key extraction for 16-byte and full-key use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_winbind.c -->
# sources/user-network-fs/samba/source3/auth/auth_winbind.c

## Purpose
This file implements the `winbind` auth backend, delegating challenge/response authentication for remote or trusted domains to winbindd through libwbclient.

## Important APIs, Types, and Functions
The key checker is `check_winbind_security`; `auth_init_winbind` creates the backend and `auth_winbind_init` registers it. It uses `wbcAuthUserParams`, `wbcAuthUserInfo`, and `wbcAuthErrorInfo`.

## Control Flow
The checker rejects missing inputs and local-SAM domains so other modules can handle them. It populates a response-level winbind auth request with the client-supplied account/domain/workstation, logon parameters, NTLM challenge, NT and LM responses, and the netlogon flag when required. It calls `wbcAuthenticateUserEx` as root, maps winbind error cases to NTSTATUS, falls back to local SAM for non-authoritative no-such-user, and converts successful winbind info to server info.

## State and Persistence
No file-local state is stored. The call can depend on winbindd caches and trusted-domain passdb configuration. Successful server info records `nss_token` if username mapping occurred.

## Dependencies and Integration Points
Dependencies include libwbclient, passdb trusted-domain enumeration, server-role configuration, source3 server-info conversion, and the auth backend registry. It sits in method chains for domain members and DCs where remote domain validation may be required.

## Risks and Test Signals
Risks include changing the domain name before NTLMv2 verification, mishandling winbind absence for roles where it is mandatory, incorrectly ignoring trusted domains, and fallback loops on non-authoritative errors. Tests should cover local-domain bypass, remote-domain success, winbind unavailable on member/DC with and without trusts, netlogon mode flagging, and authoritative/no-such-user behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/auth_winbind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/check_samsec.c -->
# sources/user-network-fs/samba/source3/auth/check_samsec.c

## Purpose
This file performs actual local SAM/passdb password verification and account policy enforcement. It validates hashes/responses, checks account restrictions, updates bad-password state, and returns server info for successful local SAM authentication.

## Important APIs, Types, and Functions
Internal helpers are `sam_password_ok`, `logon_hours_ok`, `sam_account_ok`, and `need_to_increment_bad_pw_count`. Public functions are `check_sam_security` and `check_sam_security_info3`.

## Control Flow
`check_sam_security` loads the `samu` record, rejects locked accounts early, verifies the supplied password using hash or NTLM response checks, reloads the account under a per-user named mutex, updates login attempts and bad-password counters, enforces account restrictions only after password success, resets bad counters on success, then calls `make_server_info_sam` and attaches session keys. `check_sam_security_info3` wraps this and converts server info to SamInfo3.

## State and Persistence
This file mutates passdb state: login attempt metadata, bad password count/time, and possibly lockout-related fields via passdb backend calls. The named mutex `check_sam_security_mutex_<user>` protects concurrent updates. It also flushes `PDB_GETPWSID_CACHE` after each authentication to avoid unbounded cache growth.

## Dependencies and Integration Points
Dependencies include passdb, libcli auth password-check routines, memcache, account policy APIs, named mutexes, server-info conversion, and Samba debug/logging. It is called by SAM auth modules and winbind helper paths needing local SamInfo3.

## Risks and Test Signals
Risks include race conditions around lockout updates, history-password handling that suppresses bad-count increments, policy ordering mistakes, null-password behavior, and trust-account logon-parameter enforcement. Tests should cover correct and wrong passwords, password history, disabled/locked/expired accounts, logon hours, workstation restrictions, trust account flags, bad-count reset, lockout under concurrency, and cache flush behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/check_samsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/pampass.c -->
# sources/user-network-fs/samba/source3/auth/pampass.c

## Purpose
This file implements Samba's PAM integration for plaintext password validation, account checks, session open/close, credential establishment, and password changes. It compiles to no-op account/session stubs when PAM is unavailable.

## Important APIs, Types, and Functions
With `WITH_PAM`, important helpers include `smb_pam_conv`, `smb_pam_passchange_conv`, `make_pw_chat`, `smb_setup_pam_conv`, `smb_pam_start`, `smb_pam_auth`, `smb_pam_account`, `smb_pam_setcred`, `smb_internal_pam_session`, and `smb_pam_chauthtok`. Public functions are `smb_pam_claim_session`, `smb_pam_close_session`, `smb_pam_accountcheck`, `smb_pam_passcheck`, and `smb_pam_passchange`.

## Control Flow
Authentication creates a PAM conversation carrying username/password, starts service `samba`, sets RHOST and TTY when supported, calls `pam_authenticate`, `pam_acct_mgmt`, and `pam_setcred`, maps PAM errors to NTSTATUS, and always ends the PAM handle. Session functions respect `lp_obey_pam_restrictions` and open/close sessions. Password changes build a prompt/reply chat script from `lp_passwd_chat`, substitute username/old/new password tokens, and call `pam_chauthtok`.

## State and Persistence
No long-lived file-local state is stored. PAM modules may update system credential/session/password state. Temporary conversation data is malloc-owned and freed through `smb_pam_end`; password chat nodes are explicitly freed.

## Dependencies and Integration Points
Dependencies include platform PAM headers, Samba PAM error mapping, loadparm options such as `obey pam restrictions`, `null passwords`, and `passwd chat`, string/wildcard helpers, and callers in `pass_check`, `auth.c`, and session management code.

## Risks and Test Signals
Risks include PAM stack differences across OSes, prompt matching failures during password change, memory cleanup on early start failures, null-password policy mismatches, and NTSTATUS/PAM error mapping bugs. Tests should cover PAM auth success/failure, account expired/disabled cases, session claim/close, password change prompt variants, builds without PAM, and configurations with PAM restrictions disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/pampass.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/pass_check.c -->
# sources/user-network-fs/samba/source3/auth/pass_check.c

## Purpose
This file checks plaintext Unix passwords against PAM when enabled or against system crypt-style password stores otherwise. Encrypted SMB password verification is handled elsewhere.

## Important APIs, Types, and Functions
The public API is `pass_check`. Internal `password_check` dispatches to `smb_pam_passcheck` or platform crypt functions. In non-PAM builds, static helpers maintain global copies of the current salt and encrypted password.

## Control Flow
`pass_check` rejects null passwords according to policy, short-circuits into PAM for PAM builds, otherwise loads the password hash from `passwd`, shadow, adjunct, IA, or Ultrix sources, allows empty system hashes only when null passwords are enabled, and calls `password_check`. If the initial check fails with `WRONG_PASSWORD` and `run_cracker` is true, all-uppercase passwords may be retried in lowercase unless they are mixed case.

## State and Persistence
In non-PAM builds, `ths_salt` and `ths_crypted` are static process-global buffers updated for each call. No persistent storage is written. PAM builds delegate all state to `pampass.c` and PAM modules.

## Dependencies and Integration Points
Dependencies include system passwd/shadow APIs, `crypt`/`bigcrypt`/`crypt16` variants depending on platform, PAM password checking, loadparm null-password policy, and string case helpers. It is called by `auth_unix.c`.

## Risks and Test Signals
Risks include process-global salt/hash buffers in threaded contexts, platform-specific shadow access requiring root, weak lowercase retry behavior, null-password policy mistakes, and compile-time code paths that may be rarely exercised. Tests should cover PAM and non-PAM builds, missing users, wrong passwords, null passwords, uppercase retry behavior, shadow hash retrieval, and non-password PAM failures returning without retries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/pass_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/proto.h -->
# sources/user-network-fs/samba/source3/auth/proto.h

## Purpose
This generated-style header declares the source3 auth subsystem's cross-file API. It connects the dispatcher, backends, server-info conversion, token utilities, user mapping, Kerberos helpers, PAM/plaintext checks, and source4 bridge.

## Important APIs, Types, and Functions
It declares auth registration/context APIs, GENSEC/auth4 preparation, NTLMSSP hook functions, SAM checks, backend init functions, user-info constructors, server-info and session-info constructors, token creation utilities, group/user membership helpers, PAM and plaintext password functions, Kerberos mapping functions, and `auth_samba4_init`. It also defines Unix hint flags such as `AUTH3_UNIX_HINT_QUALIFIED_NAME`, `AUTH3_UNIX_HINT_DONT_TRANSLATE_FROM_SIDS`, and `AUTH3_UNIX_HINT_DONT_EXPAND_UNIX_GROUPS`.

## Control Flow
The header itself has no runtime flow, but it documents call layering: callers build `auth_usersupplied_info`, create an `auth_context` or `auth4_context`, check credentials, receive `auth_serversupplied_info`, then convert to SamInfo or `auth_session_info` and tokens. It also exposes backend initialization for static module registration.

## State and Persistence
No state is stored in the header. The declarations expose stateful facilities implemented elsewhere, including backend registries, cached guest/system sessions, passdb mutation, PAM sessions, and token/session-key handling.

## Dependencies and Integration Points
The header forwards or references `TALLOC_CTX`, `DATA_BLOB`, `tsocket_address`, `samu`, `passwd`, Netlogon SamInfo structures, PAC structures, winbind auth info, security tokens, and Samba auth types. Some declared functions are outside this work item, so this file is the integration map for the wider auth directory.

## Risks and Test Signals
Risks include prototype drift from implementations, typo-preserved ABI names such as `AUTH3_UNIX_HINT_ISLOLATED_NAME`, and broad coupling that allows changes in one auth file to break many callers. Test signals are compile coverage, static module linkage, include hygiene, and end-to-end auth tests that exercise declarations across translation units.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/server_info.c -->
# sources/user-network-fs/samba/source3/auth/server_info.c

## Purpose
This file converts between Samba's internal `auth_serversupplied_info`, Netlogon validation structures, PAC-derived information, passdb `samu` records, and Unix passwd records. It is the structural bridge from authentication results to domain-style SamInfo data.

## Important APIs, Types, and Functions
Public functions include `make_server_info`, `serverinfo_to_SamInfo2`, `serverinfo_to_SamInfo3`, `serverinfo_to_SamInfo6`, `create_info3_from_pac_logon_info`, `create_info6_from_pac`, `samu_to_SamInfo3`, and `passwd_to_SamInfo3`. Internal helpers include `append_netr_SidAttr`, `group_sids_to_info3`, `merge_resource_sids`, and `SamInfo3_handle_sids`.

## Control Flow
`make_server_info` allocates a zeroed server-info object and initializes UID/GID to `-1` to avoid accidental root use. Serverinfo-to-SamInfo conversions copy info3 and overlay session keys. PAC conversion copies logon info and merges resource-group SIDs into extra SIDs. `samu_to_SamInfo3` extracts SIDs, times, names, account flags, and group memberships from passdb. `passwd_to_SamInfo3` resolves a Unix username to a SID, determines primary group via winbind or gid mapping, normalizes unsuitable Unix/builtin/well-known group SIDs to Domain Users, and builds SamInfo3.

## State and Persistence
No persistent state is stored. The file reads passdb domain capabilities, passdb account data, winbind user SID lists, Unix passwd/gid data, and PAC contents, then creates talloc-owned output structures.

## Dependencies and Integration Points
Dependencies include Netlogon NDR types, security SID utilities, winbind client helpers, passdb, Unix SID conversion, and PAC structures. It is used by SAM, Unix, winbind, Kerberos/PAC, and server-info helper paths throughout the auth subsystem.

## Risks and Test Signals
Risks include invalid SID/domain RID handling, loss of extra/resource SIDs, incorrect primary group normalization, missing ADS passdb support for SamInfo6, session-key truncation/copy mistakes, and `passwd_to_SamInfo3` paths that differ when winbind is unavailable. Tests should cover PAC resource groups, SamInfo2/3/6 conversion, Unix user and group SID special cases, passdb group memberships, winbind/no-winbind passwd conversion, and UID/GID root-safety initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/server_info.c -->
