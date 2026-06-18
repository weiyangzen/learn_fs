# Group Research: subset-b-009313

This grouped report covers the requested NFSv4.1 pynfs server implementation and server-side test files. Each section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4server.py -->
# sources/test-tools/pynfs/nfs4.1/nfs4server.py

## Purpose
`nfs4server.py` is the in-process pynfs NFSv4.1 server used by the test suite. It implements RPC program dispatch for NULL and COMPOUND, server control RPCs, client and session records, replay caches, state-protection scaffolding, filesystem mounting, NFSv4.1 operations, pNFS device/layout stubs, and callback transport helpers. It is intentionally test-oriented and includes many `STUB`, `BUG`, and draft-version notes.

## Important APIs, Types, and Functions
- `NFS4Server(rpc.Server)` is the main server. Key entry points are `handle_0`, `handle_1`, `op_compound`, `op_sequence`, `op_exchange_id`, `op_create_session`, filehandle operations, open/read/write/lock operations, pNFS operations, control operations, and callback helpers.
- `ClientList` maps both client owner ids and integer clientids to `ClientRecord` objects and allocates new clientids.
- `ClientRecord` stores client identity, verifier, principal, state protection, replay slot for `CREATE_SESSION`, session list, lease timestamp, and per-client stateid table.
- `SessionRecord` stores client association, sessionid, fore/back `Channel` objects, callback program, connection binding state, and nonce state.
- `Channel`, `Slot`, and `Cache` implement negotiated channel limits and DRC/replay behavior.
- `StateProtection` parses `SP4_NONE`, `SP4_MACH_CRED`, and `SP4_SSV` request state-protection args and provides `deny()` and `rv()` response helpers.
- `Recording` and `ctrl_*` functions support the separate server-control RPC used by pynfs tests to record, pause, reset, and grab traffic.

## Control Flow
Incoming COMPOUND calls enter `handle_1`, are unpacked with `FancyNFS4Unpacker`, passed to `op_compound`, then packed as `COMPOUND4res`. `op_compound` validates minor version and tag, dispatches each argop to `op_<name>`, appends encoded results, and stops at the first non-OK status. `NFS4Replay` is handled at the RPC level by waiting on the prior slot cache.

Session establishment starts with `op_exchange_id`, which implements draft case handling for new, unconfirmed, confirmed, rebooted, and update client records. `op_create_session` validates clientid, state protection, and create-session sequence, confirms the client when needed, negotiates channels, binds the fore channel to the current connection, optionally probes callback with `CB_NULL`, and registers the `SessionRecord`.

Most protocol operations call `check_session`, `check_cfh`, and sometimes `check_sfh`, then operate against `CompoundState` filehandles. OPEN dispatches by claim type into `open_claim_null` or `open_claim_fh`, then `open_file` coordinates share conflict testing, delegation recall, share-state creation, optional delegation grant, and MDS layout hooks.

## State and Persistence Behavior
Server state is in memory only. A restart or `reboot()` wipes sessions and client records and creates a fresh verifier. File state is delegated to `nfs4state.find_state` and each filesystem object's `state` field. Replay state is per-client for `CREATE_SESSION` and per-session fore-channel slot for `SEQUENCE`.

Lease tracking is represented by `ClientRecord.lastused`, but full grace-period and courtesy-client handling is mostly absent in this server implementation. The pNFS device table `devids` and filesystem registry `_fsids` are runtime maps populated by mounted filesystems.

## Dependencies and Integration Points
The module depends heavily on generated XDR constants/types in `xdrdef`, `nfs4lib` packing, `nfs4commoncode.CompoundState`, `nfs4state.find_state`, filesystem implementations in `fs`, server behavior knobs from `config`, and the local `rpc` framework. Export configuration is loaded dynamically by `read_exports`, whose Python module must provide `mount_stuff(server, opts)`. Server test modules interact with this file through NFS COMPOUNDs and through control/helper mechanisms such as `serverhelper`.

## Risks and Edge Cases
The code contains many incomplete protocol areas: GSS and SSV enforcement are stubs, size checks are stubs, UTF-8 validation is stubbed, session deletion is not fully synchronized, replay and client reboot semantics are incomplete, and pNFS layout operations are marked stubs. Several Python 2-era string assumptions remain visible, such as string-vs-bytes comparisons in some paths. `ClientRecord.principal_matches` references `env` without an argument, but the function does not appear to be used. `op_readlink`, `op_nverify`, and `op_verify` have suspicious error references (`NFS4_INVAL`, `e.code`) that should be treated as latent bugs.

Concurrency risk is high around state locks, file locks, delegation recall threads, and session/client deletion. Several comments explicitly note missing locking. The server is suitable as a test harness, not as a production NFS server.

## Test Signals
The adjacent `server41tests` modules exercise `EXCHANGE_ID`, `CREATE_SESSION`, `DESTROY_SESSION`, `DESTROY_CLIENTID`, COMPOUND validation, current stateid, block pNFS layout stateids, delegation recall, callback notification, courtesy expiry behavior, and copy semantics. The file also has runtime flags (`--use_block`, `--use_files`, `--is_ds`, `--show_summary`, `--debug_locks`) that drive integration tests.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4state.py -->
# sources/test-tools/pynfs/nfs4.1/nfs4state.py

