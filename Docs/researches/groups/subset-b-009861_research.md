# Research: subset-b-009861

This grouped report covers Samba `source3/script/tests` blackbox tests in source-tree order. Each section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_encryption_off.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_encryption_off.sh

## Purpose
This shell blackbox test verifies `smbclient` behavior when server-side encryption is globally disabled. It checks that unencrypted access still works for shares whose `smb encrypt` is default/enabled or desired, and that access fails when a share requires encryption or when the client requires encryption.

## Important APIs, Functions, and Control Flow
The script consumes `USERNAME PASSWORD SERVER SMBCLIENT`, wraps the binary with `$VALGRIND`, loads `subunit.sh`, and uses `testit` plus `testit_expect_failure`. The main body is a fixed matrix over shares `enc_desired`, `tmp`, and `tmpenc`, dialects default/SMB1, `-m smb3_02`, and `-m smb3_11`, and optional `--client-protection=encrypt`.

## State, Dependencies, Integration, and Risks
It relies on selftest shares configured with different encryption policies and on `smbclient` returning nonzero for failed tree connects. It has no persistent state except subunit output and the `failed` counter. Risks are mostly configuration drift: if share names or global encryption settings change, the expected success/failure polarity inverts. Test signals are explicit subunit pass/fail entries and final `testok`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_encryption_off.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_iconv.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_iconv.sh

## Purpose
This test ensures `smbclient ls` reports `NT_STATUS_INVALID_NETWORK_RESPONSE` when a directory listing contains a filename that cannot be converted under a forced CP850 Unix charset.

## Important APIs, Functions, and Control Flow
The script accepts `SERVER SERVER_IP SHARENAME USERNAME PASSWORD SMBCLIENT` plus optional extra args. `test_smbclient_iconv` writes a temporary client config under `$PREFIX/client/client_cp850_smbconf` that includes the normal client config, sets `unix charset = cp850`, and sets `client min protocol = core`. It executes `CLI_FORCE_INTERACTIVE=yes smbclient ... -c ls`, captures stderr/stdout, removes the config, and greps for the expected status.

## State, Dependencies, Integration, and Risks
State is limited to the generated config file. Integration depends on `$PREFIX/client/client.conf`, a share populated with an invalid CP850 name, and Samba charset conversion code. The `eval`-constructed command is sensitive to quoting in `ADDARGS`. The test signal is the presence of the exact `NT_STATUS_INVALID_NETWORK_RESPONSE` string.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_iconv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_kerberos.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_kerberos.sh

## Purpose
This test validates `smbclient` Kerberos option handling against a temporary share, including required, desired, off, explicit ccache, and no-user/password modes. It also accounts for FIPS targets where non-Kerberos authentication is expected to fail.

## Important APIs, Functions, and Control Flow
The script loads `subunit.sh` and `common_test_fns.inc`, resolves `samba4kinit`/`samba4kdestroy` if present, sets `KRB5CCNAME=FILE:$PREFIX/ccache_smbclient_kerberos`, and uses `test_smbclient`/`test_smbclient_expect_failure`. It first tests password-based SMB3 connections with different `--use-kerberos` values, branches on `TARGET` for the `off` case, obtains a ticket with `kerberos_kinit`, then tests `--use-krb5-ccache` and ticket-backed desired/required modes.

## State, Dependencies, Integration, and Risks
Persistent state is a Kerberos ccache removed at the end. Dependencies include a working KDC, realm, generated selftest credentials, `common_test_fns.inc`, and Samba Kerberos wrappers. Cleanup uses `kdestroy` and `rm -rf`. Risks include leaked ccaches on early shell interruption and target-name coupling for FIPS semantics. Test signals are subunit results per Kerberos mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_kerberos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_krb5.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_krb5.sh

## Purpose
This compact wrapper checks that Samba 3 `smbclient` can access `//$SERVER/tmp` with an externally supplied Kerberos ccache.

## Important APIs, Functions, and Control Flow
It accepts `ccache smbclient3 server` plus optional `smbclient` args, exports `KRB5CCNAME`, loads `subunit.sh`, and runs one `testit "smbclient"` invoking `$VALGRIND $SMBCLIENT3 //$SERVER/tmp -c 'ls' --use-krb5-ccache=$KRB5CCNAME $ADDARGS`.

## State, Dependencies, Integration, and Risks
The script does not create the ccache; the caller must provide it. It depends on the share `tmp`, a valid ticket, and correct `ADDARGS` from the surrounding selftest environment. The `failed` variable is incremented without being initialized locally, relying on shell empty-to-zero behavior in `expr`. The only test signal is the command exit status reported through subunit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_krb5.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_large_file.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_large_file.sh

## Purpose
This test verifies large POSIX-mode write/read behavior through `smbclient` by uploading and downloading a sparse 20 MiB file on `xcopy_share`.

## Important APIs, Functions, and Control Flow
The script accepts a ccache, `smbclient3`, server, prefix, and extra args. It exports `KRB5CCNAME`, creates `$PREFIX/largefile` using `dd if=/dev/zero seek=$((20 * 1024 * 1024)) count=1 bs=1`, then `test_large_write_read` writes an smbclient command script: `posix`, `put`, `get`, `rm`, `quit`. It expects a successful command and a `getting file` message, then runs `cmp` between the original and downloaded files.

