# subset-b-009310 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4server.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4server.py

## Purpose
`nfs4server.py` is a small Python NFSv4.0 server implementation used by pynfs test tooling. It subclasses `rpc.RPCServer`, decodes NFS COMPOUND calls, dispatches each operation to an `op_*` method, and uses `nfs4state` for the virtual filesystem, client IDs, open state, lock state, share reservations, stateid sequencing, and replay handling. It is intentionally incomplete in some protocol areas, with explicit stubs for delegation, openattr, release lockowner, and partial SECINFO behavior.

## Important APIs, Types, And Functions
- `verify_name(name)` enforces component name policy: empty names are `NFS4ERR_INVAL`, names longer than `NFS4_FHSIZE` are `NFS4ERR_NAMETOOLONG`, `"."`/`".."`
  are `NFS4ERR_BADNAME`, configured characters such as `/`, `~`, and `#` are `NFS4ERR_BADCHAR`, and invalid UTF-8 is `NFS4ERR_INVAL`.
- `verify_utf8(str)` uses `codecs.utf_8_decode` as the common tag/name validation primitive.
- `simple_error(error, *args)` uses the caller's `op_*` name to construct the matching `*_4res` and `nfs_resop4` wrapper. This keeps operation handlers compact but tightly couples handler names to generated XDR class names.
- `NFS4Server.__init__(rootfh, host, port, pubfh=None)` wires packers/unpackers, `NFSServerState`, filehandle cache, root/public handles, and verifier counter.
- `handle_0()` implements NULL RPC, including limited RPCSEC_GSS proc handling.
- `handle_1()` unpacks a COMPOUND request, calls `O_Compound`, packs `COMPOUND4res`, and returns an RPC success or XDR garbage result.
- `O_Compound()` validates minor version and UTF-8 tag, resets per-compound current/saved handles, sequentially dispatches opcodes through `nfs_opnum4`, stops at first NFS error, and returns the result array.
- `op_access`, `op_getattr`, `op_getfh`, `op_lookup`, `op_lookupp`, `op_putfh`, `op_putrootfh`, `op_savefh`, and `op_restorefh` implement basic filehandle and attribute flow.
- `op_create`, `op_open`, `op_close`, `op_open_confirm`, `op_open_downgrade`, `op_read`, `op_write`, `op_commit`, `op_lock`, `op_lockt`, `op_locku`, `op_remove`, `op_rename`, and `op_link` are the main stateful filesystem operations.
- `op_setclientid` and `op_setclientid_confirm` implement the client ID handshake over `NFSServerState.confirmed` and `.unconfirmed`.
- `startup(host, port)` builds a `VirtualHandle` root, registers with portmap if possible, and starts the RPC server loop.

## Control Flow
A TCP NFS request enters `handle_1`, which resets the `FancyNFS4Unpacker`, delegates protocol logic to `O_Compound`, and packs the resulting `COMPOUND4res`. `O_Compound` unpacks the whole request, rejects minor versions other than zero and invalid UTF-8 tags, then initializes `curr_fh` and `saved_fh` for the compound. For each `nfs_argop4`, it maps the numeric opcode to a generated name such as `OP_OPEN`, lowercases that name into a method such as `op_open`, executes it, appends the returned `nfs_resop4`, and stops on the first non-OK status. Individual handlers return through `simple_error`, so the dispatch loop only deals with uniform `(status, result_op)` tuples.

Stateful operations first validate replay sequence IDs via `self.state.check_seqid`. If a replay is detected, `check_replay` compares the newly packed operation to the cached operation and either returns the cached result or `NFS4ERR_BAD_SEQID`. Non-replay mutations call `self.state.advance_seqid` after success or after sequence-consuming errors so repeated requests can be answered consistently.

Filesystem control flow is filehandle-centered. `PUTROOTFH`, `PUTPUBFH`, and `PUTFH` set `curr_fh`; `SAVEFH` snapshots it for later `LINK`/`RENAME`; `RESTOREFH` restores it. `GETFH` inserts the current in-memory handle into `fhcache` before returning its opaque bytes; `PUTFH` can only resolve handles previously cached this way. `LOOKUP` and `LOOKUPP` replace `curr_fh` with child/parent virtual handles. `CREATE`, `REMOVE`, `RENAME`, and `LINK` mutate `VirtualHandle` directory entries and return `change_info4` derived from the directory change counters.

Open control flow validates client ID confirmation, owner sequence, current directory, claim type, target name, and open/create mode. It handles `OPEN4_CREATE` with `EXCLUSIVE4`, `GUARDED4`, and unchecked/create-attrs behavior, then delegates share reservation and stateid generation to `NFSServerState.open`. Delegations are always returned as `OPEN_DELEGATE_NONE`. `CLOSE`, `OPEN_CONFIRM`, and `OPEN_DOWNGRADE` translate stateids and update cached state through `NFSServerState`.

Read/write/control operations validate current filehandle type and stateid access. `READ`, `WRITE`, and `SETATTR(size)` call `NFSServerState.check_read` or `check_write` before touching file data. `COMMIT` validates regular-file type and offset/count overflow but returns the in-memory `write_verifier`; comments explicitly state the RAM-backed server pretends operations are `FILE_SYNC4`.

## State And Persistence Behavior
The server has no durable storage by default. `startup` uses `nfs4state.VirtualHandle`, which stores directories, file data, attributes, link counts, ACLs, and locks in memory. Restarting loses the file tree, client IDs, filehandle mappings, and all open/lock state. `fhcache` is also process-local and is only populated by `GETFH`, which the source comments identify as incomplete for handles embedded in GETATTR or READDIR results.

Persistent-looking protocol state is simulated in `NFSServerState`: server instance bytes, generated client IDs, setclientid verifiers, open owner/lock owner sequence numbers, cached replay responses, stateids, share reservations, lock ranges, and lease timestamps. `write_verifier` and `nextverf()` are generated from process time and a local counter.

## Dependencies And Integration Points
The module depends on generated XDR constants and types from `xdrdef.nfs4_const`, `xdrdef.nfs4_type`, and `xdrdef.nfs4_pack`, pynfs helpers in `nfs4lib`, RPC infrastructure in `rpc.rpc`/`rpc.portmap`, and implementation state in `nfs4state`. It is executable as a server script and adjusts `sys.path` when run from the package root. The server is implicitly exercised by the `servertests` modules through `NFS4Client` operations that expect RFC3530-style NFSv4.0 behavior.

## Risks And Edge Cases
- The shebang says Python 3, but the file contains Python 2 constructs and imports (`StringIO`, `print` statements without parentheses in places, `long` indirectly through `nfs4state`), so runtime compatibility depends on the larger pynfs conversion state.
- `simple_error` relies on generated globals and caller naming conventions; a renamed handler or missing generated class becomes a runtime `RuntimeError`.
- `op_access` computes invalid bits with `all = ~valid_mask`; Python's unbounded negative integers make expression precedence and bit handling sensitive.
- Filehandle cache behavior is explicitly incomplete and can produce `NFS4ERR_BADHANDLE` for handles not first seen through `GETFH`.
- Many RFC details are stubs or simplified: delegations, open attributes, release lockowner, SECINFO, access control, callback principals, and stable storage semantics.
- `op_setclientid_confirm` implements noted departures from RFC logic and assumes a single matching entry by client owner string.
- Several operations check type and names but not real permissions; comments mark access checking as TODO around remove/rename/link.