## Purpose
`nfs4state.py` implements the server-side stateid and per-file state model used by `nfs4server.py`. It tracks NFSv4 open share state, byte-range locks, delegations, pNFS layouts, anonymous special stateids, and a data-server stateid bypass hack.

## Important APIs, Types, and Functions
- `find_state(env, stateid, allow_0=True, allow_bypass=False)` is the central context manager for resolving and locking a stateid. It maps special all-zero, all-ones, current, layout, and data-server stateids.
- `ByteLock` models byte ranges and conflict checks.
- `DictTree` is a fixed-depth tree used to store state entries by keys such as `(client, open_owner)` or `(client, open_owner, lock_owner)`.
- `FileStateTyped` is the base for typed state collections and creates unique `other` values for stateids.
- `ShareState`, `ByteState`, `DelegState`, `LayoutState`, and `AnonState` each own one category of state for a file.
- `FileState` aggregates the typed states and exposes methods used by the server: `test_share`, `add_share`, `recall_conflicting_delegations`, `grant_delegation`, `grant_layout`, and lock-owner creation.
- `StateTableEntry` is the base class for concrete entries: `ShareEntry`, `ByteEntry`, `DelegEntry`, `LayoutEntry`, `AnonEntry`, and `DSEntry`.

## Control Flow
Protocol operations call `find_state` with the compound environment's current filehandle and requested `stateid4`. The context manager normalizes special stateids, looks up the owning `StateTableEntry` in the current client's state dictionary, verifies filehandle match and seqid validity, acquires the shared file-state lock, yields the entry, and releases the lock.

OPEN uses `ShareState.add_share` through `FileState.add_share`, which first tests current share conflicts. LOCK creates or uses a `ByteEntry`, then `ByteEntry.add_lock` tests conflicting locks and records the range. Delegation grant uses `DelegState.grant_delegation`; conflicting opens use `DelegState.recall_conflicting_delegations`, which starts callback recall threads and raises `NFS4ERR_DELAY`. Layout grant uses `LayoutState.grant_layout` to ask the file object for a layout and populate a `LayoutEntry`.

## State and Persistence Behavior
All state is in memory and tied to file objects plus client records. Each server-issued stateid uses a client-unique `other` value that also indexes `client.state`. Entry deletion marks `invalid` and removes both the file-state tree entry and client-state reference. Anonymous stateids are per-file singleton entries. Data-server mode maps all stateids to a `DS_MAGIC` anonymous entry, intentionally bypassing normal validation.

Read/write activity counters on `StateTableEntry` let state deletion wait for current I/O. Share conflict checks cache aggregate access/deny bits until share state changes.

## Dependencies and Integration Points
The module depends on `locking.Lock`, generated NFSv4 constants/types, `nfs4lib.inc_u32`, `NFS4Error`, `nfs_ops.NFS4ops`, and callback transport exposed by the dispatcher/server. It is integrated into file objects through `file.state` and into clients through `client.state`.

## Risks and Edge Cases
Several paths are incomplete or fragile. `FileState.close` references `client` without receiving it, and commented-out lock removal helpers are still referenced in comments. `ByteState.find_conflicts.match` returns after the first key comparison, which may not implement the intended tuple-template matching. `ByteEntry.remove_lock` depends on list equality for `ByteLock`, but only `__cmp__` is defined, making Python 3 behavior risky. `mark_done_writing` checks `write_count + write_count` instead of read plus write count. Delegation and layout recall tracking is skeletal.

The module deliberately ignores DS stateids in data-server mode. That is useful for tests but weakens protocol validation.

## Test Signals
State behavior is tested indirectly by `st_current_stateid.py`, `st_block.py`, `st_delegation.py`, `st_callback.py`, `st_courtesy.py`, and lock/open tests elsewhere in the suite. Key expected signals include `NFS4ERR_BAD_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_OPENMODE`, `NFS4ERR_DENIED`, `NFS4ERR_DELAY`, delegation callback activity, and layout stateid seqid changes.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4state.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs_ops.py -->
# sources/test-tools/pynfs/nfs4.1/nfs_ops.py

## Purpose
`nfs_ops.py` provides dynamic builders for NFSv4 operations, NFSv4 callback operations, and NFSv3 procedure argument objects. It hides generated XDR constructor names behind concise methods such as `op.putfh(...)`, `op.open(...)`, or `op.cb_recall(...)`.

## Important APIs, Types, and Functions
- `nfs4_op_names()` derives lower-case operation names from `nfs4_const.nfs_opnum4` and callback names from `nfs_cb_opnum4`.
- `nfs3_proc_names()` derives lower-case NFSv3 procedure names from constants beginning with `NFSPROC3_`.
- `NFSops.__getattr__` returns a lambda for recognized operation names.
- `NFSops._handle_op()` creates the matching generated `*_args` class and wraps NFSv4 args in `nfs_argop4` or `nfs_cb_argop4`.
- `NFS3ops` and `NFS4ops` specialize the base class for protocol version.

