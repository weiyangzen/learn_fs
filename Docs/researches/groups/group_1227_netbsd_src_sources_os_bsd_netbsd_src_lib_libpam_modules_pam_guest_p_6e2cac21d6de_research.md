# Group Research: group_1227_netbsd_src_sources_os_bsd_netbsd_src_lib_libpam_modules_pam_guest_p_6e2cac21d6de

Scope checked against `Docs/research_subset_a.md`; all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_guest/pam_guest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_guest/pam_guest.c

Read completely: 120 lines.

This PAM authentication module grants access only when `PAM_USER` is in a comma-separated guest list. The `guests` option overrides the default list `guest`; `nopass` skips password retrieval; `pass_is_user` requires the authentication token to equal the username; and `pass_as_ruser` stores the password token as `PAM_RUSER`.

Core logic is in `lookup`, which scans exact comma-delimited tokens, and `pam_sm_authenticate`, which fetches the target user, evaluates guest membership, optionally checks the password token, sets `GUEST=<user>` in the PAM environment on success, and otherwise returns `PAM_AUTH_ERR`. `pam_sm_setcred` is a no-op success path.

Security/reliability notes: this is intentionally permissive for configured guest accounts. `pass_as_ruser` treats a password as a remote-user identity and should be used carefully in stacks that trust `PAM_RUSER`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_guest/pam_guest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/Makefile

Read completely: 42 lines.

This builds the `pam_krb5` module from `pam_krb5.c` and installs `pam_krb5.8`. It links against Heimdal `krb5`, `asn1`, `roken`, `com_err`, local `crypt`, and OpenSSL `crypto`.

It disables clang format-security warnings for this module and includes the common PAM module build rules via `../mod.mk`.

Security/reliability notes: build-only file. The key dependency implication is that this module is Heimdal-oriented and depends on crypto and Kerberos libraries being available in the NetBSD tree.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/pam_krb5.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/pam_krb5.c

Read completely: 1135 lines.

This is a full Kerberos 5 PAM module implementing authentication, credential establishment, account checks, and password changes. It uses Heimdal by default (`COMPAT_HEIMDAL`) and has compatibility shims for MIT Kerberos guarded by macros.

Authentication flow: `pam_sm_authenticate` gets `PAM_USER`, `PAM_RUSER`, and `PAM_SERVICE`, initializes a Kerberos context, verifies that a local service key exists unless `allow_kdc_spoof` is configured, allocates initial-credential options, applies `forwardable` and `renewable` options, parses the principal, gets the password token, optionally maps realm-qualified names to local users, fetches a TGT with `krb5_get_init_creds_password`, stores it in a temporary memory ccache, verifies the TGT against the local keytab, and saves the ccache name as PAM data with `cleanup_cache`.

Credential flow: `pam_sm_setcred` copies the temporary ccache into a persistent ccache unless `no_ccache` is set. It supports refresh/reinitialize using `KRB5CCNAME`, or establishment using the `ccache` option with `%u` and `%p` substitution, defaulting to `FILE:/tmp/krb5cc_<uid>`. It temporarily drops effective gid/uid to the target user before resolving or creating the persistent cache, copies credentials, fixes ownership/mode for file caches, and sets `KRB5CCNAME`.

Account flow: `pam_sm_acct_mgmt` resolves the temporary ccache and checks `krb5_kuserok` against `PAM_USER`. If no Kerberos ccache was established, it returns success and lets authentication stack ordering decide policy.

Password flow: `pam_sm_chauthtok` handles prelim as success and update by getting old credentials for `kadmin/changepw`, prompting for a new password, calling `krb5_set_password`, and reporting Kerberos password-change result messages.

Helper functions: `verify_krb_v5_tgt_begin` searches keytab service principals, preferring `host/<host>` and falling back to the PAM service principal; `verify_krb_v5_tgt` builds and reads an AP request against the chosen local service key; `cleanup_cache` destroys the temporary ccache at `pam_end`; `log_krb5` formats Kerberos errors to PAM/syslog logging.

