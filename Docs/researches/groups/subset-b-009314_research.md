# subset-b-009314 research

Grouped research report for pynfs NFSv4.1 server tests, harness modules, and RPC support files. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_flex.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_flex.py

Purpose: flex-files pNFS server tests for `LAYOUTGET`, `LAYOUTRETURN`, `GETDEVICEINFO`, layout stateid sequencing, layoutstats reporting, and propagation of data-server errors through later layout requests. It exercises NFSv4.1 flex-file layout XDR with real packed opaque bodies.

Important APIs/types/functions: `check_seqid`, `testStateid1`, `testFlexLayoutReturnFile`, `testFlexLayoutOldSeqid`, `testFlexLayoutStress`, `testFlexGetDevInfo`, `testFlexLayoutTestAccess`, `testFlexLayoutStatsSmall`, `_LayoutStats`, `layoutget_return`, `get_layout_cred`, and the `testFlexLayoutReturn*` error matrix. It uses `NFS4ops`, `NFS4Packer/NFS4Unpacker`, `ff_layoutreturn4`, `ff_layoutupdate4`, `ff_iostats4`, `device_error4`, `layoutreturn_file4`, `stateid4`, and `get_nfstime`.

Control flow: tests create/open a file through a pNFS client session, issue `LAYOUTGET` with an open or layout stateid, decode returned flex layout bodies to find mirrors/data servers/device ids/credentials, optionally call `GETDEVICEINFO`, and finally return layouts. The stats tests build latency and I/O accounting structures from captured numeric traces, sleep between samples, and send `LAYOUTSTATS` or stats-bearing `LAYOUTRETURN` payloads. The error tests call `layoutget_return` to return layouts containing `ff_ioerr4` records, then verify subsequent layoutgets return success, delay, or the reported NFS error as appropriate for read/write mode.

State and persistence behavior: the suite mutates server layout state and checks monotonically increasing layout stateid `seqid` values. It also verifies stale layout stateids are rejected on return, access credentials vary by I/O mode, layout stats are accepted across resets/overflow-like traces, and reported data-server errors can affect future layout grants. File data persistence is secondary; persistent state is mostly NFS server layout, device, and open-state tracking.

Dependencies/integration: integrates `server41tests.environment` helpers, `nfs_ops`, generated NFSv4.1 XDR types/constants, `nfs4lib`, and flex-files data server configuration. It depends on an environment that advertises `FLAGS: flex` and sometimes `layoutstats`/`layoutreturn`.

Risks and test signals: many checks assume a single mirror/data server and index the last returned layout/device record. Layoutstats use fixed trace arrays and timing sleeps, which can be slow or environment-sensitive. The strongest signals are status checks, exact stateid sequence assertions, decoded credential comparisons, and acceptance or rejection of layout-return error propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_flex.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_getdevicelist.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_getdevicelist.py

Purpose: pNFS block-layout tests for device discovery, device info decoding, layout acquisition/return, and layout commit.

Important APIs/types/functions: `testGetDevList`, `testGetDevInfo`, `testGetLayout`, `testEMCGetLayout`, `testLayoutReturnFile`, `testLayoutReturnFsid`, `testLayoutReturnAll`, and `testLayoutCommit`. It uses `GETDEVICELIST`, `GETDEVICEINFO`, `LAYOUTGET`, `LAYOUTRETURN`, `LAYOUTCOMMIT`, `BlockPacker`, `BlockUnpacker`, `PNFS_BLOCK_INVALID_DATA`, `PNFS_BLOCK_READWRITE_DATA`, and `pnfs_block_layoutupdate4`.

Control flow: the tests first read `FATTR4_FS_LAYOUT_TYPES` from the export root, loop over advertised layout types, call device-list/info operations, and decode block layout device addresses. Layout tests create or open files, request block-volume layouts sized from `get_blocksize`, decode opaque extents, return layouts at file/fsid/all scopes, or mutate the final extent state and commit it with `LAYOUTCOMMIT`.

State and persistence behavior: file creation and layout commits alter server-side file and block extent state. `testLayoutCommit` specifically transitions a final extent from invalid data to read/write data and supplies a new end offset, making it the durable writeback/update path in this file.

Dependencies/integration: relies on block layout support, generated NFS types, `block` XDR helpers, `nfs4lib.state00`, and environment helpers such as `use_obj`, `create_file`, `open_file`, and `get_blocksize`.

Risks and test signals: several paths print decoded opaque structures rather than asserting deep contents. `testGetDevInfo` overrides `lo_type` to `LAYOUT4_BLOCK_VOLUME` inside a loop, which narrows coverage. `testEMCGetLayout` is a debugging test tied to a pre-existing `server2fs1/dump.eth` path. Failures mainly surface as NFS status mismatches or XDR decode failures.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_getdevicelist.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_lookup.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_lookup.py