## Control Flow
When a caller accesses `op.lookup`, `__getattr__` checks the derived operation list and returns a function that forwards to `_handle_op`. For NFSv4, `_handle_op` looks up the operation number constant, instantiates an args class if present, places it into the correct union keyword, and returns the generated argop object. For NFSv3 it returns the generated args instance directly.

## State and Persistence Behavior
The object holds immutable protocol metadata after construction: selected type module, constant module, suffix, and op prefix. It has no persistent external state.

## Dependencies and Integration Points
The module depends on generated `xdrdef.nfs4_type`, `nfs4_const`, `nfs3_type`, and `nfs3_const`. It is used throughout server tests, callback code, client helpers, and server implementation to build COMPOUND operation arrays.

## Risks and Edge Cases
Unknown attributes return `None` implicitly instead of raising `AttributeError`, which can make mistakes fail later. Dictionary-typed generated classes get special handling that assumes exactly one argument. The dynamic naming contract depends tightly on generated XDR class names and constants.

## Test Signals
Almost every test file in this group imports `NFS4ops()` and would fail quickly if operation packing broke. Specific signals include successful COMPOUND construction, callback argop construction, and correct behavior for illegal or undefined opcodes in `st_compound.py`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs_ops.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/sample_code/dataservers.conf -->
# sources/test-tools/pynfs/nfs4.1/sample_code/dataservers.conf

## Purpose
`dataservers.conf` is a sample configuration file for files-layout pNFS data servers. It shows the address grammar expected by pynfs sample code and documents how file striping order follows listed data servers.

## Important APIs, Types, and Functions
This is a configuration sample, not executable code. Supported line forms are documented as `server[:[port][/path]]` and multipath addresses as comma-separated server entries followed by an optional `/path`.

## Control Flow
Consumers read the file line by line to discover data-server addresses, optional ports, and optional paths. The examples cover IPv4, bracketed IPv6, and mixed multipath forms.

## State and Persistence Behavior
The file itself is static sample state. Runtime server state is created by whichever parser consumes these entries and connects data servers to an MDS/files layout.

## Dependencies and Integration Points
The server CLI in `nfs4server.py` has a `--dataservers` option defaulting to `dataservers.conf`. Files-layout sample exports and data-server code use this style of file to build pNFS DS topology.

## Risks and Edge Cases
It contains hard-coded example IP addresses and paths that are unlikely to work without local editing. IPv6 requires brackets to avoid ambiguity with port parsing. Comments say files stripe in listed order, so parser ordering matters.

## Test Signals
Useful test signals are parser acceptance of IPv4, IPv6, and multipath lines; defaulting of missing port to 2049; defaulting of missing path to `/`; and correct preservation of DS ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/sample_code/dataservers.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/sample_code/ds_exports.py -->
# sources/test-tools/pynfs/nfs4.1/sample_code/ds_exports.py

## Purpose
`ds_exports.py` is a minimal exports module for running a files-layout pNFS data server. It defines the `mount_stuff(server, opts)` hook consumed by `nfs4server.read_exports`.

## Important APIs, Types, and Functions
- `mount_stuff(server, opts)` creates a `StubFS_Mem(2)` filesystem and mounts it on `/pynfs_mds`.

## Control Flow
When the server starts with `--exports ds_exports.py`, `read_exports` imports this module and invokes `mount_stuff`. The function constructs the memory-backed stub filesystem and calls `server.mount`.

## State and Persistence Behavior
State is in memory through `StubFS_Mem`; there is no on-disk persistence in this sample. The numeric argument `2` is passed to the filesystem constructor and likely controls the sample filesystem identity or layout behavior.

## Dependencies and Integration Points
The file imports `StubFS_Mem` from `fs` and depends on the server exposing `mount(fs, path)`. It pairs with `dataservers.conf` and files-layout pNFS sample runs.

## Risks and Edge Cases
The mount path must match the MDS expectation in sample data-server configuration. Because the backing filesystem is memory-only, server restarts lose contents and state. There is no option handling despite receiving `opts`.

## Test Signals
A successful server startup with this exports file should log or print the mount and expose `/pynfs_mds`. pNFS file-layout tests can then validate data-server access through the mounted stub.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/sample_code/ds_exports.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/__init__.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/__init__.py

## Purpose
`server41tests/__init__.py` declares the server-side NFSv4.1 test modules exported by the package. The test runner uses `__all__` as a module inventory.

## Important APIs, Types, and Functions
- `__all__` is a list of test module filenames, including exchange/session lifecycle tests, security-info tests, sequence/trunking/open/delegation tests, pNFS tests, sparse/flex/xattr tests, courtesy tests, and callback tests.

## Control Flow
Importing the package exposes only the modules listed in `__all__` to `from server41tests import *` style discovery. Some modules are commented out, including `st_lookup.py`, `st_debug.py`, and `st_loop`.

## State and Persistence Behavior
There is no runtime state beyond the static module list.