## State, Dependencies, Integration, and Risks
State is temporary files under `$PREFIX` and a server-side `largefile` removed by the smbclient script. It depends on POSIX extensions, xcopy share configuration, disk/sparse-file behavior, and optional Kerberos/additional args. Risks include storage pressure if sparse files become allocated and cleanup gaps if the upload succeeds but later commands fail. The strongest signal is byte-for-byte `cmp`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_large_file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_list_servers.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_list_servers.sh

## Purpose
This regression test covers Bug 14939: listing servers via `smbclient -L` on NetBIOS port 139 must not emit the internal `smb1cli_req_writev_submit:` error when negotiating modern dialects.

## Important APIs, Functions, and Control Flow
The script accepts server, IP, username, password, and `SMBCLIENT`. `test_smbclient_list_servers` runs `CLI_FORCE_INTERACTIVE=yes $SMBCLIENT -L //$SERVER -U... -I $SERVER_IP -p139 "$ADDARGS" </dev/null 2>&1`, captures output, and fails if the internal error marker is present.

## State, Dependencies, Integration, and Risks
It has no persistent state. Integration depends on NetBIOS port 139 availability, the server list path in `smbclient`, and test credentials. Because success is "absence of a string", unrelated command failures without that string could be underdetected unless command status also fails through shell evaluation. The test signal is negative grep plus subunit status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_list_servers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_log_basename.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_log_basename.sh

## Purpose
This script verifies that `smbclient -l <log-basename>` creates and writes to the expected log file even when authentication fails.

## Important APIs, Functions, and Control Flow
It accepts `SERVER SMBCLIENT PREFIX` plus extra args, loads `subunit.sh`, and defines `$LOG_DIR=$PREFIX/st_log_basename_dir`. `test_smbclient_log_basename` recreates the directory, runs `$VALGRIND $SMBCLIENT -l $LOG_DIR -d3 //$SERVER/IPC$ $CONFIGURATION -U%badpassword -c quit $ADDARGS`, and greps `$LOG_DIR/log.smbclient` for `Client started`.

## State, Dependencies, Integration, and Risks
State is a log directory under `$PREFIX`. The command intentionally uses bad credentials, so the useful signal is log creation, not login success. It depends on `$CONFIGURATION` being available from the caller and on debug logging format. Risks include stale log files if directory cleanup fails and false failures if the startup log string changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_log_basename.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_machine_auth.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_machine_auth.sh

## Purpose
This test checks `smbclient --machine-pass` authentication against normal and force-user/group shares.

## Important APIs, Functions, and Control Flow
The script accepts `SERVER SMBCLIENT CONFIGURATION`, sets global variables consumed by `common_test_fns.inc` (`CONFIGURATION` and lowercase `smbclient`), and runs three `test_smbclient` calls against `tmp`, `forceuser`, and `forcegroup` on port 139 with `--machine-pass`.

## State, Dependencies, Integration, and Risks
No files are created. It depends on a valid machine account secret in the test environment, NetBIOS port 139, and selftest shares whose force-user/group settings are meant to work with machine auth. It exits with the raw `failed` count rather than `testok`, so callers should interpret nonzero exit status. Risks are mostly environment-coupled: stale machine passwords or changed share ACLs break all cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_machine_auth.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_mget.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_mget.sh

## Purpose
This wrapper tests recursive `mget` behavior for a directory and then verifies local cleanup of the fetched files.

## Important APIs, Functions, and Control Flow
Arguments are `smbclient3 server share user password directory`. It changes to `$SELFTEST_TMPDIR`, starts a manual subunit test because `testit` breaks the `-c` command, and invokes `smbclient //$SERVER/$SHARE -U... -c "recurse;prompt;mget $DIRECTORY"`. It emits pass/fail manually, then runs `rm "$DIRECTORY"/foo` and `rmdir "$DIRECTORY"` via `testit`.

## State, Dependencies, Integration, and Risks
It creates downloaded files under `$SELFTEST_TMPDIR/$DIRECTORY` and removes only `foo` plus the directory. It assumes the remote directory contains `foo` and that `mget` creates a matching local directory. Risks include partial downloads leaving residue and limited verification: success is mainly command status and the ability to delete expected local files, not a content comparison.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_mget.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_netbios_aliases.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_netbios_aliases.sh

## Purpose
This test verifies Kerberos access through an SMB server name that may be supplied as a NetBIOS alias.

## Important APIs, Functions, and Control Flow
It accepts `smbclient SERVER USERNAME PASSWORD PREFIX CONFIGURATION`, resolves `samba4kinit`, creates `KRB5CCNAME=FILE:$PREFIX/test_smbclient_netbios_aliases_krb5ccache`, loads `subunit.sh` and `common_test_fns.inc`, obtains a ticket with `kerberos_kinit`, then calls `test_smbclient "smbclient (krb5)" "ls" "//$SERVER/tmp" --use-krb5-ccache=$KRB5CCNAME`.

## State, Dependencies, Integration, and Risks
State is the Kerberos ccache path, removed before and after the test. It depends on correct SPN/alias setup, test KDC behavior, and the `tmp` share. `ADDADS` is assigned from extra args but not used, suggesting either historical compatibility or a typo. The signal is successful Kerberos-backed `ls` through the provided server name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_netbios_aliases.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_ntlm.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_ntlm.sh