Purpose: basic NFSv4.1 `LOOKUP` behavior tests for home-path traversal and common error cases.

Important APIs/types/functions: active tests are `testHome`, `testNoFh`, `testNonExistent`, `testZeroLength`, and `testLongName`. The module also contains a large disabled `if 0` block with older object-type, access, invalid UTF-8, dot-name, and directory-permission lookup tests.

Control flow: each active test creates a client/session, composes NFS operations with `env.home`, `putrootfh`, `lookup`, and `getfh`, then validates the compound status. The disabled block follows the same pattern but uses legacy client helper methods.

State and persistence behavior: active tests do not create persistent state. They inspect namespace resolution against existing test roots and validate server error handling for missing current filehandle, nonexistent names, empty names, and overly long names.

Dependencies/integration: uses `NFS4ops`, constants from `xdrdef.nfs4_const`, and `server41tests.environment.check/fail`. It depends on `env.home` and server path options populated by the test harness.

Risks and test signals: coverage is currently narrow because many richer tests are disabled. The long-name case notes that `NOENT` might require checking `fattr4_maxname`, but the active assertion expects `NFS4ERR_NAMETOOLONG`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_lookup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_lookupp.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_lookupp.py

Purpose: validates `LOOKUPP` parent-directory traversal and error handling for invalid current filehandle types.

Important APIs/types/functions: `testLookupp`, object-type tests `testFile`, `testFifo`, `testLink`, `testBlock`, `testChar`, `testSock`, plus `testLookuppRoot`, `testNoFH`, and `testXdev`.

Control flow: `testLookupp` walks down `env.home`, records filehandles with `GETFH`, then repeatedly issues `LOOKUPP` and compares returned handles to the earlier path handles. Object-type tests put a known non-directory filehandle as current fh and expect `NOTDIR` or `SYMLINK`. Root and missing-fh tests validate `NOENT` and `NOFILEHANDLE`; the xdev case checks parent traversal across a configured special path returns the expected parent filehandle.

State and persistence behavior: no new durable objects are created. The tests depend on prebuilt test-tree objects and the server's filehandle stability across lookup and lookupp operations.

Dependencies/integration: uses `use_obj` environment helper, `NFS4ops`, and option paths such as `usefile`, `usefifo`, `usesocket`, and `usespecial`.

Risks and test signals: most tests require `--maketree` or equivalent configured objects. Filehandle byte equality is the key signal; cross-filesystem semantics may vary for `testXdev`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_lookupp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_loop.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_loop.py

Purpose: deliberately tiny dependency-loop fixture for the test harness.

Important APIs/types/functions: `test1` has `CODE: XXX1` and `DEPEND: XXX2`; `test2` has `CODE: XXX2` and `DEPEND: XXX1`.

Control flow: both test bodies immediately return. The interesting behavior is entirely in `testmod._runtree`, which should detect circular dependency wait states when either test is selected.

State and persistence behavior: no NFS operations, external state, or persistence.

Dependencies/integration: integrates only through docstring metadata parsed by `testmod.createtests`.

Risks and test signals: the module is not a protocol test; it is useful for validating dependency-cycle handling. If run accidentally as a real protocol test, pass/fail meaning is limited.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_loop.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_open.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_open.py

Purpose: NFSv4.1 `OPEN`, open stateid sequencing, simple read/write through open state, anonymous stateid I/O, exclusive create verifier behavior, `CLAIM_FH`, and close-with-zero-seqid tests.

Important APIs/types/functions: `expect`, `testSupported`, `testServerStateSeqid`, `testReadWrite`, `testAnonReadWrite`, `testEXCLUSIVE4AtNameAttribute`, `testOPENClaimFH`, and `testCloseWithZeroSeqid`. It imports open-owner, open-flag, claim, stateid, and lock-owner XDR types, though not all are used.

Control flow: tests create sessions, create/open files via environment helpers, assert returned open stateid `seqid` values, write data at offset 5, read it back, and close. `testOPENClaimFH` closes the initial open, then reopens by current filehandle with `CLAIM_FH`.

State and persistence behavior: creates files in the test directory and writes data containing a hole prefix. The server's open-owner state and stateid sequencing are the main state under test. Some tests set `stateid.seqid = 0` to verify special current-state semantics accepted by read/write/close paths.

Dependencies/integration: uses `st_create_session`, `server41tests.environment` file helpers, `nfs_ops`, `nfs4lib.state00`, and NFSv4.1 generated constants/types.

Risks and test signals: the helper `expect` assumes the open result is at `resarray[-2]`, so compound shape changes would break it. The tests do not deeply inspect delegations, and several imported lock-related types are unused.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_putfh.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_putfh.py

