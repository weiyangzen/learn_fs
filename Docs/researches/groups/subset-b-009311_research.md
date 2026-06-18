# subset-b-009311 research

Grouped code research for selected pynfs NFSv4.0 server tests, NFSv4.0 runner/setup helpers, and NFSv4.1 pNFS/client reboot helpers. Each source file has its own source-path-titled section wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_locku.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_locku.py

Purpose: Exercises NFSv4 `LOCKU` unlock behavior for regular files, partial ranges, invalid ranges, sequence-id handling, bad/stale/old lock stateids, and lease-expired unlock attempts.

Important APIs/types/functions: Imports `NFS4ERR_*` constants, `stateid4`, and `environment.check/makeStaleId`. Test entry points are `testFile`, `testUnlocked`, `testSplit`, `testOverlap`, `test32bitRange`, `testZeroLen`, `testLenTooLong`, `testNoFh`, `testBadLockSeqid*`, `testOldLockStateid`, `testBadLockStateid`, `testStaleLockStateid`, and `testTimedoutUnlock`. They use client helpers `init_connection`, `create_confirm`, `lock_file`, `relock_file`, `unlock_file`, `lock_test`, `getLeaseTime`, and `env.sleep`.

Control flow: Each test creates or opens a file, obtains a lock owner/stateid through `lock_file`, performs one unlock operation, and checks either success or a precise protocol error. Range tests vary offset/length; sequence tests deliberately reuse or skip lockseqid values; timeout tests sleep past the lease before unlocking.

State and persistence behavior: Mutates server lock state and open state under `env.c1`, with lease expiration as a persistent server-side state transition. Lock-owner sequenceids and lock stateids are the main state under test.

Dependencies and integration points: Depends on pynfs server-test environment, NFSv4 XDR constants, and a server that supports byte-range locks. Some tests depend on previous `MKFILE`, `LOCK*`, or timed/ganesha-specific flags from docstrings.

Risks: Timing-sensitive lease tests can be flaky if server lease reporting or sleep scheduling is imprecise. Some servers legitimately return `NFS4ERR_LOCK_RANGE` for non-matching unlocks; the tests distinguish support warnings from hard failures. Bad replay semantics are noted in comments for one sequence-id case.

Test signals: `check()` validates `NFS4_OK`, `NFS4ERR_DENIED`, `NFS4ERR_LOCK_RANGE`, `NFS4ERR_BAD_RANGE`, `NFS4ERR_INVAL`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, and `NFS4ERR_EXPIRED`; `t.fail`/`t.fail_support` mark stricter conformance expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_locku.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lookup.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_lookup.py

Purpose: Tests NFSv4 `LOOKUP` over the standard pynfs test tree and malformed component cases: existing object types, missing names, zero-length names, long names, non-directory current filehandles, inaccessible directories, dot components, invalid UTF-8, and malformed opaque XDR.

Important APIs/types/functions: Imports `environment.check/get_invalid_utf8strings`, `rpc.rpc`, and `nfs_ops.NFS4ops`. Public tests include `testDir`, `testFile`, `testLink`, `testBlock`, `testChar`, `testSocket`, `testFifo`, `testNoFh`, `testNonExistent`, `testZeroLength`, `testLongName`, `test*NotDir`, `testNonAccessable`, `testInvalidUtf8`, `testDots`, `testUnaccessibleDir`, and `testBadOpaque`.

Control flow: Tests build compound op lists with `c.use_obj`, `c.go_home`, `op.lookup`, `op.putrootfh`, `c.setattr`, and sometimes raw RPC/XDR manipulation. Most cases navigate to a parent filehandle, append one `LOOKUP`, and assert the terminal status.

State and persistence behavior: Creates temporary directories/children and changes mode to `0` for access-denial cases. Otherwise it reads stable fixture paths from `env.opts.usefile`, `usedir`, `uselink`, and device/socket/fifo variants.

Dependencies and integration points: Integrates with the pynfs environment's prebuilt test tree, invalid UTF-8 samples, and `nfs_ops` operation constructors. Raw RPC usage is limited to bad opaque array-length coverage.

Risks: Access tests depend on server permission enforcement and caller credentials. Dot-name behavior allows alternate standards-compatible outcomes (`BADNAME` or `NOENT`). Invalid UTF-8 and malformed XDR paths can vary between strict and permissive servers.