## Purpose
This test validates NTLM and anonymous authentication behavior for `smbclient` over either NT1 or SMB3, including guest mapping and signing failure cases.

## Important APIs, Functions, and Control Flow
Inputs include server, username/password, `MAPTOGUEST`, `SMBCLIENT`, `PROTOCOL`, and config. The script rejects protocols other than `SMB3` or `NT1`. For NT1 it tests old-style no-SPNEGO/NTLMv1-compatible options and default NT1. For SMB3 it tests default SMB3. It covers valid username/password, anonymous no-password, anonymous bad-password with behavior depending on `MAPTOGUEST`, bad-user guest mapping, and signing-required failure paths for bad credentials.

## State, Dependencies, Integration, and Risks
No persistent state is created. Dependencies are the IPC share, server guest mapping policy, and auth options such as `clientusespnego`, `clientntlmv2auth`, and `--client-protection=sign`. Risks include broad output-only command checks and sensitivity to policy changes. Test signals are exit-status polarity through `testit` and `testit_expect_failure`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_ntlm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_s3.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_s3.sh

## Purpose
This is a broad Samba 3 `smbclient` blackbox regression harness. It exercises connection listing, interactive/noninteractive behavior, symlink handling, MSDFS, attributes, authentication files and winbind ccaches, backup privilege, mangled/bad names, streams, wide links, no-permission shares, `deltree`, `setmode`, `utimes`, path normalization, volume output, quiet output, and valid/invalid users.

## Important APIs, Functions, and Control Flow
The script accepts 13 environment parameters, builds `RAWARGS="${CONFIGURATION} -m${PROTOCOL}"`, wraps `SMBCLIENT` and `WBINFO` with `$VALGRIND`, suppresses deprecated warnings, and loads `subunit.sh`. Each `test_*` function writes temporary command files under `$PREFIX`, runs `CLI_FORCE_INTERACTIVE=yes $SMBCLIENT ... < $tmpfile`, captures output, and validates status strings or file state. Key functions include `test_noninteractive_no_prompt`, `test_interactive_prompt_stdout`, `test_bad_symlink`, `test_good_symlink`, `test_read_only_dir`, `test_message`, `test_owner_only_file`, `test_msdfs_*`, `test_rename_archive_bit`, `test_ccache_access`, `test_auth_file`, `test_backup_privilege_list`, `test_bad_names`, `test_mangled_names`, `test_scopy`, `test_toplevel_stream`, `test_widelinks`, `test_streams_depot_delete`, `test_nosymlinks`, `test_local_symlinks`, `test_noperm_share_regression`, `test_deltree`, `test_setmode`, `test_utimes`, `test_rename_dotdot`, `test_volume`, `test_stream_directory_xattr`, `test_del_nedir`, `test_valid_users`, and `test_smbclient_minus_e_stderr`.

## State, Dependencies, Integration, and Risks
The harness mutates local share content under `$LOCAL_PATH`, temporary files under `$PREFIX`, winbind credential cache state via `wbinfo`, user privileges via `net sam rights grant/revoke`, stream storage, and log directories named `test_smbclient_s3_*`. Integration points include many selftest shares (`tmp`, `ro-tmp`, `valid-users-tmp`, `msdfs-share`, `badname-tmp`, `manglenames_share`, `widelinks_share`, `nosymlinks`, `local_symlinks`, `streams_xattr`, `valid_users*`, `invalid_users*`) plus environment users like `$DC_USERNAME`. Risks include heavy quoting with `eval`, several cleanup paths that run only on success, a likely typo in the SMB3 scopy command variable (`$PROTOOCL`), and tests that depend on exact localized output; `test_utimes` mitigates locale/timezone by forcing `LANG=C` and `TZ=UTC`. Test signals are a large set of subunit cases, exact `NT_STATUS_*` expectations, MD5 comparisons, and final `testok`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_s3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_tarmode.pl -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_tarmode.pl

## Purpose
This Perl test suite validates `smbclient` tar backup mode for archive creation, extraction, filtering, incremental/archive-bit handling, long paths, large files, regex/wildcard/list filters, and multiple tar operations in one session.

## Important APIs, Types, Functions, and Control Flow
The script uses `Archive::Tar`, `Digest::MD5`, `File::Path`, `File::Temp`, `Getopt::Long`, `Pod::Usage`, and `Term::ANSIColor`. Global options configure credentials, host/share/IP, local share path, target directory, smbclient binary, selected tests, debug/verbose/subunit, and cleanup. `@TESTS` maps descriptions to test functions. Runner functions `run_test`, `run_test_normal`, and `run_test_subunit` reset state before each test, execute the selected function, and report normal or subunit output. Core helpers are `smb_client_cmd`, `smb_client`, `smb_cmd`, `smb_tar`, `check_tar`, `check_remote`, `reset_remote`, `reset_tmp`, `reset_env`, `file_list`, `combine`, and `make_env`.

The embedded `File` package models local and remote test files. Constructors `File->new_remote` and `File->new_local` create files with random or provided content and cache MD5s. Methods expose `localpath`, `remotepath`, `remotedir`, `tarpath`, `set_attr`, `attr`, `attr_any`, `attr_str`, `set_time`, `md5`, and cleanup-on-destruction. Functions `File::list`, `File::tree`, and `File::walk` inspect remote share state via `smbclient ls`.