Purpose: verifies `PUTFH` installs the exact current filehandle and rejects malformed filehandle bytes.

Important APIs/types/functions: `_try_put` and object-type tests `testFile`, `testLink`, `testBlock`, `testChar`, `testDir`, `testFifo`, `testSocket`, plus `testBadHandle`.

Control flow: `_try_put` looks up a configured object, obtains its handle with `GETFH`, issues `PUTFH` with that handle, then calls `GETFH` again and compares byte equality. `testBadHandle` sends `PUTFH(b'abc')` and expects `NFS4ERR_BADHANDLE`.

State and persistence behavior: read-only with respect to the server namespace. It depends on stable, reusable filehandles for existing test-tree objects.

Dependencies/integration: uses `use_obj`, `check`, `NFS4ops`, and configured option paths for every object kind.

Risks and test signals: object-kind tests require pre-existing test-tree entries. The test signal is direct filehandle equality, which is strong for `PUTFH`/`GETFH` but does not validate later operation behavior on the handle.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_putfh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_reboot.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_reboot.py

Purpose: non-standard reboot/grace-period tests for clientid/session invalidation, `CLAIM_PREVIOUS` reclaim, `RECLAIM_COMPLETE`, duplicate reclaim, multiple-client recovery, double reboot, and late reclaim near grace expiry.

Important APIs/types/functions: `_getleasetime`, `_waitForReboot`, local `create_session`, `reclaim_complete`, `testRebootValid`, `State`, `doTestOneClientGrace`, `doTestOneClientNoGrace`, `doTestAllClientsNoGrace`, `doTestRebootWithNClients`, and the `testRebootWith*` variants.

Control flow: tests create clients/sessions, complete normal reclaim, create confirmed open state, invoke `env.serverhelper(b"reboot")`, reconnect transport, clear cached sessions/clients, verify old sessions/clientids are stale, recreate clients, reclaim opens with `CLAIM_PREVIOUS`, send `RECLAIM_COMPLETE`, and probe whether new opens are blocked during grace and allowed after all clients recover. Multi-client variants scale to 10, 100, or 1000 clients and optionally reboot twice or reclaim twice.

State and persistence behavior: heavily stateful. It depends on server reboot persistence of reclaimable open state, lease time/grace state, clientid invalidation, session invalidation, and post-grace cleanup. It deliberately sleeps for lease time plus a buffer in `finally` blocks to leave the server in a clean state.

Dependencies/integration: requires a configured `serverhelper` capable of rebooting or restarting the target. Uses `rpc.rpc.RPCTimeout`, generated session/channel types, file/open helpers, and environment sleep/connect hooks.

Risks and test signals: expensive and disruptive; comments say reboot tests are not part of the standard suite. Large-client variants can stress server and test infrastructure. Timing around early grace lifting is logged as a warning rather than failed unless protocol status expectations are violated.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_reboot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_reclaim_complete.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_reclaim_complete.py

Purpose: tests `RECLAIM_COMPLETE` legality, no-grace behavior after completion, blocking of non-reclaim opens before completion, and duplicate completion errors.

Important APIs/types/functions: `testSupported`, `testReclaimAfterRECC`, `testOpenBeforeRECC`, and `testDoubleRECC`.

Control flow: tests create a fresh client/session, send `RECLAIM_COMPLETE` with root or current state, create/open files as needed, then attempt `CLAIM_PREVIOUS`, normal `OPEN`, or a second reclaim-complete and validate the expected NFS status.

State and persistence behavior: exercises per-client reclaim-complete state and grace-period enforcement. `testReclaimAfterRECC` creates confirmed open state only to attempt an invalid later reclaim and then closes it.

Dependencies/integration: uses the standard session/file helpers, `NFS4ops`, `nfs4lib`, and RFC 5661 status constants.

Risks and test signals: `testReclaimAfterRECC` passes a warnlist that appears to bitwise-OR two error constants instead of listing both separately, which may weaken warning handling. Grace-period behavior depends on server state at session creation.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_reclaim_complete.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_rename.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_rename.py

Purpose: broad `RENAME` conformance matrix covering successful renames for each object kind, non-directory source/target current filehandles, missing handles, nonexistent names, bad names, replacement type rules, self-renames, hard-link renames, and close-after-overwrite behavior.

Important APIs/types/functions: `testValidDir/File/Link/Block/Char/Fifo/Socket`, `testSfh*`, `testCfh*`, `testNoSfh`, `testNonExistent`, `testZeroLengthOldname`, `testZeroLengthNewname`, `testBadutf8Oldname`, `testBadutf8Newname`, `testDotsOldname`, `testDotsNewname`, `testDirToObj`, `testDirToDir`, `testFileToDir`, `testFileToFile`, `testDirToFullDir`, `testFileToFullDir`, `testSelfRenameDir`, `testSelfRenameFile`, `testLinkRename`, and `testStaleRename`.

