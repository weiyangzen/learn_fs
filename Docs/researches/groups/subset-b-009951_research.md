# Grouped Research: subset-b-009951

This grouped report covers Samba source files from `source4/selftest`, `source4/setup`, and `source4/smb_server`. Each file section preserves the original source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/tests.py -->
# Research: sources/user-network-fs/samba/source4/selftest/tests.py

Purpose: this Python script is the Samba 4 selftest manifest generator. It emits `-- TEST --` style suite declarations consumed by `selftest.pl`, using helpers from `selftesthelpers` to register smbtorture, Python, Perl, blackbox, and local binary tests across many selftest environments.

Important APIs and functions: `plansmbtorture4testsuite()` wraps the generic helper and chooses the test target `samba4` or `samba4-ntvfs` based on the environment. `planoldpythontestsuite()` builds an older `subunitrun` command line with optional `PYTHONPATH`, environment assignments, `$LISTOPT`, and `$LOADLIST`. The rest of the file is declarative control flow built around `plantestsuite`, `plantestsuite_loadlist`, `planpythontestsuite`, `planperltestsuite`, `skiptestsuite`, `smbtorture4_testsuites`, `binpath`, and `read_config_h`.

Control flow: it starts by registering LDAP/LDAPS/LDAPI coverage, then large RPC matrices by transport and bind option, DFS/NET/SMB/NTVFS/libsmbclient suites, local and DNS tests, extensive blackbox command tests, winbind/NSS/ntlm auth tests, DSDB/LDAP/schema/DRS suites, KDC and Kerberos suites, cmocka binaries, process-limit tests, and finally demote/dbcheck suites that must stay last. Feature flags from `config.h` gate Heimdal-specific tests, FIPS tests, cluster tests, and systemd userdb tests. The script intentionally enumerates tests that may be skipped or known-failed elsewhere, so it is a registration source rather than a pass-list.

State and persistence: it does not persist state itself, but generated commands mutate selftest environments heavily through Samba provisioning, joins, DRS replication, password changes, backup/restore, and database checks. Environment names such as `ad_dc`, `ad_dc_ntvfs`, `fl2008r2dc`, `rodc`, `vampire_dc`, and `schema_pair_dc` encode required topology and isolation.

Dependencies and integration: it depends on built binaries (`smbtorture`, `smbclient`, `nmblookup`, cmocka test binaries), Python modules under `python/samba/tests`, scripts under `testprogs/blackbox`, DSDB tests, nsswitch tests, and selftest environment variables like `$SERVER`, `$USERNAME`, `$PASSWORD`, `$PREFIX`, `$REALM`, and `$DOMAIN`. It integrates with `selftest.pl`, skip/knownfail files, and load-list capable runners.

Risks and test signals: ordering is a major risk because demote and dbcheck intentionally run last, while some DRS and KDC tests pollute environments. Matrix expansion can create very large runtime cost. Many commands depend on build-time feature probes and on exact environment capabilities. Strong signals are successful generation, expected skips/knownfails, load-list execution, and final database checks for every long-lived DC environment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/tests_win.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/tests_win.sh

Purpose: entry point for legacy Windows VM selftests. It refuses to run unless executed as root, without socket wrapper, and with a readable `WINTESTCONF`.

Important behavior: after validation it exports `WINTEST_DIR=$SRCDIR/selftest/win`, preserves `TMPDIR` and `NETBIOSNAME`, sources the configured Windows test file, and delegates to `$SRCDIR/selftest/test_win.sh`.

State and dependencies: state comes entirely from the sourced config and the remote VM. Dependencies include root privileges, real networking, `WINTESTCONF`, and scripts under `selftest/win`. It integrates with the broader selftest runner as the gate before Windows-oriented tests are allowed to touch the VMware-backed host.

Risks and test signals: unquoted variable tests such as `[ ! $WINTESTCONF ]` are fragile if values contain whitespace or shell metacharacters. It deliberately blocks socket wrapper because Windows VMs require real network access. A useful signal is early, explicit failure before any VM mutation when prerequisites are absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/tests_win.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/tests_win2k3_dc.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/tests_win2k3_dc.sh