## State, Dependencies, Integration, and Risks
State is deliberately created under `$LOCALPATH/$DIR` and a temp directory `$TMP`; remote state is reset via `smbclient -c "deltree ./*"` and verified by scanning `$LOCALPATH`. The suite depends on `smbclient` tar options (`-Tc`, `-Tx`, `-Tca`, `-Tcg`, `-TcN`, `-TcI/X/F/r`, `tarmode full/inc/reset/nohidden/nosystem`), local tar compatibility through `Archive::Tar`, and MD5 consistency. Risks include command construction through backticks and `quotemeta`, destructive cleanup of the configured local path when `--clean` is used, assumptions that `$LOCALPATH` mirrors the share root, and some annotated BUG expectations in regex extraction helpers where current checks intentionally preserve known behavior. Test signals are exact archive membership and content hashes from `check_tar`, exact remote membership and hashes from `check_remote`, and subunit/normal aggregate error counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_tarmode.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_tarmode.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbclient_tarmode.sh

## Purpose
This shell test performs an end-to-end smoke test of `smbclient` tarmode creation and extraction using local random file corpora and server-side tar operations.

## Important APIs, Functions, and Control Flow
It accepts server, IP, credentials, local path, prefix, and `SMBCLIENT`, then wraps with `$VALGRIND`. Helpers include `have_command`, `create_test_data`, `validate_data`, `test_tarmode_creation`, and `test_tarmode_extraction`. Creation mode builds local data, runs `smbclient ... -c "tarmode full" -Tc "$PREFIX/tarmode.tar" "/smbclient_tar"`, extracts the tar locally, and diffs extracted content against the local corpus. Extraction mode builds a tar locally and uses `smbclient ... -Tx "$PREFIX/tarmode.tar"` to restore it to the share, then diffs share-backed data.

## State, Dependencies, Integration, and Risks
State spans `$LOCAL_PATH`, `$PREFIX/tarmode`, `$PREFIX/tarmode.tar`, and remote `smbclient_tar` under the `tarmode` share. It depends on `tar`, `dd`, optional `od`, `/dev/urandom`, and the server share. Cleanup is repeated but not trap-based, so interruption can leave tar data. Test signals are command success plus recursive `diff -r`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbclient_tarmode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbcquota.py -->
# sources/user-network-fs/samba/source3/script/tests/test_smbcquota.py

## Purpose
This Python blackbox test verifies `smbcquotas` list, get, and set behavior against a selftest quota directory backed by a simple quota database and helper script.

## Important APIs, Types, Functions, and Control Flow
Classes `test_env`, `user_info`, and `Quota` store environment, passwd user data, and quota rows. Helpers include `init_quota_db`, `load_quotas`, `get_quotas`, `get_users`, `smbcquota_output_to_userinfo`, `check_quota_limits`, and `get_uid`. Test classes `listtest`, `gettest`, and `settest` inherit `test_base` and implement `run(protocol)`. `main` parses `server domain username password envdir smbcquotas`, copies sibling `getset_quota.py` into the environment directory, builds `quotas.db` from local passwd users, then runs every subtest for `smb1` and `smb2`.

## State, Dependencies, Integration, and Risks
The test writes `quotas.db` and copies `getset_quota.py` into the supplied envdir. It depends on `getent passwd`, the `quotadir` share, the quota helper script, and `smbcquotas` output format. A code risk is that `listtest` prepares an `args` list with protocol but then invokes a hard-coded command that ignores the protocol-specific `-m smb2`, so SMB2 coverage may be weaker than intended. Test signals are parsed quota limits matching defaults or updated limits, with process exit 1 on first failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbcquota.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbcquota.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbcquota.sh

## Purpose
This shell wrapper runs the Python `test_smbcquota.py` suite under Samba selftest/subunit conventions.

## Important APIs, Functions, and Control Flow
It accepts `SERVER DOMAIN USERNAME PASSWORD LOCAL_PATH SMBCQUOTAS`, derives `ENVDIR=$(dirname $5)`, wraps `SMBCQUOTAS` with `$VALGRIND`, locates `test_smbcquota.py` next to itself, loads `subunit.sh`, and runs one `testit "smbcquotas"` command passing server, domain, credentials, envdir, and smbcquotas path.

## State, Dependencies, Integration, and Risks
The wrapper itself writes nothing, but delegates envdir mutation to the Python test. It depends on the Python script being executable and in the same directory. It increments `failed` without explicit initialization, relying on shell behavior. The test signal is the Python exit code reported as a single subunit test plus final `testok`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbcquota.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbd_error.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbd_error.sh

## Purpose
This test verifies `smbd` behavior when a VFS `chdir` operation fails or panics. It confirms that an injected panic is logged as a panic and that a normal error such as `ESTALE` does not cause a panic.

## Important APIs, Functions, and Control Flow
The script loads `subunit.sh`, skips if `SMBD_DONT_LOG_STDOUT=1`, computes an `error_inject.conf` next to `SMB_CONF_PATH`, and counts `PANIC` lines in `$SMBD_TEST_LOG`. It writes `error_inject:chdir = panic` plus empty `panic action`, expects `smbclient //$SERVER_IP/error_inject -c dir` to fail, verifies the panic count increased by one, then writes `error_inject:chdir = ESTALE`, expects `smbclient` failure, and verifies no additional panic.