Control flow: tests build small directory trees with `maketree` or create special objects with `create_obj`, perform `rename_obj`, and check exact or permitted status sets. Self-rename and hard-link cases inspect `source_cinfo` and `target_cinfo` before/after change attributes to ensure no-op renames do not mutate directory metadata.

State and persistence behavior: creates, moves, replaces, and links objects in the test tree. Replacement tests encode POSIX/NFS ambiguity by accepting alternative statuses such as `EXIST` vs `NOTDIR` or `ISDIR`. `testStaleRename` validates an open target file can still be closed after being overwritten by a rename.

Dependencies/integration: uses environment namespace helpers, invalid UTF-8 corpus, generated `createtype4/specdata4`, and configured test-tree object paths.

Risks and test signals: `testValidChar` creates `NF4BLK` rather than `NF4CHR`, likely reducing char-device-specific coverage. The many accepted status alternatives make the suite tolerant of server differences but less strict. Persistent cleanup relies on environment teardown.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_rename.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo.py

Purpose: tests named `SECINFO` on a created file and confirms `SECINFO` clears current filehandle state such that following `GETFH` returns `NFS4ERR_NOFILEHANDLE`.

Important APIs/types/functions: `testSupported` and `testSupported2`; imports `create_session`, `bad_sessionid`, and `channel_attrs4` are present but not used by active code.

Control flow: each test creates a session and temporary file, records the filehandle/stateid, obtains the parent directory filehandle, issues `SECINFO(name)`, and closes the file. The second test appends `GETFH` after `SECINFO` and expects `NOFILEHANDLE`.

State and persistence behavior: creates a temporary file and open state, then closes it. The key transient protocol state is current filehandle invalidation after `SECINFO`.

Dependencies/integration: uses `use_obj`, `create_file`, `NFS4ops`, and generated constants. It relies on the target server returning legal security flavor information for the created name.

Risks and test signals: no deep validation of returned security flavors is performed; success only means the operation accepted and had the expected filehandle side effect.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo_no_name.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo_no_name.py

Purpose: tests `SECINFO_NO_NAME` styles on root and home filehandles, including current-filehandle clearing behavior.

Important APIs/types/functions: `testSupported`, `testSupported2`, `testSupported3`, and `testSupported4`.

Control flow: tests create a client/session, run `PUTROOTFH` or `env.home`, then call `SECINFO_NO_NAME` with style `0` or `SECINFO_STYLE4_PARENT`. One test appends `GETFH` and expects `NOFILEHANDLE`; root-parent style expects `NFS4ERR_NOENT`; home-parent style expects success.

State and persistence behavior: no durable objects are created. The state under test is the current filehandle before and after `SECINFO_NO_NAME`.

Dependencies/integration: uses `NFS4ops`, environment home ops, and NFSv4.1 security-info constants.

Risks and test signals: the module prints the compound result in `testSupported2`, which is useful for debugging but noisy. It validates statuses only, not returned flavor contents.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo_no_name.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_sequence.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_sequence.py

Purpose: NFSv4.1 `SEQUENCE` protocol tests for operation position, session binding, bad sessions/slots, request and operation limits, replay cache behavior, op-not-in-session errors, returned sequence fields, and sequence misordering.

Important APIs/types/functions: `testSupported`, `testNotFirst`, `testImplicitBind`, `testBadSession`, `testRequestTooBig`, `testTooManyOps`, `testBadSlot`, replay-cache tests `testReplayCache001` through `testReplayCache007`, `testOpNotInSession`, `testSessionidSequenceidSlotid`, and `testBadSequenceidAtSlot`.

Control flow: tests create sessions with default or constrained channel attributes, send compounds using session helpers or raw `env.c1.compound`, and use `seq_delta=0` to replay the same slot sequence. Replay tests normalize tags and compare full response structures with `nfs4lib.test_equal`.

State and persistence behavior: focuses on per-session forechannel state: slot ids, sequence ids, cached replies, connection binding, and channel limits. Some replay tests create/rename files to exercise non-idempotent cached replies.

Dependencies/integration: uses `channel_attrs4`, `bad_sessionid`, file helpers, raw NFS client connections, and `nfs4lib.dec_u32`/`test_equal`.

Risks and test signals: `testRequestTooBig` comments that `NAME_TOO_BIG` may be valid but is not accepted by this test. Replay tests depend on exact response equality except tag clearing. Raw slot ids in `testSessionidSequenceidSlotid` may interact with slot-range negotiation.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_sequence.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_sparse.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_sparse.py

