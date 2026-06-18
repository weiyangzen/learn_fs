# subset-b-009862 Research

Grouped research report for the requested Samba source files. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_update_keytab.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_update_keytab.sh

Purpose: blackbox regression coverage for AD member machine-account password rotation and keytab synchronization in the `ad_member_idmap_nss` selftest environment. It validates that `wbinfo --change-secret`, `rpcclient change_trust_pw`, `net rpc changetrustpw`, and `net ads changetrustpw` all leave generated keytabs usable and structurally correct.

Important functions and APIs: the script imports Samba blackbox `subunit.sh` and `common_test_fns.inc`, then wraps `$BINDIR/wbinfo`, `net`, `rpcclient`, and `smbclient`. `get_biggest_vno()` parses `net ads keytab list` output and stores the highest KVNO in global `vno`. `compare_keytabs_sync_kvno()` normalizes MIT and Heimdal enctype names and removes KVNOs before diffing, while `compare_keytabs_nosync_kvno()` preserves KVNO order for entries that should not sync KVNOs. `test_pwd_change()` drives a password change command, checks `net ads testjoin`, verifies KVNO increment, exports current keytabs, and compares them with static templates.

Control flow: after argument parsing and static keytab fixture definitions, the script creates a temporary keytab template directory under `$PREFIX/ad_member_idmap_nss`, deletes any existing test keytabs, performs an initial secret change/check to create old password history, creates/syncs keytabs with `net ads keytab create`, then runs the four password-change paths. It finally checks machine-pass SMB access before and after the password-change sequence.

State and persistence: persistent effects are machine account secret updates in the AD/member state, keytab files under `$PREFIX/ad_member_idmap_nss`, and temporary normalized comparison files under `TMPDIR`. Cleanup removes only `TMPDIR`; regenerated keytabs remain as part of the test environment state.

Dependencies and integration: depends on AD member provisioning variables (`DOMAIN`, `REALM`, `DC_SERVER`, `PREFIX`, `BINDIR`, `CONFIGURATION`) and selftest registration from `source3/selftest/tests.py` as `samba3.blackbox.update_keytab`. It is tightly integrated with Samba keytab generation semantics and with MIT/Heimdal output formats.

Risks and test signals: the large embedded expected-output fixtures are fragile when principals, casing, enctype policy, or keytab list formatting changes. Good signals are exact diff success after each password-change path, KVNO increment by one, successful `wbinfo --check-secret`, and `smbclient --machine-pass` access. Failures print command output and diff data, which is useful for identifying keytab drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_update_keytab.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_update_keytab_clustered.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_update_keytab_clustered.sh

Purpose: clustered variant of machine-account secret and keytab update testing. It verifies that a `clusteredmember` selftest environment can use the configured sync-machine-password hook to update node keytabs consistently when the machine password changes.

Important functions and APIs: uses Samba blackbox subunit helpers, `$BINDIR/wbinfo`, `net`, `rpcclient`, `smbclient`, and `smbcontrol`. `check_net_ads_testjoin()` and `test_keytab_create()` run `net ads` commands under `UID_WRAPPER_ROOT` to simulate root privileges. `get_biggest_vno()` parses keytab KVNOs. `test_pwd_change()` reads KVNOs from multiple node keytabs, executes a supplied password-change command, verifies `net ads testjoin`, and checks the new KVNO is synchronized.

Control flow: the script installs `source3/script/updatekeytab_test.sh` into the clustered prefix, writes `sync machine password script = ...` into `global_inject.conf`, reloads winbind, checks the initial join, performs an initial secret-change/check, creates keytabs, tests the synchronized password change, checks SMB machine login, then clears the injected configuration and reloads winbind again.

State and persistence: it mutates `global_inject.conf` for the cluster member test environment, writes keytabs below `$PREFIX/clusteredmember/node.*`, and changes the domain machine secret. The script resets the injected config at the end but relies on the surrounding selftest cleanup for environment state.

Dependencies and integration: registered from `selftest/tests.py` as `samba3.blackbox.update_keytab_clustered` and gated by the `clusteredmember` environment. It depends on CTDB-style node paths, UID wrapper behavior, and the update-keytab callout script.

Risks and test signals: there is a copy/paste-looking issue in the new node KVNO reads: all three new values are read from `node.0/keytab0`, so cross-node divergence after the change may not be detected. Strong signals are successful reloads, `net ads testjoin`, `wbinfo --check-secret`, machine-pass SMB access, and KVNO increment. The test is sensitive to cluster path layout and wrapper privileges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_update_keytab_clustered.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_user_in_sharelist.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_user_in_sharelist.sh

Purpose: validates that a user-specific `[homes]` share appears in `srvsvc` share enumeration output. It is a focused regression test for homes share visibility through `rpcclient netshareenum`.

Important functions and APIs: the script uses `rpcclient`, selftest-provided `USER` and `PASSWORD`, and `subunit.sh`. It runs `rpcclient SERVER -UUSER%PASSWORD -c netshareenum` and searches for a `netname: USER$` line.

Control flow: after argument validation, it invokes the single RPC enumeration command, captures `grep` status, reports the result through `testit`, and finishes with `testok`.

State and persistence: no local persistent state is created. It only reads server share enumeration state exposed by the test environment.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.netshareenum_username` against the `fileserver` environment. It assumes homes support is configured so that the authenticating user maps to a visible share named with a trailing dollar.

Risks and test signals: the check is intentionally narrow and can fail from output formatting changes, environment user naming changes, or homes share configuration drift. Passing signal is the exact `netname` line in RPC output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_user_in_sharelist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_usernamemap.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_usernamemap.sh

Purpose: verifies `username map` handling for UNIX groups and mapped usernames in an AD member selftest. It checks that a mapped login name authenticates using the target user's password and that an unmapped control user still authenticates normally.

Important functions and APIs: uses `smbclient` wrapped by `VALGRIND` and `subunit.sh`. There are no helper functions; the test is two `testit` invocations against `//SERVER/tmp`.

Control flow: parse `SERVER` and `SMBCLIENT`, source subunit support, then run `smbclient` as `SERVER/jackthemapper` and `SERVER/jacknomapper`, both using the `jacknomapper` password. Both must be able to list the share.

State and persistence: no files are created. It depends entirely on smb.conf username-map state and test users provisioned by the environment.

Dependencies and integration: registered from `selftest/tests.py` as `samba3.blackbox.smbclient_usernamemap` in `ad_member_idmap_nss:local`. It integrates with Samba authentication, domain-qualified usernames, and username-map parsing.

Risks and test signals: credentials are hard-coded for the selftest fixture, so provisioning changes break the test. It is a positive-only test and does not assert that the wrong password fails. Passing signal is successful `ls` for both mapped and unmapped identities.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_usernamemap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_usershare_not_accessible.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_usershare_not_accessible.sh

Purpose: regression test for a usershare lifetime crash where removing a usershare definition during an active connection could destroy service state still referenced by an existing tree connect, later causing a null dereference during `volume` handling.

Important functions and APIs: uses `net usershare`, `testparm --parameter-name="usershare path"`, interactive `smbclient`, named FIFOs, and subunit primitives. `cleanup()` removes the test usershare file, directory, and FIFO artifacts.