Purpose: registers Windows Server 2003 DC interoperability test groups with Samba selftest.

Control flow: it validates `WINTESTCONF`, sources `selftest/test_functions.sh`, exports `SRCDIR`, defines four groups (`RPC-DRSUAPI`, `RPC-SPOOLSS`, `ncacn_np`, `ncacn_ip_tcp`), and calls `testit $name rpc $SRCDIR/selftest/win/wintest_2k3_dc.sh $name` for each group.

State and dependencies: it depends on the shared selftest shell helper, `WINTESTCONF`, and `wintest_2k3_dc.sh` for the actual VM discovery and smbtorture execution. It does not persist local state; each child test may revert the DC snapshot on error.

Risks and test signals: the script assumes execution from a tree layout where `selftest/test_functions.sh` is resolvable. It provides a coarse group-level signal to selftest while detailed failures come from the child script.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/tests_win2k3_dc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/VMHost.pm -->
# Research: sources/user-network-fs/samba/source4/selftest/win/VMHost.pm

Purpose: Perl package wrapping VMware Server VMPerl and VIX APIs for Samba Windows selftests. It abstracts VM host connection, guest login, snapshot operations, file copy, command execution, and guest IP discovery.

Important APIs: `host_connect()` connects through VMPerl and VIX, powers on the guest via `start_guest()`, opens the VM, and logs into the guest OS. `host_disconnect()` and `host_reconnect()` reset handles. `create_snapshot()` creates a VIX snapshot and reconnects. `revert_snapshot()` powers off the guest, relying on VMware "Revert to Snapshot" behavior on power-on. `copy_to_guest()` creates a destination directory and copies either one file or flat directory contents using `copy_files_to_guest()`. `run_on_guest()` invokes `VMRunProgramInGuest()`. `get_guest_ip()` reads VMTools guest info key `ip`. `error()` returns and clears the package-level error state.

State and persistence: connection handles and credentials are package lexicals, so one process effectively manages one active VM context. Snapshot and power-state changes persist in VMware, while file copies and guest commands mutate the Windows guest. The destructor disconnects the host and releases handles.

Dependencies and integration: depends on `VMware::VmPerl`, `VMware::Vix::Simple`, and VMware Tools in the guest. It is used by `vm_get_ip.pl` and `vm_load_snapshot.pl`, and indirectly by Windows selftest shell scripts.

Risks and test signals: error state is global and reset on read, which can hide earlier failures if callers are careless. `revert_snapshot()` relies on external VM configuration instead of VIX snapshot selection. `copy_to_guest()` only copies flat directories and has weak path validation. Strong signals are successful host connection, nonempty guest IP, and clean VIX return codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/VMHost.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/test_win.conf -->
# Research: sources/user-network-fs/samba/source4/selftest/win/test_win.conf

Purpose: sample shell configuration for Windows selftests. It defines Perl library lookup, expect prompt behavior, Windows 2003 DC credentials/topology, smbtorture Windows host credentials, share paths, timeout, local Samba share settings, VMX paths, guest administrator credentials, and optional VMware host credentials.

State and dependencies: every value is exported into child shell, Perl, expect, and smbtorture processes. It bridges Samba selftest variables such as `NETBIOSNAME` to the Windows VM setup and binds tests to VMware inventory paths.

Integration points: consumed by `tests_win.sh`, `wintest_*` scripts, and the VM helper Perl scripts. The remote share path, backup hosts filename, drive letter, local hostname/IP, and credentials drive expect scripts not included in this item.

Risks and test signals: the file contains plaintext credentials and machine-specific VM paths, so it is suitable as local build-farm config rather than portable test data. Wrong host IP or VMX path causes setup failures before smbtorture can provide protocol signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/test_win.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/vm_get_ip.pl -->
# Research: sources/user-network-fs/samba/source4/selftest/win/vm_get_ip.pl

Purpose: command-line Perl helper that connects to a VMware VM and prints the guest IP address.

Control flow: it reads the VMX path from the environment variable named by `ARGV[0]`, reads optional host connection parameters and guest administrator credentials, creates a `VMHost` object, calls `host_connect()`, then `get_guest_ip()`, printing the result.