## Test Signals
This file is directly targeted by the server tests in this group: ACCESS verifies invalid masks and no-current-filehandle behavior; CREATE/LINK/GETFH/GETATTR/COMMIT/CLOSE/LOCK/LOCKT verify operation-level status returns; COMPOUND verifies minor versions, tags, illegal op packing, and long sequences; delegation and GSS tests exercise unsupported or surrounding RPC/security behavior. The strongest test signals are expected NFS status codes, replay sequence behavior, stateid transitions, and `change_info4`/attribute effects observed through client compounds.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4state.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4state.py

## Purpose
`nfs4state.py` supplies the in-memory state engine and virtual filesystem used by the Python NFSv4 server. It models client ID caches, NFSv4 stateids, open owners, lock owners, share reservations, POSIX-like byte-range locks, virtual filehandles, attributes, ACL mapping, hard links, directory cookies, and an optional hard-backed filehandle implementation. It is the semantic core behind `nfs4server.py` operations.

## Important APIs, Types, And Functions
- `NFS4Error(code, msg=None, attrs=0, lock_denied=None)` carries NFS status codes plus partial attribute masks and lock-denied payloads.
- `mod32`, `converttime`, `packnumber`, `unpacknumber`, and `printverf` implement protocol-sized counters, NFS time values, and verifier/stateid byte strings.
- Global `InstanceKey` and `Mutate()` influence generated filehandle bytes; global `POSIXLOCK` and `POSIXACL` select lock and ACL semantics.
- `NFSServerState` owns protocol state: confirmed/unconfirmed `ClientIDCache`, `state` dict of internal IDs to `StateIDInfo`, server `instance`, `write_verifier`, `openowners`, `lockowners`, and root handle for lease time.
- `ClientIDCache` stores `(client verifier, client owner id, clientid, callback, server verifier, principal, time)` entries and supports matching, renewal, expiry, and removal.
- `OwnerInfo` stores per-open-owner or per-lock-owner sequence state, cached replay response, confirmation flag, lockowner/openid linkage, and file-to-state-id mappings.
- `NFSServerState.check_seqid`, `advance_seqid`, `confirm`, `open`, `close`, `new_lockowner`, `lock`, `testlock`, `unlock`, `check_read`, `check_write`, `downgrade`, `renew`, and `remove_state` are the main server-facing operations.
- `NFSFileState` owns per-file share and lock state. It converts two-bit NFS share masks to internal three-bit values, detects share conflicts, checks access, adds/removes/merges locks, and tests conflicts.
- `NFSFileHandle` is an abstract-ish base for NFS-visible objects. `VirtualHandle` implements the RAM filesystem; `HardHandle` wraps real OS paths for limited hard-backed use.
- `VirtualHandle.supported` maps NFS attribute numbers to read/write/not-supported flags, driving both `get_attributes` and `set_attributes`.
- `DirList` stores directory entries with monotonically increasing cookies and a verifier for READDIR.

## Control Flow
Client setup starts in `NFSServerState.new_clientid`, `ClientIDCache.add`, and the server's SETCLIENTID/CONFIRM handlers. Confirmed client IDs renew leases through explicit `renew` and implicit `__renew` calls whenever stateids are used. Open owner and lock owner sequence IDs are validated with `check_seqid`; accepted responses are cached in `advance_seqid` for replay handling.

Open state flows from `open(fh, owner, access, deny)`. The method resolves or creates an `OwnerInfo`, handles unconfirmed open-owner replacement rules, allocates an internal numeric state ID for the `(owner, fh)` pair, asks the file's `NFSFileState` to test and add share reservations, and returns a generated `stateid4`. Open confirmation marks the owner confirmed and returns a fresh stateid. Close removes locks associated with the open, removes share reservations, deletes owner file mappings, marks the state entry closed, and renews the lease.

Stateid translation is centralized in private helpers. `__state2id` recognizes special all-zero and all-ones stateids, rejects stateids from older server instances with `NFS4ERR_STALE_STATEID`, rejects unknown IDs with `NFS4ERR_BAD_STATEID`, and can detect old stateid sequence numbers. `__stateid` increments the stored stateid seqid, combines server instance bytes with packed internal ID bytes, and renews the lease.

Lock flow resolves either a new lock owner or existing lock stateid to an internal ID, validates range length and overflow with `__getlockend`, checks conflicts through `__testlock`, records the lock in the file's `NFSFileState`, confirms the lock owner, and returns a new lock stateid. `LOCKT` creates or resolves a test owner, checks client ID freshness, and tests conflicts without changing the server's effective lock table. `check_read` and `check_write` combine open share access checks with range lock conflict checks; when passed an open stateid they include all lock stateids tied to that open owner.

The RAM filesystem starts with `VirtualHandle`. Construction sets default attributes, initializes `DirList` for directories, `StringIO` plus `NFSFileState` for regular files, link target state for symlinks, or raw device data for block/char nodes. `create` validates directory context, creates a child `VirtualHandle`, filters attributes inappropriate for the type, applies attributes through `set_attributes`, inserts it into the `DirList`, and updates change/time/size fields. `read`, `write`, `remove`, `rename`, `hardlink`, `lookup`, `read_dir`, `read_link`, and `do_lookupp` implement object operations used by the server handlers.

Attribute flow uses the `supported` table. `set_attributes` rejects unknown, read-only, or explicitly unsupported attrs, applies custom setters such as `set_fattr4_size`, `set_fattr4_time_modify_set`, `set_fattr4_time_access_set`, and `set_fattr4_acl`, updates metadata time/change counters, and returns a bitmap of successfully set attrs. `get_attributes` ignores unknown/unreadable attrs and either ignores or errors on not-supported attrs depending on the caller's `ignore` flag.

## State And Persistence Behavior
All primary state is process memory. Client IDs encode `self.instance`, which is derived from process start time; stateids also embed that instance. A restart causes old client IDs and stateids to become stale or bad. Virtual files store bytes in `StringIO`, directory entries in `DirList`, attributes on object instances, ACLs as generated pynfs ACL structures, and locks/shares in `NFSFileState`. There is no disk synchronization or crash recovery. `HardHandle` can read/write real filesystem paths but is incomplete and separate from the default server path.

## Dependencies And Integration Points
The module imports generated NFSv4 XDR constants/types, `rpc.rpc`, `nfs4acl`, `nfs4lib`, `sha`, `stat`, and OS/time/random/string helpers. It is tightly integrated with `nfs4server.py`, which catches `NFS4Error`, calls `NFSServerState` for protocol state, and invokes `VirtualHandle` methods for filesystem semantics. ACL behavior delegates to `nfs4acl.maps_to_posix`, `acl2mode`, and `mode2acl`. Attribute names and bitmaps rely on `nfs4lib`.

## Risks And Edge Cases
- The file mixes Python 2 idioms (`long`, `array.tostring`, `string.join`, `sha`, old exception syntax in one `except`) with Python 3-looking callers, which is a portability risk.
- Several errors are raised as strings, not exceptions; this is invalid in Python 3 and fragile even in Python 2-era code.
- `ClientIDCache.remove` deletes while iterating a zipped range/list snapshot and removes only matching indices from the live list, which is brittle for multiple matches.
- `DirList.__setitem__` tries `del self.list[x]` where `x` is a `DirEnt`, not an index, in the duplicate-name branch.
- `NFSFileState.addposixlock` and `removeposixlock` call `list.sort()` on `LockInfo` objects that define `__cmp__`, not rich comparisons, which is another Python 3 conversion risk.
- `check_read` and `check_write` have FIXME notes around reserved stateids and rely on simplified share semantics.
- `VirtualHandle.get_attributes` silently ignores unknown and some unreadable attrs, which may not match strict server behavior tests for write-only attributes.
- Hard-backed `HardHandle` is incomplete: constructor argument order in `read_dir` appears inconsistent, supported attrs are limited, and directory cache initialization is not obvious.