Security/reliability notes: the module explicitly defends against spoofed KDCs by requiring local keytab verification unless `allow_kdc_spoof` is configured. Credential-cache handling drops privileges before file creation, but failures before credential restoration still flow through cleanup that restores euid/egid. `asprintf` results for the principal are not checked before `krb5_parse_name`, so out-of-memory behavior depends on downstream tolerance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/pam_krb5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/Makefile

Read completely: 42 lines.

This builds `pam_ksu` from `pam_ksu.c`, installs `pam_ksu.8`, and links against Heimdal `krb5`, `asn1`, `roken`, `com_err`, local `crypt`, and OpenSSL `crypto`.

It also suppresses clang format-security warnings and includes the common PAM module rules.

Security/reliability notes: build-only file. It mirrors `pam_krb5` dependency selection for Kerberos-backed authentication.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/pam_ksu.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/pam_ksu.c

Read completely: 293 lines.

This module authenticates `su`-style access using Kerberos. It determines a Kerberos principal for the invoking user, checks whether that principal is allowed to become the target user via `krb5_kuserok`, and then authenticates the principal with a password and verifies initial credentials against a local keytab.

Important behavior: when target user is `root`, `get_su_principal` transforms the current/default principal into a root instance such as `user/root@REALM`; otherwise it uses the current/default principal. It temporarily switches effective uid to the real uid while locating the default ccache. It disables Heimdal home-directory access while deriving credentials, then briefly enables it only for the `.k5login` `krb5_kuserok` check.

`auth_krb5` allocates get-init-creds options, prompts for the target principal password, gets initial credentials, and verifies them with `krb5_verify_init_creds` with `ap_req_nofail` set.

Security/reliability notes: authentication requires a usable local keytab. There are memory leaks on some early returns in `auth_krb5` because allocated options are not freed on all paths, but the PAM process lifetime may limit impact.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/pam_ksu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/Makefile

Read completely: 38 lines.

This builds `pam_lastlog` from `pam_lastlog.c`, installs `pam_lastlog.8`, and defines `SUPPORT_UTMP`, `SUPPORT_UTMPX`, and `LOGIN_CAP`.

It links against `libutil` and suppresses string truncation warnings for `pam_lastlog.c`.

Security/reliability notes: build-only file. The compile flags enable both legacy `utmp` and newer `utmpx` session accounting paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/pam_lastlog.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/pam_lastlog.c

Read completely: 387 lines.

This session module records logins and logouts in `utmp`, `wtmp`, `utmpx`, `wtmpx`, `lastlog`, and `lastlogx`, depending on compile-time support. It also displays the previous login record unless silenced by `PAM_SILENT` or login class `hushlogin`.

`pam_sm_open_session` fetches `PAM_USER`, `PAM_RHOST`, `PAM_SOCKADDR`, `PAM_TTY`, and optional `PAM_NUSER`, strips `/dev/` from the tty, and records the session unless `no_nested` is set and a nested user exists. Option `no_fail` forces success even after failures.

`pam_sm_close_session` strips `/dev/` from `PAM_TTY` and logs logout records with `logoutx`/`logwtmpx` and `logout`/`logwtmp`, again respecting `no_nested`.

Helper functions build and write `utmpx`, `lastlogx`, `utmp`, and `lastlog` records; `domsg` reports the last login time, host, and line through PAM text info.

Security/reliability notes: many string copies use fixed-size legacy record fields and intentionally truncate. The legacy `lastlog` path seeks by `uid * sizeof(struct lastlog)`, so very large uids rely on `off_t` width and filesystem behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/pam_lastlog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/Makefile

Read completely: 32 lines.

This builds `pam_login_access` from `pam_login_access.c` and `login_access.c`, and installs `pam_login_access.8` plus `login.access.5`.

It uses the shared PAM module make rules.

Security/reliability notes: build-only file. It ties the PAM account module to the local `/etc/login.access` parser.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/login_access.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/login_access.c

Read completely: 254 lines.

This implements a `/etc/login.access` parser based on Wietse Venema’s access control logic. `login_access(user, from)` reads the file one line at a time, skips comments and blanks, requires three colon-separated fields, and stops at the first rule whose user list and origin list both match. A `+` rule grants access, a `-` rule denies access, and a missing file means no access control.