Test signals: Expected statuses include `NFS4_OK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_NOENT`, `NFS4ERR_INVAL`, `NFS4ERR_NAMETOOLONG`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_ACCESS`, `NFS4ERR_BADNAME`, and `NFS4ERR_BADXDR`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lookup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lookupp.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_lookupp.py

Purpose: Covers NFSv4 `LOOKUPP`, validating parent-filehandle recovery from directories, correct failure for non-directory current filehandles, behavior at root, no-current-filehandle handling, and cross-filesystem parent traversal.

Important APIs/types/functions: Uses `NFS4ops.lookupp/getfh/putrootfh/lookup`, `environment.check`, and fixture paths from `env.opts`. Test functions are `testDir`, `testFile`, `testFifo`, `testLink`, `testBlock`, `testChar`, `testSock`, `testAtRoot`, `testNoFh`, `testXdev`, and `testXdevHome`.

Control flow: Success cases save a filehandle with `GETFH`, descend with `LOOKUP`, call `LOOKUPP`, then compare the restored `GETFH` result. Failure cases build `use_obj(path) + [LOOKUPP]` against non-directories or call `LOOKUPP` without a filehandle.

State and persistence behavior: Creates a temporary child directory for the main parent equality test; otherwise uses static object paths and special cross-device fixture paths.

Dependencies and integration points: Relies on server-test path helpers, special filesystem fixture support for `usespecial`, and compound response array indexing to compare filehandles.

Risks: Symlink handling permits either `NFS4ERR_NOTDIR` or `NFS4ERR_SYMLINK`. Cross-filesystem parent behavior depends on how the export namespace maps mount roots and may be server-specific.

Test signals: Checks `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOENT`, and `NFS4ERR_NOFILEHANDLE`, plus direct `t.fail` when filehandles differ after parent traversal.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lookupp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_nverify.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_nverify.py

Purpose: Tests NFSv4 `NVERIFY`, the inverse of `VERIFY`, across mandatory attributes, object type attributes, deliberately changed sizes, no-current-filehandle handling, write-only attributes, and unsupported attributes for every standard test-tree object type.

Important APIs/types/functions: Helper functions `_try_mand`, `_try_type`, `_try_changed_size`, `_try_write_only`, and `_try_unsupported` feed dictionaries into `op.nverify`. The module imports `env.attr_info`, `c.do_getattrdict`, `c.supportedAttrs`, and constants such as `FATTR4_TYPE`, `FATTR4_SIZE`, `NF4REG`, `NF4DIR`, `NF4LNK`, `NF4BLK`, `NF4CHR`, `NF4FIFO`, and `NF4SOCK`.

Control flow: Helper functions construct a base `use_obj(path)` compound, append `NVERIFY`, and often append another `use_obj(path)` to confirm compound continuation or short-circuit behavior. Repeated public tests pass each fixture path and expected object type into the shared helpers.

State and persistence behavior: Read-only except for observing current attributes. It computes supported and unsupported masks dynamically from the server.

Dependencies and integration points: Integrates tightly with environment attribute metadata (`mandatory`, `writeonly`, `sample`, `mask`) and client attribute encoders.

Risks: Server-specific attribute support affects which unsupported cases run. A misleading message in `_try_unsupported` says `VERIFY` in one branch, but the operation is `NVERIFY`.

Test signals: Expects matching attributes to produce `NFS4ERR_SAME`, changed size to succeed (`NFS4_OK`), write-only attributes to return `NFS4ERR_INVAL`, unsupported attributes to return `NFS4ERR_ATTRNOTSUPP` or `INVAL` for write-only unsupported attributes, and no filehandle to return `NFS4ERR_NOFILEHANDLE`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_nverify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_open.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_open.py

Purpose: Broad NFSv4 `OPEN` conformance suite covering create modes, normal opens, non-regular-object failures, bad names, invalid/unsupported attributes, `CLAIM_PREVIOUS`, mode/share-deny conflicts, failed-open side effects, open upgrades, replay, and bad open sequence ids.

Important APIs/types/functions: Uses `environment.check/checkdict/get_invalid_utf8strings`, `nfs4lib.get_bitnumattr_dict`, and many client helpers including `create_confirm`, `create_file`, `open_file`, `open_confirm`, `close_file`, `read_file`, `write_file`, and `supportedAttrs`. Test functions run from `testOpen` through `testBadSeqid`.

Control flow: Tests usually initialize a client, build an `OPEN` compound via client wrappers, optionally confirm the open, then verify resulting filehandle/stateid, returned attributes, or expected failure status. Conflict tests use two clients or multiple open owners to trigger share-deny and open-mode behavior.

State and persistence behavior: Creates files under the test home, opens and closes stateids, mutates mode bits, and exercises server sequence/replay caches. Create tests inspect `FATTR4_SIZE`, `FATTR4_MODE`, link support, and returned attrsets.

Dependencies and integration points: Depends on server-test environment, prebuilt test-tree object paths, name/UTF-8 samples, and the pynfs client state machine for open-owner sequence tracking.

Risks: Share-deny and permission checks are sensitive to server policy and AUTH credentials. Replay tests can alter client-side seqid tracking. Some object-type docstrings say `SYMLINK` for block/char/socket/fifo failures, while checks expect protocol-specific statuses.

Test signals: Covers `NFS4_OK`, `NFS4ERR_EXIST`, `NFS4ERR_NOENT`, `NFS4ERR_ISDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_NAMETOOLONG`, `NFS4ERR_NOTDIR`, `NFS4ERR_ATTRNOTSUPP`, `NFS4ERR_RECLAIM_BAD`, `NFS4ERR_NO_GRACE`, `NFS4ERR_ACCESS`, `NFS4ERR_SHARE_DENIED`, `NFS4ERR_OPENMODE`, `NFS4ERR_LOCKED`, and `NFS4ERR_BAD_SEQID`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_openconfirm.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_openconfirm.py

Purpose: Tests NFSv4 `OPEN_CONFIRM` behavior for successful create-confirm flow, duplicate confirmation, missing filehandle, bad seqid, bad stateid, and stale stateid.

Important APIs/types/functions: Imports `stateid4`, `makeStaleId`, `nfs_ops.NFS4ops`, and `environment.check`. `_confirm` builds `use_obj(file) + [open_confirm]` using the current owner seqid. Public tests are `testConfirmCreate`, `testNoFh`, `testBadSeqid`, `testBadStateid`, and `testStaleStateid`.

Control flow: Tests create an unconfirmed open with `create_file`, extract the returned filehandle/stateid/rflags, and send explicit `OPEN_CONFIRM` operations. Error cases alter the filehandle, seqid, or stateid before confirmation.

State and persistence behavior: Mutates open-owner seqids and open state. A duplicate confirmation should fail because the state is already confirmed.

Dependencies and integration points: Relies on client wrapper internals such as `c.get_seqid(t.word())`, response-array indexes for OPEN results, and NFSv4 servers that may or may not set `OPEN4_RESULT_CONFIRM`.

Risks: Servers not requiring confirmation produce warning paths. Sequence-id expectations are tied to pynfs client-owner tracking.

Test signals: Checks `NFS4ERR_BAD_STATEID` for duplicate/bad stateid, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_SEQID`, and `NFS4ERR_STALE_STATEID`, with success for valid confirmation.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_openconfirm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_opendowngrade.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_opendowngrade.py

Purpose: Validates `OPENDOWNGRADE` for regular files, invalid downgrades to unopened access modes, bad seqids/stateids, stale/old stateids, missing current filehandle, complex upgrade/downgrade sequences, and interaction with locks.

Important APIs/types/functions: Imports constants and `makeStaleId`. Public tests include `testRegularOpen`, `testNewState1`, `testNewState2`, `testBadSeqid`, `testBadStateid`, `testStaleStateid`, `testOldStateid`, `testNoFh`, `testOpenDowngradeSequence`, and `testOpenDowngradeLock`. The local `open_sequence` class wraps `open`, `downgrade`, `close`, and `lock` state transitions.

Control flow: Basic cases create/open a file, call `downgrade_file`, and assert status. Sequence tests repeatedly open with READ/WRITE/BOTH access, downgrade to narrower access, and close. Lock interaction opens, locks with `READ_LT`, downgrades, then closes.

State and persistence behavior: Mutates open-owner seqids, open share access, stateids, and optionally lock state. `open_sequence.downgrade` updates its stored stateid from the response.

Dependencies and integration points: Uses pynfs client open/downgrade wrappers and NFSv4 share access constants. Tests depend on normal `MKFILE` setup and lock support.

Risks: The helper does not check every intermediate result explicitly in complex sequences, so exceptions or wrapper assertions are the primary failure signal there. Sequence-id behavior depends on client wrapper tracking.