State and dependencies: depends on `PERLLIB` or `-I` pointing to `VMHost.pm`, VMware host connectivity, guest credentials, and VMware Tools reporting the IP. It mutates VM power state because `host_connect()` powers on a stopped guest.

Risks and test signals: missing or empty environment variables produce VMware connection errors rather than local validation errors. A nonempty printed IP is the main signal consumed by `wintest_2k3_dc.sh`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/vm_get_ip.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/vm_load_snapshot.pl -->
# Research: sources/user-network-fs/samba/source4/selftest/win/vm_load_snapshot.pl

Purpose: Perl helper to connect to the configured VMware VM and revert it to its snapshot state.

Control flow: it reads `VM_CFG_PATH`, host connection variables, and guest admin credentials, connects via `VMHost->host_connect()`, then calls `revert_snapshot()`. `check_error()` terminates with a diagnostic if either operation records an error in `VMHost`.

State and dependencies: it changes persistent VM state by powering off and reconnecting to trigger snapshot restoration. It relies on the same VMware APIs and guest credentials as `vm_get_ip.pl`.

Risks and test signals: it performs a full VM connection before reverting, which can fail if the guest is already unhealthy. The test signal is process exit code; no subunit formatting is emitted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/vm_load_snapshot.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_2k3_dc.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_2k3_dc.sh

Purpose: executes smbtorture RPC groups against a Windows Server 2003 domain controller VM.

Important functions: `on_error()` increments `all_errs` and restores the DC snapshot. `drsuapi_tests()` runs DRSUAPI over `ncacn_ip_tcp` with `seal` and `seal,bigendian`. `spoolss_tests()` runs SPOOLSS over named pipes. `ncacn_ip_tcp_tests()` and `ncacn_np_tests()` iterate bind options over selected RPC suites.

Control flow and state: it sources the Windows config and shared functions, discovers the DC IP with `vm_get_ip.pl WIN2K3_DC_VM_CFG_PATH`, builds `OPTIONS` from DC credentials, dispatches on `TESTGROUP`, and exits with accumulated error count. Snapshot restore is the persistence recovery mechanism.

Dependencies and risks: depends on `bin/smbtorture`, VMware IP discovery, real network access, and Windows DC credentials. The bind options include a likely typo `ntml,seal` that may reduce intended NTLM coverage. Every failure restores the snapshot, which is safe but expensive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_2k3_dc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_base.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_base.sh

Purpose: runs a small set of Samba `BASE-*` smbtorture tests against a Windows server share created by expect setup scripts.

Control flow: it sources selftest and Windows helpers, validates `SERVER USERNAME PASSWORD DOMAIN`, exports `SMBTORTURE_REMOTE_HOST`, then loops over `BASE-UNLINK`, `BASE-ATTR`, `BASE-DELETE`, `BASE-TCON`, `BASE-OPEN`, and `BASE-CHKPATH`. Each test performs `setup_share_test`, invokes `$SMBTORTURE_BIN_PATH` against `//$server/$SMBTORTURE_REMOTE_SHARE_NAME`, then runs `remove_share_test` or restores the snapshot on setup/test/cleanup failure.

State and dependencies: expect scripts create and remove Windows shares/directories; VMware snapshot restore is the recovery path. Dependencies include `WINTESTCONF`, expect, smbtorture, Windows credentials, and a configured VM.