## State, Dependencies, Integration, and Risks
State is the injected config file and server log observation. It depends on the error-inject VFS module, live smbd log path, `SMBD_DONT_LOG_STDOUT`, and selftest reloading the config. Cleanup removes the config after each phase, but interruption can leave fault injection enabled. Test signals are exact panic count deltas and expected command failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbd_error.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbd_no_krb5.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbd_no_krb5.sh

## Purpose
This test verifies server-side Kerberos disablement: Kerberos access works first, then fails after `gensec:gse_krb5=no`, while NTLM/SPNEGO downgrade still works.

## Important APIs, Functions, and Control Flow
The script accepts `smbclient SERVER USERNAME PASSWORD PREFIX`, resolves `samba4kinit` if available, loads `subunit.sh` and `common_test_fns.inc`, and sets `opt="--option=gensec:gse_krb5=yes -U..."`. It calls `test_smbclient` with `--use-kerberos=required`, writes `global_inject.conf` next to `SMB_CONF_PATH` with `gensec:gse_krb5=no`, verifies `--use-kerberos=required` fails, verifies `--use-kerberos=disabled` succeeds, then clears the config.

## State, Dependencies, Integration, and Risks
State is `global_inject.conf`, which directly affects the test server. It depends on configuration reload behavior and the `tmp` share. The most important risk is leaving the global injection file populated if the script is interrupted before the final clear. Test signals are success, expected failure, and downgrade success through common `test_smbclient` helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbd_no_krb5.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbget.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbget.sh

## Purpose
This Bash blackbox suite validates `smbget` download modes: guest access, explicit credentials, UPN/domain formats, credentials in SMB URLs and auth files, interactive password prompting, recursive downloads including empty directories, resume/update behavior, MSDFS paths, rate limiting, encryption, Kerberos ccache, and trusted-domain Kerberos.

## Important APIs, Functions, and Control Flow
The script accepts server/IP/domain/realm credentials, domain user credentials, workdir, and `SMBGET`. It loads `subunit.sh` and `common_test_fns.inc`, resolves `kinit` through `system_or_builddir_binary`, and uses `texpect` for interactive password entry. `create_test_data` writes random files and directories in `$WORKDIR`; each `test_*` clears the download area, invokes `$SMBGET` with a specific auth or transfer mode, and validates exit status plus `cmp` against source files. Kerberos tests create `KRB5CCNAME=FILE:$TMPDIR/smget_krb5ccache` and call `kerberos_kinit`.

## State, Dependencies, Integration, and Risks
State is local random test data in `$WORKDIR`, downloads in `$SELFTEST_TMPDIR`, temporary auth/expect files, empty directories, and Kerberos ccache files. Integration points include `smbget_guest`, `smbget`, `msdfs-share`, KDC, trust environment variables, and `texpect`. Risks include time-sensitive rate limiting using wall-clock seconds, residual files on failure, and environment-only trust variables. Test signals are exit codes, byte comparisons, directory-existence checks, and expected failure status for modified resume.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbget.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbpasswd.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbpasswd.sh

## Purpose
This test covers local SMB user creation, remote password change, and deletion via `smbpasswd` under the selftest uid wrapper.

## Important APIs, Functions, and Control Flow
It accepts `SERVER SERVER_IP USERNAME PASSWORD`, resolves `$BINDIR/texpect` and `$BINDIR/smbpasswd`, and uses test account `alice_smbpasswd`. `create_local_smb_user` writes a texpect script for new/retype password prompts and runs `smbpasswd -a` as uid/euid 0 using `UID_WRAPPER_INITIAL_RUID/EUID`. `test_smbpasswd` gets the user's uid, writes a change-password expect script, runs `smbpasswd -r $SERVER` as that uid, and greps for `Password changed for user`. `delete_local_smb_user` runs `smbpasswd -x`.

## State, Dependencies, Integration, and Risks
State is a local Unix/SMB test user and temporary expect scripts under `$PREFIX`. It depends on uid_wrapper, nss/getent visibility, prompt strings, and the server password-change path. Risks include leaving the test user if creation or password change fails before deletion and brittle prompt matching. Test signals are subunit cases for create/change/delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbpasswd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbspool.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbspool.sh

## Purpose
This test validates printing through `smbspool`, `smbspool_krb5_wrapper`, device URI handling, argv0 sanitization, virtual printer queue verification, and delete-on-close behavior.

## Important APIs, Functions, and Control Flow
The script accepts server/IP/credentials/target env, loads `subunit.sh` and `common_test_fns.inc`, and resolves `vlp`, `smbspool`, `smbspool_argv_wrapper`, `smbtorture3`, and `smbspool_krb5_wrapper`. Helper `test_smbspool_noargs` checks discovery output. `test_smbspool_authinforequired_none/unknown` cover wrapper environment behavior. `test_vlp_verify` inspects `$PREFIX/$TARGET_ENV/lockdir/vlp.tdb` using `vlp lpq`, validates a job id and spool file, then removes the job. `test_delete_on_close` runs `smbtorture3 DELETE-PRINT` and confirms the queue size does not change.