List matching supports comma/space/tab-separated tokens and `EXCEPT` clauses. User tokens support `ALL`, exact username matches, local Unix group membership, and netgroup syntax. Origin tokens support `ALL`, exact matches, domain suffixes beginning with `.`, `LOCAL` for names without dots, and network prefixes ending in `.`.

Netgroup support is stubbed out: `netgroup_match` logs that NIS netgroup support is not configured and returns no match.

Security/reliability notes: malformed lines are logged and ignored, which can accidentally broaden access if an intended deny rule is invalid. Matching uses `strtok`, so parsing is destructive and not thread-safe on shared input, but this function uses a local line buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/login_access.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.c

Read completely: 106 lines.

This PAM account module applies `login_access()` to the current login attempt. It fetches `PAM_USER`, `PAM_RHOST`, and `PAM_TTY`; local logins are checked against the tty, while remote logins are checked against the remote host.

On a match allowing access it returns `PAM_SUCCESS`; otherwise it emits a verbose PAM error naming the denied user and tty/host, then returns `PAM_AUTH_ERR`.

Security/reliability notes: it calls `gethostname` into a local buffer but does not use the result. If `PAM_TTY` is null for a local login, it passes null through to `login_access`, whose string matching assumes non-null input.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.h

Read completely: 39 lines.

This header declares the shared helper:

`int login_access(const char *, const char *);`

It is included by both the PAM wrapper and parser implementation.

Security/reliability notes: declaration-only file with no include guard, relying on simple single-prototype usage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_nologin/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_nologin/Makefile

Read completely: 34 lines.

This builds `pam_nologin` from `pam_nologin.c`, installs `pam_nologin.8`, and links against `libutil`.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_nologin/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_nologin/pam_nologin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_nologin/pam_nologin.c

Read completely: 158 lines.

This authentication module denies logins when a configured nologin file exists. It defaults to `/etc/nologin`, but login class capability `nologin` can override the path, and `ignorenologin` can bypass the check. Root defaults to bypass unless the login class overrides that default.

`pam_sm_authenticate` fetches the user, requires an existing passwd entry, obtains login class capabilities, opens the nologin file, prints its contents via `pam_error`, and denies authentication. Missing nologin file means success; other open failures deny login.

Security/reliability notes: the file is allocated based on `st_size` and read once without checking short read, so changing files can produce partial messages. The policy is fail-closed for existing-but-unreadable nologin files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_nologin/pam_nologin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_permit/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_permit/Makefile

Read completely: 32 lines.

This builds `pam_permit` from `pam_permit.c` and installs `pam_permit.8`.

Security/reliability notes: build-only file for an intentionally always-successful PAM module.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_permit/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_permit/pam_permit.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_permit/pam_permit.c

Read completely: 99 lines.

This module implements all main PAM service hooks as unconditional success. `pam_sm_authenticate` first calls `pam_get_user` and propagates errors, but otherwise returns `PAM_SUCCESS`; setcred, account, password, open-session, and close-session hooks all return success.

Security/reliability notes: this module deliberately permits access and should only appear where the PAM stack is intentionally bypassing checks or providing a placeholder.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_permit/pam_permit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/Makefile

Read completely: 35 lines.

This builds `pam_radius` from `pam_radius.c`, installs `pam_radius.8`, and links against `libradius`.

A comment notes that `libradius` “doesn't exist yet” in the historical context, though the build references `${.CURDIR}/../../../libradius`.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/pam_radius.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/pam_radius.c

Read completely: 389 lines.

This authentication module delegates password authentication to a RADIUS server through `radlib`. Options include `conf`, `template_user`, `nas_id`, and `nas_ipaddr`.

`build_access_request` creates a `RAD_ACCESS_REQUEST` with user, password, NAS identifier, NAS IP address, state, and `RAD_AUTHENTICATE_ONLY` service type. It defaults NAS identifier/IP input to the local hostname when applicable.