## Dependencies and Integration Points
The file integrates with the pynfs `testmod` discovery layer and the server test runner. The presence of filenames rather than module objects suggests the runner may treat entries as loadable script names.

## Risks and Edge Cases
Commented-out modules may contain useful tests but are intentionally excluded. Duplicate or missing filenames here directly affect coverage. The list mixes active protocol areas and feature-gated tests, so runners must still honor each test's `FLAGS`.

## Test Signals
Discovery should include the requested active modules such as `st_exchange_id.py`, `st_compound.py`, `st_create_session.py`, `st_destroy_session.py`, `st_destroy_clientid.py`, `st_delegation.py`, `st_block.py`, `st_current_stateid.py`, `st_courtesy.py`, and `st_callback.py`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/environment.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/environment.py

## Purpose
`server41tests/environment.py` defines the shared test environment and helper functions for NFSv4.1 server tests. It creates clients and credentials, prepares a test tree, performs cleanup, wraps common COMPOUND patterns, and centralizes assertions.

## Important APIs, Types, and Functions
- `AttrInfo` models attribute metadata used by tests.
- `Environment(testmod.Environment)` owns primary client `c1`, credentials, test paths, sample file/link data, setup and teardown.
- `Environment.init`, `_maketree`, `finish`, `startUp`, `serverhelper`, `new_verifier`, `testname`, `clean_sessions`, and `clean_clients` implement lifecycle behavior.
- Assertion helpers `fail`, `check`, and `checkdict` raise `testmod` exceptions.
- File/object helpers include `clean_dir`, `do_readdir`, `do_getattrdict`, `create_obj`, `open_create_file`, `open_create_file_op`, `create_file`, `open_file`, `create_confirm`, `create_close`, `write_file`, `read_file`, `get_blocksize`, `close_file`, `maketree`, `lookup_obj`, `rename_obj`, and `link`.

## Control Flow
`Environment.__init__` builds the base `NFS4Client`, initializes the selected auth flavor, establishes default credentials, and sets `opts.home`. `init()` creates a session, optionally builds `/tmp` and `/tree`, verifies and empties the home directory, then destroys leftover sessions and clients. Test helpers produce operation arrays using `nfs_ops.NFS4ops` and call `sess.compound`.

`check()` accepts either one expected status or a list, converts statuses to names, and raises failures or warnings. `open_create_file_op()` is a key composition helper: it chooses the filehandle path, open flag, create mode, claim, owner, access/deny masks, and appends `GETFH`.

## State and Persistence Behavior
The environment keeps per-run unique names based on a timestamp and monotonically increasing verifiers. It creates and cleans server-side files under `opts.home`. Persistent server state is not stored here; the helpers manipulate server state through NFS operations.

## Dependencies and Integration Points
The module depends on `testmod`, `nfs4client`, `nfs4lib`, generated XDR constants/types, `rpc.security`, and `nfs_ops`. Every server41 test module imports at least `check` and often the file/open helpers.

## Risks and Edge Cases
Several defaults are mutable dictionaries in function signatures. Some helpers mix byte strings and text strings depending on call site. `clean_clients` assumes `DESTROY_CLIENTID` support. `makeStaleId` and `makeBadID` are intentionally server-specific. Long sleeps in courtesy tests can dominate runtime.

## Test Signals
Successful setup creates an empty home directory and optional `/tree` with representative object types. Helper-level failures usually indicate protocol regressions in OPEN, CLOSE, CREATE, READ, WRITE, READDIR, GETATTR, layout attribute support, or cleanup operations.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/environment.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_block.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_block.py

## Purpose
`st_block.py` contains pNFS block-layout server tests focused on layout stateid sequence handling and `LAYOUTCOMMIT` behavior.

## Important APIs, Types, and Functions
- `testStateid1` validates sequential layout stateid increments across repeated `LAYOUTGET` calls.
- `testStateid2` validates layout merging and commits an updated block extent.
- `testEmptyCommit` sends a normal `LAYOUTCOMMIT` followed by an empty opaque commit.
- `testSplitCommit` sends a disjoint block-layout update with two extents.

## Control Flow
Each test creates a pNFS client session, creates a file, extracts the filehandle and open stateid, sends one or more `LAYOUTGET` operations, unpacks block-layout opaque bodies where needed, builds `pnfs_block_layoutupdate4`, and commits with `LAYOUTCOMMIT`.

## State and Persistence Behavior
The tests exercise server layout state stored behind layout stateids and block extent metadata returned by the filesystem. They expect layout stateid seqids to start at one and increment on later layout grants.

## Dependencies and Integration Points
The module depends on `block.Packer`, `block.Unpacker`, block layout types, `nfs4lib.FancyNFS4Packer`, `get_nfstime`, `create_file`, and the server's pNFS MDS/block support.

## Risks and Edge Cases
The tests are flagged `block` and require a block-layout capable setup. Opaque parsing is noted as not general. Python string/bytes use in empty layoutupdate bodies can be sensitive under Python 3.