Test signals: Expected statuses include `NFS4_OK`, `NFS4ERR_INVAL`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_OLD_STATEID`, and `NFS4ERR_NOFILEHANDLE`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_opendowngrade.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_putfh.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_putfh.py

Purpose: Tests `PUTFH` by round-tripping filehandles for every standard object type, then checking bad and stale filehandle error handling.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops`, `environment.check`, and helper `_try_put(t, c, path)`. Public tests cover file, symlink, block, char, directory, fifo, socket, `testBadHandle`, and `testStaleHandle`.

Control flow: `_try_put` looks up a path, obtains its handle with `GETFH`, then issues `PUTFH(oldfh), GETFH` and compares returned handles. Bad-handle tests feed `b'abc'`; stale-handle tests create, close, remove, and reuse an old handle.

State and persistence behavior: Mostly read-only except the stale-handle test, which creates and removes a file to invalidate a handle.

Dependencies and integration points: Relies on fixture paths and response-array access to `switch.switch.object`. Stale handling is marked ganesha-specific because servers may keep removed filehandles valid.

Risks: Stale filehandle behavior is not universally deterministic across servers/export implementations. The failure message joins byte paths using text `'/'.join(path)`, which may be fragile on Python 3 if reached.

Test signals: Checks success for valid handles, `NFS4ERR_BADHANDLE` for malformed handles, and `NFS4ERR_STALE` for removed handles in the optional stale test.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_putfh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_putpubfh.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_putpubfh.py

Purpose: Tests support for `PUTPUBFH` and compares the public filehandle with the root filehandle as an RFC "should" condition.

Important APIs/types/functions: Imports NFS constants, `environment.check`, and `nfs_ops.NFS4ops`. Test functions are `testSupported` and `testSameAsRoot`.

Control flow: `testSupported` sends a single `PUTPUBFH`. `testSameAsRoot` obtains `GETFH` after `PUTPUBFH`, obtains `GETFH` after `PUTROOTFH`, and compares the opaque handles.

State and persistence behavior: Read-only server namespace operation; it only changes the compound current filehandle.

Dependencies and integration points: Uses the server's public filehandle support and root filehandle semantics. Integrated with test flags `putpubfh` and dependency on `PUB1`.

Risks: The spec comparison is advisory, so mismatch calls `t.pass_warn` instead of failing. Some NFSv4 servers may not expose a distinct public handle concept.

Test signals: `check()` validates operation success; mismatched root/public handles produce a warning rather than a failure.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_putpubfh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_putrootfh.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_putrootfh.py

Purpose: Minimal conformance test that verifies the server accepts `PUTROOTFH`.

Important APIs/types/functions: Imports constants, `environment.check`, and `nfs_ops.NFS4ops`; exposes one test, `testSupported`.

Control flow: Builds a compound containing only `op.putrootfh()` and checks for success.

State and persistence behavior: Read-only; updates only the current filehandle within the compound to the root filehandle.

Dependencies and integration points: This is a foundational operation used by many other path traversal helpers in the server-test suite.

Risks: Low implementation risk; failures usually indicate fundamental export/root namespace setup problems.

Test signals: A single `check(res)` is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_putrootfh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_read.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_read.py

Purpose: Tests NFSv4 `READ` semantics for normal reads, stateid zero/one/open-stateid, large counts and offsets, zero count, non-file objects, missing filehandles, bad/stale/old stateids, stolen stateids, and multi-read large-data behavior.

Important APIs/types/functions: Imports `check`, `makeBadID`, `makeBadIDganesha`, `makeStaleId`, and `rpc.rpc`. `_compare` validates returned data prefix and EOF behavior. Public tests include `testSimpleRead`, `testStateidOnes`, `testWithOpen`, `testLargeCount`, `testLargeOffset`, `testVeryLargeOffset`, `testZeroCount`, object-type failures, `testBadStateidGanesha`, `testStaleStateid`, `testOldStateid`, `testStolenStateid`, and `testLargeMultipleRead`.

Control flow: Tests call `c.read_file` on fixture paths or freshly created filehandles, then `_compare` the returned bytes and EOF flag. Stateid tests create/confirm opens and mutate or reuse stateids.

State and persistence behavior: Mostly read-only, with setup creating sparse or zero-filled files and changing client security temporarily for stolen-stateid coverage.

Dependencies and integration points: Relies on `env.filedata`, fixture object paths, client helpers for open/confirm, and AUTH_SYS credential manipulation.

Risks: Large read tests can stress memory and server transfer limits. EOF expectations and symlink/non-file status alternatives vary by server.

Test signals: Checks `NFS4_OK`, `NFS4ERR_ISDIR`, `NFS4ERR_INVAL`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_ACCESS`, and `NFS4ERR_PERM`, plus direct byte/EOF failures from `_compare`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_readdir.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_readdir.py

Purpose: Exercises `READDIR` for empty and populated directories, requested attributes, cookie continuation, non-directory current filehandles, missing filehandles, count limits, dircount behavior, write-only attributes, reserved cookies, and inaccessible directories.

Important APIs/types/functions: Imports `get_attr_name` and `environment.check`. `_compare` validates returned entry names and exact requested attribute sets; `_try_notdir` centralizes non-directory checks. Public tests run from `testEmptyDir` through `testUnaccessibleDirAttrs`.

Control flow: Tests create directory trees with `c.maketree`, call `c.do_readdir` or explicit `c.readdir`, and check returned entries/cookies/errors. Attribute tests compare `e.attrdict` against requested lists.

State and persistence behavior: Creates temporary directory trees and changes mode to `0` for access-denial tests. It observes directory cookies and verifier/count behavior returned by the server.

Dependencies and integration points: Uses environment attribute metadata and client helpers for tree creation, `READDIR` construction, and supported attributes.

Risks: The `testSubsequent` loop decreases `maxcount` until cookie counts split; unusual servers may make this slow or fail to split. Access-denial behavior is credential and export-policy sensitive. Attribute filtering can expose server bugs or unsupported optional attributes.

Test signals: Expects `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_TOOSMALL`, `NFS4ERR_INVAL`, `NFS4ERR_BAD_COOKIE`, and `NFS4ERR_ACCESS`; `_compare` calls `t.fail` for entry or attribute mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_readdir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_readlink.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_readlink.py

Purpose: Tests `READLINK` success on symlinks and expected failures on non-symlink object types and missing current filehandle.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.readlink`, `environment.check`, and fixture paths from `env.opts`.

Control flow: `testReadlink` performs `use_obj(uselink) + READLINK`, extracts `link` from the final result, and compares it to `env.linkdata`. Other tests call `READLINK` against file, block, char, directory, fifo, socket, or no filehandle.

State and persistence behavior: Read-only; no filesystem mutations.