Control flow: the script discovers the usershare path, creates a backing directory and usershare, starts a persistent forced-interactive `smbclient` connected to that usershare, verifies `ls`, records the current client tree id, deletes the usershare definition file, issues a new `tcon` to force `find_service()`/`usershare_exists()` failure, restores the original tid, runs `volume`, then runs `ls` and checks whether the server stayed alive.

State and persistence: creates a usershare definition, a backing directory under `$LOCAL_PATH/usershares`, and named pipes in `$SELFTEST_TMPDIR`. It removes these at startup and exit, although abnormal exits can leave the usershare directory or definition until the next cleanup.

Dependencies and integration: registered as `samba3.blackbox.usershare_not_accessible` in `fileserver:local`. It relies on smbclient interactive commands (`tid`, `tcon`, `volume`), usershare support, and a server build with the crash path fixed.

Risks and test signals: FIFO timing uses sleeps and fixed reads, so slow environments can make output parsing fragile. Passing signal is a final directory listing containing `.` and no `NT_STATUS_CONNECTION_DISCONNECTED`; failure output captures the smbclient transcript.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_usershare_not_accessible.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_valid_users.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_valid_users.sh

Purpose: blackbox check that a share guarded by the `valid users` smb.conf parameter can be listed by a permitted user.

Important functions and APIs: uses forced-interactive `smbclient` and `subunit.sh`. `test_valid_users_access()` writes an input file containing `ls` and `quit`, runs `smbclient //SERVER/share -I SERVER_IP -UUSERNAME%PASSWORD`, then checks for the expected interactive prompt marker.

Control flow: after parsing server, domain, credentials, prefix, and smbclient path, the script invokes `test_valid_users_access valid-users-access` through `testit` and exits with the failure count.

State and persistence: creates a temporary command file under `$PREFIX` and removes it after the client run. It does not modify server state.

Dependencies and integration: registered under the `fileserver` loop in `selftest/tests.py` as `samba3.blackbox.valid_users`. It depends on the share `valid-users-access` being configured with access for the provided test user.

Risks and test signals: the success check uses prompt text, not a specific directory listing, so prompt-format changes can affect it. A nonzero smbclient exit or missing prompt is the failure signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_valid_users.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_veto_files.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_veto_files.sh

Purpose: regression and behavior coverage for `veto files`, hidden-file filtering, name mangling, and per-user veto rules. It verifies clients cannot read or create paths hidden by veto rules, including within vetoed directories.

Important functions and APIs: imports `subunit.sh` and `common_test_fns.inc`; uses `smbclient` helpers plus local filesystem setup. `do_cleanup()` removes all test fixture paths. `smbclient_get_expect_error()` and `smbclient_create_expect_error()` run interactive `get`/`put` commands and match either no `NT_STATUS_` errors or a specific NT status. `test_get_veto_file()`, `test_create_veto_file()`, and `test_per_user()` compose the assertions.

Control flow: it first verifies normal and hidden file behavior on `veto_files_nohidden`, then builds a nested directory tree with vetoed names, hash2-mangled aliases, and user/group-specific files. It runs create, get, and per-user tests, then cleans the share path and temp directory.

State and persistence: creates many files and directories under the provided `SHAREPATH` and temporary smbclient input files under `$PREFIX/<scriptname>`. Cleanup is explicit but depends on successful progress to the end.

Dependencies and integration: registered as `samba3.blackbox.test_veto_files` in the `fileserver` environment. It depends on configured shares `veto_files` and `veto_files_nohidden`, hash2 mangling outputs, test users `user1` and `user2`, and group-based veto configuration.

Risks and test signals: expected mangled names are hard-coded, so mangling algorithm changes require fixture updates. The test provides strong behavior signals through exact NT status checks for top-level, nested, mangled, create, and per-user cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_veto_files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_veto_rmdir.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_veto_rmdir.sh

Purpose: covers directory removal semantics when directories contain vetoed files, including the `delete veto files` behavior and interaction with DFS links.

Important functions and APIs: uses forced-interactive `smbclient` with hand-written command files. `test_veto_nodelete_rmdir()` operates against the `veto_files_nodelete` share and expects `NT_STATUS_DIRECTORY_NOT_EMPTY` while a vetoed file remains. `test_veto_delete_rmdir()` operates against `veto_files_delete` and expects removal to succeed after a visible DFS symlink is removed.

Control flow: each helper creates `$SHAREPATH/dir`, a vetoed file, and an `msdfs:` symlink. It lists the directory to confirm only `dfs_link` is visible, removes the DFS link, then attempts `rd dir` and checks the expected outcome. The top-level script runs the nodelete case, cleans, runs the delete case, and cleans again.

State and persistence: creates and removes `dir`, the veto file, DFS symlink, and temporary smbclient input under `$PREFIX`. It mutates only the supplied test share path.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.test_veto_rmdir` under `fileserver`. It depends on share definitions for `veto_files_nodelete` and `veto_files_delete`, DFS symlink interpretation, and the client/server returning stable NT status strings.

Risks and test signals: the test assumes only the DFS link is visible before removal; changes to listing behavior or veto visibility can produce false failures. Good signals are the exact presence or absence of `NT_STATUS_DIRECTORY_NOT_EMPTY` and no generic `NT_STATUS_` errors in the delete-enabled case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_veto_rmdir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_virus_scanner.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_virus_scanner.sh

Purpose: blackbox validation of the `vfs_virusfilter` behavior for infected and healthy files on read and write paths. It checks that infected paths are renamed using the configured prefix/suffix and are not transferred, while healthy files round-trip correctly.

Important functions and APIs: uses `smbclient`, selftest `USER`/`PASSWORD`, and subunit. `check_infected_read()` creates a nested `infected.txt`, attempts `get`, and expects `virusfilter.infected.txt.infected` to exist with no downloaded copy. `check_infected_write()` uploads a non-empty infected source and expects `virusfilter.infected.upload.txt.infected`. `check_healthy_read()` and `check_healthy_write()` use `cmp` to verify content integrity.

Control flow: each check starts by clearing the share directory, prepares the fixture, invokes `smbclient`, validates filesystem side effects, and returns a subunit result. The four checks run sequentially.

State and persistence: repeatedly removes contents of `${LOCAL_PATH}/${SHARE}` and creates test files below it. It leaves healthy-write artifacts until the next check or environment cleanup.

Dependencies and integration: registered as `samba3.blackbox.virus_scanner` in `fileserver:local`. It assumes the share `virusfilter` has a scanner fixture that treats names containing `infected` as positive detections and performs configured rename-on-infection behavior.

Risks and test signals: the test does not inspect smbclient exit status for infected transfers, relying on filesystem effects instead. Strong signals are renamed infected files, absence of transfer artifacts, and byte-for-byte healthy file comparisons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_virus_scanner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_volume_serial_number.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_volume_serial_number.sh

Purpose: verifies that the per-share `volume serial number` parameter is exposed through smbclient's `volume` command.

Important functions and APIs: uses `smbclient` and `subunit.sh`. `test_serial_number()` runs `smbclient //SERVER_IP/SHARENAME -U USERNAME%PASSWORD -c volume`, echoes the output, and greps for `0xdeadbeef`.