Purpose: NFSv4.2 sparse-file `ALLOCATE` smoke tests with open, all-zero, and all-one stateids.

Important APIs/types/functions: `testAllocateSupported`, `testAllocateStateidZero`, and `testAllocateStateidOne`.

Control flow: each test creates a write-open file, extracts its filehandle and sometimes open stateid, then issues `ALLOCATE` for offset `0`, length `1` with the selected stateid and checks success.

State and persistence behavior: creates files and asks the server to reserve or allocate one byte of backing storage. The operation may change file allocation metadata without changing visible data.

Dependencies/integration: requires minor version 2 or later (`VERS: 2-`), `create_file`, environment special stateids `stateid0`/`stateid1`, and `NFS4ops.allocate`.

Risks and test signals: no readback or allocation attribute verification is performed. The suite only verifies that the server accepts the requests.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_sparse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_trunking.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_trunking.py

Purpose: basic multi-session-per-client tests used as a starting point for trunking/session-lifetime coverage.

Important APIs/types/functions: `testTwoSessions` and `testUseTwoSessions`.

Control flow: `testTwoSessions` creates one client and two sessions. `testUseTwoSessions` creates two sessions, sends empty compounds on both, destroys the first session via `DESTROY_SESSION`, then verifies the second session remains usable.

State and persistence behavior: mutates client session state on the server but no filesystem data. It specifically checks that session destruction is scoped to the target session and not the whole clientid.

Dependencies/integration: uses `NFS4ops.destroy_session`, `nfs4lib`, generated types, and environment client/session factories.

Risks and test signals: imports `random` and `threading` are unused. Comments outline many unimplemented trunking/callback scenarios, so current coverage is intentionally shallow.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_trunking.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_verify.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_verify.py

Purpose: `VERIFY` operation helper module with one active mandatory-attribute test and many disabled legacy cases for type, size, write-only, unsupported, and invalid UTF-8 attributes.

Important APIs/types/functions: helpers `_try_mand`, `_try_type`, `_try_changed_size`, `_try_write_only`, `_try_unsupported`; active test `testMandFile`. The helper code uses `do_getattrdict`, `use_obj`, `verify`, and supported-attribute discovery.

Control flow: `_try_mand` gathers all mandatory attributes except `rdattr_error`, issues `GETATTR`, then verifies the same attributes and reuses the object path. Disabled helpers would verify types, deliberately changed sizes, write-only attributes, and unsupported attributes.

State and persistence behavior: active code is read-only. It validates attribute comparison semantics against the current server view of a file.

Dependencies/integration: depends on `env.attr_info`, configured `usefile`, and the environment's attribute metadata. Some helper code references legacy `env.c1` methods rather than session-based helpers.

Risks and test signals: only `testMandFile` is active; most broader VERIFY coverage is commented out. The active signal is strong for mandatory-attribute round-trip consistency but narrow.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_xattr.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_xattr.py

Purpose: NFSv4.2 extended-attribute tests for support advertisement, get/set/remove/list behavior, create/replace/either semantics, and missing/existing attribute errors.

Important APIs/types/functions: `testGetXattrAttribute`, `testGetMissingAttr`, `testCreateNewAttr`, `testCreateNewIfMissingAttr`, `testUpdateOfMissingAttr`, `testExclusiveCreateAttr`, `testUpdateExistingAttr`, `testRemoveNonExistingAttr`, `testRemoveExistingAttr`, `testListNoAttrs`, and `testListAttrs`.

Control flow: tests create a file with `open_create_file_op`, close it with a module-level `current_stateid`, then operate on `user.attr*` names via `GETXATTR`, `SETXATTR`, `REMOVEXATTR`, and `LISTXATTRS`. Value tests read back bytes and compare exact values; list tests compare returned names and EOF.

State and persistence behavior: creates files and mutates their xattr namespace. The suite checks missing, create-only, replace-only, either, remove, and list states for user attributes.

Dependencies/integration: requires NFS minor version 2 or later (`VERS: 2-`), generated xattr constants, `FATTR4_XATTR_SUPPORT`, and server filesystem xattr support.

Risks and test signals: test docstrings have minor typos such as `NFS4_ON`, but assertions use actual status checks. It does not test list pagination beyond a large enough 8192-byte buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_xattr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server_exports.py -->
# sources/test-tools/pynfs/nfs4.1/server_exports.py

Purpose: helper for mounting in-process pynfs test server exports, including memory, disk, block-layout, and file-layout exports.

Important APIs/types/functions: `mount_stuff`, `_create_simple_block_dev`, and `_load_dataservers`.