## Test Signals
The associated server tests exercise this module indirectly. Close tests validate sequence IDs, bad/old/stale stateids, lease expiry, lock release on close, and replay. Lock and LOCKT tests validate lock conflict detection, range overflow, zero length, stateid freshness, share/open mode interactions, POSIX lock merge/split behavior, and lease expiry cleanup. CREATE/LINK/GETATTR/GETFH/COMMIT tests validate virtual file type handling, attributes, link counts, directory cookies, and filehandle generation. ACL tests specifically signal `set_fattr4_acl` and POSIX ACL mapping behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4state.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs_ops.py -->
# sources/test-tools/pynfs/nfs4.0/nfs_ops.py

## Purpose
`nfs_ops.py` is a convenience factory for building NFSv3 procedure argument instances and NFSv4 operation wrapper structures from generated XDR type modules. It lets tests call `op.lookup(name)` or `op.getattr(mask)` instead of manually constructing `LOOKUP4args`, `nfs_argop4(OP_LOOKUP, oplookup=...)`, and equivalent callback wrappers.

## Important APIs, Types, And Functions
- `nfs4_op_names()` derives lowercase operation names from `nfs4_const.nfs_opnum4` and callback operation names from `nfs_cb_opnum4`.
- `nfs3_proc_names()` derives lowercase NFSv3 procedure names from constants named `NFSPROC3_*`.
- `NFSops.__init__(is_v4)` selects type/constant modules, operation names, argument suffixes, and opcode prefixes for v3 or v4.
- `NFSops.__getattr__(attrname)` dynamically returns a lambda builder when `attrname` is a known operation/procedure name.
- `NFSops._handle_op(opname, args)` constructs the matching generated argument class and wraps it in `nfs_argop4`/`nfs_cb_argop4` for v4, or returns the generated procedure args for v3.
- `NFS3ops` and `NFS4ops` are thin typed constructors.

## Control Flow
Callers instantiate `NFS4ops()` or `NFS3ops()`. Accessing a valid operation name triggers `__getattr__`, returning a function that captures the operation name and forwards positional arguments to `_handle_op`. `_handle_op` uppercases the operation, finds the generated `*4args` or `*3args` class, constructs it when needed, looks up the opcode constant, then returns a generated wrapper. For NFSv4 callback operation names beginning with `CB_`, it uses `nfs_cb_argop4` and the `opcb...` keyword; otherwise it uses `nfs_argop4` and `op...`.

## State And Persistence Behavior
Instances store only immutable factory configuration: whether they are v4, selected module references, operation names, suffixes, and prefixes. There is no persistence, caching of generated operations, or external state mutation.

## Dependencies And Integration Points
The module depends on `xdrdef.nfs4_type`, `xdrdef.nfs4_const`, `xdrdef.nfs3_type`, and `xdrdef.nfs3_const`. It is used broadly in the `servertests` package and in delegation callback helpers to build compounds. Its output structures are consumed by `NFS4Client.compound`, server dispatch, packers, and callback servers.

## Risks And Edge Cases
- Unknown attributes return `None` from `__getattr__` rather than raising `AttributeError`, which can mask typos until call time.
- The special `if type(klass) is dict` branch suggests generated type metadata can be a dict; callers must pass exactly one prebuilt argument for that path.
- Operation names are derived from constant dictionaries at import/runtime, so generated XDR naming changes directly alter the dynamic API surface.
- There is no keyword-argument support; all operation argument constructors must be satisfied positionally.

## Test Signals
All server tests in this group use `op = nfs_ops.NFS4ops()` for raw operation construction. Failures in this factory surface as malformed compounds, packer errors, or wrong `resop`/argument union fields in ACCESS, COMPOUND, CREATE, LINK, LOCK, DELEGRETURN, and GSS scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs_ops.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/__init__.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/__init__.py

## Purpose
`servertests/__init__.py` declares the NFSv4 server test modules exported by the package. The `__all__` list is a manifest of test modules that the surrounding pynfs test runner can discover or import, including operation-specific tests, replay/reboot/spoof tests, filesystem-location tests, GSS tests, and delegation tests.

## Important APIs, Types, And Functions
- `__all__` is the only API. It lists module filenames such as `st_access.py`, `st_create.py`, `st_lock.py`, `st_gss.py`, and `st_delegation.py`.
- Inline comments annotate maturity, for example "mostly done", "inprogress", "needs work", or "Not Done at all".

## Control Flow
There is no executable control flow beyond module import. The test framework can use `__all__` to know which modules to enumerate.

## State And Persistence Behavior
No runtime state is stored other than the module-level list. There is no persistence.

## Dependencies And Integration Points
The file is part of the `servertests` package and integrates with Python import semantics and the pynfs test harness. The names align with sibling `st_*.py` modules, including every test file in this work item.

## Risks And Edge Cases
- Entries include `.py` suffixes rather than bare module names, which is a convention the test runner must understand.
- Comments indicate some areas are incomplete; a runner that blindly treats all entries as equally mature may hit known gaps.
- Missing or renamed files would break discovery because this manifest is manually maintained.

## Test Signals
The file has no direct assertions. Its signal is discovery coverage: whether server test modules are visible to the test harness and remain synchronized with the package contents.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/environment.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/environment.py

## Purpose
`environment.py` defines the shared NFSv4 server test environment, common assertion helpers, attribute metadata, invalid input generators, and stateid mutation utilities. Test modules receive an `Environment` instance containing configured clients, paths, data samples, security choices, setup/cleanup methods, and helper functions for comparing protocol results.

## Important APIs, Types, And Functions
- `AttrInfo(name, access, sample)` describes an NFS attribute by name, bit number, bitmap mask, access flags, and sample value. Properties classify writable, readable, mandatory, readonly, and writeonly attributes.
- `Environment.attr_info` is a comprehensive table of NFSv4 attrs used by GETATTR/CREATE/SETATTR tests to derive mandatory, unsupported, writable, and sample values.
- `Environment.__init__(opts)` creates `c1` and `c2` `NFS4Client` instances, configures security, long names, sample file/link data, special stateids, and options.
- `_get_security(opts)` chooses auth flavor setup for `none`, `sys`, or `krb5*`.
- `init()` optionally creates the test tree, validates the base path, empties it, and sends a NULL call.
- `_maketree()` creates `/tree` objects for directory, socket, FIFO, symlink, block/char devices, and a regular file with known data.
- `finish()`, `startUp()`, `sleep()`, `serverhelper()`, `clean_sessions()`, and `clean_clients()` provide lifecycle and external server hooks.
- `check(res, stat=NFS4_OK, msg=None, warnlist=[])` is the central status assertion helper, raising `testmod.WarningException` or `FailureException`.
- `checkdict(expected, got, translate={}, failmsg='')` validates returned attribute dictionaries.
- `get_invalid_utf8strings()`, `get_invalid_clientid()`, `makeStaleId()`, `makeBadID()`, `makeBadIDganesha()`, and `compareTimes()` provide shared negative-test inputs.

## Control Flow
The test runner constructs `Environment(opts)`, which creates two clients using selected security credentials. Before test execution, `init()` may build or clean the configured root. `_maketree()` walks the configured path, creates missing path components, resets a `tree` directory, creates special objects, then opens/writes/closes the canonical test file. Each test's `startUp()` sends a NULL RPC to keep the connection warm. After all tests, `finish()` cleans the base path unless cleanup is disabled.