Dependencies and integration points: Depends on a configured symlink fixture with expected `env.linkdata` and standard object fixtures for negative cases.

Risks: Some servers may return alternate errors for special files, but this module expects `NFS4ERR_INVAL` for all non-symlink object types.

Test signals: Success for symlink, `NFS4ERR_INVAL` for non-symlinks, `NFS4ERR_NOFILEHANDLE` when no current filehandle exists, and direct `t.fail` on link-target mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_readlink.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_reboot.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_reboot.py

Purpose: Optional, non-default NFSv4.0 server reboot/grace-period suite covering `CLAIM_PREVIOUS`, stale clientids after reboot, multiple clients, late reclaims, RFC edge cases for lock reclaim, root-squash preservation, delegation reclaim, repeated reboots, and grace-period seqid handling.

Important APIs/types/functions: `_waitForReboot` reads lease time, calls `env.serverhelper(b"reboot")`, waits with `c.null()`, and returns an estimated grace wait. Public tests include `testRebootValid`, `testManyClaims`, `testRebootWait`, `testEdge1`, `testEdge2`, `testRootSquash`, `testValidDeleg`, `testRebootMultiple`, and `testGraceSeqid`.

Control flow: Tests create confirmed opens or locks, reboot the server through the environment helper, then try `OPEN` with `CLAIM_PREVIOUS` before/during/after grace. `finally` blocks sleep until grace ends to avoid poisoning later tests.

State and persistence behavior: Intentionally destroys and reclaims server state across reboot. It relies on persistent filehandles/files surviving reboot and server lock/clientid databases being reset according to the protocol.

Dependencies and integration points: Requires configured `serverhelper`, real server reboot support, lease time reporting, optional delegation helper from `st_delegation`, AUTH_SYS root setup for root-squash testing, and multiple clients.

Risks: Highly timing- and environment-sensitive. It can disrupt other tests and is not part of the standard suite. Incorrect grace cleanup can leave the server in a transient state for subsequent tests.

Test signals: Checks `NFS4_OK`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_NO_GRACE`, `NFS4ERR_RECLAIM_BAD`, and `NFS4ERR_GRACE`, plus owner/delegation comparisons and support failures when prerequisites are missing.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_reboot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_releaselockowner.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_releaselockowner.py

Purpose: Tests `RELEASE_LOCKOWNER` for a normal unlocked owner, an owner whose file has been removed after unlock, and rejection while locks are still held.

Important APIs/types/functions: Imports `lock_owner4`, `nfs_ops.NFS4ops.release_lockowner`, and `environment.check`. Public tests are `testFile`, `testFile2`, and `testLocksHeld`.

Control flow: Each test initializes a connection, creates a confirmed file, locks it with a named lock owner, and either unlocks before release or attempts release while the lock remains. `testFile2` removes the file before releasing the lock owner.

State and persistence behavior: Mutates lock owner state, lock records, and in one case removes the locked file after unlocking.

Dependencies and integration points: Depends on lock support and the client's current confirmed `clientid` to construct `lock_owner4(c.clientid, owner_bytes)`.

Risks: Servers that garbage collect lock owners aggressively or tie owners to removed files differently may expose edge behavior. The test expects locks-held protection before owner release.

Test signals: Success for unlocked release paths and `NFS4ERR_LOCKS_HELD` when trying to release an owner with an active lock.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_releaselockowner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_remove.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_remove.py

Purpose: Tests NFSv4 `REMOVE` for all removable object types, non-directory current filehandle errors, missing filehandle, zero-length and invalid UTF-8 target names, nonexistent targets, dot names, and nonempty directory removal.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.remove`, `environment.check/get_invalid_utf8strings`, and object constants `NF4LNK`, `NF4BLK`, `NF4CHR`, `NF4FIFO`, and `NF4SOCK`. Public tests run from `testDir` through `testNotEmpty`.

Control flow: Positive tests create an object under `c.homedir`, then run `use_obj(parent) + REMOVE(name)`. Negative tests point the current filehandle at non-directories, use invalid names, or build a nonempty directory before removal.

State and persistence behavior: Creates and removes filesystem objects under the test directory; mode and invalid-name tests are otherwise local to temporary paths.

Dependencies and integration points: Depends on create helpers for special objects and fixture paths for existing non-directory current filehandles.

Risks: Invalid UTF-8 coverage is ganesha-flagged. Dot-name behavior permits either `BADNAME` or `NOENT`. Extra indented legacy methods appear after the main tests and look like disabled/unreachable ported test fragments.

Test signals: Checks `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_NOENT`, `NFS4ERR_BADNAME`, and `NFS4ERR_NOTEMPTY`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_remove.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_rename.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_rename.py

Purpose: Comprehensive `RENAME` suite covering valid renames for regular and special objects, source/current filehandle non-directory failures, no source filehandle, nonexistent and invalid names, dot names, overwriting directories/files, no-op self renames, hard-link renames, and closing an open target after replacement.

Important APIs/types/functions: Uses `environment.check/get_invalid_utf8strings`, `c.rename_obj`, `c.maketree`, `c.create_obj`, `c.link`, and object constants for symlink/block/char/fifo/socket creation. Public tests include `testValid*`, `testSfh*`, `testCfh*`, `testNoSfh`, `testNonExistent`, name validation tests, overwrite matrix tests, `testSelfRenameDir`, `testSelfRenameFile`, `testLinkRename`, and `testStaleRename`.

Control flow: Positive tests create source and target directories then call `rename_obj(old, new)`. Negative tests deliberately set source or target parent to non-directories or pass invalid old/new components. No-op tests inspect returned source and target change-info values.

State and persistence behavior: Performs filesystem namespace mutations and observes change info before/after values. `testStaleRename` keeps an open stateid across replacement and confirms close still succeeds.

Dependencies and integration points: Depends on server hard-link support for `testLinkRename`, special object creation support, and name validation samples.

Risks: Several checks accept POSIX-vs-RFC alternatives (`EXIST` vs `NOTDIR`/`ISDIR`, `BADNAME` vs `OK`). Disabled/indented legacy extra tests remain at the bottom and are not normal module-level tests.

Test signals: Expected statuses include `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_NOENT`, `NFS4ERR_INVAL`, `NFS4ERR_BADNAME`, `NFS4ERR_EXIST`, `NFS4ERR_ISDIR`, and `NFS4ERR_NOTEMPTY`, plus direct failures on unexpected change-info changes.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_rename.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_renew.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_renew.py

Purpose: Tests NFSv4 `RENEW` for a valid clientid, a stale/bad clientid, and an expired lease.