`pam_sm_authenticate` fetches user and password, opens/configures the RADIUS handle, sends the access request, then handles accept, reject, challenge, and transport errors. On accept, `do_accept` may update `PAM_USER` from a returned `RAD_USER_NAME`; `template_user` can map authenticated users without local passwd entries to a configured local account. On challenge, `do_challenge` displays up to ten reply messages, prompts for a response, includes returned `RAD_STATE`, and resubmits.

Security/reliability notes: challenge-message cleanup is incomplete on several error returns, causing leaks. `template_user` is a powerful identity mapping option and should be restricted to stacks that expect shared local accounts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/pam_radius.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rhosts/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rhosts/Makefile

Read completely: 8 lines.

This builds `pam_rhosts` from `pam_rhosts.c`, installs `pam_rhosts.8`, and includes the common PAM module rules.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rhosts/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rhosts/pam_rhosts.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rhosts/pam_rhosts.c

Read completely: 103 lines.

This module authenticates using classic rhosts trust. It gets the target user, verifies the user exists, denies root unless `allow_root` is configured, fetches `PAM_RUSER` and `PAM_RHOST`, then calls `ruserok`.

`pam_sm_setcred` is a no-op success path.

Security/reliability notes: rhosts trust is host/user-name based and generally weak by modern standards. The module prevents root use by default, but `allow_root` re-enables that risk.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rhosts/pam_rhosts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rootok/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rootok/Makefile

Read completely: 32 lines.

This builds `pam_rootok` from `pam_rootok.c` and installs `pam_rootok.8`.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rootok/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rootok/pam_rootok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rootok/pam_rootok.c

Read completely: 78 lines.

This authentication module succeeds only when the real uid is 0. Non-root callers get a verbose refusal and `PAM_AUTH_ERR`. `pam_sm_setcred` returns success.

Security/reliability notes: it checks `getuid`, not effective uid, so setuid-root programs invoked by non-root users do not automatically pass.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rootok/pam_rootok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_securetty/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_securetty/Makefile

Read completely: 32 lines.

This builds `pam_securetty` from `pam_securetty.c` and installs `pam_securetty.8`.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_securetty/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_securetty/pam_securetty.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_securetty/pam_securetty.c

Read completely: 125 lines.

This PAM account module restricts root logins to secure terminals. It gets the user and passwd entry, immediately succeeds for non-root users, fetches `PAM_TTY`, strips a `/dev/` prefix, and checks `getttynam` for `TTY_SECURE`.

If root is not on a secure tty, it logs a notice including `PAM_RHOST` when available, emits “Not on secure TTY”, and returns `PAM_AUTH_ERR`.

Security/reliability notes: only root is subject to this check. It logs `(const char *)tty` even if tty is null in the refusal path, depending on syslog printf behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_securetty/pam_securetty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_self/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_self/Makefile

Read completely: 32 lines.

This builds `pam_self` from `pam_self.c` and installs `pam_self.8`.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_self/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_self/pam_self.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_self/pam_self.c

Read completely: 97 lines.

This module authenticates when the real uid matches the target account’s uid. It fetches `PAM_USER`, resolves the passwd entry, denies real uid 0 unless `allow_root` is configured, and succeeds only on uid equality.

`pam_sm_setcred` is a no-op success path.

Security/reliability notes: this is identity-continuity authorization, not password authentication. It uses real uid to avoid effective-uid privilege confusion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_self/pam_self.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_skey/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_skey/Makefile

Read completely: 15 lines.

This builds `pam_skey` from `pam_skey.c`, installs `pam_skey.8`, disables lint/profile/PIC archive installation, and links against `libskey`.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_skey/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_skey/pam_skey.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_skey/pam_skey.c

Read completely: 110 lines.

This authentication module validates S/Key one-time passwords. It uses `PAM_OPT_AUTH_AS_SELF` to authenticate `getlogin()` instead of `PAM_USER`, checks that the user has S/Key state, retrieves challenge text with `skey_keyinfo`, prompts as `Password [ <challenge> ]:`, duplicates the response, and calls `skey_passcheck`.

`pam_sm_setcred` is a no-op success path.

Security/reliability notes: if `getlogin()` returns null under `auth_as_self`, the code passes null into S/Key functions. The response is freed but not explicitly zeroed before free.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_skey/pam_skey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/Makefile