Assertions flow through `check`. It accepts one status or a list, returns silently on expected status, otherwise derives the failing operation name from the last response op or supplied message and raises a testmod exception. `warnlist` converts certain statuses to warnings. Many tests use `t.fail_support` or `t.pass_warn` after a successful `check` to mark unsupported optional server behavior.

`serverhelper` is an integration escape hatch for tests that require out-of-band server-side mutation, especially delegation recall scenarios. It either prompts for manual action or invokes a configured helper command with byte arguments.

## State And Persistence Behavior
The environment stores clients, user/group IDs, option values, sample payloads, and generated stateid constants in memory. It mutates server-side test directories through NFS operations and optionally through an external server helper. It does not persist local metadata except whatever the server stores in the export. Cleanup behavior is option-controlled.

## Dependencies And Integration Points
The module depends on `testmod`, `nfs4lib.NFS4Client`, generated NFS constants/types, `rpc.rpc`, `nfs_ops`, and OS/time helpers. All sibling `st_*.py` modules import `check` and many import mutation helpers. `Environment.attr_info` drives GETATTR/CREATE/ACL tests, while `serverhelper` connects delegation tests to external filesystem mutation tools.

## Risks And Edge Cases
- The header says Python 3.2, while some surrounding pynfs code is Python 2-era; byte/string handling is intentionally mixed and must be preserved.
- `check` treats a string second positional argument as a programmer error by raising a string, which is not valid Python 3 behavior.
- `warnlist` has a mutable default list, though it is not mutated in this function.
- `get_invalid_clientid()` returns `0`, which is only a guessed invalid client ID and may collide with a server's behavior.
- `makeStaleId` and `makeBadID*` intentionally inspect opaque stateid layout and are server-specific; tests using them carry flags such as `staleid` or `ganesha`.
- `_maketree()` may warn rather than fail when special object creation is unsupported, so later tests depend on dependency flags and environment options.

## Test Signals
Every server test module in this group relies on `Environment` and `check`. Meaningful signals include expected NFS status codes, raised warning/failure exceptions, created test tree shape, lease-time sleeps, server helper side effects, and generated invalid UTF-8/stateid/clientid inputs.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/environment.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_access.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_access.py

## Purpose
`st_access.py` tests the NFSv4 `ACCESS` operation across regular files, directories, symlinks, FIFOs, sockets, character devices, and block devices. It verifies readable access, all valid access-bit combinations, invalid access masks, and no-current-filehandle handling.

## Important APIs, Types, And Functions
- `_valid_access_ops` contains every subset of the six defined access bits.
- `_invalid_access_ops` contains masks with bits beyond the legal `0x3f` range.
- `_try_all_combos(t, c, path, forbid=0)` sends ACCESS for all valid masks and verifies returned `supported` and `access` are subsets of the requested mask and exclude type-meaningless bits.
- `_try_read(c, path)` checks that `ACCESS4_READ` succeeds.
- `_try_invalid(t, c, path)` accepts either `NFS4ERR_INVAL` or an OK response whose returned bitmasks do not expose invalid bits.
- `testRead*`, `testAll*`, `testNoFh`, and `testInvalids*` are per-object-type test entry points with FLAGS/DEPEND/CODE metadata.

## Control Flow
Each test builds a compound from `c.use_obj(path)` plus `op.access(mask)`, runs it through `NFS4Client.compound`, and calls `check`. Valid-combination tests inspect the last response's `supported` and `access` fields. Invalid tests loop over invalid masks and either require `NFS4ERR_INVAL` or validate that an OK server did not echo illegal bits.

## State And Persistence Behavior
The module does not create persistent state. It uses the prebuilt environment test tree and reads protocol access masks from server responses.

## Dependencies And Integration Points
It imports NFSv4 constants, `check`, and `nfs_ops.NFS4ops`. It depends on environment paths such as `opts.usefile`, `opts.usedir`, `opts.uselink`, and special object paths created by `Environment._maketree`.

## Risks And Edge Cases
- The `forbid` masks encode test expectations about meaningful bits per type; server implementations with different but spec-legal support semantics may get warnings/failures.
- `_try_invalid` allows OK for invalid input if returned masks are sanitized, reflecting interoperability flexibility.
- The tests assume the special object paths exist; missing device/socket support in the test export can invalidate dependent cases.

## Test Signals
Primary signals are ACCESS status, subset relations between requested/supported/access masks, rejection or sanitization of invalid bits, and `NFS4ERR_NOFILEHANDLE` when ACCESS is sent without a current filehandle.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_access.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_acl.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_acl.py

## Purpose
`st_acl.py` tests whether a server advertises, accepts, stores, and returns the `FATTR4_ACL` attribute. It covers support discovery, a simple ACL, and a larger ACL payload.

## Important APIs, Types, And Functions
- `testACLsupport(t, env)` calls `supportedAttrs` on the configured file and fails support if `FATTR4_ACL` is not advertised.
- `testACL(t, env)` creates a confirmed file, sets a one-entry ACL using `SETATTR`, then fetches `FATTR4_ACL`.
- `testLargeACL(t, env)` sets a twenty-entry ACL intended to produce a larger reply.
- The tests use `nfsace4` entries and `list2bitmap` for support masks.

## Control Flow
Tests initialize the connection, create a file where needed, build `PUTFH` plus `SETATTR` or `GETATTR` compounds, and assert OK with `check`. The support test gates later ACL cases through dependency metadata.

## State And Persistence Behavior
The module creates temporary files in the server export and mutates their ACL attributes. State persistence is only whatever the server stores between SETATTR and GETATTR in the same test.

## Dependencies And Integration Points
It imports NFSv4 constants/types, `check`, and `nfs4lib.list2bitmap`. It relies on `NFS4Client.create_confirm`, `setattr`, `getattr`, and the server's ACL implementation, which in the local Python server maps ACLs through `nfs4acl`.

## Risks And Edge Cases
- Comments note owner names are simple byte/integer strings and may not work under Kerberos name expectations.
- `testACL` checks successful GETATTR but does not compare the returned ACL to the set value.
- Large ACL behavior may expose max response or XDR packing issues, but the test currently only checks operation success.

## Test Signals
Signals are support-mask presence for `FATTR4_ACL`, successful `SETATTR(FATTR4_ACL)`, and successful `GETATTR(FATTR4_ACL)` after simple and larger ACL writes.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_acl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_close.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_close.py

## Purpose
`st_close.py` tests NFSv4 `CLOSE` behavior for normal created/opened files, sequence ID validation, bad/old/stale stateids, no-current-filehandle errors, lease expiry, lock release, and replay handling.

## Important APIs, Types, And Functions
- `testCloseCreate` and `testCloseOpen` validate ordinary close paths.
- `testBadSeqid`, `testBadStateid`, `testOldStateid`, `testStaleStateid`, and `testNoCfh` cover negative protocol cases.
- `testTimedoutClose1` and `testTimedoutClose2` sleep past lease time, force conflicting opens, and expect `NFS4ERR_EXPIRED`.
- `testReplaySeqid1`, `testNextSeqid`, and `testReplaySeqid2` exercise replay and next-seqid behavior, including multiple opens under the same owner.
- The module uses `makeStaleId` from `environment`.

## Control Flow
Tests initialize a client, create or open files with confirmed stateids, then call `close_file` with normal or manipulated seqid/stateid/current-fh arguments. Timeout tests sleep for twice the lease, use `env.c2` to force state cleanup through a conflicting write open, and then attempt CLOSE with the old state. Replay tests capture the sequence ID before CLOSE and repeat the request.