Control flow: argument parsing is followed by a single subunit-wrapped check. Any smbclient failure or missing expected serial string fails the test.

State and persistence: no local or server-side mutation.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.volumeserialnumber`, targeting the `volumeserialnumber` share in the `fileserver` environment. It depends on smb.conf setting the expected serial value.

Risks and test signals: string matching is simple and case-sensitive; output-format changes can require updates. Passing signal is the expected hexadecimal serial value in `volume` output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_volume_serial_number.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_lookuprids_cache.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_lookuprids_cache.sh

Purpose: regression coverage for winbind `LookupRids` cache behavior. It verifies that deleting an NDR cache key for `wbint_LookupRids` does not prevent a subsequent `wbinfo -R` lookup from succeeding.

Important functions and APIs: uses `wbinfo`, `net cache flush`, `tdbdump`, `tdbtool`, Python import `samba.dcerpc.winbind.wbint_LookupRids`, and subunit helpers. It computes the runtime opnum instead of hard-coding it, dumps `winbindd_cache.tdb`, extracts matching `NDR/.../<opnum>/...` keys, escapes spaces as `\20`, deletes one key, then reruns the lookup.

Control flow: flush cache, run first lookup for RIDs `512,12345`, find/delete the generated cache key, run second lookup, and report through `testok`. On delete failure it prints a post-failure dump of NDR keys.

State and persistence: mutates `$LOCK_DIR/winbindd_cache.tdb` by flushing and deleting a selected cache key. It intentionally exercises persistent winbind cache state.

Dependencies and integration: registered as `samba.wbinfo_lookuprids_cache` in `nt4_member:local`. It requires working Samba Python bindings, TDB tooling, and the winbind cache file.

Risks and test signals: key extraction is dependent on tdbdump formatting and the exact `NDR` key schema. The script disables Bash history expansion because cache keys may contain `!`. Passing signal is successful key deletion and successful second `wbinfo -R`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_lookuprids_cache.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids.sh

Purpose: thin subunit wrapper around the Python integration test for `wbinfo --sids-to-unix-ids` consistency with singular SID/UID/GID conversion paths.

Important functions and APIs: constructs `WBINFO` and `NET` command variables with `VALGRIND` and `CONFIGURATION`, locates `test_wbinfo_sids2xids_int.py`, sources subunit, and runs the Python helper through one `testit` call.

Control flow: no internal assertions are implemented in the shell wrapper; all substantive control flow lives in the Python helper. The wrapper reports aggregate pass/fail with `testok`.

State and persistence: no direct state mutation except whatever the Python helper performs via `net cache del` and `wbinfo`.

Dependencies and integration: intended for source3 selftest use where `BINDIR`, `CONFIGURATION`, and Samba Python modules are available. The wrapper ensures the helper uses the same configured binaries as the rest of the selftest environment.

Risks and test signals: any quoting or whitespace in `WBINFO`/`NET` command variables is passed as positional arguments to Python and then used both as argv and shell snippets by the helper. The only shell-level signal is the helper's exit status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids_int.py -->
# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids_int.py

Purpose: validates consistency between batched SID-to-XID conversion and singular SID/UID/GID conversion APIs across different winbind cache states.

Important functions and APIs: uses `subprocess.check_output`, `samba.common.get_string`, `wbinfo --own-domain`, `wbinfo -n DOMAIN/`, `wbinfo --sids-to-unix-ids`, `--sid-to-gid`, `--sid-to-uid`, `--uid-to-sid`, `--gid-to-sid`, and `net cache del`. `run()` returns decoded command output. `flush_cache()` deletes IDMAP cache keys. `fill_cache()` primes reverse caches. `check_singular()` compares batched results with singular lookups. `check_multiple()` verifies batched type classifications after cache priming.

Control flow: derive the local domain SID, build a mix of domain, builtin, world, creator, and authentication authority SIDs, flush their cache entries, run the batched conversion, parse id types and numeric IDs, then perform four rounds: singular checks with existing batch cache, singular checks after SID and XID cache flushes, batched checks after UID-to-SID cache fill, and batched checks after GID-to-SID cache fill. It flushes cache entries before exit.

State and persistence: deliberately deletes and primes winbind IDMAP cache keys. No filesystem artifacts are created.

Dependencies and integration: called by `test_wbinfo_sids2xids.sh` and requires Samba Python modules plus working `wbinfo`/`net`. It assumes the output format of `--sids-to-unix-ids` has the ID type at field index 2.

Risks and test signals: `flush_cache()` uses `os.system()` with command strings, so unusual command paths or SID strings could be problematic; in selftest inputs are controlled. Failure exits immediately after printing expected/got details and attempts cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids_int.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_u_large_ad.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_u_large_ad.sh

Purpose: load/regression test that a large number of AD users are returned by `wbinfo -u`.

Important functions and APIs: uses `ldbsearch` to find `defaultNamingContext`, `ldbmodify` to add/delete users over LDAP, `wbinfo -u`, and `testit_grep_count` from subunit. `NUM_USERS` is fixed at 1234.

Control flow: it generates LDIF add records for `large_ad_0001` through `large_ad_1234` under `CN=Users`, applies them as domain Administrator, then asserts that exactly 1234 lines containing `$DOMAIN/large_ad_` appear in `wbinfo -u`. It then generates matching delete LDIF and removes the users.

State and persistence: creates many users in the AD database and removes them at the end. If the script aborts before deletion, those test users can persist and affect later runs.

Dependencies and integration: depends on an AD DC available via `$DC_SERVER`, administrator credentials, Samba ldb tools, and the `wbinfo` domain enumeration path. It is likely registered or run in AD environments that can tolerate LDAP mutation.

Risks and test signals: no trap ensures cleanup on failure, so mid-run errors can leave users behind. The pass signal is an exact count, which catches paging or enumeration truncation but can be disturbed by stale leftover users from failed runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_wbinfo_u_large_ad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_widelink_dfs_ci.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_widelink_dfs_ci.sh

Purpose: regression test that a DFS share with wide links enabled remains case-insensitive for normal directory operations.

Important functions and APIs: uses forced-interactive `smbclient`, subunit, and common blackbox helpers. `test_ci()` writes commands to create directory `x`, change into uppercase `X`, return, remove `x`, and quit, then checks for absence of `NT_STATUS_`.

Control flow: after suppressing deprecated option warnings, the script runs the single case-insensitivity scenario against `//SERVER/msdfs-share-wl`, using the supplied `SERVER_IP`, credentials, prefix, and extra smbclient args.