Read completely: 29 lines.

This builds `pam_ssh` from `pam_ssh.c` using OpenSSH sources from `${NETBSDSRCDIR}/crypto/external/bsd/openssh/dist`. It links against private `libssh`, local `crypt`, and OpenSSL `crypto`, and marks the private libssh subdir as a dependency.

It disables lint/profile/PIC archive installation and includes the common PAM module rules.

Security/reliability notes: build-only file. The module depends on OpenSSH private interfaces such as `sshkey` and auth-agent helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/pam_ssh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/pam_ssh.c

Read completely: 482 lines.

This PAM module authenticates by decrypting SSH private keys and can start an `ssh-agent` for the session. It tries `.ssh/identity`, `.ssh/id_rsa`, `.ssh/id_dsa`, and `.ssh/id_ecdsa`.

Authentication flow: `pam_sm_authenticate` resolves the user home directory, obtains a passphrase from `PAM_AUTHTOK`, borrows the target user credentials, tries to load known key files, stores successfully loaded keys as PAM data, and records `pam_ssh_have_keys`. With `try_first_pass`, it retries after clearing the token if an existing token unlocked no keys. `nullok` permits empty passphrases for unencrypted keys; otherwise unencrypted keys are rejected.

Key loading uses `sshkey_load_private`; it first tests for unencrypted keys with an empty passphrase so dummy passphrases cannot bypass `nullok`.

Session flow: `pam_sm_open_session` starts `/usr/bin/ssh-agent -s` when keys exist or `want_agent` is set. The child drops gid/groups/uid to the user, redirects output to a pipe, closes file descriptors, and execs ssh-agent. The parent parses `SSH_*=` assignments from agent output into the PAM environment. It then borrows user credentials, connects to the agent using the PAM environment, adds stored keys, and clears key PAM data. `pam_sm_close_session` kills the agent pid from `SSH_AGENT_PID`.

Security/reliability notes: agent output parsing mutates `fgetln` buffers in place and accepts any line beginning `SSH_` with `key=value;`. `pam_ssh_add_keys_to_agent` temporarily replaces global `environ`, which is process-global and unsafe in threaded PAM consumers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/pam_ssh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/Makefile

Read completely: 56 lines.

This builds `pam_unix` from `pam_unix.c`, installs `pam_unix.8`, and links against `libutil` and `libcrypt`. When `USE_YP` is not `no`, it defines `YP` and links `librpcsvc`.

It disables lint/profile/PIC archive installation and uses the common PAM module rules.

Security/reliability notes: build-only file. The `YP` conditional compiles NIS password-change support into the module.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/pam_unix.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/pam_unix.c

Read completely: 632 lines.

This module implements Unix password authentication, account expiry checks, and password changes for local files and optionally NIS.

Authentication: `pam_sm_authenticate` gets the target user or `getlogin()` under `auth_as_self`, obtains the passwd entry, handles empty passwords only when `nullok` is set and `PAM_DISALLOW_NULL_AUTHTOK` is absent, prompts for `PAM_AUTHTOK`, and compares `crypt(pass, realpw)` to the stored hash. Unknown users get dummy authentication against `"*"` to reduce obvious branching.

Account management: `pam_sm_acct_mgmt` checks null password policy, login class lookup, account expiry (`pw_expire`), password expiry (`pw_change`), and warning windows from login class `password-warn`.

Password changes: `pam_sm_chauthtok` chooses `passwd_db` from option, NIS availability, or local files. In prelim mode it verifies old password unless root is changing a local password, and denies non-root changes to root. In update mode it reads login class `minpasswordlen` and `passwordtime`, prompts for a new password with retry handling, rejects very short and all-lowercase passwords on first attempts, generates a salt from password configuration, hashes with `crypt`, sets password expiry, and updates either local master.passwd or NIS.

Local update uses `pw_lock`, opens `_PATH_MASTERPASSWD`, calls `pw_copyx`, and rebuilds the password database with `pw_mkdb`. NIS update finds the master server, ensures `yppasswdd` is on a privileged port, checks caller uid, builds a `yppasswd` RPC structure, and calls `YPPASSWDPROC_UPDATE`.