## State And Persistence Behavior
The module relies heavily on server open-owner state, lease timers, stateid sequence numbers, and replay caches. It creates temporary files in the test export and expects lock state to be released when close succeeds or state expires.

## Dependencies And Integration Points
It imports constants, `check`, and `makeStaleId`. It uses `NFS4Client` helpers for `init_connection`, `create_confirm`, `open_confirm`, `close_file`, `lock_file`, `get_seqid`, and lease-time queries.

## Risks And Edge Cases
- Timeout tests use real sleeps based on server-reported lease time, so they are slow and timing-sensitive.
- `testNextSeqid` intentionally does not assert a specific error after a replay with next seqid, only that the server does not crash.
- Stale stateid behavior depends on `makeStaleId`'s server-specific opaque stateid assumptions.

## Test Signals
Signals include `NFS4_OK`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_EXPIRED`, successful replayed CLOSE, and lock-release behavior after close.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_close.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_commit.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_commit.py

## Purpose
`st_commit.py` tests the NFSv4 `COMMIT` operation on regular files and invalid current filehandle/object cases. It focuses on offset/count boundary behavior, non-regular object errors, no filehandle behavior, and overflow validation.

## Important APIs, Types, And Functions
- `_commit(t, c, offset=0, count=0, statlist=[NFS4_OK])` creates and confirms a file, writes `_text` with `UNSTABLE4`, then commits a specified range and checks allowed statuses.
- `testCommitOffset0`, `testCommitOffset1`, `testCommitOffsetMax1`, `testCommitOffsetMax2`, `testCommitCount1`, and `testCommitCountMax` exercise range boundaries.
- `testLink`, `testBlock`, `testChar`, `testDir`, `testFifo`, and `testSocket` commit against non-regular objects and expect type-specific errors.
- `testNoFh` sends COMMIT without a current filehandle.
- `testCommitOverflow` covers offset-plus-count overflow.

## Control Flow
Most tests call `_commit`, which sets up file state and delegates range-specific assertions. Non-regular tests use environment object paths and client commit helpers. The helper checks write success before issuing COMMIT so failures are isolated to COMMIT semantics.

## State And Persistence Behavior
The tests create temporary files and write unstable data before COMMIT. No local persistent state is maintained. For RAM-backed test servers, COMMIT may be a verifier-only no-op, but the protocol result remains observable.

## Dependencies And Integration Points
It imports NFS constants and `check`. It depends on `NFS4Client` methods `create_confirm`, `write_file`, `commit_file`, and environment paths for file types.

## Risks And Edge Cases
- The helper default `statlist=[NFS4_OK]` is a mutable default but not mutated.
- Maximum offset/count tests allow either OK or `NFS4ERR_INVAL`, acknowledging server variability.
- The local Python server treats commits as FILE_SYNC and does not implement durable storage, so these tests only validate protocol handling, not actual disk flushes.

## Test Signals
Signals are successful COMMIT on regular files, acceptable handling of maximum ranges, `NFS4ERR_ISDIR` or `NFS4ERR_INVAL` for non-regular objects, `NFS4ERR_NOFILEHANDLE` without cfh, and overflow rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_commit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_compound.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_compound.py

## Purpose
`st_compound.py` tests NFSv4 COMPOUND request-level behavior: zero operations, valid and invalid tags, minor-version rejection, undefined opcodes, malformed op packing, and long compounds.

## Important APIs, Types, And Functions
- `testZeroOps(t, env)` sends an empty compound and expects OK.
- `testGoodTag(t, env)` verifies a valid UTF-8 tag is echoed in the response.
- `testBadTags(t, env)` iterates invalid UTF-8 byte strings and expects `NFS4ERR_INVAL`.
- `testInvalidMinor(t, env)` sends minor version 50 and expects `NFS4ERR_MINOR_VERS_MISMATCH`.
- `testUndefined(t, env)` builds an undefined op (`argop=100`) and expects `NFS4ERR_OP_ILLEGAL`, then monkey-patches a packer to emit an invalid opcode and expects an RPC/XDR failure.
- `testLongCompound(t, env)` sends a repeated `PUTROOTFH` sequence and accepts OK or `NFS4ERR_RESOURCE`.

## Control Flow
The tests call `c.compound` with explicit tags/minor versions or raw operation lists. `testUndefined` uses `nfs_argop4` and a custom `NFS4Packer` subclass to produce a malformed operation that cannot be normally packed. It catches `RPCError` for the malformed case as the expected transport-level failure.

## State And Persistence Behavior
The tests do not create persistent state. They exercise COMPOUND parser/dispatcher behavior and current filehandle reset with repeated PUTROOTFH operations.

## Dependencies And Integration Points
Imports include NFS constants/types/packer, `check`, invalid UTF-8 generator, `RPCError`, and `nfs_ops`. It directly exercises server request unpacking and operation dispatch in `NFS4Server.O_Compound`.

## Risks And Edge Cases
- Malformed-op expectations may vary by RPC stack; the test expects an RPC-level exception rather than a normal NFS status.
- Long-compound length is hard-coded at 500 operations and accepts resource exhaustion as compliant.
- Invalid tag behavior depends on byte/string handling in the packer and server UTF-8 validation.

## Test Signals
Signals are COMPOUND response status and tag echo, minor-version mismatch, illegal op status for undefined operations, RPC failure on impossible packed opcode, and no crash/resource behavior for long operation arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_compound.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_create.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_create.py

## Purpose
`st_create.py` tests the NFSv4 `CREATE` operation for directory, symlink, block/char device, socket, FIFO, invalid parent types, missing filehandle, invalid names, regular-file rejection, read-only/unsupported attributes, and naming policy edge cases.

## Important APIs, Types, And Functions
- `getDefaultAttr(c)` returns default create attributes, currently mode `0o755`.
- `_test_create(t, env, type, name, **keywords)` creates an object of the requested type under the home directory, handles optional support failures, checks OK, then retries and expects `NFS4ERR_EXIST`.
- `_test_notdir(t, env, devpath)` verifies creating under a non-directory returns `NFS4ERR_NOTDIR`.
- `testDir`, `testLink`, `testBlock`, `testChar`, `testSocket`, and `testFIFO` cover supported object types.
- `testDirOff*`, `testNoFh`, `testZeroLength`, `testZeroLengthForLNK`, `testRegularFile`, `testInvalidAttrmask`, `testUnsupportedAttributes`, `testDots`, `testSlash`, and `testLongName` cover negative and edge behavior.

## Control Flow
Most type tests delegate to `_test_create`, which builds a `createtype4`, issues a `go_home()` compound plus `CREATE`, and repeats the same compound for existence validation. Negative tests use `c.create_obj` on composed paths or raw compounds without current filehandle. Unsupported-attribute tests compute unsupported writable attrs from `env.attr_info` and the server's `supportedAttrs`.

## State And Persistence Behavior
Tests create objects under the test export and rely on repeated CREATE observing existing names. They mutate directory entries and may leave objects for environment cleanup. No local persistent state is maintained.

## Dependencies And Integration Points
The module imports NFS constants, `createtype4`, `specdata4`, `check`, and `nfs_ops`. It depends on environment home directory paths, long name bytes, attribute metadata, and client helpers.

## Risks And Edge Cases
- `_test_create` passes `t.word()` as the created name instead of the `name` label, so repeated calls depend on `t.word()` stability within a test.
- Some tests accept multiple statuses or warn for optional behavior, such as allowing `"."`/`".."`
  or slash-containing names.
- `testZeroLengthForLNK` has a message mentioning zero-length name while the code uses zero-length symlink data and generated object name; expected statuses include `NFS4ERR_NOENT`.
- The nested `testNamingPolicy` is indented under a non-test block and likely not discovered.

## Test Signals
Signals include OK object creation, `NFS4ERR_EXIST` on duplicate names, `NFS4ERR_NOTDIR`/`NFS4ERR_SYMLINK` under invalid parents, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_BADTYPE`, `NFS4ERR_ATTRNOTSUPP`, `NFS4ERR_BADNAME`/`BADCHAR`, and `NFS4ERR_NAMETOOLONG`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_create.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_delegation.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_delegation.py