Risks and test signals: the local `err` variable is not reset inside the loop after a failure, so later tests may be treated as failed even if smbtorture succeeds. Exit code is accumulated `all_errs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_base.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_client.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_client.sh

Purpose: runs an expect-driven Windows client against a Samba server share.

Control flow: it sources selftest and Windows helper scripts, sources `WINTESTCONF`, exports `SMBTORTURE_REMOTE_HOST` from the first argument, concatenates `common.exp` and `wintest_client.exp` into `$TMPDIR/client_test.exp`, runs `expect`, restores the snapshot on failure, removes the temporary expect script, and exits with `all_errs`.

State and dependencies: remote Windows drive mappings, file creation, and Samba share interaction happen inside expect scripts. It depends on `TMPDIR`, `WINTEST_DIR`, expect, and VM snapshot tooling.

Risks and test signals: `all_errs` is not initialized before arithmetic and `[ $all_errs ] >0` uses shell redirection semantics rather than a numeric comparison, which is fragile. The main signal is expect exit status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_client.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_functions.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_functions.sh

Purpose: shared shell functions for Windows VM setup, cleanup, and snapshot recovery.

Important functions: `setup_share_test()` builds a temporary expect script from `common.exp` and `wintest_setup.exp`, runs it, stores status in global `err_rtn`, and removes the temp file. `remove_share_test()` does the same for `wintest_remove.exp`. `restore_snapshot()` prints a failure message and invokes `vmrun revertToSnapshot`, either locally or with `-h/-P/-u/-p` host credentials.

State and dependencies: global variables from `test_win.conf` drive paths, credentials, and VMX location. The functions mutate the Windows VM by creating/removing shares and reverting snapshots.

Risks and test signals: temporary filenames are fixed per `$TMPDIR`, so concurrent tests can collide. Arguments are mostly unquoted. `restore_snapshot()` reports success/failure but does not return a hard failure to callers beyond `err_rtn`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_net.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_net.sh

Purpose: runs NET-API smbtorture suites against a Windows server over selected DCE/RPC transports.

Control flow: after sourcing configuration and validating credentials, it defines test lists for `ncalrpc`, `ncacn_np`, and `ncacn_ip_tcp`, loops over bind options `seal,padcheck` and `bigendian`, selects the right test list by transport, and invokes `$SMBTORTURE_BIN_PATH -U user%password -W domain transport:server[opts] TEST`.

State and dependencies: no local persistent state; failures call `restore_snapshot` on the configured VM. Depends on smbtorture, real network access, and Windows credentials.

Risks and test signals: failing tests are documented in comments and excluded from lists, so this is a regression suite for known-working NET-API paths. Snapshot restore on every failure can mask independent failures but preserves VM cleanliness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_net.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_raw.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_raw.sh

Purpose: runs raw SMB file operation smbtorture tests against a Windows server share.

Control flow: it validates server credentials, exports `SMBTORTURE_REMOTE_HOST`, loops over RAW tests such as qfileinfo, sfileinfo, mkdir, seek, open, write, unlink, read, close, ioctl, rename, EAs, and streams. For each test it creates the Windows share via expect, runs smbtorture against `//$server/$SMBTORTURE_REMOTE_SHARE_NAME`, then cleans up or restores snapshot.

State and dependencies: setup and cleanup mutate the Windows VM filesystem/share configuration. Dependencies mirror `wintest_base.sh`.

Risks and test signals: `err` is not reset per test after failure. `RAW-QFSINFO` is deliberately excluded as failing. Exit status is the accumulated error count after any snapshot recovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_raw.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_rpc.sh -->
# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_rpc.sh

Purpose: runs selected RPC smbtorture suites against a Windows server over local RPC, named pipes, and TCP RPC transports.

Control flow: it validates arguments, defines known-working tests per transport, loops over bind options `seal,padcheck` and `bigendian`, dispatches by transport, and invokes smbtorture with credentials and domain. Failures increment `all_errs` and restore the configured VM snapshot.

State and dependencies: it does not create shares, but RPC tests may change remote server state depending on the smbtorture suite. It depends on the Windows config, smbtorture, and snapshot helper.

Risks and test signals: comments document omitted failing tests, making this a curated interoperability subset. Snapshot restore after any RPC failure is conservative but can be costly and may obscure which subtest dirtied the VM.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/win/wintest_rpc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/krb5.conf -->
# Research: sources/user-network-fs/samba/source4/setup/krb5.conf

Purpose: Kerberos configuration template emitted during Samba AD provisioning.

Content and integration: it sets `default_realm` from `${REALM}`, disables DNS realm lookup, enables DNS KDC lookup, maps the realm to `${DNSDOMAIN}`, and maps `${HOSTNAME}` to `${REALM}` in `[domain_realm]`.