State and persistence: creates and removes directory `x` on the target DFS share. Temporary command file lives under `$PREFIX`.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.widelink_dfs_ci` in the `fileserver` environment. It depends on share `msdfs-share-wl` and the wide-links/DFS configuration being active.

Risks and test signals: the `SHARE` argument is parsed but the UNC is hard-coded to `msdfs-share-wl`, so callers cannot vary the share without editing the script. Passing signal is a successful smbclient run with no NT status errors during uppercase `cd`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_widelink_dfs_ci.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_winbind_cache_sanity.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_winbind_cache_sanity.sh

Purpose: sanity-checks the structural contents of `winbindd_cache.tdb` after a simple name lookup, including cache version, sequence number, and an NDR cache entry.

Important functions and APIs: uses `tdbtool`, `dbwrap_tool`, `wbinfo`, Python `samba.dcerpc.winbind.wbint_LookupName.opnum()`, and subunit helpers. It tests cache readability, performs `wbinfo -n DOMAIN<separator>` to populate cache, fetches `WINBINDD_CACHE_VERSION` as a uint32, checks `SEQNUM/DOMAIN`, and checks the raw NDR key with `tdbtool`.

Control flow: the script validates cache file presence, fills it with a lookup, verifies version key via dbwrap and tdbtool, compares version with `2`, verifies sequence-number key existence, then constructs a byte-escaped NDR key for LookupName and confirms it has the expected data size.

State and persistence: reads and populates the supplied winbind cache file. It does not delete cache entries.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.winbind_cache_sanity` for `ad_member:local`. It depends on the TDB key layout and Samba Python opnum provider.

Risks and test signals: raw NDR key construction is very format-sensitive and domain-length-sensitive; the script currently embeds length bytes for the selftest domain shape. Good signals are successful dbwrap/tdbtool probes and cache version equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_winbind_cache_sanity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_winbind_call_depth_trace.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_winbind_call_depth_trace.sh

Purpose: verifies winbind debug trace call-depth logging and indentation for a nested group membership query.

Important functions and APIs: uses `smbcontrol`, `global_inject.conf`, `id`, `grep`, and subunit. `test_winbind_call_depth_trace()` injects `debug syslog format = no` and `log level = 10`, reloads winbind, runs `id ADDOMAIN/alice`, clears the injected config, reloads again, then checks log growth and formatting.

Control flow: the script first maps `TESTENV` to a log directory and skips if only stdout logging is available. It only permits `ad_member*` environments. The test records the count of `wb_group_members_send` lines before/after the `id` command, expects the count to increase, expects the last such trace to include `depth=3`, and expects the related `WB command group_members start` line to be indented by 14 spaces.

State and persistence: temporarily modifies `global_inject.conf` and appends to the winbind log through debug logging. It resets the file to empty after the command.

Dependencies and integration: registered as `samba3.winbind_call_depth_trace` for `ad_member:local`. It depends on log file path conventions and exact debug output formats.

Risks and test signals: log formatting and function-name changes will break the grep checks. If winbind logs to stdout via `WINBINDD_DONT_LOG_STDOUT=1`, the script skips rather than failing because debug headers are absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_winbind_call_depth_trace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_winbind_ignore_domains.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_winbind_ignore_domains.sh

Purpose: integration test for `winbind:ignore domains`, verifying that authentication from a trusted domain succeeds normally and is blocked after the trusted domain is ignored.

Important functions and APIs: uses `ldbsearch`, `ldbmodify`, `smbcontrol winbindd reload-config`, `wbinfo -p`, and smbclient helpers from `common_test_fns.inc`. `add_posix_ids()` and `remove_posix_ids()` modify `uidNumber`/`gidNumber` attributes for trusted-domain Administrator, Domain Users, and Domain Admins.

Control flow: derive the trusted domain base DN, add POSIX IDs, clear injected config, reload winbind, verify trusted-domain NTLM by IP, NTLM by FQDN, and Kerberos by FQDN all work. Then write `winbind:ignore domains = TRUST_DOMAIN`, reload winbind, verify the same three accesses fail, clear config again, reload, and remove the POSIX IDs.

State and persistence: mutates trusted-domain LDAP attributes and local `global_inject.conf`. Cleanup is explicit at the end but not protected by a trap.

Dependencies and integration: registered as `samba3.blackbox.winbind_ignore_domain` in `ad_member_idmap_ad:local`. It requires a trusted domain fixture, idmap AD semantics, Kerberos and NTLM test credentials, and working winbind reload behavior.

Risks and test signals: failures before `remove_posix_ids()` can leave LDAP attributes behind. Passing signal is the before/after contrast: three successful accesses without the ignore setting and three expected failures with it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_winbind_ignore_domains.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_worm.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_worm.sh

Purpose: tests WORM VFS behavior around deletion and overwrite protection after the configured grace period, including ctime refresh handling and rename-over protection.

Important functions and APIs: uses forced-interactive `smbclient`, local filesystem checks, `touch`, `chmod`, and subunit. `do_cleanup()` removes test files and temporary command files. `test_worm()` performs the full scenario.

Control flow: the test uploads several files to the `worm` share and immediately deletes one, which should be allowed. After sleeping one second, it tries POSIX chmod and delete operations on protected files, refreshes ctime for one file, and validates that the protected file remains. It then uploads a sentinel value and attempts `rename ... -f` over a protected file, verifying original contents are unchanged. If running as root, it also checks the ctime-refreshed file was deleted.

State and persistence: creates and deletes files in `$LOCAL_PATH/worm`, command files under `$PREFIX`, and a sentinel file. Cleanup removes expected artifacts.

Dependencies and integration: registered for both NT1 and SMB3 in the `fileserver` environment. It depends on a WORM share with short grace-period behavior and on the client supporting POSIX commands for the relevant protocol path.

Risks and test signals: the one-second sleep encodes timing expectations and can be flaky if filesystem timestamp granularity or VFS settings change. Strong signals are protected deletion refusal, successful recent-file deletion, and no overwrite through forced rename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_worm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_zero_data.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_zero_data.sh

Purpose: verifies SMB2 `ZERO_DATA` sparse-file behavior through smbtorture and local disk allocation checks.

Important functions and APIs: uses `dd`, `du -k`, `smbtorture smb2.set-sparse-ioctl`, `smbtorture smb2.zero-data-ioctl`, and subunit. It passes torture options for filename, offset, and `beyond_final_zero`.

Control flow: create `$LOCAL_PATH/zero_data/testfile` with 128 KiB of random data, assert allocated size is 128 KiB, set the file sparse through SMB2 IOCTL, zero the full range through SMB2 `zero-data-ioctl`, then assert local allocation drops to zero KiB.

State and persistence: creates and removes `$LOCAL_PATH/zero_data`. It writes a real file on the backing filesystem and relies on sparse allocation reporting.

Dependencies and integration: registered as `samba3.blackbox.zero-data` in the `fileserver` loop. Requires a filesystem that reports sparse allocation as expected and supports Samba's zero-data path.

Risks and test signals: `chmod 777 p $TESTDIR` appears malformed and may emit an error, though the script continues. Allocation sizes are filesystem-dependent; non-sparse or block-accounting differences can cause false failures. Passing signal is allocation dropping from 128 to 0 after the SMB2 zero operation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_zero_data.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_zero_readsize.sh -->
# sources/user-network-fs/samba/source3/script/tests/test_zero_readsize.sh

Purpose: regression test for invalid SMB2 negotiation behavior when `smb2 max read = 0` is injected into the server config.