## Purpose
`st_delegation.py` tests NFSv4 read and write delegation behavior, callback recall handling, callback-server errors, delegation return, lease renewal under callback path failure, share interactions, callback-server changes, CLAIM_DELEGATE_CUR, recall triggers from namespace operations, server-side external mutations, and self-conflict cases.

## Important APIs, Types, And Functions
- `_handle_error` retries failed `DELEGRETURN` callback handling asynchronously.
- `_recall(c, thisop, cbid)` is a callback handler that sends `PUTFH` plus `DELEGRETURN` for `CB_RECALL`.
- `_cause_recall(t, env)` uses `env.c2` to open a conflicting writer, retrying on `NFS4ERR_DELAY`.
- `_verify_cb_occurred(t, c, count)` checks callback recall count and validates stored recall response.
- `_get_deleg(...)` creates or opens a file with callback recall configured and returns delegation info, filehandle, and stateid, warning if the expected delegation type is not granted.
- `_read_deleg` and `_write_deleg` parameterize read/write delegation recall scenarios.
- `testReadDeleg*`, `testWriteDeleg*`, `testCloseDeleg`, `testManyReaddeleg`, `testRenew`, `testIgnoreDeleg`, `testDelegShare`, `testChangeDeleg`, `testClaimCur`, `testRemove`, `testLink`, `testRename`, `testRenameOver`, `testServer*`, and self-conflict tests cover the scenario matrix.

## Control Flow
Tests initialize a client with a callback server (`init_connection(..., cb_ident=0)`), request a delegation through create/open helpers with `set_recall=True`, then create conflicts using a second client, namespace operations, or `env.serverhelper`. Callback handling is synchronized by a module-level `threading.Lock` because the callback thread and tester thread share the client's packer/unpacker. Many loops accept `NFS4ERR_DELAY`, sleep, and retry until the conflicting operation completes or an expected denial occurs.

`testChangeDeleg` creates a new `CBServer`, swaps the callback endpoint with SETCLIENTID/CONFIRM, and then verifies recalls arrive on the new server. Server-side tests call `serverhelper` to run operations such as unlink, rename, link, and chmod outside the NFS client. CLAIM_DELEGATE_CUR tests use a recalled delegation stateid to perform delegated opens before returning the delegation.

## State And Persistence Behavior
The module creates files and open/delegation state on the server, manipulates callback server state (`opcounts`, stored recall results, `c.cbid`), and may invoke external server-side mutations. It relies on lease time, callback paths, delegation stateids, and open/share state persisting across multiple clients and threads during each test.

## Dependencies And Integration Points
It imports NFS constants/types, `check`, `os`, `threading`, `time`, `nfs_ops`, and dynamically imports `nfs4lib.CBServer` in one test. It depends on `NFS4Client` callback-server support, `env.c1`/`env.c2`, `env.serverhelper`, and server delegation support.

## Risks And Edge Cases
- The local `nfs4server.py` returns no delegations and `DELEGRETURN`/`DELEGPURGE` are not supported, so these tests primarily apply to real NFS servers.
- `_handle_error.run` references `ops` instead of `self.ops`, a likely bug in the retry path.
- Threading is timing-sensitive; sleeps are used to let callback paths settle.
- Many tests use `t.word()` repeatedly to build paths; correctness depends on stable per-test word behavior.
- Callback and security behavior can vary significantly across servers, producing warnings for unsupported delegation instead of hard failures.

## Test Signals
Signals include receiving `OPEN_DELEGATE_READ` or `OPEN_DELEGATE_WRITE`, `OP_CB_RECALL` count increments, successful `DELEGRETURN`, expected callback error handling, `NFS4ERR_DELAY` retry behavior, `NFS4ERR_SHARE_DENIED` for deny-write cases, callback path down behavior on RENEW, and no unnecessary recall for same-client/self-conflict scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_delegation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_fslocations.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_fslocations.py

## Purpose
`st_fslocations.py` tests referral and `FATTR4_FS_LOCATIONS` behavior around `NFS4ERR_MOVED`. It verifies how GETFH, GETATTR, and READDIR behave for a path supplied by `--usespecial`, including restricted attributes and `FATTR4_RDATTR_ERROR` handling.

## Important APIs, Types, And Functions
- `testReference`, `testReference2`, and `testReference3` inspect referral behavior and `fs_locations` fetches.
- `testAttr1a`/`1b` expect MOVED when GETATTR/READDIR requests normal attrs without FS_LOCATIONS or RDATTR_ERROR.
- `testAttr2a`/`2b` add `RDATTR_ERROR`; READDIR should report MOVED per-entry while returning what it can.
- `testAttr3a`/`3b` request only restricted attrs and expect success.
- `testAttr4a`/`4b` request FS_LOCATIONS plus RDATTR_ERROR and validate returned attr counts.
- `testAttr5a`/`5b` request FS_LOCATIONS without RDATTR_ERROR and validate partial attrs.

## Control Flow
Tests build paths from `env.opts.usespecial`. GETFH/LOOKUP reference tests walk from root with `PUTROOTFH`, `GETFH`, `LOOKUP`, and `GETFH` until a MOVED status is expected. Attribute tests use `c.use_obj`, `c.getattr`, `op.readdir`, `c.do_getattrdict`, or `c.do_readdir` and inspect returned per-entry attr dictionaries.

## State And Persistence Behavior
No test-created persistent state is required. The tests depend on an existing special referral node in the server export configured outside the module.

## Dependencies And Integration Points
Imports include NFS constants, `nfs4lib.list2bitmap`, `check`, and `nfs_ops`. The module integrates with test runner options via `env.opts.usespecial` and with client helpers for GETATTR/READDIR decoding.

## Risks And Edge Cases
- Tests require `--usespecial` to point at a valid referral; without that environment they are not meaningful.
- Several attr-count expectations are hard-coded and can be sensitive to server-specific allowed attrs around referrals.
- Print messages indicate exploratory inspection rather than strict comparison of `fs_locations` contents.

## Test Signals
Signals include `NFS4ERR_MOVED`, successful restricted GETATTR/READDIR, per-entry `FATTR4_RDATTR_ERROR == NFS4ERR_MOVED`, and expected attr dictionary sizes when FS_LOCATIONS is present or absent.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_fslocations.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_getattr.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_getattr.py

## Purpose
`st_getattr.py` tests NFSv4 `GETATTR` across file types and attributes. It verifies mandatory attribute support, no-current-filehandle handling, write-only attribute rejection, unknown and empty attr requests, supported-attrs correctness, large legal attr requests, FS_LOCATIONS support, many repeated GETATTR operations, and selected optional attributes.