## Test Signals
Expected signals are `NFS4_OK` for layoutget and layoutcommit calls, exact layout stateid seqids in `BLOCK1`, and correct acceptance of empty and split layout commit opaque updates.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_block.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_callback.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_callback.py

## Purpose
`st_callback.py` tests callback behavior around lock notification, specifically that expired clients do not receive `CB_NOTIFY_LOCK` while active waiters can.

## Important APIs, Types, and Functions
- `testCbNotifyLockExpiredClient` is the sole test. It installs callback hooks with `cb_pre_hook` and `cb_post_hook`, obtains conflicting locks, expires a client, and observes callback delivery.

## Control Flow
The test creates client/session pairs, has the first client take a write lock, has the second client fail a conflicting read lock with `NFS4ERR_DENIED`, keeps the first client alive while the second expires, forces server expiration with `env.serverhelper`, then closes the first lock and verifies no callback for the expired client. It then recreates the second client, repeats the conflict, closes the first lock, and expects `CB_NOTIFY_LOCK` so the second can retry the lock successfully.

## State and Persistence Behavior
The test manipulates open and byte-range lock state, client lease expiry, and callback hook state via `threading.Event`.

## Dependencies and Integration Points
It depends on environment file helpers, NFS lock owner types, `nfs_ops`, callback hook support in `nfs4client`, and an optional external server helper command capable of expiring a client.

## Risks and Edge Cases
The test uses fixed 60-second sleeps and an external expiration helper, so runtime and reliability depend on server lease settings and environment configuration. Courtesy-client behavior can affect intermediate expectations.

## Test Signals
Signals include `NFS4ERR_DENIED` for conflicting locks, no callback after forced expiry, `NFS4ERR_BADSESSION` for the expired session close, and callback delivery plus successful lock retry for the recreated active waiter.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_callback.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_compound.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_compound.py

## Purpose
`st_compound.py` tests basic NFSv4.1 COMPOUND request validation: empty compounds, tags, invalid minor versions, and illegal or undefined opcodes.

## Important APIs, Types, and Functions
- `_simple_ops` builds a valid `EXCHANGE_ID` operation sequence.
- `testZeroOps`, `testGoodTag`, `testBadTags`, `testInvalidMinor`, `testInvalidMinor2`, and `testUndefined` each target one COMPOUND rule.
- `CustomPacker` inside `testUndefined` intentionally packs invalid opcodes.

## Control Flow
Tests send COMPOUND calls through `env.c1`, sometimes with custom tags or minor versions. Invalid opcode testing uses a packer override to force raw opnum emission when generated XDR packing would reject the object.

## State and Persistence Behavior
The tests mostly avoid persistent server state, except for `_simple_ops` creating or referencing client owner identity through `EXCHANGE_ID`.

## Dependencies and Integration Points
The module depends on `nfs_ops`, environment assertions, generated XDR types/constants, `rpc.rpc.RPCAcceptError`, and `nfs4lib.FancyNFS4Packer`.

## Risks and Edge Cases
The invalid UTF-8 test depends on server UTF-8 validation, which the local test server stubs out. The undefined-opcode behavior allows either `NFS4ERR_OP_ILLEGAL` or RPC `GARBAGE_ARGS` for some cases, reflecting protocol ambiguity noted in comments.

## Test Signals
Expected statuses include `NFS4_OK`, `NFS4ERR_INVAL`, `NFS4ERR_MINOR_VERS_MISMATCH` with empty result arrays, `NFS4ERR_OP_ILLEGAL`, and acceptable RPC-level `GARBAGE_ARGS`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_compound.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_copy.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_copy.py

## Purpose
`st_copy.py` tests server-side `COPY` behavior for the special zero-length copy case, where length zero means copy to EOF.

## Important APIs, Types, and Functions
- `testZeroLengthCopy` creates a source file, writes data, creates a destination file, sends `COPY`, and checks the copied byte count.

## Control Flow
The test opens/creates a source file, writes fixed data, creates a second file, builds a compound of `PUTFH(source)`, `SAVEFH`, `PUTFH(dest)`, and `COPY(source_stateid, dest_stateid, 0, 0, 0, ...)`, then checks that `wr_count` equals the source data length.

## State and Persistence Behavior
It uses open stateids for both source and destination and writes persistent file contents in the test directory for the duration of the test.

## Dependencies and Integration Points
It depends on `create_file`, `write_file`, `nfs_ops.NFS4ops`, and a server implementing `OP_COPY`.

## Risks and Edge Cases
The local `nfs4server.py` read in this group does not implement `op_copy`, so this test is aimed at external servers or later code, not necessarily the embedded test server. It does not explicitly close files after the assertion.

## Test Signals
The core signal is `NFS4_OK` and a `COPY` response count equal to `len(b"write test data")` when copy length is zero.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_copy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_courtesy.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_courtesy.py

## Purpose
`st_courtesy.py` tests NFSv4 courtesy-client behavior after lease expiry, with emphasis on locks, share reservations, conflicting opens, and purge performance.