Important functions and APIs: uses `smbcontrol smbd reload-config`, `global_inject.conf`, `dd`, forced-interactive `smbclient`, and subunit. `do_setup()` creates a test file and injects the invalid config. `do_cleanup()` removes files and the injection. `test_smb2_zero_readsize()` attempts put/get/delete through SMB2 and expects negotiation failure.

Control flow: setup writes `smb2 max read = 0`, reloads smbd, then the client script tries normal file operations against `//SERVER/SHARE`. The expected client exit status is `1` and output must contain `NT_STATUS_INVALID_NETWORK_RESPONSE`. Cleanup removes the injection and reloads smbd.

State and persistence: creates files in `$PREFIX` and writes/removes `global_inject.conf` next to the server configuration. It changes live smbd config for the duration of the test.

Dependencies and integration: registered as `samba3.blackbox.zero_readsize` in `simpleserver:local` with `-mSMB2`. It depends on `smbcontrol` reload working and the server rejecting invalid max-read negotiation consistently.

Risks and test signals: if the script exits before cleanup, the invalid config can affect later tests. The expected failure is protocol negotiation failure; a successful smbclient run is explicitly a test failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/test_zero_readsize.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/timelimit.c -->
# sources/user-network-fs/samba/source3/script/tests/timelimit.c

Purpose: small utility that runs a command with a maximum wall-clock timeout and signal handling suitable for Samba test harness use.

Important functions and APIs: uses POSIX `fork`, `execvp`, `setpgid`, `wait`, `kill`, `signal`, and `alarm`. `new_process_group()` places the child in a new process group. `sig_alrm_term()` sends SIGTERM to the child process group and schedules SIGKILL after 5 seconds. `sig_term()` handles parent SIGTERM/SIGINT/SIGQUIT similarly with a 1-second kill grace. `sig_usr1()` forwards SIGTERM without exiting immediately.

Control flow: parse `<time> <command>`, fork, exec the command in the child, install signal handlers in the parent, set the timeout alarm, wait until no children remain, then kill the child process group with SIGKILL and exit with the last child exit status.

State and persistence: no persistent state. Runtime state is the global `child_pid`, process group membership, and alarm timers.

Dependencies and integration: imported by `selftest/tests.py` through `selftesthelpers.timelimit` and used as a wrapper for long-running blackbox tests. It assumes process-group signaling is available.

Risks and test signals: `WEXITSTATUS(status)` is used without checking `WIFEXITED`, so signal-terminated children may yield misleading exit codes. The final unconditional SIGKILL is defensive but can report ESRCH silently. Test signal is a nonzero exit with "Maximum time expired" when timeout escalation occurs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/timelimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/vfstest-acl/run.sh -->
# sources/user-network-fs/samba/source3/script/tests/vfstest-acl/run.sh

Purpose: runs a scripted `vfstest` ACL scenario and fails if the scripted operations produce `NT_STATUS_ACCESS_DENIED`.

Important functions and APIs: uses `vfstest -f $TESTBASE/vfstest.cmd`, subunit, and a temporary directory under `$PREFIX`. `test_vfstest()` executes the command, checks the process status, and scans output for access denied.

Control flow: parse `VFSTEST` and `PREFIX`, create and enter a temp directory, run the one vfstest command through `testit`, then exit with the failure count.

State and persistence: creates a `vfstest_XXXXXX` temp directory under `$PREFIX` and does not remove it. The vfstest command may create files inside that temp directory.

Dependencies and integration: registered as `samba.vfstest.acl` in `nt4_dc:local` from `selftest/tests.py`. It depends on sibling `vfstest.cmd` and the `vfstest` binary.

Risks and test signals: no cleanup may accumulate temp dirs. The negative grep is broad: any `NT_STATUS_ACCESS_DENIED` in debug output fails the test, even if later expected behavior changes. Passing signal is zero exit and no access-denied status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/vfstest-acl/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/vfstest-catia/run.sh -->
# sources/user-network-fs/samba/source3/script/tests/vfstest-catia/run.sh

Purpose: verifies `vfs_catia` filename character translation in both directory listing and directory creation directions.

Important functions and APIs: uses `vfstest`, subunit, `--option=vfsobjects=catia`, and a hard-coded `catia:mappings` table. `test_vfstest()` runs `vfstest.cmd` and expects the translated Windows filename to appear. `test_vfstest_dir()` runs `vfstest1.cmd` and checks the translated UNIX directory exists.

Control flow: create a temp directory, create a UNIX filename containing Windows-illegal characters, run the unix-to-windows translation test, and if it passes run the windows-to-unix mkdir translation test. Finally remove the temp directory.

State and persistence: uses a temporary directory under `$PREFIX` and removes it on normal completion. It creates files and directories with special characters, including byte values rendered in the current locale.

Dependencies and integration: registered as `samba.vfstest.catia` in `nt4_dc:local`. Depends on sibling command files and exact catia mapping behavior.

Risks and test signals: unquoted variable expansions around filenames with backslashes and special characters are fragile but controlled by the script's constants. Passing signals are seeing the translated Windows filename in output and finding exactly one translated UNIX directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/vfstest-catia/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/wb_pad.sh -->
# sources/user-network-fs/samba/source3/script/tests/wb_pad.sh

Purpose: build-time ABI check that `struct winbindd_request` and `struct winbindd_response` have identical sizes in 32-bit and 64-bit builds.

Important functions and APIs: dynamically writes a small C program including `nsswitch/winbind_client.h`, compiles it with `${CC:-gcc} -m32` and `-m64`, runs each binary with `req` and `resp`, and compares printed `sizeof` values. `cleanup()` removes generated sources/binaries and the temp directory.

Control flow: create `/tmp/wb_padXXXXXX`, generate C source, compile 32-bit and 64-bit binaries, run them to collect request/response sizes, cleanup, then fail if either pair differs.

State and persistence: creates temporary files under `/tmp` and removes them on normal paths, including compile failures.

Dependencies and integration: requires a compiler with both 32-bit and 64-bit support, Samba headers in the relative include paths, and any caller-provided `RPM_OPT_FLAGS`/`CFLAGS`. It is a low-level compatibility test for winbind client protocol structs.

Risks and test signals: many modern systems lack 32-bit build support, causing environment failures unrelated to Samba ABI. Passing signal is exact size equality for both request and response structures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/wb_pad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/xattr-tdb-1/run.sh -->
# sources/user-network-fs/samba/source3/script/tests/xattr-tdb-1/run.sh

Purpose: runs a scripted `vfstest` scenario for the `xattr_tdb` behavior and fails on unexpected access-denied output.

Important functions and APIs: same harness pattern as the ACL vfstest runner: `vfstest -f $TESTBASE/vfstest.cmd`, subunit, and a temp working directory under `$PREFIX`.

Control flow: parse arguments, create and enter `vfstest_XXXXXX`, execute the command through `test_vfstest`, treat nonzero exit or `NT_STATUS_ACCESS_DENIED` output as failure, and exit with the failure count.

State and persistence: creates a temporary directory under `$PREFIX` and does not remove it on normal exit. Any TDB/xattr artifacts produced by `vfstest.cmd` remain in that directory.