Control flow: `mount_stuff` creates a disk-backed stub filesystem at `/tmp/py41/fs1`, memory stub filesystems, mounts them at `/a`, `/b`, and `/foo/bar/c`, and conditionally mounts block or file layout exports depending on options. `_create_simple_block_dev` builds a simple/sliced/concatenated block volume over `/dev/ram4`. `_load_dataservers` instantiates `DSDevice`, loads configuration from a file, and returns it.

State and persistence behavior: disk export state persists under `/tmp/py41/fs1` unless reset; memory exports are transient. Block layout state depends on the backing ram device. File-layout state depends on configured data servers.

Dependencies/integration: imports `StubFS_Mem`, `StubFS_Disk`, `BlockLayoutFS`, `FileLayoutFS`, `DSDevice`, and block volume classes. It is used by the local test server setup rather than by client-side tests directly.

Risks and test signals: paths and `/dev/ram4` are hard-coded, making this environment-specific. `_load_dataservers` ends with a semicolon but works in Python. If data-server loading returns `None`, file-layout mount is skipped.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server_exports.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/setup.py -->
# sources/test-tools/pynfs/nfs4.1/setup.py

Purpose: setuptools packaging script for the `nfs4` Python package, with a custom build step to generate Python modules from XDR definition files.

Important APIs/types/functions: custom `build_py` subclass, `build_packages`, `expand_xdr`, and the final `setup(...)` call.

Control flow: import `xdrgen`, falling back through `use_local` if needed. During build, `build_packages` calls `expand_xdr` for each package directory before finding/building modules. `expand_xdr` changes into `<package_dir>/xdrdef`, runs `xdrgen.run` on each `*.x` file, attempts to remove parser artifacts, and returns to the original cwd in a `finally`.

State and persistence behavior: generates or overwrites `_const.py`, `_pack.py`, and `_type.py` style generated modules under `xdrdef`; removes `parser.out` and `parsetab.py` when present. Package metadata itself is static.

Dependencies/integration: integrates setuptools, local `xdrgen`, globbing, and package layout `{"nfs4": ""}` with package names `nfs4` and `nfs4.server41tests`.

Risks and test signals: build behavior depends on current working directory and local `use_local` path injection. Broad `except` during parser artifact cleanup can hide cleanup errors, though it prints a message.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/testclient.py -->
# sources/test-tools/pynfs/nfs4.1/testclient.py

Purpose: command-line runner for pynfs NFSv4.1 client-side tests.

Important APIs/types/functions: `parse_useparams`, `scan_options`, `Argtype`, `run_filter`, `printflags`, and `main`.

Control flow: `main` parses options, builds tests from `client41tests` with `testmod.createtests`, handles `--showflags`/`--showcodes`, parses the server path, normalizes `--use*` paths, maps remaining arguments to flags or test codes, initializes `client41tests.environment.Environment`, runs tests via `testmod.runtests`, pickles results when requested, prints results, and calls environment cleanup.

State and persistence behavior: writes optional pickle output, mutates option fields for path/test selection, and creates/cleans server-side test state through the environment. It does not persist internal state beyond the output file.

Dependencies/integration: uses `use_local` path injection, `nfs4lib`, `testmod`, `client41tests.environment`, `socket`, `rpc.rpc`, and `pickle`. Security-option code is present but commented out.

Risks and test signals: `parse_useparams` assumes a non-`None` string, but the option default is `None`; the loop can call it if `attr == 'useparams'`. Result output file is opened in text mode while `pickle.dump` writes bytes in Python 3, which may be problematic if used.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/testclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/testmod.py -->
# sources/test-tools/pynfs/nfs4.1/testmod.py

Purpose: generic pynfs test discovery, dependency resolution, execution, result formatting, and JSON/XML reporting engine.

Important APIs/types/functions: result constants, `Result`, `TestException` subclasses, `Test`, base `Environment`, `runtests`, `_runtree`, `_import_by_name`, `parseversions`, `createtests`, `printresults`, `json_printresults`, and `xml_printresults`.

Control flow: `createtests` imports a suite package, scans modules in `package.__all__`, wraps every callable whose name starts with `test`, parses docstring fields `FLAGS`, `DEPEND`, `CODE`, and `VERS`, creates flag bitmasks, validates unique codes, and resolves dependencies to tests or dependency functions. `runtests` walks tests and `_runtree` recursively runs dependencies, handling circular wait states, omitted tests, failed dependencies, forced/rundeps behavior, and actual `Test.run` execution.

State and persistence behavior: each `Test` stores result, timing, flags, dependencies, doc metadata, and status. Pickling strips function/dependency/flag references. Reporting functions serialize current result state to stdout, JSON, or XML.