## Important APIs, Types, and Functions
- `_getleasetime(sess)` reads `FATTR4_LEASE_TIME`.
- `cour_lockargs(fh, stateid)` builds a write lock operation sequence.
- Tests `testLockSleepLockU`, `testLockSleepLock`, `testShareReservation00`, `testShareReservationDB01`, `testShareReservationDB02`, `testShareReservationDB03`, and `testExpiringManyClients` cover courtesy lock/share scenarios.

## Control Flow
Tests create one or more client sessions, create/open files with selected access and deny modes, sleep beyond the lease period, and then verify whether conflicting locks or opens succeed. `testExpiringManyClients` creates many expired clients and measures whether a conflicting open can trigger purge without excessive delay.

## State and Persistence Behavior
The tests rely on server lease expiry, courtesy preservation of client state, open share reservations, and byte-range locks. State transitions are time-driven through sleeps of lease time plus a margin.

## Dependencies and Integration Points
The module depends on environment helpers for open/create/close, generated NFS lock and open types, and server support for courtesy-client semantics. It reads lease time through GETATTR.

## Risks and Edge Cases
These tests are slow and timing-sensitive. They assume lease expiry can be observed by sleeping and that servers distinguish expired courtesy state from active conflicts. The 1000-client test can be resource-intensive.

## Test Signals
Expected statuses include retained client operations succeeding or warning with `NFS4ERR_BADSESSION`, post-expiry conflicting locks/open succeeding, pre-expiry conflicts returning `NFS4ERR_SHARE_DENIED`, and large courtesy purges not blocking a valid conflicting open.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_courtesy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_create_session.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_create_session.py

## Purpose
`st_create_session.py` tests NFSv4.1 `CREATE_SESSION` behavior, including basic creation, replay handling, principal changes, invalid clientids, callback security parameters, RDMA arrays, channel limits, response-size errors, and DRC memory stress.

## Important APIs, Types, and Functions
- `create_session(c, clientid, sequenceid, cred=None, flags=0)` sends a basic `CREATE_SESSION`.
- Tests include `testSupported1`, `testSupported2`, `testSupported2b`, `testNoExchange`, replay tests, bad sequence tests, principal collision tests, callback security/RDMA tests, channel limit tests, and stress tests like `testDRCMemLeak`.

## Control Flow
Most tests create a client through `env.c1.new_client`, then call either the client's high-level `create_session` or the module helper with custom args. Replay tests resend identical or sequence-wrapped requests and compare responses with tags cleared. Limit tests construct custom `channel_attrs4`.

## State and Persistence Behavior
The file exercises unconfirmed and confirmed client records, per-client `CREATE_SESSION` sequence ids, session replay cache, session tables, backchannel callback configuration, and DRC memory allocation under repeated failed calls.

## Dependencies and Integration Points
It depends on `nfs_ops`, environment helpers, generated channel/callback types, `nfs4lib`, threading, and RPC error classes. It integrates with callback handling through client program hooks and callback security parameter arrays.

## Risks and Edge Cases
Some tests use large iteration counts (`10000`) or rely on servers returning SHOULD-level errors like `NFS4ERR_TOOSMALL`. Callback program/version tests are Ganesha-flagged and depend on transient callback behavior. Some server implementations may accept or reject RDMA array encodings differently.