State and dependencies: placeholders are substituted by Samba setup/provisioning code before installation. The resulting file affects Kerberos client behavior for Samba tools and test environments.

Risks and test signals: correctness depends on consistent realm, DNS domain, and hostname substitutions. Because KDC lookup is DNS-driven, DNS setup failures can appear as Kerberos failures. Signals include successful kinit/samba-tool Kerberos tests registered by `tests.py`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/named.conf -->
# Research: sources/user-network-fs/samba/source4/setup/named.conf

Purpose: BIND named configuration template for Samba AD DNS zones.

Content and integration: it defines a master forward zone for `${DNSDOMAIN}.`, stores data in `${ZONE_FILE}`, includes dynamic update policy from `${NAMED_CONF_UPDATE}`, and sets `check-names ignore` to allow AD-specific records such as `_msdcs`. It also documents an optional reverse zone and GSS-TSIG update policy considerations.

State and dependencies: placeholders are filled by provisioning. Runtime DNS updates depend on generated update-policy content and BIND support for secure updates.

Risks and test signals: wrong include paths or zone filenames break DNS startup. Removing update policies disables secure dynamic updates. Test signals come from DNS-related selftests and samba-tool DNS update tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/named.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_group.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_group.sh

Purpose: blackbox coverage for `samba-tool group` and related user/contact membership commands against a freshly provisioned DC.

Control flow and APIs: it provisions `simple-dc`, creates users, verifies `user getgroups`, creates six groups across Domain/Global/Universal and Security/Distribution combinations, adds/removes users, tests primary group rules, creates contacts, tests `--object-types`, `--member-dn`, duplicate CN handling in OUs, `--member-base-dn`, group deletion, group listing, and listmembers. It uses subunit helpers `testit`, `testit_grep`, and expected-failure helpers.

State and persistence: it creates and deletes a target directory and mutates the provisioned `sam.ldb` through `samba-tool`.

Dependencies and risks: depends on `$PYTHON`, `$BINDIR/samba-tool`, NTVFS provisioning, and exact DN layout under `DC=foo,DC=example,DC=com`. Shell quoting limitations are noted in comments. Strong signals are expected failure matching for invalid primary group and ambiguous object lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_group.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_newuser.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_newuser.sh

Purpose: blackbox test for `samba-tool user create`, `enable`, `setpassword`, and `setexpiry`.

Control flow: it provisions a simple DC, builds `CONFIG` for that target, creates `NewUser` with many profile/contact attributes and `NewUser1` with `--use-username-as-cn`, enables both accounts, changes both passwords, sets no-expiry, and then sets a seven-day expiry.

State and dependencies: it creates `$PREFIX/simple-dc` and mutates its `sam.ldb`. It depends on subunit helpers, `$PYTHON`, `$BINDIR/samba-tool`, and NTVFS provisioning.

Risks and test signals: assertions are command-exit based rather than LDAP attribute verification, so regressions that accept but mishandle attributes may escape. It still provides useful CLI parsing and account lifecycle smoke coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_newuser.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_provision.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_provision.sh

Purpose: blackbox coverage for `samba-tool domain provision` variants and base schema selection.

Control flow: it verifies provisioning over existing empty/whitespace `smb.conf`, explicit GUID/SID provisioning, DC provisions with base schemas 2008_R2 through 2019, member and standalone roles, blank DC provisioning, and reprovision of an existing target. `check_baseschema()` uses `ldbsearch` on each `sam.ldb` to verify schema `objectVersion` constants.

State and dependencies: it creates many target directories under the supplied prefix and removes them at the end. It depends on build or system `ldbsearch`, `$PYTHON`, `$BINDIR/samba-tool`, and stable schema version numbers.

Risks and test signals: failures may leave large provision directories if interrupted. Schema validation is a strong signal because it inspects the resulting database rather than just command status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_provision.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_s3upgrade.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_s3upgrade.sh

Purpose: blackbox tests for classic Samba 3 to Samba 4 upgrade paths.

Control flow: it copies `testdata/samba3`, writes three temporary Samba 3 configs, runs `samba-tool domain classicupgrade` for member and DC-like configurations, tests upgrade with `--testparm`, and verifies local/domain SIDs using `net getlocalsid` and `net getdomainsid`. It exercises both dbdir-driven and testparm-driven discovery.