Dependencies/integration: used by both `testclient.py` and `testserver.py`; relies on suite packages exposing `__all__`, docstring metadata discipline, `nfs4lib`, and environment lifecycle hooks.

Risks and test signals: `Result.__eq__` compares non-int results by identity, which is intentional for singleton defaults but subtle. `parseversions` error references undefined `s` in one branch. XML/JSON reporters include every test rather than only requested tests, so consumers must interpret skipped/omitted state.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/testmod.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/testserver.py -->
# sources/test-tools/pynfs/nfs4.1/testserver.py

Purpose: command-line runner for pynfs NFSv4.1 server tests.

Important APIs/types/functions: `scan_options`, `Argtype`, `run_filter`, `printflags`, and `main`. Module-level defaults derive AUTH_SYS host/uid/gid values.

Control flow: `main` parses server URL and test selectors, creates test metadata from `server41tests`, handles display-only modes, validates `--use*` object paths, maps security names to RPC flavor/service pairs, checks supported security flavors, initializes `server41tests.environment.Environment`, runs tests, pickles optional result output, prints results, and optionally writes JSON or XML.

State and persistence behavior: writes optional pickle/JSON/XML result artifacts and triggers environment setup/cleanup that creates server-side test data. It also sets `environment.nfs4client.SHOW_TRAFFIC` and `environment.debug_fail` from options.

Dependencies/integration: uses `use_local`, `nfs4lib.parse_nfs_url`, `testmod`, `server41tests.environment`, `rpc.rpc` security constants/support table, `socket`, and `pickle`.

Risks and test signals: target path parsing expects byte strings for some path checks. The security mapping supports `krb5*` names only if `rpc.security.supported` includes `RPCSEC_GSS`. JSON and XML output are mutually exclusive due to `elif`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/testserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/use_local.py -->
# sources/test-tools/pynfs/nfs4.1/use_local.py

Purpose: local import-path shim used by pynfs scripts during development so generated/local modules can be imported without installing the package.

Important APIs/types/functions: module-level code only; imports `sys`, `os`, and `join/split`.

Control flow: captures the current working directory, computes its parent, and inserts the sibling `xdr` directory, the parent directory, and the cwd into `sys.path` near the front. The condition is `if True or cwd not in sys.path`, so insertion always happens on import.

State and persistence behavior: mutates process-global `sys.path`; no filesystem writes.

Dependencies/integration: imported by `testclient.py`, `testserver.py`, and `setup.py` fallback paths.

Risks and test signals: unconditional path insertion can duplicate entries and make imports cwd-dependent. It is intentionally labeled as a hack by callers.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/use_local.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/xdrdef/__init__.py -->
# sources/test-tools/pynfs/nfs4.1/xdrdef/__init__.py

Purpose: empty package marker for generated NFSv4.1 XDR modules.

Important APIs/types/functions: none; the file has zero lines.

Control flow: no runtime behavior.

State and persistence behavior: no state beyond making `xdrdef` importable as a package.

Dependencies/integration: sibling generated modules such as `nfs4_const`, `nfs4_type`, and `nfs4_pack` are imported throughout server tests.

Risks and test signals: absence of package initialization is intentional. Any needed generated module availability is handled by build/setup rather than this file.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/xdrdef/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/rpc/MANIFEST.in -->
# sources/test-tools/pynfs/rpc/MANIFEST.in

Purpose: packaging manifest rules for the pynfs RPC package XDR sources and generated artifacts.

Important APIs/types/functions: includes `*.x`; excludes `*_const.py`, `*_pack.py`, and `*_type.py`.

Control flow: declarative packaging metadata only.

State and persistence behavior: affects source distributions by keeping XDR inputs and excluding generated Python outputs.

Dependencies/integration: complements the XDR generation flow used by setup/build tooling.

Risks and test signals: packaging must regenerate excluded files at build time; missing generator integration would produce incomplete installs.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/rpc/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/rpc/__init__.py -->
# sources/test-tools/pynfs/rpc/__init__.py

Purpose: package initializer for the RPC package.

Important APIs/types/functions: `from rpc import *` and `__all__ = ["rpc"]`.

Control flow: imports the top-level `rpc` module into package namespace at import time.

State and persistence behavior: import side effects only; no persistence.

Dependencies/integration: intended to expose RPC helpers to pynfs modules, but the absolute import style can be sensitive to `sys.path` layout.

Risks and test signals: `from rpc import *` may resolve a top-level module rather than relative `.rpc` under Python 3 packaging semantics, depending on path setup. The local `use_local` shims likely mask this in development.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/rpc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/rpc/rpc.py -->
# sources/test-tools/pynfs/rpc/rpc.py