## Test Signals
Signals include `NFS4_OK`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_SEQ_MISORDERED`, `NFS4ERR_CLID_INUSE`, `NFS4ERR_INVAL`, `NFS4ERR_BADXDR` or `GARBAGE_ARGS`, `NFS4ERR_NOT_ONLY_OP`, `NFS4ERR_TOOSMALL`, `NFS4ERR_REP_TOO_BIG`, and `NFS4ERR_REP_TOO_BIG_TO_CACHE`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_create_session.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_current_stateid.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_current_stateid.py

## Purpose
`st_current_stateid.py` tests NFSv4.1 current-stateid processing, where `stateid4(seqid=1, other=all-zero)` refers to the current stateid produced by prior operations in the same compound.

## Important APIs, Types, and Functions
- `current_stateid = stateid4(1, b'\0' * 12)` is the test's current-stateid marker.
- Tests cover OPEN+CLOSE, LOCK+LOCKU, OPEN+WRITE+CLOSE, LOCK+WRITE+LOCKU, current stateid invalidation after filehandle changes, close without prior stateid, OPEN+LAYOUTGET, OPEN+SETATTR, FREE_STATEID interactions, and SAVEFH/RESTOREFH preservation.

## Control Flow
Tests build multi-op compounds where an operation that returns a stateid is followed by an operation that consumes `current_stateid`. Negative tests change the current filehandle with LOOKUP or omit a stateid-producing op and expect stale/bad stateid errors.

## State and Persistence Behavior
The file exercises compound-local state tracking in the client/server response flow, not durable state. It also touches open, lock, layout, setattr, and free-stateid server state.

## Dependencies and Integration Points
It depends on helpers from `environment.py`, generated open/lock types, `nfs_ops`, and pNFS support for the layout test.

## Risks and Edge Cases
Current-stateid semantics are sensitive to current filehandle changes and to which operation last produced state. Tests expect either `NFS4ERR_STALE_STATEID` or `NFS4ERR_BAD_STATEID` in some negative paths, allowing implementation variation.

## Test Signals
Positive signals are `NFS4_OK` for valid same-compound current-stateid consumers. Negative signals include stale or bad stateid errors after unrelated LOOKUP or when no usable current stateid exists, and `NFS4ERR_LOCKS_HELD` for FREE_STATEID plus CLOSE sequencing.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_current_stateid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_debug.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_debug.py

## Purpose
`st_debug.py` contains ad hoc/debug-oriented server tests for open/delegation behavior, simple read/write, concurrent write/getattr deadlocks, and early layout/device-list checks. It is commented out of `server41tests.__all__`.

## Important APIs, Types, and Functions
- `testSupported2` probes open delegation handling across two clients.
- `testReadWrite` creates a file, writes, reads, and closes.
- `testDeadlock` sends multiple asynchronous write/getattr compounds on separate slots.
- `testLayout` and `testGetDevList` test layout and device-list basics.

## Control Flow
The tests build lower-level open operations directly, use sessions created from raw clients, and issue compounds manually. `testDeadlock` starts four async compounds and then listens for each result.

## State and Persistence Behavior
It exercises open stateids, delegation recall, file contents, asynchronous slot state, and pNFS layout/device state. Debug tests leave more printed output than normal tests.

## Dependencies and Integration Points
The module depends on `st_create_session`, environment helpers, generated NFS types, and `nfs_ops`. Layout tests assume helpers such as `get_blocksize` and `use_obj`, but the imports appear incomplete for those names in this file.

## Risks and Edge Cases
Several visible issues make this file unsuitable for default runs: text strings instead of bytes in some owners/data, undefined variables (`res`, `sess1`) in layout paths, and missing imports for helper names. Its exclusion from `__all__` matches these risks.

## Test Signals
When run manually after fixes, useful signals would be successful open/read/write/close, no deadlock under async write/getattr load, and `GETDEVICELIST` success for block-layout exports.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_debug.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_delegation.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_delegation.py

## Purpose
`st_delegation.py` tests NFSv4.1 open delegations, recall callbacks, callback security parameters, delegation revocation, delegation conflict rules, CB_GETATTR, and reads using delegation stateids after close.

## Important APIs, Types, and Functions
- `_got_deleg`, `__create_file_with_deleg`, and `_create_file_with_deleg` obtain and validate delegations.
- `_testDeleg` sets callback hooks, triggers a conflicting open from another client, waits for `CB_RECALL`, returns the delegation, and checks the waiting open.
- `_testCbGetattr` installs `CB_GETATTR` response hooks and compares attributes seen by another client.
- Tests cover read/write/any/no delegation, callback auth flavors, `BACKCHANNEL_CTL`, revocation with `TEST_STATEID`/`FREE_STATEID`, self-conflict behavior, write-open vs read delegation, `CB_GETATTR`, and delegation read after close.

## Control Flow
Most tests create a first session with callback hooks, obtain a delegation through OPEN/create, then create a second session to issue a conflicting OPEN or GETATTR. The first session responds to recall or getattr callbacks, and the test checks the second request outcome.

## State and Persistence Behavior
The tests rely on delegation stateids surviving close in valid cases, revocation state being reflected in SEQUENCE status flags, callback channels carrying recall/getattr, and server state clearing after `FREE_STATEID`.

## Dependencies and Integration Points
The module depends on environment helpers, `st_open.open_claim4`, generated NFS types/constants, `nfs_ops`, `nfs4lib`, and callback-hook support in the client harness.

## Risks and Edge Cases
Delegation support varies by server and export. Tests use short waits for callbacks and can be timing-sensitive. Some expectations, such as `OPEN_DELEGATE_NONE_EXT` for no-delegation requests, require modern protocol support. The file has duplicated imports and minor typos in comments, but functional intent is clear.

## Test Signals
Expected signals include `NFS4_OK` for valid delegation operations, callback arrival events for `OP_CB_RECALL` and `OP_CB_GETATTR`, `NFS4ERR_DELAY` as an acceptable conflict response, `NFS4ERR_DELEG_REVOKED`, `SEQ4_STATUS_RECALLABLE_STATE_REVOKED`, and correct callback credential flavors.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_delegation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_clientid.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_clientid.py

## Purpose
`st_destroy_clientid.py` tests `DESTROY_CLIENTID` behavior for unconfirmed clients, nonexistent clientids, clients with sessions, compound placement, and repeated destroy calls.

## Important APIs, Types, and Functions
- Tests include `testSupported`, `testDestroyCIDWS`, `testDestroyBadCIDWS`, `testDestroyBadCIDIS`, `testDestroyCIDSessionB`, `testDestroyCIDCSession`, `testDestroyCIDNotOnly`, and `testDestroyCIDTwice`.

## Control Flow
Tests create clients and sometimes sessions, then send `op.destroy_clientid(clientid)` either outside a session through `env.c1.compound` or inside a session through `sess.compound`. They assert the status for each lifecycle case.

## State and Persistence Behavior
The file exercises client records before and after confirmation, session association, and removal from the server's clientid table. Repeated calls validate stale-clientid behavior after removal.

## Dependencies and Integration Points
It depends on `st_create_session.create_session`, environment assertions, `nfs_ops`, and `nfs4lib`.

## Risks and Edge Cases
The embedded `nfs4server.py` in this group does not implement `op_destroy_clientid`, so these tests target compliant external servers or code not shown here. The use of clientid `0` as nonexistent is a heuristic and can collide in artificial servers.

## Test Signals
Expected statuses are `NFS4_OK`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_CLIENTID_BUSY`, and `NFS4ERR_NOT_ONLY_OP`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_clientid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_session.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_session.py