Dependencies and integration: registered from `selftest/tests.py` as `samba.vfstest.xattr-tdb-1` in `nt4_dc:local`. Depends on sibling `vfstest.cmd`, the configured `vfstest` binary, and xattr TDB VFS behavior.

Risks and test signals: output-based access-denied detection is coarse, and lack of cleanup can accumulate artifacts. Passing signal is a clean `vfstest` exit without access-denied status text.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/tests/xattr-tdb-1/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/updatekeytab_test.sh -->
# sources/user-network-fs/samba/source3/script/updatekeytab_test.sh

Purpose: callout script used by clustered keytab selftests to run `net ads keytab create` on every local CTDB test daemon node.

Important functions and APIs: delegates to `./ctdb/tests/local_daemons.sh "$PREFIX/clusteredmember" onnode all 'net ads keytab create --option="sync machine password script=" --configfile=$CTDB_BASE/lib/server.conf'`.

Control flow: no argument parsing or functions. It executes one CTDB helper command, which invokes `onnode all` for the clustered member prefix.

State and persistence: causes each node to create/update its keytab via `net ads keytab create`; the script itself creates no files.

Dependencies and integration: installed temporarily by `test_update_keytab_clustered.sh` as the `sync machine password script`. Depends on `PREFIX`, CTDB local daemon layout, `local_daemons.sh`, `onnode`, and `$CTDB_BASE` in the command evaluated on nodes.

Risks and test signals: the relative path assumes the current working directory is Samba source root. There is no explicit error handling beyond shell exit status. Its main signal is whether the caller sees synchronized node keytabs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/updatekeytab_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/updatesmbpasswd.sh -->
# sources/user-network-fs/samba/source3/script/updatesmbpasswd.sh

Purpose: filter script for updating or sanitizing smbpasswd-style colon-separated records, preserving comments and replacing invalid password hashes with `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`.

Important functions and APIs: implemented as a `nawk` program with `FS=":"`. It checks whether a line begins with `#`, whether field 4 is a 32-character all-hex, all-`X`, or all-`*` hash, and otherwise reconstructs the line with fields 1-3 preserved and field 4 replaced.

Control flow: for each input line, comments are printed unchanged; valid hash lines are printed unchanged; invalid hash lines are rewritten as `user:uid:...:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX:` followed by fields 4 through `NF` and a trailing colon.

State and persistence: stateless stream filter. It reads stdin and writes stdout, leaving file replacement to callers.

Dependencies and integration: uses `nawk` and smbpasswd file format assumptions. It is an administrative compatibility script rather than a selftest.

Risks and test signals: the reconstruction loop starts at original field 4 after already outputting a replacement hash, so it appends the invalid original field as subsequent data; this may be intentional for legacy field shifting or may duplicate data unexpectedly. It also only accepts uppercase hex. Correct behavior should be checked with representative smbpasswd lines.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/updatesmbpasswd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/winbind_ctdb_updatekeytab.sh -->
# sources/user-network-fs/samba/source3/script/winbind_ctdb_updatekeytab.sh

Purpose: CTDB-installed callout for winbind machine-password synchronization that refreshes AD keytabs on connected cluster nodes.

Important functions and APIs: executes `onnode -p connected "net ads keytab create --option='sync machine password script='"`. The `-p connected` selector limits the operation to connected nodes.

Control flow: no local branching; command exit status is the script exit status.

State and persistence: updates AD keytabs on selected nodes through `net ads keytab create`. Passing `sync machine password script=` disables recursive invocation of the same hook.

Dependencies and integration: installed by `source3/script/wscript_build` into the CTDB scripts directory when `conf.env.with_ctdb` is true. It depends on `onnode`, CTDB node state, and Samba `net` being in PATH in the CTDB script environment.

Risks and test signals: failures can be partial across nodes depending on CTDB connectivity. The script has no logging or retry logic itself; callers must inspect `onnode`/`net` output and exit status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/winbind_ctdb_updatekeytab.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/wscript_build -->
# sources/user-network-fs/samba/source3/script/wscript_build

Purpose: Waf build/install declarations for selected Samba source3 scripts.

Important functions and APIs: imports `MODE_755`, calls `bld.INSTALL_FILES()` for `smbtar` and `samba-log-parser` into `${BINDIR}`, conditionally installs `winbind_ctdb_updatekeytab.sh` into `CTDB_DATADIR/scripts`, and declares `bld.SAMBA_SCRIPT()` wrappers for `smbaddshare`, `smbchangeshare`, and `smbdeleteshare`.

Control flow: all statements run at build-description evaluation time; only the CTDB script install is conditional on `conf.env.with_ctdb`.

State and persistence: affects the build/install manifest rather than runtime state. It determines which scripts are installed and with executable mode.

Dependencies and integration: part of Samba's Waf build system. It depends on `samba_utils.MODE_755`, `bld`, `conf`, and environment variables such as `CTDB_DATADIR`.

Risks and test signals: install path mistakes affect packaging/runtime availability of helper scripts, especially the CTDB keytab update hook. Build/install tests or packaging manifests are the primary signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/selftest/tests.py -->
# sources/user-network-fs/samba/source3/selftest/tests.py

Purpose: generates the Samba 3 selftest suite plan consumed by `selftest.pl`. It enumerates blackbox scripts, smbtorture suites, RPC matrices, feature-gated tests, and environment-specific command lines.

Important functions and APIs: imports `selftesthelpers` functions such as `plantestsuite`, `planpythontestsuite`, `plansmbtorture4testsuite`, `binpath`, `samba3srcdir`, and command paths (`smbclient3`, `smbtorture3`, `smbtorture4`, `wbinfo`, `net`, `smbcontrol`, `timelimit`). Local `plansmbtorture4testsuite()` selects the target (`samba3`, `samba4`, or `samba4-ntvfs`) based on environment naming. `compare_versions()` supports Linux kernel feature gating. `is_module_enabled()` checks configured static/shared module lists.

Control flow: reads `config.h` feature data, derives booleans for kernel oplocks, inotify, ldwrap, pthreadpool, cluster support, and QUIC wrapper support, then emits hundreds of test registrations. The files in this subset are wired in several clusters: vfstest runners around lines 598-600; username-map and keytab tests around 617 and 678-687; winbind trace/cache and lookup-rids tests around 719-740; valid users, WORM, zero-data, volume serial, veto tests, and usershare tests in the fileserver loop; zero-readsize, share-list, ignore-domain, virus-scanner, and wide-link DFS tests later in the plan. The RPC list includes `rpc.samba3.spoolss`, `rpc.samba3.winreg`, `rpc.samba3.netlogon`, `rpc.svcctl`, `rpc.winreg`, and spoolss/netlogon variants that exercise the service-control code in this subset.

State and persistence: the script emits a plan to stdout; it does not run tests directly or mutate service state. Its "state" is derived from build configuration, platform, and helper-provided paths.

Dependencies and integration: central integration point for source3 testing. It maps scripts to environments such as `fileserver`, `simpleserver:local`, `ad_member:local`, `ad_member_idmap_nss:local`, `nt4_member:local`, and `clusteredmember:local`, and passes required environment variables into scripts as literal selftest substitutions.