Purpose: TCP ONC RPC transport implementation with record marking, asynchronous polling, per-call deferred replies, client/server base classes, and hooks into RPC authentication/security.

Important APIs/types/functions: `inc_u32`, exceptions `RPCError/RPCTimeout/RPCAcceptError/RPCDeniedError`, `FancyRPCUnpacker`, `FancyRPCPacker`, `DeferredData`, `Alarm`, `Pipe`, `RpcPipe`, `ConnectionHandler`, `Server`, and `Client`.

Control flow: `ConnectionHandler.start` runs a `select` loop over listening sockets, active pipes, write-ready pipes, and an internal alarm connection. Incoming bytes are reassembled by `Pipe.recv_records` using RFC record marks, then each full RPC record is dispatched to a worker thread. Calls are unpacked, RPC version/auth/program/version/procedure are checked, procedure handlers run, results are secured and sent as replies. Client calls allocate an XID, pack a CALL, store `DeferredData`, send the record, and wait for the matching reply.

State and persistence behavior: runtime state includes socket sets, fd-to-pipe maps, write/read buffers, pending XID map, XID counter, security flavor instances, and active flags. There is no durable persistence.

Dependencies/integration: depends on generated RPC XDR pack/type/const modules, `security`, `rpclib`, Python `socket/select/threading`, and subclass implementations of program/version/procedure lookup.

Risks and test signals: heavily threaded with daemon workers and a custom alarm socket. Some exception paths drop requests silently. `RpcPipe.rcv_reply` catches `IndexError` for missing XID even though dict lookup raises `KeyError`. `expose(safe=True)` buzzes a string command instead of bytes in one branch, which can matter on Python 3 if used.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/rpc/rpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/rpc/rpclib.py -->
# sources/test-tools/pynfs/rpc/rpclib.py

Purpose: small RPC flow-control and reply-building helper library used by the transport when request processing should stop and a specific RPC reply should be emitted.

Important APIs/types/functions: `NULL_CRED`, `RPCFlowContol`, `RPCDrop`, `RPCDeniedReply`, `RPCUnsuccessfulReply`, and `RPCSuccessfulReply`.

Control flow: server-side RPC handling raises these exceptions to short-circuit normal procedure processing. Each reply exception has a `body()` method that builds an accepted or denied `reply_body` plus optional payload bytes. `RPCDrop` signals silent drop.

State and persistence behavior: no persistent state. Instances store status codes, mismatch/auth data, verifier, or message data for one reply.

Dependencies/integration: used by `rpc.py` and `security.py`; imports generated RPC constants/types and builds `rejected_reply`, `accepted_reply`, `rpc_reply_data`, and `rpc_mismatch_info` objects.

Risks and test signals: class name `RPCFlowContol` is misspelled but consistently used. Broad exception handling inside `body()` masks construction bugs by returning generic auth/system errors while logging critical messages.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/rpc/rpclib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/rpc/security.py -->
# sources/test-tools/pynfs/rpc/security.py

Purpose: authentication/security abstraction for ONC RPC flavors `AUTH_NONE`, `AUTH_SYS`, and optionally `RPCSEC_GSS`, including credential packing, verifier generation/checking, context establishment, sequence-window replay protection, and integrity/privacy wrapping.

Important APIs/types/functions: `SecError`, `CredInfo`, `AuthNone`, `AuthSys`, `GSSContext`, `AuthGss`, `supported`, `klass`, `instances`, and `instance`.

Control flow: callers create `CredInfo` from an auth instance. Client-side `make_cred`, `make_call_verf`, and `secure_data` prepare RPC calls. Server-side `check_auth` validates flavor-specific credentials/verifiers and returns a credential context or raises `rpclib` flow-control replies. `AuthGss.init_cred` performs an RPCSEC_GSS init/continue token exchange over a supplied call function, while `handle_gss_init` accepts server-side tokens and returns `rpc_gss_init_res`.

State and persistence behavior: `AuthNone` is stateless; `AuthSys` carries per-call authsys parameters. `AuthGss` stores context handles mapped to `GSSContext`, and each context tracks client seqid, highest server seqid, and a replay-window bitmask. No durable state is written.

Dependencies/integration: depends on generated RPC/GSS XDR modules, optional `gssapi`, `rpclib`, `xdrlib3` or stdlib `xdrlib`, threading locks, and logging. If `gssapi` import fails, RPCSEC_GSS is omitted from `supported`.

Risks and test signals: several comments mark STUB/BUG areas, including service authorization, qop handling, context locking, overflow, and incomplete verifier checks during GSS init. `handle_gss_init` uses `major` after an exception path where it may be undefined. Replay-window logic silently drops repeats/out-of-window requests via `RPCDrop`, which can appear as timeouts at callers.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/rpc/security.py -->