## Important APIs, Types, And Functions
- `_try_mandatory(t, env, path)` requests all mandatory attrs except `rdattr_error` and fails if any are missing.
- `_try_write_only(env, path)` requests size plus each write-only attr and expects `NFS4ERR_INVAL`.
- `_try_unknown(t, c, path)` requests attr bit 1000 and expects OK with no attrs.
- `_try_empty(t, c, path)` requests an empty attr list and expects OK with empty attrs.
- `_try_supported(t, env, path)` validates `FATTR4_SUPPORTED_ATTRS` contains all mandatory attrs and no bits outside `env.attr_info`.
- `_try_long(env, path)` requests all non-write-only legal attrs.
- `testMand*`, `testWriteOnly*`, `testUnknownAttr*`, `testEmpty*`, `testSupported*`, `testLong*`, and optional attr tests form the entrypoint matrix.

## Control Flow
Each type matrix test delegates to a helper with an environment path. Helpers build `use_obj(path)` compounds plus `GETATTR` and inspect response `obj_attributes`. Optional attr tests request one attr and accept OK or `NFS4ERR_ATTRNOTSUPP`, converting unsupported attrs to support failures. `testLotsofGetattrsFile` appends ninety GETATTR ops in one compound and accepts OK or `NFS4ERR_RESOURCE`.

## State And Persistence Behavior
The module does not mutate server state except for possible access-time effects on the server. It reads attributes from the existing test tree.

## Dependencies And Integration Points
It imports NFS constants, `check`, attribute-name helpers from `nfs4lib`, and `nfs_ops`. It relies on `Environment.attr_info`, environment object paths, and `NFS4Client.supportedAttrs`/compound helpers.

## Risks And Edge Cases
- Server interpretation of write-only attrs may return `NFS4ERR_ATTRNOTSUPP` instead of `NFS4ERR_INVAL` in some optional tests; helper expectations are stricter for the matrix.
- `_try_supported` assumes `env.attr_info` fully describes protocol-supported attrs; newer/generated constants could make this check stale.
- Optional attr tests mostly check support presence, not returned value semantics.
- The mounted-on-fileid test is nested under a disabled method-like block and is not normal test discovery.

## Test Signals
Signals include mandatory attr presence, empty/unknown request behavior, write-only attr rejection, `FATTR4_SUPPORTED_ATTRS` bit correctness, compound resource handling, support or attr-not-supported status for optional attrs, and no-current-filehandle status.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_getattr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_getfh.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_getfh.py

## Purpose
`st_getfh.py` tests the NFSv4 `GETFH` operation for all standard test-tree object types and the no-current-filehandle error path.

## Important APIs, Types, And Functions
- `testFile`, `testDir`, `testLink`, `testSocket`, `testFifo`, `testBlock`, and `testChar` call `env.c1.do_getfh` on environment paths.
- `testNoFh(t, env)` sends raw `GETFH` without establishing current filehandle and expects `NFS4ERR_NOFILEHANDLE`.

## Control Flow
Object tests delegate entirely to the client helper, which performs the LOOKUP/use-object and GETFH sequence. The no-fh test constructs a compound with only `op.getfh()` and checks the status.

## State And Persistence Behavior
No persistent state is created. On the local Python server, GETFH also populates the server's in-memory filehandle cache, which may influence later PUTFH behavior outside this module.

## Dependencies And Integration Points
Imports include NFS constants, `check`, and `nfs_ops`. It depends on `Environment._maketree` object paths and `NFS4Client.do_getfh`.

## Risks And Edge Cases
- `testFifo` appears to call `do_getfh(env.opts.uselink)` rather than `env.opts.usefifo`, likely reducing FIFO coverage.
- The helper abstracts away response content, so these tests mainly validate status and decoding rather than uniqueness or volatility properties.

## Test Signals
Signals are successful GETFH on each object type and `NFS4ERR_NOFILEHANDLE` for a missing current filehandle.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_getfh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_gss.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_gss.py

## Purpose
`st_gss.py` tests RPCSEC_GSS error handling around NFSv4 compounds. It deliberately corrupts GSS sequence numbers, header fields, verifier checksums, data checksums, procedure numbers, service numbers, and high sequence numbers, then verifies RPC-level denial or accept errors.

## Important APIs, Types, And Functions
- `BadGssHeader(sec, bad_cred_funct)` wraps an existing security object, overrides credential creation, passes through most attributes, and leaves secure/unsecure data as identity for cases expected to fail before body protection.
- `_using_gss`, `_using_service`, and `_using_integrity` are dependency predicates for the test runner.
- `testBadGssSeqnum` decrements the outgoing GSS sequence and expects a timeout or dropped reply.
- `testInconsistentGssSeqnum` changes the body credential sequence after the header and expects `GARBAGE_ARGS`.
- `testBadVerfChecksum` corrupts verifier checksum input and expects `RPCSEC_GSS_CREDPROBLEM`.
- `testBadDataChecksum` corrupts integrity-protected data and expects `GARBAGE_ARGS`.
- `testBadVersion`, `testHighSeqNum`, `testBadProcedure`, and `testBadService` mutate credential header fields and expect appropriate auth errors.

## Control Flow
Tests first ensure a normal `PUTROOTFH` compound works where useful. They then monkey-patch methods or replace `c.security` with `BadGssHeader`, issue a simple compound, catch expected `timeout`, `OSError`, `RPCAcceptError`, or `RPCDeniedError`, and restore the original security object in `finally` blocks.

## State And Persistence Behavior
The module mutates only the client-side security object and sequence counters during a test and restores them afterward. Server state is not intentionally changed beyond simple `PUTROOTFH` compounds and RPC context behavior.

## Dependencies And Integration Points
Imports include NFS constants, `check`, socket timeout, `rpc.rpc`, `rpc.rpcsec.gss_const`, `rpc_gss_cred_t`, and `nfs_ops`. The tests depend on RPCSEC_GSS support in `rpc.supported`, the selected environment security flavor, and the security object's packer/checksum APIs.

## Risks And Edge Cases
- GSS tests are transport/security-stack dependent and may produce timeouts, OS errors, accept errors, or denied errors depending on implementation.
- Monkey-patching security methods must exactly match the expected method signatures; `testBadDataChecksum` assumes the integrity `secure_data` signature takes `(data, seqnum)`.
- Some failure messages contain typos but do not affect behavior.

## Test Signals
Signals are dropped replies for replayed/old GSS sequence numbers, `rpc.GARBAGE_ARGS` for inconsistent body/header or bad data checksum, `rpc.AUTH_ERROR` with `RPCSEC_GSS_CREDPROBLEM`, `RPCSEC_GSS_CTXPROBLEM`, or `AUTH_BADCRED` for malformed credentials.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_gss.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_link.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_link.py

## Purpose
`st_link.py` tests NFSv4 hard link support and `LINK` operation semantics. It validates advertised link support, linking each object type, source/current filehandle errors, non-directory target directories, duplicate names, invalid names, long names, invalid UTF-8, and dot-name policy.

## Important APIs, Types, And Functions
- `_basictest(t, c, path, error=NFS4_OK)` links `path` into the home directory, checks the expected status, and verifies `FATTR4_NUMLINKS` increases by one when available and successful.
- `testSupported` checks `FATTR4_LINK_SUPPORT` on the home directory.
- `testFile`, `testDir`, `testFifo`, `testLink`, `testBlock`, `testChar`, and `testSocket` cover source object types.
- `testNoSfh`, `testNoCfh`, `testCfh*`, `testExists`, `testZeroLenName`, `testLongName`, `testInvalidUtf8`, and `testDots` cover negative cases.