Security/reliability notes: password quality checks are minimal and partly advisory by retry count. `crypt` return is not checked for null before assignment/comparison. The NIS path uses UDP RPC and legacy trust assumptions, with a privileged-port check as mitigation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/pam_unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/staticmodules/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpam/staticmodules/Makefile

Read completely: 8 lines.

This makefile builds PAM modules statically by setting `MAKEDIRTARGETENV=MKPIC=no`, including `bsd.own.mk`, and delegating to `../modules` through `bsd.subdir.mk`.

Security/reliability notes: build-only file. It changes PIC behavior for the module subtree.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpam/staticmodules/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/Makefile

Read completely: 57 lines.

This builds `libpanel`, installs `panel.h`, and compiles the panel implementation files for curses window Z-order management. It links against `libcurses`.

It installs manual pages for panel creation, movement, visibility, user pointers, Z-order, and updates, with mlinks for related function names.

Security/reliability notes: build-only file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/_deck.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/_deck.c

Read completely: 34 lines.

This defines the hidden global panel deck `_deck` as a TAILQ initialized empty, and the hidden phantom `_stdscr_panel`.

These globals back all libpanel Z-order operations.

Security/reliability notes: global state means libpanel operations are not independently namespaced per screen or thread.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/_deck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/above.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/above.c

Read completely: 49 lines.

`panel_above` returns the visible panel above a given panel. With a null argument, it returns the bottom user-visible panel by asking for the panel above the phantom `stdscr` panel, or null if the deck is empty.

It returns null for hidden panels.

Security/reliability notes: callers must not pass stale/freed `PANEL *` values; hidden detection depends on internal TAILQ link state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/above.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/below.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/below.c

Read completely: 50 lines.

`panel_below` returns the panel below a given visible panel. With a null argument, it returns the top panel. It hides the phantom `stdscr` panel from callers by returning null when that would be the result.

Security/reliability notes: same stale-pointer caveat as other panel list helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/below.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/bottom.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/bottom.c

Read completely: 48 lines.

`bottom_panel` moves a visible panel to the bottom of the user-visible deck, just above the phantom `stdscr` panel. It rejects null and hidden panels, hides the panel to remove it from its current position, then reinserts it after `_stdscr_panel`.

Security/reliability notes: relies on `_stdscr_panel` being present, which is established when the first real panel is created.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/bottom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/del.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/del.c

Read completely: 63 lines.

`del_panel` hides a panel, frees its `PANEL` object, and, if the last remaining panel is the phantom `stdscr` panel, hides that too and asserts the deck is empty.

It does not delete or free the associated curses `WINDOW`.

Security/reliability notes: callers must not use the `PANEL *` after deletion. The associated window lifetime remains the caller’s responsibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/del.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/getuser.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/getuser.c

Read completely: 41 lines.

`panel_userptr` returns the panel’s stored user pointer, or null for a null panel.

Security/reliability notes: the API type is `char *`, but the pointer is arbitrary caller-owned data by convention; no ownership is transferred.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/getuser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/hidden.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/hidden.c

Read completely: 45 lines.

`panel_hidden` returns `ERR` for a null panel, `TRUE` when the panel is not linked into the deck, and `FALSE` otherwise.

Security/reliability notes: hidden state is inferred from internal TAILQ link pointers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/hidden.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/hide.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/hide.c

Read completely: 56 lines.

`hide_panel` removes a visible panel from the deck. If the panel is already hidden it returns success. After removal, it calls `touchoverlap` for every remaining panel so exposed areas will be repainted by later updates.

Security/reliability notes: hiding does not clear or free the associated window; it only changes deck membership and refresh state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/hide.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/move.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/move.c

Read completely: 58 lines.

`move_panel` moves the associated curses window to a new origin using `mvwin`. If the panel is visible, it touches overlaps at the old location before moving so newly exposed regions are refreshed. Moving to the same coordinates is a no-op success.

Security/reliability notes: direct `mvwin` on a panel’s window would bypass this exposed-area handling; callers should use `move_panel`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/move.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/new.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/new.c