## State, Dependencies, Integration, and Risks
State includes the `vlp.tdb` virtual print queue and spool files under the target environment. It depends on printing testdata `example.ps`, `vlp` output fields, environment variables `DEVICE_URI` and `AUTH_INFO_REQUIRED`, and printer shares `print1`/`print4`. Risks include queue residue if verification/removal fails and field-position parsing with `awk`. Test signals combine command exit statuses, queue validation, job file existence, and queue count stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbspool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbspool_krb.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbspool_krb.sh

## Purpose
This test verifies Kerberos-backed `smbspool` printing when `AUTH_INFO_REQUIRED=negotiate`, and verifies that printing fails after Kerberos credentials are destroyed.

## Important APIs, Functions, and Control Flow
It accepts server, username, password, and realm, loads `subunit.sh` and `common_test_fns.inc`, resolves `smbspool`, `samba4kinit`, and `samba4kdestroy`, sets `KRB5CCNAME=FILE:$PREFIX/ccache_smbclient_kerberos`, and defines positive/negative helpers that run `smbspool smb://$SERVER/print3 ... example.ps` with `AUTH_INFO_REQUIRED=negotiate`. The script kinit's, runs the positive test, destroys the ccache, removes it, then expects the same print command to fail.

## State, Dependencies, Integration, and Risks
State is the Kerberos ccache and any print job created by the positive test. Dependencies are the KDC, print3 share, CUPS-style AuthInfoRequired behavior, and example PostScript file. Cleanup destroys/removes credentials but does not explicitly inspect print backend state. Test signals are positive zero exit and negative nonzero exit through subunit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbspool_krb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbstatus.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbstatus.sh

## Purpose
This test suite validates `smbstatus` plain, UID-resolved, sectioned, JSON, and JSON profile output while a real `smbclient` session holds an open file.

## Important APIs, Functions, and Control Flow
The script accepts server/IP/domain/user/password/userid/local path/prefix/client/status/config/protocol. Helpers create an smbclient command file that uploads and opens a file on `tmp`, runs `smbstatus` locally via `!UID_WRAPPER_INITIAL_RUID=0 UID_WRAPPER_INITIAL_EUID=0`, then closes and removes the file. `test_smbstatus` greps for numeric uid and `DENY_NONE`; `test_smbstatus_resolve_uids` is intended to check username output with `--resolve-uids`; `test_smbstatus_output` writes `--shares`, `--processes`, and `--locks` files; `test_smbstatus_json` validates JSON keys and selected fields with `jq`; `test_smbstatus_json_profile` validates profile JSON keys.

## State, Dependencies, Integration, and Risks
State is temporary command/status files under `$PREFIX` and a transient open remote file. Dependencies include `jq`, optional Jansson JSON support, uid_wrapper, exact `smbstatus` field names, and SMB signing/cipher output. The call labeled `resolve_uids` invokes `test_smbstatus` rather than `test_smbstatus_resolve_uids`, which appears to reduce coverage. Risks also include locale/output drift and cleanup after command failure. Test signals are absence of `NT_STATUS_`, grep checks, valid JSON parse, exact key lists, and expected field values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbstatus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbtorture_nocrash_s3.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbtorture_nocrash_s3.sh

## Purpose
This wrapper runs one `smbtorture` test and asserts that `smbd` does not log an additional panic during the run.

## Important APIs, Functions, and Control Flow
It accepts `TEST UNC USERNAME PASSWORD SMBTORTURE` plus extra args, loads `subunit.sh`, counts `PANIC` lines in `$SMBD_TEST_LOG`, runs `$VALGRIND $SMBTORTURE $unc -U"$username"%"$password" $ADDARGS $t`, recounts panics, then uses `testit "check_panic" test $panic_count_0 -eq $panic_count_1`.

## State, Dependencies, Integration, and Risks
State is only log observation, plus debug writes to `/tmp/look`. It depends on `$SMBD_TEST_LOG` and stable panic logging. Risks include shared log noise from other tests and `/tmp/look` collisions. Test signals are smbtorture exit status and unchanged panic count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbtorture_nocrash_s3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbtorture_s3.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_smbtorture_s3.sh

## Purpose
This minimal wrapper runs a specified `smbtorture` test against a UNC with supplied credentials and passes through additional torture arguments.

## Important APIs, Functions, and Control Flow
It validates `TEST UNC USERNAME PASSWORD SMBTORTURE`, loads `subunit.sh`, and performs one `testit "smbtorture"` command: `$VALGRIND $SMBTORTURE $unc -U"$username"%"$password" $ADDARGS $t`. It finalizes with `testok`.

## State, Dependencies, Integration, and Risks
The script creates no local state. It depends entirely on the requested smbtorture test, UNC, credentials, and extra args supplied by the selftest harness. Risks are low in the wrapper but high in caller configuration: no additional output validation is done beyond process status. The test signal is the smbtorture exit code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_smbtorture_s3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_stream_dir_rename.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_stream_dir_rename.sh

## Purpose
This regression test covers Bug 15314: after requesting an invalid stream path below a directory, the directory should still be renameable and not fail with `NT_STATUS_ACCESS_DENIED`.