## Purpose
`st_destroy_session.py` tests `DESTROY_SESSION` lifecycle behavior, connection binding, callback recovery after session destruction, compound placement rules, and a skeleton for lock conflict races.

## Important APIs, Types, and Functions
- `testDestroyBasic` checks that operations using a destroyed session fail and a new session works.
- `testDestroy` verifies connection binding before destroying from a new TCP connection.
- `testDestroy2` and `testDestroy3` verify callback behavior after session destruction and recreation.
- `testDestoryNotFinalOps` and `testDestoryNotSoleOps` check RFC placement rules.
- `testDestroyLockConfRace` is present but incomplete.

## Control Flow
Tests create sessions, destroy them through raw or session compounds, then attempt further operations. Callback tests obtain delegations, trigger recalls from a second client, destroy the callback-bearing session, create a new session, and wait for callback delivery.

## State and Persistence Behavior
The tests manipulate session tables, connection binding state, callback channels, delegation state, and open state. They expect destroyed sessions to become invalid while client records can create replacement sessions.

## Dependencies and Integration Points
The module depends on environment helpers, generated open types, `nfs_ops`, threading events, and `rpc.rpc` connection helpers.

## Risks and Edge Cases
Two function names spell `Destroy` as `Destory`, but that only affects test names. Callback retry timing uses long waits and depends on server callback policy. `testDestroyLockConfRace` is incomplete and should not be treated as a full assertion.

## Test Signals
Expected statuses include `NFS4ERR_BADSESSION` after destruction, `NFS4ERR_CONN_NOT_BOUND_TO_SESSION` before binding a new connection, `NFS4_OK` after proper binding, callback arrival events, and `NFS4ERR_NOT_ONLY_OP` for illegal compound placement.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_destroy_session.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_exchange_id.py -->
# sources/test-tools/pynfs/nfs4.1/server41tests/st_exchange_id.py

## Purpose
`st_exchange_id.py` tests NFSv4.1 `EXCHANGE_ID` behavior, including basic support, pNFS flag reporting, SSV setup, implementation id encoding, invalid flags, confirmed/unconfirmed client-owner replacement cases, update semantics, not-only-op rules, and lease expiry of unconfirmed records.

## Important APIs, Types, and Functions
- `_getleasetime(sess)` reads the server lease time.
- `_raw_exchange_id(c, name, verf=None, cred=None, protect=None, flags=0)` sends a configurable `EXCHANGE_ID`.
- `testSupported`, `testSupported1a`, `testSupported2`, `testSSV`, `testNoImplId`, `testLongArray`, and `testBadFlags` cover basic protocol validation.
- `testNoUpdate*` and `testUpdate*` encode draft-21 client-owner case matrix tests.
- `testNotOnlyOp` and `testLeasePeriod` cover operation placement and unconfirmed record expiry.

## Control Flow
Tests construct `client_owner4` values from verifier/name pairs, choose state protection, send `op.exchange_id`, and inspect returned status, clientid, flags, and later session behavior. Matrix tests vary confirmed state, verifier equality, principal equality, and update flag presence.

## State and Persistence Behavior
The tests exercise server client-owner records, unconfirmed vs confirmed clientids, verifier-based reboot detection, principal ownership, session invalidation after replacement, and lease-driven expiry of unconfirmed records.

## Dependencies and Integration Points
The module depends on environment assertions and verifier generation, generated NFS types/constants, `nfs_ops`, `nfs4lib` hash/encryption OID registries, RPC exceptions, and real credentials from the test environment.

## Risks and Edge Cases
There are two functions named `testSupported1a`; the latter server-only-flag test overwrites the earlier simple-flag test in normal Python module loading. Several tests are draft-21 specific and may differ from final RFC behavior or server policy. Lease tests use sleeps and can be slow or flaky when lease times are large or cleanup policies vary.

## Test Signals
Expected signals include `NFS4_OK`, server pNFS/non-pNFS use flags set in `eir_flags`, `NFS4ERR_BADXDR` or RPC `GARBAGE_ARGS` for too-long implementation arrays, `NFS4ERR_INVAL` for bad/server-only flags, `NFS4ERR_NOENT`, `NFS4ERR_NOT_SAME`, `NFS4ERR_PERM`, `NFS4ERR_CLID_INUSE`, `NFS4ERR_STALE_CLIENTID`, and `NFS4ERR_NOT_ONLY_OP`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/server41tests/st_exchange_id.py -->