Read completely: 76 lines.

`new_panel` creates a visible panel for a non-null, non-`stdscr` curses window. On first use it initializes the phantom `_stdscr_panel` with current `stdscr` and inserts it at the bottom of the deck, then allocates and inserts the new panel at the top.

The internal `_new_panel` initializes `win`, sets `user` null, and links into the deck.

Security/reliability notes: panel allocation failure returns null. The phantom panel tracks `stdscr` only when the deck is first initialized.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/new.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/panel.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/panel.h

Read completely: 61 lines.

This public header declares opaque `PANEL` and the libpanel API: create/delete, replace/window access, user pointer set/get, hide/show/hidden, top/bottom, above/below, move, and `update_panels`.

It includes `<curses.h>` and wraps declarations in C linkage macros.

Security/reliability notes: public ABI exposes user pointer as `char *`, though callers may use it as arbitrary data by convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/panel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/panel_impl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/panel_impl.h

Read completely: 92 lines.

This private header defines the `struct __panel` layout: associated `WINDOW *`, `char *user`, and TAILQ z-order entry. It declares the global deck and phantom `stdscr` panel, and defines macros for inserting/removing panels, detecting hidden state, and iterating the deck.

Hidden panels are represented by nulling the TAILQ entry’s internal next/prev pointers after removal.

Security/reliability notes: it relies on `<sys/queue.h>` internals to detect unlinked entries, which is intentionally a local implementation detail and not portable outside this queue implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/panel_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/replace.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/replace.c

Read completely: 53 lines.

`replace_panel` changes the curses window associated with a panel. For visible panels, it touches overlap regions for the old window before replacing it, so exposed regions are refreshed.

It rejects null panel or null window and returns `OK` on success.

Security/reliability notes: ownership of old and new `WINDOW *` remains with the caller.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/replace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/setuser.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/setuser.c

Read completely: 42 lines.

`set_panel_userptr` stores a caller-supplied pointer in the panel’s `user` field and returns `OK`; it returns `ERR` for null panels.

Security/reliability notes: no allocation or ownership management is performed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/setuser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/show.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/show.c

Read completely: 47 lines.

`show_panel` makes a hidden panel visible by inserting it at the top of the deck. It rejects null panels and already-visible panels.

Security/reliability notes: unlike some ncurses behavior, this implementation separates `show_panel` for hidden panels from `top_panel` for visible panels.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/show.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/top.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/top.c

Read completely: 49 lines.

`top_panel` moves a visible panel to the top of the deck. It rejects null and hidden panels, then implements the move as `hide_panel` followed by `show_panel`.

Security/reliability notes: this path touches exposed areas during the hide step even though the panel is immediately reinserted at the top.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/top.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/update.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/update.c

Read completely: 62 lines.

`update_panels` propagates refresh state through the deck and then calls `wnoutrefresh` from bottom to top. For each panel, it touches overlaps in every panel above it so higher panels repaint over lower ones.

Security/reliability notes: this function updates curses virtual screen state; callers still need the normal curses refresh/doupdate flow to display changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/update.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/window.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpanel/window.c

Read completely: 42 lines.

`panel_window` returns the curses window associated with a panel, or null for a null panel.

Security/reliability notes: returned pointer is borrowed; caller must not free or mutate it in ways that bypass panel bookkeeping for movement/replacement.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpanel/window.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpci/Makefile

Read completely: 28 lines.

This builds `libpci` from local userland wrapper files plus `pci_subr.c` and `dev_verbose.c` from the kernel source tree. It installs `pci.h`, `pci.3`, and mlinks for config read/write and device information helpers.

It adds `${NETBSDSRCDIR}/sys` to include paths and source search paths.

Security/reliability notes: build-only file. The library is a userland bridge to kernel PCI ioctl interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci.h

Read completely: 69 lines.

This public header declares userland PCI helper APIs. It defines `pcireg_t` as `uint32_t` and prototypes bus-wide config reads/writes, device-file config reads/writes, driver-name lookups, and shared PCI info/printing helpers.

Security/reliability notes: declaration-only file. The APIs operate on file descriptors expected to refer to PCI device/bus nodes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci_bus.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci_bus.c