## Important APIs, Functions, and Control Flow
It accepts server, credentials, prefix, and `SMBCLIENT`, suppresses deprecated warnings, and defines `test_stream_xattr_rename`. The helper writes smbclient commands against `streams_xattr_nostrict`: delete any old directories, create `stream_xattr_test`, upload a file, attempt `get stream_xattr_test/file.txt:abcf`, rename the directory to `stream_xattr_test1`, cleanup, and quit. It fails if the command exits nonzero or output contains `NT_STATUS_ACCESS_DENIED`.

## State, Dependencies, Integration, and Risks
State is a temporary command file and remote directories/files on the streams share. It depends on stream syntax, `streams_xattr_nostrict`, and exact access-denied output. Cleanup is embedded in the command script, so early connection failure can leave remote state. Test signal is successful rename after invalid stream access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_stream_dir_rename.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_substitutions.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_substitutions.sh

## Purpose
This script tests Samba configuration substitution expansion in share names, valid-user expressions, include files, and RPC share enumeration.

## Important APIs, Functions, and Control Flow
It accepts server, credentials, and prefix, resolves `smbclient` and `rpcclient` from `$BINDIR`, and loads `subunit.sh` plus `common_test_fns.inc`. It runs `test_smbclient` against shares `sub_dug`, `sub_dug2`, `sub_valid_users`, `sub_valid_users_domain`, and `sub_valid_users_group`. It then tests include-substitution share `${USERNAME}_share` with the real user, expects failure with `$DC_USERNAME`, and uses `testit_grep_count` around `rpcclient ... -c netshareenum` to verify share enumeration visibility.

## State, Dependencies, Integration, and Risks
No state is created. Dependencies include configured substitution-heavy shares, `$DC_USERNAME/$DC_PASSWORD`, and RPC share enumeration. A spelling typo in a test name (`Netative`) is harmless. Risks are output-string coupling for `netname:` and group/domain environment drift. Signals are smbclient success/failure and exact share count in rpcclient output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_substitutions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_success.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_success.sh

## Purpose
This is a trivial blackbox harness sanity test that should always succeed.

## Important APIs, Functions, and Control Flow
It loads `subunit.sh`, initializes `failed=0`, defines `test_success` as `true`, runs it through `testit "success"`, and calls `testok`.

## State, Dependencies, Integration, and Risks
It has no state or external Samba dependency beyond the subunit helper file. Its purpose is likely validating test harness plumbing rather than product behavior. A failure indicates shell/subunit environment breakage, not SMB behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_success.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_dosmode.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_symlink_dosmode.sh

## Purpose
This test verifies that listing a local symlink through `smbclient` reports the expected DOS mode `N`.

## Important APIs, Functions, and Control Flow
It accepts server/IP/credentials/local path/prefix/smbclient, suppresses deprecated warnings, prepares `$LOCAL_PATH/testdir/dir/symlink` pointing to `../file`, then `test_symlink_dosmode` writes `ls testdir/dir/*` and runs `smbclient //$SERVER/local_symlinks -I$SERVER_IP`. It extracts the mode field from the symlink listing using `awk '/symlink/ {print $2}'` and compares it with `N`.

## State, Dependencies, Integration, and Risks
State is a local fixture under the share path, removed after the test. It depends on Unix symlink support, the `local_symlinks` share, and stable listing columns. Risks include cleanup failure if permissions or command errors intervene. Test signal is exact parsed mode plus successful smbclient command.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_dosmode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_rename_smb1_posix.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_symlink_rename_smb1_posix.sh

## Purpose
This test checks SMB1 POSIX rename semantics when the target path is an existing symlink. All attempted renames from a real file to symlink targets should fail with `NT_STATUS_OBJECT_NAME_COLLISION`.

## Important APIs, Functions, and Control Flow
The script builds local files, directories, missing targets, and no-permission targets both outside and inside the share. `do_cleanup` removes fixtures and restores permissions. `smbclient_expect_error` writes a command file with `posix`, the requested command, and `quit`, then runs `smbclient //$SERVER/local_symlinks -mNT1` and greps for the expected status. `test_symlink_rename_SMB1_posix` iterates rename cases for symlinks to nonexistent, outside-share, no-permission, and inside no-permission objects.

## State, Dependencies, Integration, and Risks
State includes share-local symlinks and `/tmp/symlink_rename_*.$$` outside-share fixtures. It depends on SMB1 POSIX extensions, Unix symlinks, and permission behavior. Risks include use of `/tmp` rather than `$TMPDIR` and permission cleanup requirements for chmod 0 directories. Test signals are exact `NT_STATUS_OBJECT_NAME_COLLISION` matches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_rename_smb1_posix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1.sh

## Purpose
This test validates SMB1 non-POSIX error mappings when traversing, listing, deleting, or renaming through symlinks to nonexistent, outside-share, and no-permission targets.

## Important APIs, Functions, and Control Flow
It creates a matrix of symlinks in the share root and under `emptydir`, plus no-permission file/directory objects inside the share. `smbclient_expect_error` runs a generated command file against `//$SERVER/local_symlinks -mNT1` and checks either absence of `NT_STATUS_` for `NT_STATUS_OK` or presence of an expected error. `test_symlink_traversal_SMB1_onename` applies `get`, `ls`, `del`, and optional `rename` checks for one symlink name. `test_symlink_traversal_SMB1` calls it for multiple symlink categories and then checks no-permission direct and symlinked paths.