State and dependencies: it writes temporary `smb*.conf` files and upgraded S4 target directories under `$PREFIX/samba3-upgrade`, then removes them. Dependencies include `samba-tool`, `net`, `testparm`, testdata, and passdb/WINS files.

Risks and test signals: it uses generated configs with paths embedded from `$PREFIX`, so whitespace in paths can be risky. SID checks are strong signals that upgrade preserved domain identity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_s3upgrade.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_setpassword.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_setpassword.sh

Purpose: blackbox password-management coverage for `samba-tool user setpassword` and domain password settings.

Control flow: it provisions a simple DC, creates `testuser`, sets the password normally, sets it with `--must-change-at-next-login`, repeats with a non-ASCII password, then resets domain password settings to defaults with plaintext storage enabled.

State and dependencies: it mutates a provisioned test database under `$PREFIX/simple-dc`. Dependencies include `samba-tool`, Python, and subunit helpers.

Risks and test signals: it primarily checks CLI success, not subsequent authentication. The non-ASCII password is an important encoding signal; environment locale problems could affect this script.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_setpassword.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_spn.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_spn.sh

Purpose: blackbox coverage for `samba-tool spn add` and `spn delete` against an existing provisioned DC.

Control flow: it builds `CONFIG` from the supplied prefix, adds and deletes `FOO/bar` for `Administrator`, verifies duplicate SPN add fails for `Guest`, verifies protected or wrong-user deletion fails, adds/deletes the SPN for `Guest`, and verifies deleting a missing SPN or adding for a nonexistent user fails.

State and dependencies: it mutates servicePrincipalName attributes in the target database. It depends on a provisioned `$PREFIX/etc/smb.conf`.

Risks and test signals: because it runs against an existing environment, preexisting `FOO/bar` values would affect results. Expected-failure checks are strong negative-path signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_spn.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_start_backup.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_start_backup.sh

Purpose: verifies Samba refuses to start directly from a database marked as a backup.

Control flow: `do_provision()` creates a DC under `$PREFIX/start-backup`. `add_backup_marker()` uses `ldbmodify` to add `backupDate` to `@SAMBA_DSDB`. `start_backup()` runs `samba --maximum-runtime=5 -i --debug-stdout`, expects a nonzero exit, and greps output for `failed to start: Database is a backup`.

State and dependencies: it creates and removes a provisioned database. It depends on `samba`, `samba-tool`, `ldbmodify`, and common blackbox helper binary lookup.

Risks and test signals: the five-second maximum runtime prevents hangs if the bad condition regresses. The output grep ensures the failure reason is the backup marker, not an unrelated startup error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_start_backup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_supported_features.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_supported_features.sh

Purpose: tests Samba database feature gating via `compatibleFeatures` and `requiredFeatures` on `@SAMBA_DSDB`.

Control flow: it provisions a DC, adds a fake compatible feature with `ldbmodify`, verifies it is not returned by `ldbsearch`, verifies a normal object can still be found, then adds a fake required feature and expects subsequent `ldbsearch` to fail.

State and dependencies: directly mutates `sam.ldb` using build or system `ldbmodify`, `ldbdel`, and `ldbsearch`. It removes the database path at the end.

Risks and test signals: direct LDB writes bypass normal tooling, which is intentional for feature-flag simulation. Expected search failure after `requiredFeatures` is the core signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_supported_features.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_upgradeprovision.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_upgradeprovision.sh

Purpose: blackbox regression test for `samba_upgradeprovision`.

Control flow: it provisions reference, normal-upgrade, and full-upgrade DC databases from the same 2008_R2 base schema. It runs `samba_upgradeprovision --debugchange` and `--full --debugchange`, then compares upgraded databases to the reference with `samba-tool ldapcmp`, both normal and security-descriptor modes, skipping missing DNs and filtering `servicePrincipalName`.

State and dependencies: creates three provision directories and removes them. Depends on `samba-tool`, `samba_upgradeprovision`, and database comparison semantics.