Risks and test signals: because this file is plan-generation glue, regressions often appear as missing tests, tests run under the wrong environment, or wrong argument ordering. Feature guards such as `have_cluster_support` and `have_inotify` can silently suppress coverage. The best validation signal is a generated selftest plan containing the expected suite names and command arguments for each script.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/selftest/tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/services.h -->
# sources/user-network-fs/samba/source3/services/services.h

Purpose: shared declarations for Samba's source3 service-control implementation, including service operation dispatch and service handle metadata.

Important types and APIs: includes generated `svcctl.h`. Defines `SVCCTL_SCRIPT_DIR` as `svcctl`. `SERVICE_CONTROL_OPS` contains function pointers for `stop_service`, `start_service`, and `service_status`, all returning `WERROR` and using `struct SERVICE_STATUS`. `SERVICE_INFO` stores handle type, service name, granted access mask, and the operations table. Handle type constants distinguish SCM, service, and database lock handles.

Control flow: header-only; control flow is supplied by service implementation files and the svcctl server dispatch that invokes the function pointers.

State and persistence: `SERVICE_INFO` instances carry per-handle state in memory. No persistent state is declared here.

Dependencies and integration: consumed by internal service implementations such as `svc_netlogon.c`, `svc_spoolss.c`, `svc_winreg.c`, `svc_wins.c`, and `svc_rcinit.c`, and by the RPC service-control server.

Risks and test signals: function pointer signatures are ABI-sensitive within source3. Mis-set handle type constants or access masks can expose incorrect service-control behavior. RPC svcctl torture tests in `selftest/tests.py` are the broad integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/services.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_netlogon.c -->
# sources/user-network-fs/samba/source3/services/svc_netlogon.c

Purpose: internal Service Control Manager facade for Samba's Netlogon service.

Important functions and APIs: `netlogon_status()` zeroes a `SERVICE_STATUS`, reports type `SERVICE_TYPE_WIN32_SHARE_PROCESS`, accepts no controls, and sets state to running if `lp_servicenumber("NETLOGON")` exists, otherwise stopped. `netlogon_stop()` returns status and denies access. `netlogon_start()` returns `WERR_SERVICE_DISABLED` when the share/service is absent and otherwise denies access. Exports `SERVICE_CONTROL_OPS netlogon_svc_ops`.

Control flow: all svcctl operations are simple synchronous status or denial paths; no process is started or stopped.

State and persistence: reads Samba loadparm service configuration. It does not modify persistent or runtime service state.

Dependencies and integration: depends on `lp_servicenumber`, `SERVICE_STATUS`, SVCCTL constants, and the svcctl dispatch table. Tested indirectly by RPC svcctl/netlogon torture suites registered in `selftest/tests.py`.

Risks and test signals: service state is tied to whether `NETLOGON` is configured, not a live daemon state. Clients expecting Windows-like start/stop behavior receive access denied. Test signals are correct SCM status and error codes from svcctl RPC calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_rcinit.c -->
# sources/user-network-fs/samba/source3/services/svc_rcinit.c

Purpose: legacy/disabled Service Control Manager bridge for Unix rc/init scripts.

Important functions and APIs: `rcinit_stop()`, `rcinit_start()`, and `rcinit_status()` contain disabled `#if 0` implementations that would construct commands under `${MODULESDIR}/svcctl/<service>` and run them as root via `smbrun`. In compiled code, they return `WERR_ACCESS_DENIED` unless the disabled command path is re-enabled and succeeds. Exports `SERVICE_CONTROL_OPS rcinit_svc_ops`.

Control flow: current compiled control flow is denial-only. The disabled code shows the intended start/stop/status sequence, root transition, command execution, and `SERVICE_STATUS` population.

State and persistence: no runtime state changes in the active build. If re-enabled, it would execute external scripts and reflect their exit codes as service state.

Dependencies and integration: included in the svcctl operations ecosystem through `services.h`. The disabled path references `get_dyn_MODULESDIR`, `SVCCTL_SCRIPT_DIR`, `become_root`, `smbrun`, and service-control status constants.

Risks and test signals: the comments explicitly cite security concerns and unknown field use as the reason for disabling. Re-enabling would create a high-risk root command-execution surface. Current test signal is that start/stop/status through this backend are denied.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_rcinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_spoolss.c -->
# sources/user-network-fs/samba/source3/services/svc_spoolss.c

Purpose: internal Service Control Manager facade for Samba's spoolss/spooler state.

Important functions and APIs: `spoolss_stop()` zeroes the status, calls `lp_set_spoolss_state(SVCCTL_STOPPED)`, fills type `SERVICE_TYPE_INTERACTIVE_PROCESS | SERVICE_TYPE_WIN32_OWN_PROCESS`, and returns OK. `spoolss_start()` refuses when `lp__disable_spoolss()` is true, returns already-running if applicable, otherwise sets state running. `spoolss_status()` reports `lp_get_spoolss_state()`. Exports `spoolss_svc_ops`.

Control flow: start/stop do not launch or kill a separate process; they mutate Samba's configured spoolss state flag. Status reads that flag.

State and persistence: state is held in loadparm/runtime spoolss state through `lp_set_spoolss_state`/`lp_get_spoolss_state`. Persistence depends on how that state is backed elsewhere; this file does not write config.

Dependencies and integration: used by svcctl RPC handling and exercised indirectly by spoolss and svcctl torture tests. It depends on loadparm spoolss helpers and SVCCTL constants.

Risks and test signals: because stop is "not really" stopping an OS service, clients may observe Windows-compatible SCM responses without real process lifecycle changes. Test signals are correct start/stop/status error codes, especially disabled and already-running cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_spoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_winreg.c -->
# sources/user-network-fs/samba/source3/services/svc_winreg.c

Purpose: internal Service Control Manager facade for the winreg service.

Important functions and APIs: `winreg_stop()` and `winreg_start()` always return `WERR_ACCESS_DENIED`. `winreg_status()` zeroes the status, reports type `SERVICE_TYPE_WIN32_SHARE_PROCESS`, accepts no controls, and always reports `SVCCTL_RUNNING`. Exports `SERVICE_CONTROL_OPS winreg_svc_ops`.

Control flow: all operations are synchronous and side-effect free. The service is modeled as always running but not controllable by clients.

State and persistence: no local state or persistent storage. Status is constant.

Dependencies and integration: part of the svcctl service table and related to the registry service glue in `svc_winreg_glue.c`. RPC tests `rpc.winreg`, `rpc.samba3.winreg`, and `rpc.svcctl` registered in `selftest/tests.py` exercise this surface indirectly.

Risks and test signals: fixed running status can diverge from actual registry RPC availability if other subsystems fail. Expected SCM behavior is access denied for start/stop and running status for queries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_winreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_winreg_glue.c -->
# sources/user-network-fs/samba/source3/services/svc_winreg_glue.c

Purpose: glue layer between the service-control subsystem and the registry backend under `HKLM\SYSTEM\CurrentControlSet\Services`.