## State, Dependencies, Integration, and Risks
State is the generated filesystem matrix under `$LOCAL_PATH` and outside fixtures under `${TMPDIR:-/tmp}`. It depends on `follow symlinks` behavior for the `local_symlinks` share and SMB1 wildcard semantics. Risks are exact error-code coupling and chmod cleanup on no-permission directories. Signals are many precise `NT_STATUS_*` assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1_posix.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1_posix.sh

## Purpose
This companion to the SMB1 traversal test verifies SMB1 POSIX-specific symlink behavior, especially that symlinks can be listed/stat'ed and wildcard `*` is treated as a valid path component rather than only a search pattern.

## Important APIs, Functions, and Control Flow
The setup and cleanup matrix mirrors `test_symlink_traversal_smb1.sh`. `smbclient_expect_error` adds `posix` before each command and forces `-mNT1`. `test_symlink_traversal_SMB1_posix_onename` validates `get`, `ls`, `stat`, `del`, and optional rename behavior for each symlink category with POSIX-specific expected statuses. The main test covers nonexistent, outside-share, no-permission, and inside-share no-permission paths.

## State, Dependencies, Integration, and Risks
State is local symlink and permission fixtures under the share plus temporary outside targets. It depends on SMB1 POSIX extensions being enabled and `smbclient` POSIX command mode. Risks include differences between POSIX and non-POSIX error mappings causing brittle expectations, and fixture cleanup requiring permission restoration. Signals are exact status checks including `NT_STATUS_OK` for list/stat paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb1_posix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb2.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb2.sh

## Purpose
This larger symlink traversal regression test verifies SMB2 behavior for symlink traversal, wildcard paths, path component error precedence, no-permission directories, and an attempted symlink escape toward `/etc/passwd`.

## Important APIs, Functions, and Control Flow
The setup creates root and `emptydir` fixtures: regular files, directories with subfiles/subdirs, symlinks to dot, files, dirs, nonexistent and outside-share targets, no-permission objects, and `x` pointing outside the share. `smbclient_expect_error` runs commands against `//$SERVER/local_symlinks` without forcing NT1. `test_symlink_traversal_SMB2_onename` covers `get`, `ls`, `del`, and rename cases for each symlink name. `test_symlink_traversal_SMB2` adds detailed checks for ordinary files/directories, symlinks to those objects, nonexisting multi-component paths, access-denied paths, and `get x/passwd`.

## State, Dependencies, Integration, and Risks
State is a broad local fixture tree and outside temporary targets. It depends on SMB2 symlink semantics, share configuration with `follow symlinks = yes`, and exact server-side path resolution precedence. The security-sensitive signal is `x/passwd` returning `NT_STATUS_OBJECT_PATH_NOT_FOUND`. Risks are high brittleness from many exact error strings and cleanup needing chmod restoration for denied directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_symlink_traversal_smb2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_testparm_s3.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_testparm_s3.sh

## Purpose
This test validates Samba 3 `testparm` parsing and logic for special handlers, macro expansions, deprecated-option warnings, share `copy`, and `sync machine password to keytab` grammar.

## Important APIs, Functions, and Control Flow
It accepts `LOCAL_PATH`, writes temporary configs to `$LOCAL_PATH/smb.conf.tmp`, defines `TESTPARM` with `--suppress-prompt --skip-logic-checks`, and `TESTPARM_LOGIC` without skip-logic. Helpers write one-off configs: `test_include_expand_macro`, `test_one_global_option`, `test_one_global_option_logic`, `test_copy`, `test_testparm_deprecated`, and `test_testparm_deprecated_suppress`. The main flow tests valid and invalid `name resolve order`, core global options, include expansions for macro letters `U G D I i L N M R T a d h m v w V`, share copy, deprecated warning emission/suppression, and a positive/negative suite of `sync machine password to keytab` forms.

## State, Dependencies, Integration, and Risks
State is a temporary smb.conf removed at the end. It depends on `testparm`, `subunit.sh`, `testit_grep`, and exact warning text. Risks include output wording drift and no trap cleanup if interrupted. Test signals are command success/failure, expected failures for invalid config, and grep validation for deprecation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_testparm_s3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_timestamps.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_timestamps.sh

## Purpose
This test verifies `smbclient allinfo` reports nontrivial timestamps correctly, including epoch zero, negative epoch seconds, and a pre-1970 date.

## Important APIs, Functions, and Control Flow
It accepts server IP, credentials, prefix, and `SMBCLIENT`, exports `TZ=GMT`, and defines `setup_testfiles`, `remove_testfiles`, and `test_time`. Setup uses `touch -d "$(date --date=@0)"`, `@-1`, `@-2`, and `touch -t 196801010000`. `test_time` calls `smbclient //$SERVER/tmp -c "allinfo $file"` and verifies `access_time` and `write_time` lines contain the expected formatted string, ignoring synthesized `create_time`.

## State, Dependencies, Integration, and Risks
State is four files under `$PREFIX` exposed by the `tmp` share, removed at the end. It depends on GNU `date --date=@...`, filesystem support for negative timestamps, timezone formatting, and exact `smbclient allinfo` strings. Risks include platform-specific date formatting and cleanup not running after early failure. Test signals are exact timestamp greps for access and write times.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_timestamps.sh -->