Important APIs/types/functions: Imports `nfs_ops.NFS4ops.renew` and `environment.check`; exposes `testRenew`, `testBadRenew`, and `testExpired`.

Control flow: `testRenew` initializes a client and renews its `clientid`. `testBadRenew` renews clientid `0`. `testExpired` creates deny state, sleeps for twice the lease time, lets another client open the file, then renews with the original client.

State and persistence behavior: Mutates and observes client lease state. The expired test intentionally lets a lease lapse and introduces another client to force conflict/state expiration.

Dependencies and integration points: Uses lease time from the client wrapper, two environment clients, and open/share deny state.

Risks: Timing-sensitive and can be affected by server grace/lease implementation. Sleeping twice the lease time may slow runs.

Test signals: Expects success for valid renew, `NFS4ERR_STALE_CLIENTID` for bad clientid, and `NFS4ERR_EXPIRED` after lease expiry.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_renew.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_replay.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_replay.py

Purpose: Tests duplicate request cache/replay behavior by sending repeated compounds with the same XID for stateful and non-stateful operations including `OPEN`, failed opens/lookups, `LOCK`, denied locks, `LOCKU`, `CLOSE`, `OPEN_CONFIRM`, and directory `CREATE`.

Important APIs/types/functions: `_replay(env, c, ops, error=NFS4_OK)` captures `c.xid`, temporarily overrides `c.get_new_xid`, sleeps between repeats, and checks that replayed calls return the same status. Tests use XDR types such as `exist_lock_owner4`, `locker4`, `createtype4`, and operations from `nfs_ops`.

Control flow: Each public test builds an operation list, calls `_replay`, and relies on duplicate XID reuse to trigger server replay cache behavior. Some tests first create locks/open state and then replay a conflicting or cleanup operation.

State and persistence behavior: Mutates open, lock, close, and create state and exercises server duplicate request cache persistence. Timed variants sleep past the lease before replaying.

Dependencies and integration points: Relies on pynfs client internals (`xid`, `get_new_xid`) and server DRC timing. Comments note Linux may drop too-fast replays and that this imitates a buggy client.

Risks: Replay semantics are transport/server-implementation sensitive and can be flaky. Overriding XID generation can disturb later client sequence expectations if not restored; the helper uses `finally`.

Test signals: Expects stable replay of `NFS4_OK`, `NFS4ERR_NOENT`, `NFS4ERR_ISDIR`, `NFS4ERR_DENIED`, `NFS4ERR_EXPIRED`, and `NFS4ERR_BAD_SEQID` depending on the original call.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_replay.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_restorefh.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_restorefh.py

Purpose: Tests `SAVEFH`/`RESTOREFH` round-tripping for all standard object types and `RESTOREFH` errors when no saved filehandle exists.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.savefh/restorefh/getfh/putrootfh`, `environment.check`, and helper `_try_sequence`.

Control flow: `_try_sequence` navigates to a path, records `GETFH`, calls `SAVEFH`, switches current filehandle to root, restores saved filehandle, obtains `GETFH` again, and compares both handles. Error tests call `RESTOREFH` without a saved handle, with and without a current root filehandle.

State and persistence behavior: Only compound-local filehandle stack state is mutated; filesystem is read-only.

Dependencies and integration points: Depends on fixture paths for file, directory, fifo, link, block, char, and socket objects.

Risks: Response-array indexing assumes all intermediate operations succeed and remain in a fixed order. Failure message uses saved/restored filehandle comparison as the strongest signal.

Test signals: Success for valid save/restore sequences and `NFS4ERR_RESTOREFH` when there is no saved filehandle.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_restorefh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_savefh.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_savefh.py

Purpose: Minimal negative test for `SAVEFH` without a current filehandle; positive save/restore behavior is covered in `st_restorefh.py`.

Important APIs/types/functions: Imports `nfs_ops.NFS4ops.savefh` and `environment.check`; exposes `testNoFh`.

Control flow: Sends a compound containing only `SAVEFH` and expects failure because no current filehandle has been established.

State and persistence behavior: No filesystem persistence; only tests compound-local filehandle preconditions.

Dependencies and integration points: Complements `st_restorefh.py` and shares `savefh` test flags.

Risks: Low; a failure indicates fundamental current-filehandle precondition handling.

Test signals: Expects `NFS4ERR_NOFILEHANDLE`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_savefh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_secinfo.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_secinfo.py

Purpose: Tests NFSv4 `SECINFO` for an existing file, non-directory current filehandle, nonexistent child, missing filehandle, zero-length and invalid UTF-8 names, and presence of RPCSEC_GSS mechanisms.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.secinfo`, `environment.check/get_invalid_utf8strings`, and fixture path `env.opts.usefile`. Tests are `testValid`, `testNotDir`, `testVaporFile`, `testNoFh`, `testZeroLenName`, `testInvalidUtf8`, and `testRPCSEC_GSS`.

Control flow: Successful tests navigate to the parent directory and call `SECINFO(filename)`, then inspect the returned mechanism list. Error cases call `SECINFO` with wrong current filehandle or invalid name components.

State and persistence behavior: Creates temporary directories for vapor/invalid-name cases but otherwise reads server security metadata.

Dependencies and integration points: Integrates with server security-flavor configuration. `testRPCSEC_GSS` assumes at least one returned mechanism has flavor `6`.

Risks: Security mechanism availability is export/server-specific; RPCSEC_GSS may not be configured in all test environments. Invalid UTF-8 behavior is ganesha-flagged.

Test signals: Checks success and non-empty mechanism lists, `NFS4ERR_NOTDIR`, `NFS4ERR_NOENT`, `NFS4ERR_NOFILEHANDLE`, and `NFS4ERR_INVAL`; direct failure if RPCSEC_GSS flavor is absent where required.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_secinfo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_setattr.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_setattr.py

Purpose: Large `SETATTR` conformance suite covering mode changes, size changes, mixed size/owner changes, stateid handling, no filehandle, read-only/unsupported attributes, malformed attribute XDR, invalid UTF-8 principals, invalid timestamps, max size, non-file size setting, change attribute updates, and empty owner/group principals.

Important APIs/types/functions: Helpers `_set_mode`, `_set_size`, `_set_mixed`, `_try_readonly`, `_try_unsupported`, and `check_res` centralize mutation and verification. Imports `bitmap2list`, `dict2fattr`, `nfstime4`, `settime4`, `nfs_ops`, and many `FATTR4_*` constants.

Control flow: Common helpers issue `use_obj(file) + SETATTR`, verify status, compare `attrsset` against requested attributes, then refetch attributes with `do_getattrdict`. Public tests create target objects of different types and call helpers or build malformed `fattr4` payloads.