Important functions and APIs: `svcctl_gen_service_sd()` builds a default self-relative security descriptor with ACEs for World read, Power Users execute, Server Operators full, and Administrators full. `svcctl_get_secdesc()` opens `<Services>\<name>\Security`, queries value `Security`, and falls back to the generated default descriptor if missing. `svcctl_set_secdesc()` opens the service key, creates the `Security` subkey, and writes the descriptor. `svcctl_get_string_value()` reads string values from a service key. `svcctl_lookup_dispname()` and `svcctl_lookup_description()` return registry `DisplayName`/`Description` or defaults.

Control flow: all registry operations go through internal winreg RPC helpers (`dcerpc_winreg_int_hklm_openkey`, `dcerpc_winreg_query_sd`, `dcerpc_winreg_CreateKey`, `dcerpc_winreg_set_sd`, `dcerpc_winreg_query_sz`). Error handling maps NTSTATUS transport failures to internal errors and propagates WERROR registry failures.

State and persistence: security descriptors and string metadata persist in the Samba registry TDB/hive backing HKLM. Temporary allocations use talloc stack frames; policy handles are closed when valid.

Dependencies and integration: depends on messaging/auth session context, generated winreg NDR client bindings, security descriptor helpers, global SIDs, and svcctl callers. It is the persistence path for service ACLs and display metadata exposed over service-control RPC.

Risks and test signals: missing close of `hive_hnd` may be handled by helper lifetime but should be reviewed with the winreg API contract. Registry path creation and descriptor serialization are security-sensitive. Strong test signals come from svcctl security descriptor get/set RPC tests and registry metadata lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_winreg_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_winreg_glue.h -->
# sources/user-network-fs/samba/source3/services/svc_winreg_glue.h

Purpose: public header for service-control registry glue helpers.

Important functions and APIs: forward-declares `struct auth_session_info` and declares `svcctl_gen_service_sd`, `svcctl_get_secdesc`, `svcctl_set_secdesc`, `svcctl_get_string_value`, `svcctl_lookup_dispname`, and `svcctl_lookup_description`. The prototypes expose `messaging_context`, `auth_session_info`, `TALLOC_CTX`, `security_descriptor`, `WERROR`, and boolean success conventions.

Control flow: header-only; describes callable operations implemented in `svc_winreg_glue.c`.

State and persistence: documents the interface to persistent registry-backed service descriptors and metadata, but holds no state itself.

Dependencies and integration: included by svcctl server code and `svc_winreg_glue.c`. Callers must provide auth/session context because registry access is security-scoped.

Risks and test signals: pointer ownership is talloc-based and must be respected by callers, especially for returned strings and descriptors allocated on `mem_ctx`. Compile-time consistency and svcctl RPC tests are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_winreg_glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_wins.c -->
# sources/user-network-fs/samba/source3/services/svc_wins.c

Purpose: internal Service Control Manager facade for Samba's WINS service.

Important functions and APIs: `wins_status()` zeroes status, reports `SERVICE_TYPE_WIN32_OWN_PROCESS`, accepts no controls, and reports running only when `lp_we_are_a_wins_server()` is true; otherwise it reports stopped with `WERR_SERVICE_NEVER_STARTED`. `wins_stop()` refreshes status and denies access. `wins_start()` always denies access. Exports `wins_svc_ops`.

Control flow: status is a direct projection of configuration; start and stop do not mutate state.

State and persistence: reads loadparm WINS-server configuration but performs no writes.

Dependencies and integration: used by svcctl RPC service enumeration/control paths. It depends on SVCCTL constants and loadparm WINS helper state.

Risks and test signals: a configured WINS server is considered running regardless of deeper daemon health. Expected tests should assert status reflects configuration and start/stop return access denied.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/services/svc_wins.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbadduser.in -->
# sources/user-network-fs/samba/source3/smbadduser.in

Purpose: legacy C shell utility template for adding UNIX users to Samba password and username-map files.

Important functions and APIs: uses substituted install variables (`@prefix@`, `@libdir@`, `@privatedir@`, `@configdir@`), `getent passwd` by default, `awk`, `grep`, and `smbpasswd`. It expects arguments in `unixid:ntid` form.

Control flow: with no arguments it prints usage. It ensures `$PRIVATEDIR/smbpasswd` and `$CONFIGDIR/smbusers` exist, then iterates each mapping. For each entry it validates the colon format, extracts UNIX and NT IDs, checks the UNIX account exists, checks it is not already in smbpasswd, runs `smbpasswd -a -n unix`, appends a username-map line if UNIX and NT IDs differ, records the new UNIX name, and finally prompts interactively for each new user's password via `smbpasswd`.

State and persistence: mutates the private `smbpasswd` file and config `smbusers` map, and invokes `smbpasswd` to set password state.

Dependencies and integration: depends on C shell, local passwd database, old smbpasswd backend paths, and interactive terminal input. It is a compatibility/admin script, not part of automated selftest.

Risks and test signals: the script hard-codes `/usr/bin/smbpasswd` for initial add while later using PATH `smbpasswd`; it appends maps without locking and is not safe for concurrent edits. It should be considered legacy and high-risk in modern deployments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbadduser.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/avahi_register.c -->
# sources/user-network-fs/samba/source3/smbd/avahi_register.c

Purpose: registers Samba SMB, Time Machine disk, and device-info services with Avahi/mDNS for discovery by clients.

Important functions and APIs: defines `struct avahi_state_struct` holding Avahi poll, client, entry group, and SMB port. Provides a custom Avahi allocator backed by talloc (`avahi_allocator_malloc/free/realloc/calloc`) and installs it with `avahi_set_allocator`. `avahi_entry_group_callback()` logs group states. `avahi_client_callback()` handles Avahi client states and, when running, creates an entry group, registers `_smb._tcp`, optionally registers `_adisk._tcp` TXT records for shares with `fruit:time machine = yes`, registers `_device-info._tcp` with `fruit:model`, and commits the group. `avahi_start_register()` allocates state, creates a tevent-backed Avahi poll object, and starts an `AvahiClient`.

Control flow: Avahi drives asynchronous callbacks through the tevent poll bridge. On `AVAHI_CLIENT_S_RUNNING`, service registration is built from current loadparm state. On disconnected client failure, the code frees and recreates the Avahi client. Errors during any registration step log a debug message, free the entry group, and stop that registration attempt.

State and persistence: runtime-only mDNS registration state lives in Avahi client/entry-group objects under the supplied talloc context. It reads Samba configuration but does not persist settings.

Dependencies and integration: compiled when Avahi support is available; includes Avahi client/publish/common headers and `smbd/smbd.h`. It integrates with Samba loadparm (`lp_numservices`, `lp_snum_ok`, `lp_parm_bool`, `lp_const_servicename`, `lp_mdns_name`, `lp_netbios_name`, `lp_parm_const_string`) and tevent via `tevent_avahi_poll`.

Risks and test signals: `avahi_allocator_ctx` is global, so allocator lifetime and multiple registrations require care. Registration failure frees the whole entry group, which can remove already-added services. The `_adisk` TXT list grows from share enumeration and must be freed on all paths. Runtime signals are debug logs for Avahi state transitions and visible mDNS records for `_smb._tcp`, `_adisk._tcp`, and `_device-info._tcp`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/avahi_register.c -->