Risks and test signals: the test checks a null-upgrade scenario, so it is strongest for idempotency and template drift, not for real old production databases. LDAP compare results are strong structural signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/blackbox_upgradeprovision.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/provision_fileperms.sh -->
# Research: sources/user-network-fs/samba/source4/setup/tests/provision_fileperms.sh

Purpose: validates private-file permissions after provisioning despite selftest's default zero umask.

Control flow: it saves the current umask, sets `0022`, writes a small fake-ACL `smb.conf`, provisions a basic DC, then `check_private_file_perms()` iterates regular files under `private`, uses `stat -c %A`, strips owner bits, and fails if group/other permissions contain write access.

State and dependencies: creates and removes `$PREFIX/basic-dc`; restores the original umask. Depends on GNU-style `stat`, `samba-tool`, and subunit helpers.

Risks and test signals: it skips directories and sockets, so it only covers regular private files. The permission check is direct and provides a strong filesystem-level signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/tests/provision_fileperms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/wscript_build -->
# Research: sources/user-network-fs/samba/source4/setup/wscript_build

Purpose: Waf build/install declarations for Samba setup templates and schema data.

Important APIs: `bld.INSTALL_WILDCARD()` installs groups of schema, display-specifier, adprep, and templated setup files under `${SETUPDIR}`. `bld.INSTALL_FILES()` installs explicit update lists such as `dns_update_list` and `spn_update_list`.

State and integration: it does not execute provisioning; it determines which static setup assets are installed into the build prefix for provisioning and upgrade tools to consume.

Risks and test signals: missing wildcard coverage can produce runtime provisioning failures despite successful compilation. Build/install tests and provisioning blackbox tests are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/setup/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/blob.c -->
# Research: sources/user-network-fs/samba/source4/smb_server/blob.c

Purpose: SMB server helper code for encoding and decoding passthrough SMB/SMB2 information levels into `DATA_BLOB` buffers, especially TRANS2/query/set/file-search reply formats.

Important APIs: `smbsrv_blob_grow_data()` reallocates a blob and sets length. `smbsrv_blob_fill_data()` grows and zero-fills new bytes. `smbsrv_blob_pull_string()` range-checks and delegates to `req_pull_string`. `smbsrv_blob_append_string()` reserves room, writes string data through the private `smbsrv_blob_push_string()`, stores length fields, and shrinks to actual size. `smbsrv_push_passthru_fsinfo()`, `smbsrv_push_passthru_fileinfo()`, `smbsrv_pull_passthru_sfileinfo()`, and `smbsrv_push_passthru_search()` translate raw union fields to and from wire layouts.

Control flow and state: all functions are stateless except for mutating caller-owned talloc-backed blobs and output unions. Switch statements map protocol information levels to fixed offsets, endian macros, time conversion helpers, GUID NDR blobs, EA list helpers, and chained search entry alignment.

Dependencies and integration: used by SMB server request handlers to pass NTVFS backend data through to SMB1/SMB2 wire formats. It depends on `libcli/raw`, string conversion flags, `DATA_BLOB`, talloc, and low-level put/get macros.

Risks and test signals: offset, alignment, and length-field mistakes cause client-visible protocol incompatibility. `NT_STATUS_FOOBAR` on string push/pull failure is vague. The explicit panic for zero SMB2 EAs catches backend contract violations. Signals come from raw SMB, SMB2, search, EA, stream, and file-info torture suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/blob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/handle.c -->
# Research: sources/user-network-fs/samba/source4/smb_server/handle.c

Purpose: manages per-tree-connect SMB handle IDs and their lifetime.

Important APIs: `smbsrv_init_handles()` initializes an idtree with a masked 24-bit limit and an empty list. The private `smbsrv_handle_find()` validates nonzero ID, limit, idtree lookup, type, and `ntvfs` validity before updating `last_use_time`. `smbsrv_smb_handle_find()` and `smbsrv_smb2_handle_find()` adapt SMB1 `fnum` and SMB2 handle IDs. `smbsrv_handle_new()` allocates a handle, reserves an ID with `idr_get_new_above()`, links it to the tcon list and session handle list, installs a destructor, and records open/last-use times.