Read completely: 97 lines.

This implements PCI configuration-space access for a bus/domain file descriptor. `pcibus_conf_read` fills a `pciio_bdf_cfgreg` with bus/device/function/register, calls `PCI_IOC_BDF_CFGREAD`, and returns the value. `pcibus_conf_write` fills the same structure and calls `PCI_IOC_BDF_CFGWRITE`.

Security/reliability notes: it performs no validation of bus/device/function/register ranges, relying on the kernel ioctl layer to enforce validity and permissions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci_bus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci_device.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci_device.c

Read completely: 89 lines.

This implements PCI configuration-space access for a specific PCI device file descriptor. `pcidev_conf_read` calls `PCI_IOC_CFGREAD` for a register and returns the value; `pcidev_conf_write` calls `PCI_IOC_CFGWRITE`.

Security/reliability notes: range and permission checks are delegated to the kernel. The read function requires a non-null output pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci_device.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci_drvname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpci/pci_drvname.c

Read completely: 84 lines.

This provides driver-name lookup helpers through PCI ioctls. `pci_drvname` looks up the driver for a device/function on the opened bus/device context using `PCI_IOC_DRVNAME`; `pci_drvnameonbus` includes an explicit bus number and uses `PCI_IOC_DRVNAMEONBUS`. Both copy the kernel-returned name with `strlcpy`.

Security/reliability notes: name truncation is possible when caller-provided `len` is too small, but bounded. Ioctl errors are returned as `-1` with `errno` from the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpci/pci_drvname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/Makefile

Read completely: 19 lines.

This builds `libperfuse` from `perfuse.c`, `ops.c`, `subr.c`, and `debug.c`, links against `libpuffs`, installs `perfuse.h`, and installs `libperfuse.3`.

It defines `_KERNTYPES`, includes the local directory and `libpuffs`, sets warnings to 5, and provides an optional debug flags variable.

Security/reliability notes: build-only file. `_KERNTYPES` affects kernel type visibility in userland headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/debug.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/debug.c

Read completely: 276 lines.

This implements perfuse tracing and debug formatting. It maps FUSE opcodes to names, defines queue-type strings, formats selected inbound operation payloads, records trace start/end timestamps, prunes completed traces past `PERFUSE_TRACECOUNT_MAX`, and dumps trace history plus per-op timing statistics.

`perfuse_opname` linear-searches the opcode table and returns `UNKNOWN` for unmatched operations. `perfuse_opdump_in` currently formats `FUSE_LOOKUP` path payloads. `perfuse_trace_begin` records opcode, initial status, timestamp, node path, and extra operation text, then appends to `ps_trace`. `perfuse_trace_end` records completion time/error and prunes old completed traces. `perfuse_trace_dump` truncates and rewinds an output file, prints individual traces, computes min/avg/max latency by opcode, and prints global node/exchange counts.

Security/reliability notes: `perfuse_opdump_in` uses a static buffer, so concurrent calls race. `perfuse_trace_dump` indexes arrays by `pt_opcode`; opcodes outside `FUSE_OPCODE_MAX` would be unsafe if inserted into traces.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/fuse.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/fuse.h

Read completely: 515 lines.

This private/local FUSE protocol header defines Linux FUSE kernel protocol constants and wire structures used by perfuse. It sets protocol version 7.12, root node id, buffer sizing, xattr limits, flag constants, opcode enums, notify enums, and request/response structures for attributes, statfs, locks, lookup, getattr, mknod, mkdir, rename, link, setattr, open/create, release/flush, read/write, fsync, xattr, locking, access, init, CUSE init, interrupt, bmap, ioctl, poll, fallocate, directory entries, and invalidation notifications.

The header also defines compatibility structure sizes for older protocol forms and directory-entry alignment macros. Kernel-to-process and process-to-kernel header definitions are present under `#if 0` because equivalent definitions live in `perfuse.h`.

Security/reliability notes: this is ABI/wire-format-sensitive. Structure layout, integer widths, and alignment macros must match the Linux FUSE protocol expected by translated userspace filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/fuse.h -->