State and persistence behavior: Mutates file modes, sizes, ownership metadata, time metadata, and change attributes. Several tests create special objects and truncate files.

Dependencies and integration points: Depends on dynamic server supported-attribute masks, environment attribute metadata, object creation support, and correct XDR packing/unpacking in `nfs4lib`.

Risks: Attribute support and permission policy vary widely by server and export. `testInodeLocking` is explicitly risky in comments because it historically exposed kernel inode-locking bugs. `check_res` references `get_bitnumattr_dict()` without importing it, which may be a latent bug if unexpected attrs are returned.

Test signals: Checks `NFS4_OK`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_OPENMODE`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_ATTRNOTSUPP`, `NFS4ERR_BADXDR`, `NFS4ERR_FBIG`, `NFS4ERR_ISDIR`, and `NFS4ERR_SYMLINK`, plus direct failures on attrset/getattr mismatch and unchanged change attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_setattr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_setclientid.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_setclientid.py

Purpose: Tests NFSv4.0 `SETCLIENTID` state-machine cases: valid initialization, client reboot invalidating old state, callback-info update, duplicate client ids across principals, lost replies, RFC case matrix, confirmed/unconfirmed replacement rules, many clients, and unconfirmed clientid use.

Important APIs/types/functions: Imports `os`, `struct`, `time`, `nfs_ops`, and `environment.check`. `_checkprinciples` is a stub that always returns true. Tests use `c.init_connection`, `c.setclientid`, `op.setclientid_confirm`, response fields `clientid` and `setclientid_confirm`, and owner ids built from pid/test names.

Control flow: Most tests call `init_connection` to create confirmed client records, send additional `SETCLIENTID` requests with same/different verifier bytes, and assert whether clientids/confirm verifiers are replaced or stale. Some tests create file state to make a client id active before duplicate-id checks.

State and persistence behavior: Heavily mutates server client records, confirmed and unconfirmed records, callback info, open state, and clientid-confirm verifiers.

Dependencies and integration points: Uses the pynfs client's SETCLIENTID/CONFIRM wrappers and response-array internals. Tests requiring different principals are limited by `_checkprinciples` being unimplemented.

Risks: Clientid replacement behavior is subtle and server-specific bugs are easy to expose. The principal-check stub weakens coverage for `CLID_INUSE` scenarios. `testLotsOfClients` creates 1024 client records and can be expensive.

Test signals: Checks success, `NFS4ERR_CLID_INUSE`, `NFS4ERR_EXPIRED`, and `NFS4ERR_STALE_CLIENTID`; direct failures validate zero confirm verifiers, reused clientids, reused confirms, and stale unconfirmed records.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_setclientid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_setclientidconfirm.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_setclientidconfirm.py

Purpose: Tests `SETCLIENTID_CONFIRM` error and state-machine behavior for unknown clientids, a case not covered by the RFC, and selected RFC confirmation cases.

Important APIs/types/functions: Imports `os`, `nfs_ops.NFS4ops.setclientid_confirm`, and `environment.check`. Public tests are `testStale`, `testBadConfirm`, and `testAllCases`.

Control flow: `testStale` confirms clientid `0`. `testBadConfirm` initializes a client, sends another `SETCLIENTID`, then reconfirms the first pair. `testAllCases` sequences confirmations and new `init_connection` calls with different verifiers.

State and persistence behavior: Mutates confirmed and unconfirmed clientid records and confirm verifiers.

Dependencies and integration points: Tightly coupled to the pynfs client initialization helper and raw `SETCLIENTID_CONFIRM` op constructor.

Risks: Some behavior is explicitly marked ganesha or "case not covered in RFC"; portability may vary. The final RFC-case sequence is more of an execution path check than exhaustive validation.

Test signals: `NFS4ERR_STALE_CLIENTID` for unknown/stale confirmations and success for accepted confirmation transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_setclientidconfirm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_spoof.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_spoof.py

Purpose: Manual/security-oriented tests for spoofing user access or filehandles, using supplied `--usefile`, `--uid`, `--gid`, and `--usefh` options.

Important APIs/types/functions: Uses `environment.check` and client helpers `open_confirm`, `read_file`, `write_file`, and `close_file`. `_convert` decodes command-line filehandle strings containing `\xhh` escape sequences into raw bytes.

Control flow: `testSpoofUser` reads and writes a configured file through opens with read and write access. `testSpoofFhRead` and `testSpoofFhWrite` convert an externally supplied filehandle and attempt direct I/O using stateid zero/defaults.

State and persistence behavior: Mutates the configured target file in spoof-user and spoof-write tests. Direct filehandle tests may access objects outside the normal test tree if a user supplies such a handle.

Dependencies and integration points: Requires explicit test options and server/export security configuration. These tests are not safe generic conformance tests; they are diagnostic probes.

Risks: Can overwrite user-selected files. `_convert` uses `eval` to parse hex escapes and returns a text string in Python 3 style code, which can be unsafe/incorrect for raw bytes. The module assumes the user intentionally supplies sensitive paths/handles.

Test signals: Success or failure comes from `check()` around read/write/close operations; no specific error status is asserted for spoof blocking.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_spoof.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_verify.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_verify.py

Purpose: Tests NFSv4 `VERIFY` across mandatory attributes, object type attributes, deliberately incorrect sizes, no-current-filehandle handling, write-only attributes, and unsupported attributes for standard object types.

Important APIs/types/functions: Mirrors `st_nverify.py` with helpers `_try_mand`, `_try_type`, `_try_changed_size`, `_try_write_only`, and `_try_unsupported`, but calls `op.verify`. Uses `env.attr_info`, `c.do_getattrdict`, and `c.supportedAttrs`.

Control flow: Matching mandatory/type attributes are verified and followed by another path use to confirm compound continuation. Changed-size tests increment `FATTR4_SIZE` and expect `VERIFY` to fail with `NOT_SAME`. Attribute-class tests iterate environment metadata over all fixture object types.

State and persistence behavior: Read-only except for observing live attributes. Supported attribute masks are dynamically queried.

Dependencies and integration points: Integrates with NFSv4 attribute descriptors from the environment and operation constructors from `nfs_ops`.

Risks: Attribute availability and write-only handling differ between servers. Imports `get_invalid_clientid` and `makeStaleId` are unused, suggesting copy/paste from related stateid tests.