State and persistence: state is in `tcon->handles.idtree_hid`, `tcon->handles.list`, and `session->handles`. The destructor removes all links and frees the NTVFS backend handle.

Dependencies and integration: depends on talloc destructors, idtree allocation, DLIST macros, and NTVFS handle ownership. Request handlers use these helpers to validate client-provided handle IDs.

Risks and test signals: ID exhaustion returns NULL after logging. A handle is hidden until `handle->ntvfs` is set, which prevents premature use but requires backend setup ordering. Signals come from open/close, file ID, and handle lifetime torture tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/management.c -->
# Research: sources/user-network-fs/samba/source4/smb_server/management.c

Purpose: exposes runtime SMB server session and tree-connect information over Samba IRPC.

Important APIs: `smbsrv_session_information()` counts `smb_conn->sessions.list`, allocates `smbsrv_session_info` records, and fills client IP, VUID, account/domain names, connect/auth/last-use times. `smbsrv_tcon_information()` does the same for `smb_conn->smb_tcons.list`, filling TID, share name, connect time, and last-use time. `smbsrv_information()` dispatches on `SMBSRV_INFO_SESSIONS` or `SMBSRV_INFO_TCONS`. `smbsrv_management_init()` registers the IRPC handler with `IRPC_REGISTER`.

State and dependencies: it reads live connection state but does not mutate sessions or tcons. It depends on IRPC, generated NDR types, tsocket address formatting, and auth session info fields.

Risks and test signals: comments mark this as debugging only; no access filtering is visible here beyond messaging context registration. Missing `session_info` would be unsafe if unfinished sessions reached the list exposed here. Signals are management queries returning accurate session/tcon counts and timestamps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/management.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/service_smb.c -->
# Research: sources/user-network-fs/samba/source4/smb_server/service_smb.c

Purpose: registers and initializes the Samba 4 SMB server service task.

Control flow: `server_service_smb_init()` obtains the loadparm context, initializes NTVFS and shares, and registers service `smb` with task details that inhibit fork-on-accept and pre-fork. `smbsrv_task_init()` sets the process title, binds sockets either to configured interfaces when `bind interfaces only` is true or to wildcard addresses otherwise, registers the messaging name `smb_server`, and terminates the task on startup failure.

State and dependencies: it opens listening sockets through `smbsrv_add_socket()` and registers the service in Samba's process model. It depends on loadparm, network interface discovery, service task APIs, stream service support, NTVFS, and share initialization.

Risks and test signals: binding failure on any selected address aborts the whole SMB task. Interface configuration and wildcard discovery are common integration risk points. Signals include successful smbd startup, socket binding, and acceptance of SMB connections in selftests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/service_smb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/session.c -->
# Research: sources/user-network-fs/samba/source4/smb_server/session.c

Purpose: manages authenticated SMB session IDs (VUIDs) and their lifecycle on a server connection.

Important APIs: `smbsrv_init_sessions()` initializes the session idtree and list with a masked 24-bit limit. `smbsrv_session_find()` validates VUID, checks the idtree, returns only sessions with `session_info`, and updates `last_request_time`. `smbsrv_session_find_sesssetup()` returns an in-progress session for session setup. `smbsrv_session_sesssetup_finished()` requires non-NULL `auth_session_info`, steals it onto the session, and records auth time. `smbsrv_session_new()` allocates a session, assigns a random VUID with `idr_get_new_random()`, steals optional `gensec_ctx`, links the session, installs a destructor, and records connect time.

State and persistence: all state is connection-local and talloc-scoped. The destructor removes the VUID idtree entry and list link. No disk persistence is involved.

Dependencies and integration: depends on idtree_random, talloc ownership, GENSEC authentication context, and auth session info. SMB session setup handlers use it to separate in-progress authentication from usable authenticated sessions.

Risks and test signals: VUID exhaustion fails session creation. Freeing the session on NULL auth info prevents partially authenticated sessions from surviving programmer errors. Signals come from session setup, reconnect, authentication, and multi-session smbtorture tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/smb_server/session.c -->