## Control Flow
The basic flow reads `FATTR4_NUMLINKS`, calls `c.link(source_path, target_path)`, checks the expected status, then re-reads link count for successful cases. No-filehandle tests build raw compounds to omit saved or current filehandles. Invalid UTF-8 tests create a containing directory and iterate shared invalid byte strings from `environment`.

## State And Persistence Behavior
Tests create hard links and directories in the test export, changing link counts and directory contents. Cleanup is delegated to the environment.

## Dependencies And Integration Points
Imports include NFS constants, `check`, invalid UTF-8 generator, and `nfs_ops`. It relies on environment paths and `NFS4Client.link`, `do_getattrdict`, and `create_obj`.

## Risks And Edge Cases
- Some filesystems do not support hard links for special object types; tests use dependency/support metadata to account for this.
- Dot-name behavior accepts OK or BADNAME and can issue warnings, reflecting server policy variance.
- The nested `testNamingPolicy` is not a normal top-level test.

## Test Signals
Signals include `FATTR4_LINK_SUPPORT`, successful link creation and numlinks increment, `NFS4ERR_ISDIR` for directory source, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_NOTDIR`/`SYMLINK` for invalid current filehandle, `NFS4ERR_EXIST`, `NFS4ERR_INVAL`, `NFS4ERR_NAMETOOLONG`, and invalid UTF-8 rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_link.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lock.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_lock.py

## Purpose
`st_lock.py` is the main NFSv4 `LOCK` test module. It exercises basic locking, close interactions, existing-file opens, range size, overlapping lock merge/split, lock upgrade/downgrade, open-mode checks, invalid ranges, missing filehandles, sequence IDs, old/stale/bad stateids, client ID freshness, lease timeout cleanup, inter-owner and inter-client conflicts, read-lock coexistence, blocking-lock fairness/polling, lockowner reuse ideas, and open/lock/open-downgrade sequences.

## Important APIs, Types, And Functions
- `testFile`, `testClose`, `testExistingFile`, `test32bitRange`, `testOverlap`, `testDowngrade`, `testUpgrade`, `testMode`, `testZeroLen`, and `testLenTooLong` cover core lock semantics.
- `testNoFh`, `testBadLockSeqid`, `testBadOpenSeqid`, `testNonzeroLockSeqid`, `testOldLockStateid`, `testOldOpenStateid`, `testOldOpenStateid2`, `testStaleClientid`, `testBadStateid`, `testBadStateidganesha`, `testStaleLockStateid`, and `testStaleOpenStateid` cover protocol validation.
- `testTimedoutGrabLock`, `testGrabLock1`, `testGrabLock2`, `testReadLocks1`, and `testReadLocks2` cover lease expiry and conflict behavior.
- `testFairness`, `testBlockPoll`, `testBlockTimeout`, `testBlockingQueue`, and `testLongPoll` probe blocking lock queue/fairness semantics.
- `open_sequence` encapsulates open/downgrade/close/lock/unlock state for `testOpenUpgradeLock`.
- `testOpenDowngradeLock` and `testOpenUpgradeLock` combine open share transitions with lock operations.

## Control Flow
Most tests initialize a connection, create or open a confirmed file, acquire a lock with `lock_file`, then issue `lock_test`, `relock_file`, `unlock_file`, `downgrade_file`, or second-client/second-owner operations. Sequence and stateid tests deliberately pass bad sequence numbers, old stateids, all-zero stateids, Ganesha-specific bad IDs, or stale IDs. Timeout and blocking tests sleep for fractions or multiples of the lease time and poll or renew to shape server state.

Blocking-lock tests use write-wait lock types (`WRITEW_LT`) and expect denied responses while another owner holds a conflicting lock, then check fairness by attempting to let later owners steal the lock. The module also contains an indented block of older method-style tests under `testLockowner2`; those are not normal top-level tests.

## State And Persistence Behavior
This module creates many server-side open, lock, lockowner, and share states. It relies on stateids and lock state persisting across operations, owners, clients, sequence IDs, and lease intervals. It also depends on server cleanup when clients expire and on close releasing locks or returning `NFS4ERR_LOCKS_HELD`.

## Dependencies And Integration Points
Imports include NFS constants, `stateid4`, `check`, `get_invalid_clientid`, `makeStaleId`, `makeBadIDganesha`, `time`, and `nfs_ops`. It depends on extensive `NFS4Client` helper methods and environment lease timing.

## Risks And Edge Cases
- Real-time sleeps make lease and fairness tests slow and sensitive to server timing.
- Some checks accept alternate statuses or convert behavior to support warnings, especially 64-bit ranges, lock consolidation, atomic upgrades/downgrades, and closing locked files.
- Stateid mutation helpers are server-specific.
- Several owner strings are plain strings while much of the framework uses bytes; compatibility depends on client helper normalization.
- The older nested lockowner tests are likely not discovered and include outdated APIs.

## Test Signals
Signals include OK lock acquisition, `NFS4ERR_DENIED` for conflicts, denied lock owner details from LOCKT, `NFS4ERR_LOCK_RANGE`, `NFS4ERR_LOCK_NOTSUPP`, `NFS4ERR_OPENMODE`, `NFS4ERR_INVAL`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, lease-expiry lock cleanup, and fairness warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lock.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lockt.py -->
# sources/test-tools/pynfs/nfs4.0/servertests/st_lockt.py

## Purpose
`st_lockt.py` tests NFSv4 `LOCKT`, the non-mutating byte-range lock test operation. It covers unlocked files, non-file object types, partial locked ranges, 64-bit ranges, overlapping lock reports, invalid zero/overflow lengths, missing filehandle, and stale client IDs.

## Important APIs, Types, And Functions
- `testUnlockedFile` verifies LOCKT succeeds on an unlocked regular file.
- `testDir`, `testFifo`, `testLink`, `testBlock`, `testChar`, and `testSocket` validate errors for non-regular object types.
- `testPartialLockedFile1` and `testPartialLockedFile2` create locks and test overlapping/non-overlapping ranges.
- `test32bitRange`, `testOverlap`, `testZeroLen`, `testLenTooLong`, `testNoFh`, and `testStaleClientid` cover boundary and protocol errors.

## Control Flow
Tests initialize a client, create/confirm files where needed, and call `c.lock_test` directly or after creating locks via `c.lock_file`. Non-file tests call `lock_test` on environment paths. Range tests inspect status and, for overlap, the denied range reported in the response.

## State And Persistence Behavior
LOCKT itself should not mutate lock state, but many tests create locks first to observe conflict reporting. The module uses existing environment objects and temporary files.

## Dependencies And Integration Points
It imports NFS constants, `check`, and `get_invalid_clientid`. It relies on `NFS4Client.lock_test`, `lock_file`, `create_confirm`, environment paths, and client ID state.

## Risks And Edge Cases
- Expected status for symlink/non-file cases allows some variance, such as `NFS4ERR_SYMLINK`.
- 64-bit range support can return `NFS4ERR_BAD_RANGE` and be treated as unsupported.
- Stale client ID uses `get_invalid_clientid()` returning zero, which is a heuristic.

## Test Signals
Signals include OK LOCKT for unlocked/non-conflicting ranges, `NFS4ERR_DENIED` with correct denied range/type/owner for conflicts, `NFS4ERR_ISDIR` or `NFS4ERR_INVAL` for non-files, `NFS4ERR_INVAL` for zero length or overflow, `NFS4ERR_NOFILEHANDLE`, and `NFS4ERR_STALE_CLIENTID`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/servertests/st_lockt.py -->