Test signals: Expects success for matching attributes, `NFS4ERR_NOT_SAME` for changed size, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL` for write-only attrs, and `NFS4ERR_ATTRNOTSUPP` or `INVAL` for unsupported write-only attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_write.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_write.py

Purpose: Tests NFSv4 `WRITE` for sync modes, zero and max data, file growth, open stateids, non-file errors, missing filehandle, open-mode/share-deny enforcement, bad/stale/old/stolen stateids, compound writes, large write/read combinations, change attribute granularity, and varied write sizes.

Important APIs/types/functions: Imports XDR types, `check`, `compareTimes`, `makeBadID*`, `makeStaleId`, `struct`, `rpc.rpc`, and `nfs_ops`. `_compare` validates write count/committed/verifier and readback data; `_get_iosize` reads `FATTR4_MAXREAD/MAXWRITE`.

Control flow: Tests create or open files, call `c.write_file` or explicit `op.write`, then often read back data and compare. Large and compound tests build multiple `READ`/`WRITE` ops in one compound. Stateid tests mutate credentials or stateid values.

State and persistence behavior: Writes file data, grows/truncates files, updates change/time metadata, and changes open/share/lock-related server state. `testStolenStateid` temporarily replaces client security credentials.

Dependencies and integration points: Depends on server I/O size attributes, stable write semantics, AUTH_SYS credential behavior, and pynfs XDR packing.

Risks: Large-data tests can be expensive. Some code has Python 3 division/string issues (`maxread/4`, `data = ""` with `struct.pack` bytes) that may be latent in rarely run ganesha tests. Server maxwrite and sync verifier behavior can vary.

Test signals: Checks `NFS4_OK`, `NFS4ERR_ISDIR`, `NFS4ERR_INVAL`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_OPENMODE`, `NFS4ERR_LOCKED`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_ACCESS`, and `NFS4ERR_PERM`, plus byte/count/commit/change-attribute comparisons.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_write.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/setup.py -->
# sources/test-tools/pynfs/nfs4.0/setup.py

Purpose: setuptools packaging script for the NFSv4.0 pynfs package, with eager generation of Python XDR support files from `.x` definitions before packaging/install.

Important APIs/types/functions: Imports `setuptools.setup`, `setuptools.modified.newer_group` or legacy `setuptools.dep_util.newer_group`, `glob`, `xdrgen`, `use_local`, and `VERSION` from `testserver`. Functions are `needs_updating(xdrfile)`, `use_xdr(dir, xdrfile)`, and `generate_files()`.

Control flow: On import/execution it adjusts `sys.path` when run from the package root, falls back to `use_local` if `xdrgen` is not importable, calls `generate_files()` unconditionally, then invokes `setup()`. `generate_files` regenerates NFSv4, NFSv3, RPC, and GSS XDR modules if source `.x` files are newer than generated `_const.py`, `_type.py`, and `_pack.py` targets.

State and persistence behavior: Changes process working directory while generating files, writes generated Python modules via `xdrgen.run`, and deletes parser artifacts matching `parse*` in each XDR directory. Packaging metadata installs packages from `lib`.

Dependencies and integration points: Integrates with local `xdrgen`, `testserver.VERSION`, `lib/testmod.py`, `xdrdef`, `lib/rpc`, and setuptools. Scripts installed are `testserver.py` and `showresults.py`.

Risks: Unconditional generation during setup import can mutate the source tree unexpectedly. Working-directory changes require the final `os.chdir(home)` path to run. Deleting `parse*` is broad within target directories.

Test signals: No direct tests; success is observable through generated XDR modules being current and `setup()` completing. Install mode prints `PYTHONPATH` guidance.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/showresults.py -->
# sources/test-tools/pynfs/nfs4.0/showresults.py

Purpose: CLI utility to redisplay pickled pynfs server-test results with configurable pass/warn/fail/omit visibility.

Important APIs/types/functions: Imports `pickle`, `testmod`, and `OptionParser`. Functions are `show(filename, opt)`, `scan_options(p)`, and `main()`.

Control flow: When run directly, it adjusts `sys.path` for package-root execution, parses display options, requires one or more filenames, unpickles each file, and passes the loaded test list to `testmod.printresults`.

State and persistence behavior: Read-only against result pickle files; no output files are written.

Dependencies and integration points: Consumes pickle files written by `testserver.py --outfile`. Depends on `testmod.printresults` and compatible pickled test object classes.

Risks: Loading pickle files executes Python pickle deserialization and must not be used on untrusted files. The direct-run path check refers to `nfs4.1/testmod.py`, which looks suspicious for an NFSv4.0 script and may be stale.

Test signals: CLI errors if no filename is supplied. Successful operation is printed result summaries respecting `--show*`/`--hide*` flags.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/showresults.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/testserver.py -->
# sources/test-tools/pynfs/nfs4.0/testserver.py

Purpose: Main NFSv4.0 pynfs server test runner. It parses server URL/options, builds the test database, selects tests by flags/codes, initializes the test environment, runs tests, prints and optionally serializes results.

Important APIs/types/functions: Imports `nfs4lib`, `testmod`, `servertests.environment`, `rpc.rpc`, `pickle`, `socket`, and `optparse`. Key functions/classes are `unixpath2comps`, `scan_options`, `Argtype`, `run_filter`, `printflags`, and `main`. Constants include `VERSION`, `HOST`, `UID`, and `GID`.

Control flow: `main` parses options, creates tests via `testmod.createtests('servertests')`, handles informational listing modes, parses `SERVER:/PATH`, normalizes `--use*` paths, maps security flavor to RPC auth classes, converts remaining args to include/exclude flag/code selectors, initializes `environment.Environment`, runs `testmod.runtests`, pickles output if requested, finalizes environment, prints results, and writes JSON/XML if requested.

State and persistence behavior: Mutates `nfs4lib.SHOW_TRAFFIC`, environment debug flags, option fields, and test result objects. Can create cleanup/output files through environment and result serialization.

Dependencies and integration points: The central integration point for all `servertests/st_*.py` modules. It depends on test docstring metadata parsed by `testmod`, RPC security support registry, NFS URL parsing, and environment setup/cleanup.

Risks: Test selection defaults to no tests unless flags/codes are supplied. Pickle output is binary and version-coupled to test classes. Initialization failures raise after printing hints, so automation must capture stack traces. `printflags` contains bare `print` statements without parentheses that are no-ops under Python 3 when intended as blank lines.

Test signals: Exit behavior follows result count: initialization errors exit/raise, `nfail < 0` exits `3`, and normal output comes from `testmod.printresults`; optional JSON/XML outputs are written by `testmod`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/testserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/use_local.py -->
# sources/test-tools/pynfs/nfs4.0/use_local.py

Purpose: Path bootstrap helper that makes local pynfs modules importable when scripts are run from the source tree rather than an installed package.

Important APIs/types/functions: Imports `sys`, `os`, and `join/split` from `os.path`. It has no functions; all behavior runs at import time.

Control flow: Captures `cwd`, splits it into parent/head, constructs paths for sibling `xdr`, parent RPC area, and current directory, then inserts them into `sys.path[1:1]`.

State and persistence behavior: Mutates only process-local `sys.path`.

Dependencies and integration points: Used by `setup.py` fallback when `xdrgen` import fails. It assumes the current working directory is the `nfs4.0` package root and sibling directories follow the historical pynfs layout.

Risks: The condition is `if True or cwd not in sys.path`, so it always inserts paths and can duplicate entries on repeated imports. It depends on current working directory rather than file location.

Test signals: No direct tests; import success of local `xdrgen`/RPC modules is the practical signal.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/use_local.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/MANIFEST.in -->
# sources/test-tools/pynfs/nfs4.1/MANIFEST.in

Purpose: Source distribution manifest rules for NFSv4.1 pynfs XDR files.

Important APIs/types/functions: This is a packaging data file, not Python code. It includes `*.x` files and excludes generated `*_const.py`, `*_pack.py`, and `*_type.py` files.

Control flow: Interpreted by setuptools/distutils during source distribution creation.

State and persistence behavior: Does not mutate runtime state; controls which files appear in built sdists.

Dependencies and integration points: Integrates with the XDR generation workflow where generated Python files can be recreated from checked-in `.x` specifications.

Risks: If generated files are needed at install time but generation is unavailable, excluding them can break consumers. Conversely, including only `.x` avoids stale generated code in source archives.

Test signals: Packaging validation should confirm `.x` files are present in sdists and generated files are absent.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/__init__.py -->
# sources/test-tools/pynfs/nfs4.1/__init__.py

Purpose: Empty package marker for the NFSv4.1 pynfs tree.

Important APIs/types/functions: Defines no imports, classes, functions, or package exports.

Control flow: No executable code.

State and persistence behavior: No runtime state.

Dependencies and integration points: Allows Python package import mechanics for the `nfs4.1` directory in layouts that rely on traditional `__init__.py` markers.

Risks: No direct code risk; package naming with a dot-like directory (`nfs4.1`) can be awkward depending on import path layout.

Test signals: Import/package discovery behavior is the only signal.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/block.py -->
# sources/test-tools/pynfs/nfs4.1/block.py

Purpose: Models pNFS block-layout volume topology and address encoding for NFSv4.1, mapping logical offsets through simple, slice, concat, and stripe volumes to backing block devices.

Important APIs/types/functions: Imports pNFS block packer/unpacker, block XDR types/constants, `fs_base`, `Lock`, and `struct`. Key functions/classes are `getid`, `BlockVolume`, nested `BlockVolume.FakeFs`, abstract `Volume`, `Simple`, `Slice`, `Concat`, `Stripe`, and `remove_dups`.

Control flow: Volume trees expose `_dump()` to produce an ordered device list, `get_xdr(mapping)` to create `pnfs_block_volume4` variants, and `get_addr()` to pack a `pnfs_block_deviceaddr4`. `resolve`/`extent` map logical offsets into a `Simple` volume and local offset. `BlockVolume.open` opens all leaf backing devices and `FakeFs._find_extent` adapts topology mapping to `fs_base.LayoutFile`.

State and persistence behavior: Global `id` increments under `id_lock`. `Simple` may write signatures to backing devices during construction. `BlockVolume.open/close` manages file descriptors and stores `_fd` on leaf volumes.

Dependencies and integration points: Integrates pNFS block XDR definitions with the generic layout-file abstraction in `fs_base`. Backing devices must be writable for signature setup and later I/O.

Risks: Uses manual lock acquire/release instead of context management. `Slice` comments call start/length block offsets but all sizes are otherwise bytes, so unit mismatch is a risk. `Stripe._size` assumes compatible volume sizes. Close handling does not guard partial-open failures. `remove_dups` mutates its input list.

Test signals: No built-in tests; useful validation would round-trip `get_addr()` through `PNFS_BLOCKUnpacker`, verify `resolve/extent` boundaries, and exercise `BlockVolume` context manager against temporary backing files.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/block.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/client41tests/__init__.py -->
# sources/test-tools/pynfs/nfs4.1/client41tests/__init__.py

Purpose: Declares available NFSv4.1 client test modules for package/test discovery.

Important APIs/types/functions: Sets `__all__ = ["ct_reboot.py"]`.

Control flow: No executable control flow beyond module import and assignment.

State and persistence behavior: No persistent state.

Dependencies and integration points: Intended to advertise `ct_reboot.py` to client test discovery, though including the `.py` suffix in `__all__` is unusual for Python module export names.

Risks: Importers expecting module names without extensions may not handle `"ct_reboot.py"` correctly.

Test signals: Package discovery should verify the reboot client tests are found.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/client41tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/client41tests/ct_reboot.py -->
# sources/test-tools/pynfs/nfs4.1/client41tests/ct_reboot.py

Purpose: NFSv4.1 client-side reboot/session/delegation behavior tests driven through local filesystem operations and a controllable test server environment.

Important APIs/types/functions: Imports `os` and `fail` from `.environment`. Public tests are `testReboot`, `testReboot2`, `testDelegReturn`, `testOpenZeroes`, `testSessionReset`, `testSessionReset2`, and `testTwoValueSetupOrCleanup`.

Control flow: Tests use `os.chdir`, local file/directory operations under `env.home`/`env.root`, and environment controls such as `reboot_server`, `set_error`, `set_error_wait_lease`, `clear_two_values`, `control_reset`, `control_record`, `control_pause`, `control_grab_calls`, `find_op`, and `set_two_values`. They simulate server reboot, delegation-return errors, bad session responses, and operation error injection.

State and persistence behavior: Creates/removes files and directories in the mounted NFS test area, changes process working directory, and mutates server-side error-injection configuration through environment helpers.

Dependencies and integration points: Depends on a special NFSv4.1 client test environment with action/config/control channels, plus constants such as `OP_OPEN` expected in the runtime namespace.

Risks: `testReboot2` references `data` in a failure message without defining it. `testDelegReturn` reuses `env.testname(t)` after reading, likely overwriting the same test file but the intent is recall-by-write. Global cwd mutation can affect later tests if failures interrupt cleanup.

Test signals: Uses `fail()` for mismatched file contents, directory listing, nonzero OPEN seqid/clientid, bad `--useparams`, and relies on absence of exceptions for reboot/session recovery paths.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/client41tests/ct_reboot.py -->
