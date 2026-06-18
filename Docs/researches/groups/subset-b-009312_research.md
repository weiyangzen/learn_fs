# subset-b-009312 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/client41tests/environment.py -->
# sources/test-tools/pynfs/nfs4.1/client41tests/environment.py

## Purpose
`client41tests/environment.py` is the shared NFSv4.1 client-test environment module. It supplies per-run configuration derived from test options, a catalog of attribute metadata, status checking helpers, invalid protocol-value generators, and convenience operations for cleanup, READDIR loops, object creation, OPEN/GETFH, and CLOSE. Test modules import this file to avoid rebuilding low-level NFSv4.1 COMPOUND sequences by hand.

## Important APIs, Types, And Functions
- `AttrInfo` records attribute name, bit number, bit mask, access string, and a sample value; its `readable`, `writable`, `mandatory`, `readonly`, and `writeonly` properties are used by attribute tests.
- `Environment(testmod.Environment)` stores `opts`, derived `root`/`home` paths, a unique timestamp, verifier state, sample file/link data, and a thread lock around verifier generation.
- `Environment.attr_info` is a source-level table of mandatory/read/write attributes and representative encoded values such as `fsid4`, `fs_locations4`, `nfsace4`, `specdata4`, `nfstime4`, and `settime4`.
- `reboot_server()`, `set_error()`, `set_error_wait_lease()`, `set_two_values()`, and `clear_two_values()` manipulate the server's exported `/config` pseudo-files to force operation errors, paired values, or reboot behavior.
- `new_verifier()` returns monotonically increasing eight-byte verifier data using wall-clock time guarded by `_lock`.
- `testname(t)` builds run-unique object names from a test code and the environment timestamp.
- `fail()`, `check()`, `checklist()`, and `checkdict()` convert protocol mismatches into `testmod.FailureException` or `WarningException`.
- `get_invalid_utf8strings()`, `get_invalid_clientid()`, `makeStaleId()`, and `makeBadID()` produce negative-test protocol values.
- `compareTimes()` compares `nfstime4` seconds/nanoseconds tuples.
- `clean_dir()`, `do_readdir()`, `use_obj()`, `create_obj()`, `create_file()`, `create_confirm()`, and `close_file()` build and execute common test compounds.

## Control Flow
The test runner constructs `Environment(opts)`, which derives a root path from `opts.path`, sets `opts.home`, and records the timestamp used for unique names and verifiers. Most lifecycle hooks (`init`, `finish`, `startUp`) are placeholders, so test-specific setup is driven by helpers called directly from client41 test modules.

Status validation flows through `check` or `checklist`: a result status is compared against one expected code or a list, the failed operation name is inferred from the last `resarray` entry when no explicit message is provided, and a test exception is raised on mismatch. Directory cleanup loops through `do_readdir`, makes each child removable by setting mode to `0o755`, tries `REMOVE`, and recursively cleans entries that return `NFS4ERR_NOTEMPTY`.

Object and file helpers compose NFSv4.1 operations using `nfs_ops.NFS4ops`. `use_obj` turns `None`, an existing filehandle, or path components into the required `PUTFH`/`PUTROOTFH`/`LOOKUP` chain. `create_file` issues `OPEN` with `OPEN4_CREATE`, adds `OPEN4_SHARE_ACCESS_WANT_NO_DELEG` unless a delegation is explicitly requested, and appends `GETFH`. `create_confirm` checks the result and returns a filehandle plus a stateid based on the `OPEN` result.

## State And Persistence Behavior
The module itself persists nothing outside process memory except when tests intentionally write server configuration pseudo-files. `Environment` stores per-run timestamp, home/root names, data samples, and verifier monotonic state. `new_verifier` is process-local and only guarantees uniqueness inside the active test process. Config writes under `/config` are interpreted by the pynfs server and can persist in that server's exported in-memory or disk-backed filesystem until reset.

## Dependencies And Integration Points
The file depends on generated NFSv4 constants and types, `nfs_ops.NFS4ops`, `nfs4client`, `nfs4lib`, `rpc.rpc`, `rpc.security.AuthSys/AuthGss`, `testmod`, and the server configuration filesystem implemented in `config.py`/`fs.py`. It integrates with `SessionRecord.compound`-style client sessions and with test modules that expect helper failures to be `testmod` exceptions.

## Risks And Edge Cases
- `check` raises a string if the caller passes a string as the expected status; that is invalid under Python 3 despite the file header claiming Python 3.2.
- `check` and `checklist` assume `nfsstat4` contains both expected and received status values.
- `do_readdir` raises `UnexpectedCompoundRes`, but this name is not imported in this file; callers may hit `NameError` if a server returns neither entries nor EOF.
- `makeStaleId` and `makeBadID` rely on CITI/Linux server-specific stateid byte layout and are deliberately marked for tests requiring those flags.
- Several default arguments are mutable dictionaries, though the functions mostly treat them as input templates.
- `set_error_wait_lease` reads a lease file and indexes `lease[1]`; malformed or short config-file content will fail before the intended wait.

## Test Signals
Strong signals are successful helper compounds, expected NFS status mismatches reported with operation names, recursive cleanup leaving empty directories, unique verifier generation, and config-driven error injection taking effect after lease waits. Negative tests should exercise invalid UTF-8 strings, stale/bad stateid helpers, wrong status paths through `check`/`checklist`, and multi-page READDIR loops.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/client41tests/environment.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/config.py -->
# sources/test-tools/pynfs/nfs4.1/config.py

## Purpose
`config.py` defines the server configuration model exposed by the NFSv4.1 test server, especially values surfaced through the pseudo-filesystem under `/config`. It provides typed `ConfigLine` entries, metaclass-generated config properties, server-wide values, per-client limits, per-operation error injection state, and action triggers such as reboot.

## Important APIs, Types, And Functions
- `ConfigAction` is raised by verifier functions when a config write should trigger behavior rather than simply store a value.
- `_action`, `_int`, `_bool`, `_statcode`, and `_opline` verify and coerce text written through config files.
- `_opline(value)` accepts `ERROR <nfsstat-or-name> <ceiling>` lines and stores them as `["ERROR", status_code, ceiling]`.
- `ConfigLine(name, value, comment, verifier=None)` stores one configurable value plus its parser and documentation string.
- `MetaConfig` deep-copies class `attrs` into each instance and replaces each `ConfigLine` with a Python property backed by `self.attrs[i].value`.
- `ServerConfig` contains server-wide settings such as `allow_null_data`, `tag_info`, `lease_time`, and `catch_ctrlc`, plus server owner, scope, and implementation identity data.
- `ServerPerClientConfig` holds session negotiation limits and behavior toggles such as request/response sizes, operation count, slot count, stateid handling, close-with-locks behavior, and debug state.
- `OpsConfigServer` builds one config line per `nfs_opnum4` operation, defaulting every operation to `ERROR 0 0`.
- `Actions` defines the `reboot` action config line.

## Control Flow
Class creation for config classes goes through `MetaConfig`, which consumes the declared `attrs` list, installs an `__init__` wrapper that deep-copies it, and creates properties with the same names as the config lines. Runtime reads and writes therefore look like normal attribute access while preserving comments and verifier behavior in `self.attrs`.

When a config pseudo-file is written and later closed by `ConfigObj` in `fs.py`, the raw non-comment line is assigned into `ConfigLine.value`. The property setter calls the verifier. Normal verifiers coerce to the stored type; `_action` raises `ConfigAction`; `_opline` parses operation fault-injection lines into structured lists. `ConfigObj.close` catches `ConfigAction` and dispatches actions such as server reboot.

## State And Persistence Behavior
The config objects are in-memory Python structures by default. Their values may be represented as file contents by `ConfigFS`, but the authoritative state is each `ConfigLine._value`. `MetaConfig` deep-copies class defaults per instance, preventing normal cross-client mutation for per-client configs. `ServerConfig.__init__` also creates process-specific owner data from `os.getpid()` and a fixed implementation timestamp.

## Dependencies And Integration Points
The module depends on generated NFSv4 constants/types, `nfs4lib.get_nfstime`, and `copy.deepcopy`. It is consumed by `fs.ConfigObj`/`ConfigFS`, by server code that reads limits and action flags, and by client test helpers that write `/config/ops/<operation>` or `/config/actions/reboot`.

## Risks And Edge Cases
- `_statcode` references `xdr.nfs4_const` even though the module imported `xdrdef.nfs4_const`; this typo can break symbolic status parsing.
- The metaclass declaration uses Python 2 `__metaclass__` syntax, which does not apply to classes under Python 3 without adaptation.
- `_opline` emits debug prints and has a print path using `len` rather than `len(l)`, reducing clarity during failures.
- `_opline` only supports `ERROR`; additional message types require verifier and server handling changes.
- `_valid_server_ops` and `_invalid_ops` are declared but not enforced in this file.
- Generated `OpsConfigServer.attrs` includes invalid operations despite comments saying some should not be set.

## Test Signals
Tests should verify text-to-type coercion for booleans/integers, operation error injection by numeric and symbolic status code, reboot action propagation through `ConfigObj.close`, independent per-client defaults, and session negotiation values reflected in `CREATE_SESSION` behavior. Python-version compatibility is a major signal for this file.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/dataserver.py -->
# sources/test-tools/pynfs/nfs4.1/dataserver.py

## Purpose
`dataserver.py` manages pNFS data-server access for the NFSv4.1 test server. It abstracts active data servers, opens backing files derived from MDS filehandles, reads/writes/truncates data through NFSv4.1 or NFSv3 clients, and builds file-layout device address bodies used by MDS layout responses.

## Important APIs, Types, And Functions
- `DataServer(server, port, path, flavor=AUTH_SYS, active=True, mdsds=True, multipath_servers=None, summary=None)` stores endpoint/path state and controls activation.
- `DataServer.up()`, `down()`, `reset()`, `get_netaddr4()`, `get_multipath_netaddr4s()`, and `fh_to_name()` provide common lifecycle, device-address, and name-mapping behavior.
- `DataServer41` connects to an NFSv4.1 DS, creates a client/session, ensures the root path exists, and implements `open_file`, `close_file`, `read`, `write`, `truncate`, and `get_size`.
- `DataServer3` connects through portmap and mountd, uses NFSv3 CREATE/LOOKUP/READ/WRITE/SETATTR/GETATTR, and implements the same high-level file API with no open stateid.
- `DSDevice` loads data-server configuration files, stores active server objects, packs `nfsv4_1_file_layout_ds_addr4`, and dispatches open/close/filehandle retrieval across active data servers.

## Control Flow
`DSDevice.load(filename, server_obj)` parses each non-comment line with `nfs4lib.parse_nfs_url`, treats the last server tuple as the direct endpoint, treats earlier tuples as multipath alternates, constructs `DataServer41` entries, and exits on parse/connect failure. After loading, it computes `address_body` by packing stripe indices and multipath netaddr lists.

For NFSv4.1 data servers, `connect` creates AUTH_SYS root credentials, instantiates `NFS4Client`, runs NULL, performs `EXCHANGE_ID` through `new_client`, creates a session with broad channel attrs, and sends `RECLAIM_COMPLETE`. `make_root` walks the configured path, creating missing directories, gets the root filehandle, and verifies read/lookup/modify/extend access. `open_file` hashes the MDS filehandle into a name, attempts guarded create/open, falls back to `OPEN4_NOCREATE` on `NFS4ERR_EXIST`, and caches `(ds_fh, open_stateid)` by MDS filehandle.

For NFSv3 data servers, `connect` locates mount and NFS ports, gets the export root filehandle, and verifies ACCESS. `open_file` attempts guarded CREATE and falls back to LOOKUP on existing files. Read/write/truncate/size methods map directly to NFSv3 procedures.

## State And Persistence Behavior
Each `DataServer` tracks active state, endpoint fields, root/path filehandle, and a `filehandles` map keyed by MDS filehandle. Backing file contents are persisted by the external DS server, not by this module. `DSDevice.address_body` is cached after load and must be refreshed when active servers or multipath addresses change. NFSv4.1 DS sessions are reset on state errors such as stale client ID or bad/dead session.

## Dependencies And Integration Points
The module depends on `rpc.rpc`, `nfs4client`, `nfs3client`, generated NFSv4/NFSv3 types and constants, `nfs_ops`, `nfs4lib`, `NFS4Packer`, `hashlib`, `socket`, and the pNFS file-layout classes in `fs.py`. `FSLayoutFSObj` calls `DSDevice.open_ds_file`, `close_ds_file`, and `get_ds_filehandles`; `FilelayoutVolWrapper` calls per-DS read/write/truncate/size methods.

## Risks And Edge Cases
- `DataServer.fh_to_name` hashes a Python `"%r"` string without encoding; under Python 3 `hashlib.sha1` expects bytes.
- `DataServer41._execute` logs `nfsstat4` without importing it into the module namespace; it imported `const4.nfsstat4`.
- `close_file` for NFSv4.1 uses `seqid=0` with a FIXME that it must not always be zero.
- `DataServer41.write` and `DataServer3.write` ignore result details and short-write semantics.
- `make_root` has comments noting DS directories are not cleaned.
- `DSDevice.load` exits the whole process on configuration/connect errors rather than reporting recoverable failures.
- `get_ds_filehandles` assumes every active DS has already opened the file and stored a mapping.

## Test Signals
Signals include successful parsing of single and multipath DS URLs, correct packed device address bodies, NFSv4.1 reset on session/client state errors, DS root creation/access validation, stable MDS-fh-to-DS-fh mapping, file-layout open/close hooks creating and deleting DS file mappings, and read/write/truncate operations reflected through layout-backed files.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/dataserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/errorfunctions.py -->
# sources/test-tools/pynfs/nfs4.1/errorfunctions.py

## Purpose
`errorfunctions.py` contains mutation functions used by the proxy error-injection framework. Instead of returning a protocol status, these functions alter selected operation arguments to simulate malformed or surprising behavior.

## Important APIs, Types, And Functions
- `Errors.__init__()` seeds the random generator.
- `short_read(opname, arg, env=None)` reduces `arg.opread.count` to a random value in the original range.
- `wrong_offset(opname, arg, env=None)` attempts to move a READ offset to a random later offset.
- `wrong_sequenceid(opname, arg, env=None)` decrements a sequenceid field.

## Control Flow
`errorparser.ErrorParser.get_error` instantiates `Errors`, picks a named function from XML, and calls it with the operation name, mutable XDR argument object, and proxy compound environment. The function mutates the object in place; the proxy later repacks and forwards the modified request unless a status-code injection already returned.

## State And Persistence Behavior
The file stores no persistent state. It uses module-global random state and mutates the passed argument object directly for the lifetime of a proxied request.

## Dependencies And Integration Points
It depends only on `random`, but it is tightly coupled to generated XDR field names used by NFS READ and SEQUENCE-like operations. It integrates with `errorparser.py` and `nfs4proxy.py`.

## Risks And Edge Cases
- `wrong_offset` uses `arg.offset` and `arg.count`, while `short_read` uses `arg.opread.count`; if the generated wrapper stores fields under `opread`, `wrong_offset` will fail.
- `wrong_sequenceid` assumes a top-level `sa_sequenceid` field, which may not exist for all configured operations.
- There is no validation that the selected function matches the selected operation.
- Random mutation makes tests nondeterministic unless the random seed is controlled externally.

## Test Signals
Proxy tests should verify XML-selected functions are invoked, request XDR is mutated before forwarding, malformed field assumptions surface as logged proxy errors, and mutation frequency/delay from `errorparser` are honored around these functions.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/errorfunctions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/errorparser.py -->
# sources/test-tools/pynfs/nfs4.1/errorparser.py

## Purpose
`errorparser.py` reads XML descriptions of proxy fault-injection scenarios and applies them to NFSv4 operations. It supports per-operation matching, random frequency, optional delay, injected status codes, and argument-mutation functions defined in `errorfunctions.py`.

## Important APIs, Types, And Functions
- `ErrorDesc` stores lists for `name`, `operation`, `errorcode`, `function`, `delay`, and `frequency`, with defaults of no delay and one-in-ten frequency.
- `ErrorDesc.addField(field, value)` assigns parsed XML text lists to descriptor attributes.
- `ErrorParser(filename)` parses XML with `xml.dom.minidom`, initializes `errors`, and calls `get_error_desc`.
- `getText(nodelist)` extracts lowercased text nodes.
- `handleErrorConf`, `handleError`, and `handleElement` traverse `<error>` entries and child tags.
- `get_error(opname, arg=None, env=None)` checks descriptors for a matching operation and returns a status code or mutates arguments.

## Control Flow
Initialization parses the XML document and builds one `ErrorDesc` per `<error>`. During proxy request handling, `get_error` scans descriptors in order. Nonmatching operations are skipped. For a match, it applies frequency by picking a random integer from `1..frequency` and only proceeding when it hits the upper bound. It sleeps for configured delay, then either chooses an error code from XML or chooses an error function. Numeric error strings are converted with `int`; symbolic names are matched against `nfsstat4`; functions are looked up on a fresh `Errors` object and called.

## State And Persistence Behavior
`ErrorParser` keeps the parsed DOM and an in-memory list of descriptors. It does not persist state. Randomness is global and seeded during parser construction. Delays block the proxy request-handling thread synchronously.

## Dependencies And Integration Points
The module depends on `xml.dom.minidom`, generated `nfsstat4`, logging, traceback/sys for error reporting, and `Errors` from `errorfunctions.py`. It is instantiated by `nfs4proxy.NFS4Proxy` and consulted for each operation while the request is still mutable.

## Risks And Edge Cases
- `__init__` calls `xml.dom.minidom.parse(filename)` before checking whether `filename is None`; passing no error file can fail before the intended "No error description" path.
- Symbolic error lookup uses `nfsstat4.iteritems()`, which is Python 2 style and breaks under Python 3.
- When a function injection is used, `get_error` returns `None` after mutation, so callers must rely on the mutated forwarded request.
- Exceptions during XML loading are swallowed after logging, leaving a partially initialized parser.
- Text is lowercased; symbolic constants are uppercased later, but function names and operation names must match expected lower-case conventions.
- Frequency defaults to one-in-ten, which may surprise tests expecting an error every time.

## Test Signals
Test signals include XML files with numeric and symbolic status codes, no-error descriptors, delay timing, deterministic behavior under seeded randomness, function mutation paths, and `None`/missing-file handling. Proxy-level tests should assert injected errors are encoded in the correct operation result and stop forwarding.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/errorparser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/fs.py -->
# sources/test-tools/pynfs/nfs4.1/fs.py

## Purpose
`fs.py` implements the NFSv4.1 test server's filesystem object model. It provides in-memory and disk-backed filesystems, filesystem objects with NFS attributes and locking hooks, a `/config` pseudo-filesystem, and pNFS block/file layout filesystems that coordinate with data servers.

## Important APIs, Types, And Functions
- `MetaData` holds persistent object metadata: change counter, type, refcount, create verifier, owner, mode, timestamps, parent ID, symlink target, and device data.
- `FSObject` models one NFS object. It exposes NFS attributes as `fattr4_*` properties, stores metadata through `MetaData`, owns a `FileState`, a read/write lock, a seek lock, file/directory contents, layout state, and mount-covering pointers.
- Core `FSObject` APIs include `read`, `write`, `sync`, `close`, `set_attrs`, `lookup`, `lookup_parent`, `link`, `unlink`, `readdir`, `create`, `get_layout`, and `commit_layout`.
- `FileSystem` is the base filesystem with fsid, active-object cache, disk lock, root object, supported attributes, mount handling, object allocation, lookup, creation, sync, delegation options, layout options, and device-list hooks.
- `RootFS` is a read-only root filesystem; `StubFS_Mem` is volatile memory-backed; `StubFS_Disk` persists metadata and data files under a shelve-backed directory.
- `ConfigObj` and `ConfigFS` expose server, client, operation, and action config lines as read/write files under a synthetic config tree.
- `LayoutFSObj`, `BlockLayoutFS`, `FSLayoutFSObj`, `FileLayoutFS`, `FileLayoutFile`, and `FilelayoutVolWrapper` implement pNFS block-layout and file-layout behavior.
- `Device`, `my_ro_extent`, `my_rw_extent`, and `test_layout_dict` provide backing layout metadata for test layouts.

## Control Flow
`FileSystem.__init__` initializes supported attrs, an object cache, mount state, and a root directory created through `create`. `create` checks read-only state, allocates an ID, constructs the configured object class, and inserts it into `_ids`. `find` returns cached objects or calls `find_on_disk` under `_disk_lock`.

`FSObject.__init__` either wraps existing `MetaData` loaded from disk or creates fresh metadata from an NFS kind/createtype. It initializes regular-file storage with `init_file`, directory entries, directory cache, `FileState`, locks, layout state, and subclass hooks. `__getattr__` and `__setattr__` forward metadata fields to `self.meta`, so object attributes and persisted metadata share the same access surface.

Read/write/truncate flows acquire `seek_lock`, perform file-object operations, and bump the change counter. Attribute setting iterates the incoming bitmap dict, verifies server support and writeability via `nfs4lib.attr_info`, chooses either object or metadata target, sets values, returns the successfully-set bitmask, and records partial success in `NFS4Error.attrs` on failure.

Directory flow uses `entries` as a name-to-object-ID map. `lookup` checks access, resolves the ID, and follows mount overlays through `covered_by`. `lookup_parent` climbs to the mounted-on object when at a filesystem root. `create` allocates an object, defaults owner to the principal name, sets attrs, and links it into the parent. `readdir` caches name/object lists under timestamp verifiers and rejects unknown nonzero verifiers.

Config flow dynamically computes directory entries from encoded IDs. File objects associated with config lines reset their content to a comment plus current value. On close, dirty config files parse one non-comment line, assign through `ConfigLine.value`, dispatch `ConfigAction` reboot, and then reset displayed content.

pNFS flow checks filesystem support in `FSObject.get_layout`/`commit_layout`, then delegates to layout subclasses. `LayoutFSObj` expands block extents and commits block layout updates. `FSLayoutFSObj` packs `nfsv4_1_file_layout4` using DS filehandles and uses `FileLayoutFile` to stripe reads/writes/truncates through `DataServer` wrappers.

## State And Persistence Behavior
`StubFS_Mem` and `RootFS` are process-memory filesystems. `StubFS_Disk` persists metadata as pickled `m_<id>` files, file/directory data as `d_<id>` files, and filesystem metadata in a shelve DB named `fs_info`. `FSObject._last_sync` tracks whether the current change counter has reached disk. `UNSTABLE4` sync returns without writing and `FILE_SYNC4` updates `_last_sync`.

Per-object state includes metadata, in-memory file handles (`StringIO` or layout wrappers), directory entries, a small directory-cookie cache, `FileState`, locks, current layout tuple, mount overlay pointers, and config dirty flags. Block layout state is partly global in `test_layout_dict`; file-layout backing data is persisted on remote data servers through `dataserver.py`.

## Dependencies And Integration Points
The module depends on `nfs4state.FileState`, generated NFS constants/types/packers, `nfs4lib`, `locking.Lock/RWLock`, `config.ServerPerClientConfig`, `ConfigAction`, Python filesystem modules, pNFS block generated types, and a local `block` module. It integrates with server operation handlers for LOOKUP, CREATE, READ, WRITE, SETATTR, READDIR, layouts, device IDs, config pseudo-files, and pNFS DS access.

## Risks And Edge Cases
- The file mixes Python 2 and Python 3 assumptions: `cStringIO`, text `StringIO`, `chr(0)` writes, pickle opened in text mode, division producing floats, and string/bytes mismatches can all break binary NFS data paths.
- `FSObject.isempty` assumes `entries` exists, which is not true for all object types.
- `unlink` decrements refcount and syncs the target but does not call `destroy` or deallocate IDs when refcount reaches zero.
- Directory verifier cache is timestamp keyed, small, and per-object; concurrent clients can see `NFS4ERR_NOT_SAME`.
- `ConfigObj._build_entries` encodes object identity into bit fields and comments admit unused bits are not carefully checked.
- `StubFS_Disk` opens pickle/data files in text mode and can corrupt bytes data.
- pNFS block layout code mutates global test layout state and has many explicit stubs around alignment, allocation locking, commit semantics, and poisoned reads.
- File layout striping assumes active DS count is nonzero and every DS has a cached filehandle.

## Test Signals
Signals include correct NFS attribute masks and partial-set errors, file size/read/write/truncate behavior, directory lookup/readdir cookies, mount traversal, config pseudo-file read/write/reboot/error-injection behavior, disk-backed restart preservation, read-only root errors, block layout GET/COMMIT behavior, file-layout DS open/close/read/write/truncate integration, and lock-safe concurrent access to object data.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/fs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/fs_base.py -->
# sources/test-tools/pynfs/nfs4.1/fs_base.py

## Purpose
`fs_base.py` defines generic extent and file-like abstractions for layout-backed files. It is a small base for sparse or externally mapped files where logical file offsets map to extents on backing volumes.

## Important APIs, Types, And Functions
- Extent type constants: `HOLE`, `VALID`, `INVALID`, and `EOF`.
- `Extent(type, v_pos, f_pos, length, volume)` records extent state, backing-volume offset, file offset, length, and volume object.
- `LayoutFile(inode, fs, size=None)` stores logical file size, current position, owning filesystem, and inode ID.
- `LayoutFile.seek`, `tell`, `read`, `write`, and `_find_extent` implement a minimal file-like API.
- `LayoutFile` expects filesystem methods `_find_extent`, `_map_extent`, and possibly `_create_hole`, though `_create_hole`/`_map_extent` are not implemented here.

## Control Flow
`seek` computes a new logical position from start/current/end and enforces bounds unless the file is resizable. `read` limits the count to bytes before EOF, repeatedly asks the filesystem for the current extent, emits zero bytes for `HOLE`, reads from the backing volume for mapped extents, advances position, and joins segments. `write` creates a hole when writing beyond EOF, maps EOF or HOLE extents before using them, writes bounded segments to the backing volume, advances position, and grows `_size`.

## State And Persistence Behavior
The object stores only logical size and current seek position. Durable data belongs to backing `volume` objects and the filesystem extent map. `size=None` makes the logical file resizable; a fixed `size` makes seek reject positions outside the current file extent.

## Dependencies And Integration Points
The file is standalone, but its classes are conceptually used by pNFS layout filesystem implementations. It requires the owning filesystem to provide extent lookup and mapping operations and backing volumes to implement `seek`, `read`, and `write`.

## Risks And Edge Cases
- `LayoutFile.write` calls `_create_hole` and `_map_extent`, but those methods are not defined in this class.
- `_find_extent` calls `self._fs._find_extent(pos, self._inode)` and raises on `INVALID`, so filesystem implementations must use the same extent contract.
- It uses text strings (`'\0'`, `"".join`) for binary file data, which is fragile under Python 3.
- `seek` does not handle unknown `whence` values and can reference `newpos` before assignment.
- Fixed-size seek requires `newpos < self._size`, rejecting a seek exactly to EOF.

## Test Signals
Tests should cover reads through holes and valid extents, writes that allocate at EOF, writes beyond EOF that create holes, invalid extent errors, non-resizable seek bounds, and filesystem/volume mock interactions for extent mapping.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/fs_base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/locking.py -->
# sources/test-tools/pynfs/nfs4.1/locking.py

## Purpose
`locking.py` provides small concurrency primitives for the NFSv4.1 test server: a named counter, a switchable debug wrapper around `threading.Lock`, and a simple read/write lock with optional verbose acquisition tracing.

## Important APIs, Types, And Functions
- `DEBUG` selects normal locks or debug/verbose lock wrappers at creation time.
- `Counter(first_value=0, name="counter")` uses a lock to return monotonically increasing values from `next()`.
- `Lock(name="")` returns `_DebugLock` when debugging or a normal `threading.Lock` otherwise.
- `RWLock(name="")` returns `_RWLockVerbose` when debugging or `_RWLock` otherwise.
- `_DebugLock` wraps a normal lock and records/prints thread lock state on acquire/release.
- `_RWLock` implements `acquire` for read, `acquire_write` for write, `release`, `upgrade`, and `downgrade`.
- `_RWLockVerbose` subclasses `_RWLock` and decorates internal read/write operations with debug tracing.

## Control Flow
`Counter.next` locks, returns the current value, increments, and releases. Normal `Lock` is just `threading.Lock`; debug mode records waiting/holding/released states on the current thread.

`_RWLock.acquire` increments read-waiter count and waits while any writer wants or owns the lock. `_RWLock.acquire_write` increments writer count, waits for readers to drain, then waits until it can acquire the write mutex. `release` infers whether to release read or write based on global read-lock count. `upgrade` releases one read lock without notifying, then waits for write access; `downgrade` releases write access and reacquires read access.

## State And Persistence Behavior
All state is in process memory. `_RWLock` keeps condition, write mutex, writer count, reader count, and active-reader count. Debug locks also attach a `locks` dictionary to thread objects for inspection. There is no persistence.

## Dependencies And Integration Points
The module depends on `threading`. `fs.py`, `nfs4lib.SSVContext`, `nfs4proxy`, and other server modules use `Lock`, `RWLock`, or `Counter` for object state, replay/cache state, and ID generation.

## Risks And Edge Cases
- `_RWLock.release` decides release type from aggregate `_read_lock`, not per-thread ownership; a writer calling release while any reader exists can incorrectly release a read lock.
- `upgrade` can deadlock or starve when multiple readers attempt upgrade.
- `threading.Condition.notifyAll()` and `threading.currentThread()` are old names; modern Python prefers `notify_all()` and `current_thread()`.
- `_RWLockVerbose` calls `super(_RWLockVerbose, self)._acquire_read()` instead of `super(...)._acquire_read`, which retrieves an attribute incorrectly in Python.
- Debug mode is selected at lock creation, so toggling `DEBUG` later does not affect existing locks.

## Test Signals
Tests should cover counter uniqueness under concurrency, multiple readers, writer exclusion, read-to-write upgrade, write-to-read downgrade, unmatched releases, and debug-mode tracing compatibility with context-manager usage.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/locking.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs3client.py -->
# sources/test-tools/pynfs/nfs4.1/nfs3client.py

## Purpose
`nfs3client.py` is a lightweight RPC client stack for NFSv3 and mount/portmap services. It is primarily used by pNFS data-server support to access NFSv3-backed data servers with a uniform procedural API.

## Important APIs, Types, And Functions
- `PORTMAPClient` calls the portmapper and provides `get_port(prog, vers)`.
- `Mnt3Client` calls the MOUNT v3 service and provides `get_rootfh(export)`.
- `NFS3Client` calls the NFS v3 service, owns a `Mnt3Client`, stores a verifier, and exposes `null`, `proc_async`, `proc`, and `listen`.
- Module-level `op3 = nfs_ops.NFS3ops()` builds generated NFSv3 procedure argument objects.

## Control Flow
Each client subclass derives from `rpc.Client`, stores a target server address, lazily establishes an RPC pipe with `get_pipe`, packs generated argument objects using the appropriate generated packer, sends calls, listens for replies, and unpacks the expected generated result type.

`NFS3Client.__init__` uses `PORTMAPClient` to discover mountd and NFS ports unless a port is supplied, creates a `Mnt3Client`, and records callback/control metadata. `proc` sends a request and derives the result class name from the argument class name by replacing `3args` with `3res`. Optional summary output records operation names and returned `nfsstat3` strings.

## State And Persistence Behavior
State is limited to RPC pipes, server addresses, credentials, discovered ports, verifier, and summary object. NFS filehandles and server-side data are external. `get_pipe` reconnects when the stored pipe is missing or inactive.

## Dependencies And Integration Points
The module depends on generated NFSv3, MOUNTv3, and PORTMAP XDR constants/types/packers, `rpc.rpc`, `nfs_ops`, `nfs4lib`, `threading`, `hmac`, and `os.path`. `dataserver.DataServer3` uses it for NFSv3-backed pNFS file layout operations.

## Risks And Edge Cases
- `Mnt3Client.get_rootfh` builds `dirpath('/' + os.path.join(*export))`; an empty export list or bytes components can fail.
- `PORTMAPClient.proc` requires an explicit `restypename`, while NFS3 `proc` derives it; misuse is easy.
- `listen` assumes any nonempty response data can be unpacked into the expected result type.
- Imported modules such as `threading`, `hmac`, and `traceback` are mostly unused here, suggesting copy/paste surface.
- `NFS3Client.set_cred` only changes `default_cred`; existing in-flight calls keep their original credentials.

## Test Signals
Signals include portmap lookup, mount root filehandle acquisition, NULL calls, each packed NFSv3 operation returning the matching generated result type, summary logging, reconnect behavior after inactive pipes, and integration with `DataServer3` create/read/write/truncate/getattr paths.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs3client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4client.py -->
# sources/test-tools/pynfs/nfs4.1/nfs4client.py

## Purpose
`nfs4client.py` implements the pynfs NFSv4.1/4.2 client and callback server used by tests. It can issue raw COMPOUND calls, establish client IDs and sessions, manage foreground/backchannel sequence slots, handle callback COMPOUND requests, install callback hooks, and assist state-protection/SSV tests.

## Important APIs, Types, And Functions
- `NFS4Client(rpc.Client, rpc.Server)` connects to an NFS server, exposes NFSv4 RPC client methods, and registers as an NFS callback server.
- `compound_async`, `compound`, `listen`, `null_async`, `null`, `control_async`, and `control` are the primary RPC call helpers.
- Callback handlers `handle_0`, `handle_1`, `op_cb_compound`, `op_cb_sequence`, `op_cb_getattr`, `op_cb_recall`, `op_cb_notify_lock`, and `op_cb_layoutrecall` process server-to-client callbacks.
- `new_client`, `new_client_session`, and `new_pnfs_client_session` wrap `EXCHANGE_ID`, `CREATE_SESSION`, and `RECLAIM_COMPLETE`.
- `ClientStateProtection` builds SSV crypto context data from `EXCHANGE_ID` state-protection results.
- `ClientRecord` stores clientid, sequence id, flags, credentials, SSV handles, and session creation/hook registration helpers.
- `SendChannel` stores channel attrs and outbound sequence `Slot` objects.
- `SessionRecord` owns session ID, client pointer, fore/back channels, credential, and sequence-aware compound helpers.

## Control Flow
`NFS4Client.__init__` initializes the RPC client for NFSv4, configures callback program metadata, stores minor version, server tag/implementation ID/verifier, connects to the server, and initializes client/session maps. `compound` creates a per-call test tag via stack inspection, packs `COMPOUND4args`, sends procedure 1, unpacks `COMPOUND4res`, optionally records summary output, and returns the decoded result.

Client/session setup starts with `new_client`, which sends `EXCHANGE_ID`, checks the expected status, creates a `ClientRecord`, and stores it by clientid. `ClientRecord.create_session` retries on `NFS4ERR_DELAY`, then `_add_session` increments the client sequence, creates a `SessionRecord`, and stores it in the dispatcher's session map.

Session compounds prepend `SEQUENCE`. `_prepare_compound` chooses a free foreground slot, generates a sequence op, and records the slot. `compound` sends `[SEQUENCE] + ops`, updates slot state from the SEQUENCE result, retries NFS4ERR_DELAY with special handling for delay on the SEQUENCE operation, marks the slot free, strips the sequence result on success, and returns the application-level response.

Callback flow unpacks `CB_COMPOUND4args`, creates a `CBCompoundState`, dispatches each callback op by generated name, appends encoded results, and stores replay-cache data when a callback `SEQUENCE` provides a cache object. `op_cb_sequence` validates position, session ID, slot ID, and sequence ID, then sets environment caching/session fields. Hook helpers allow tests to attach pre/post handlers per clientid and callback op.

## State And Persistence Behavior
The client stores process-local server connection, credentials, sessions, client records, verifier, callback hooks, slots, SSV contexts, and replay/cache state. It persists nothing to disk. Sequence slots are marked `inuse` for outbound calls and updated using `Slot.finish_call`. SSV contexts maintain key windows and are mutated by `set_ssv`.

## Dependencies And Integration Points
The module depends on `rpc.rpc`, `nfs4lib`, generated NFSv4 constants/types, SCTRL packers, `nfs_ops`, `nfs4commoncode` callback encoders, `nfs4server.Slot` and `Channel`, Python threading/hmac/inspect/logging, and security classes from `rpc.security`. It is used by client tests, data-server management, and pNFS callback/layoutrecall flows.

## Risks And Edge Cases
- The file imports `os.path.basename` but `create_tag` calls `os.fsencode` without importing `os`.
- There are two `handle_1` definitions; the second overwrites the first stub.
- `op_cb_compound` catches `NFS4Errror` with a misspelled name, so invalid UTF-8 tag handling may raise unexpectedly.
- `new_pnfs_client_session` calls `fail` but does not import it.
- Session `compound` assigns `saved_kwargs = kwargs` rather than copying; retry preparation mutates the same dict.
- Slot release happens after the retry loop, but exceptions before release can leak `inuse`.
- Many callback operations are stubs that return OK with empty or hook-provided results.
- State-protection errors sometimes raise strings.

## Test Signals
Signals include EXCHANGE_ID/CREATE_SESSION/RECLAIM_COMPLETE success, correct slot sequence increments and replay behavior, NFS4ERR_DELAY retry semantics, stripped SEQUENCE results, callback SEQUENCE validation, callback hook invocation, CB_LAYOUTRECALL triggering LAYOUTRETURN, SSV SET_SSV digest updates, and summary output matching issued operations.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4commoncode.py -->
# sources/test-tools/pynfs/nfs4.1/nfs4commoncode.py

## Purpose
`nfs4commoncode.py` dynamically generates shared client/server helper classes for NFSv4 COMPOUND processing. It provides result encoders, compound result accumulators, replay-cache-aware paired results, and per-compound state classes for both normal and callback operations.

## Important APIs, Types, And Functions
- `encode_status_by_name(name, status, *args, **kwargs)` constructs an `nfs_resop4` for an operation name and generated `NAME4res` payload.
- `encode_status(status, *args, **kwargs)` infers the operation name from the caller `op_<name>` and delegates to `encode_status_by_name`.
- `CompoundArgResults` stores result structs, their packed XDR bytes, current status, tag prefix, and computed reply size.
- `PairedResults` stores both the reply sent now and the replay-cache response, inserting `NFS4ERR_RETRY_UNCACHED_REP` when only the SEQUENCE result should be cached.
- `CompoundState` stores current/saved filehandles and stateids, current session/cache/caching flag, request metadata, credential-derived principal/connection/header size, tag, and paired results.
- Callback equivalents `cb_encode_status*`, `CBCompoundArgResults`, `CBPairedResults`, and `CBCompoundState` are created from the same template.

## Control Flow
The module defines a format string containing Python source and executes it twice: once with normal operation names/types and once with callback operation names/types. Encoders create the generated result payload, wrap it in the correct `nfs_resop4` or `nfs_cb_resop4` union, attach a synthetic `status` attribute for uniform handling, and optionally attach a tag message.

During server or callback dispatch, operations append encoded results to `env.results`. `PairedResults.append` updates the reply result array and also constructs the replay-cache array depending on whether caching is enabled and which operation index is being appended. `CompoundState` is constructed once per COMPOUND and carries mutable interim state across operation handlers.

## State And Persistence Behavior
State is per-COMPOUND and in memory. `CompoundArgResults` stores packed result bytes and base length for response-size accounting. `PairedResults` stores reply and cache views for the active COMPOUND; long-term persistence is owned by session slot caches outside this module.

## Dependencies And Integration Points
The module depends on `nfs4lib`, generated constants/types, and `sys._getframe`. It is used by `nfs4server`, `nfs4client` callback handling, and `nfs4proxy` to share encoding and environment behavior across normal and callback COMPOUND processing.

## Risks And Edge Cases
- Heavy use of `exec` and generated names means errors surface at runtime and are difficult to statically inspect.
- `encode_status` depends on caller function names beginning with `op_`.
- The result union field naming conventions are acknowledged as fragile for NFSv4.1.
- `PairedResults` has comments noting missing size checks for reply and cache limits.
- `CompoundState.get_principal` assumes credentials expose `credinfo.principal`; AUTH_SYS or malformed creds may differ.
- `set_cfh` defaults state to `nfs4lib.state00`, which can unintentionally clear current stateid when resetting current filehandle.

## Test Signals
Tests should assert generated result structures pack/unpack correctly for normal and callback operations, operation tags propagate, replay-cache arrays contain either full cached results or `RETRY_UNCACHED_REP` as appropriate, and `CompoundState` exposes principal/connection/header fields used by server handlers.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4commoncode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4lib.py -->
# sources/test-tools/pynfs/nfs4.1/nfs4lib.py

## Purpose
`nfs4lib.py` is the central utility library for pynfs NFSv4.1 code. It wraps generated XDR packers/unpackers, converts attribute bitmaps and fattr structures, defines common NFS exceptions and principals, implements SSV security-context helpers, parses NFS URLs and paths, provides special stateids, and declares attribute access metadata.

## Important APIs, Types, And Functions
- Special stateids `state00`, `state11`, and `state01` are generated `stateid4` values used throughout tests and server code.
- Hash/encryption OID dictionaries and `_e_wrap` support SSV state protection with hashlib and AES.
- `set_attrbit_dicts()` builds `attr2bitnum`, `bitnum2attr`, `bitnum2packer`, and `bitnum2unpacker` from generated `FATTR4_*` constants.
- `set_flags()` builds dictionaries/masks for exchange-id, create-session, and access flags.
- Exception classes `BadCompoundRes`, `UnexpectedCompoundRes`, `InvalidCompoundRes`, `NFS4Error`, and `NFS4Replay` normalize test/server error handling.
- `FancyNFS4Packer` and `FancyNFS4Unpacker` convert bitmap integers, dict-style fattrs, and simple directory-entry lists to/from generated XDR shapes.
- `dict2fattr`, `fattr2dict`, `list2bitmap`, `bitmap2list`, `test_equal`, `inc_u32`, `dec_u32`, `xdrlen`, `verify_time`, `get_nfstime`, `parse_nfs_url`, `path_components`, `attr_name`, `check`, and `use_obj` are broad helper functions.
- `SSVContext` manages SSV subkeys, HMAC MIC tokens, wrap/unwrap encryption tokens, and SET_SSV state.
- `NFS4Principal` is the access-check identity abstraction.
- `AttrConfig` and `attr_info` classify NFSv4 attributes by readable/writeable and object/filesystem/server ownership.

## Control Flow
Import-time initialization creates attribute lookup dictionaries and flag masks. Packing flow passes dict fattrs and integer bitmaps through `FancyNFS4Packer` filters before generated packers run; unpacking reverses the representation. Attribute dict conversion sorts attribute bit numbers, packs values one by one with generated packers, concatenates opaque attr bytes, and builds an `fattr4` with a bitmap.

SSV flow starts with an all-zero SSV. `set_ssv` XORs incoming SSV material with the current SSV, derives subkeys, stores them in a bounded deque, and increments `ssv_seq`. MIC and wrap operations choose initiator-to-target or target-to-initiator keys based on whether the context is local/client-side, pack token plaintext, compute HMACs, and optionally encrypt/decrypt with AES-CBC.

URL parsing accepts optional `nfs://`, one or more comma-separated `host[:port]` servers, bracketed IPv6 addresses, and an optional path. It returns a tuple of `(host, port)` pairs and byte path components normalized by `path_components`.

## State And Persistence Behavior
Most helpers are stateless after import-time dictionaries. `SSVContext` owns mutable key windows, sequence number, and a lock. `NFS4Error` carries protocol status plus attrs, lock-denied, tag, and custom check message. There is no disk persistence.

## Dependencies And Integration Points
The module depends on generated NFSv4 constants/types/packers, `rpc.rpc`, `nfs_ops`, `locking.Lock`, `hashlib`, `hmac`, optional `Crypto.Cipher.AES`, regex/path/time/random/struct utilities, and is imported by nearly every NFSv4.1 client, server, proxy, filesystem, environment, and dataserver module.

## Risks And Edge Cases
- Multiple helpers still use Python 2 string semantics: `ord(c)` over bytes/text, `'\0'` string keys, string joins for binary data, and raising strings.
- `ssv_mech_oid` is a text string while other OIDs are bytes.
- `parse_nfs_url` calls `os.fsencode(m.group('path'))`; if the path group is `None`, it handles it separately, but server host parts remain text.
- `SSVContext.verifyMIC` catches missing old keys with `KeyError`, but deque indexing raises `IndexError`.
- AES is represented by a fake class when PyCrypto is missing; failures occur only when SSV wrap/unwrap is exercised.
- `check` assumes `res.status` and `res.resarray` exist and that status maps contain all values.
- `attr_info` marks many attributes as object/filesystem/server-owned by hand; any generated constant changes require manual updates.

## Test Signals
Signals include fattr dict round trips, bitmap/list conversions, dirlist list/chain conversions, NFS URL parsing for IPv4/IPv6/multipath/default ports, stateid constants, 32-bit sequence wraparound, SSV MIC/wrap/set_ssv behavior with and without AES, `check` exception messages, and attribute ownership/writeability decisions used by `fs.FSObject.set_attrs`.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4lib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4proxy.py -->
# sources/test-tools/pynfs/nfs4.1/nfs4proxy.py

## Purpose
`nfs4proxy.py` implements an NFSv4 proxy used for testing traffic forwarding, callback forwarding, channel-attribute rewriting, and fault injection. It listens as an RPC server, forwards client COMPOUND and NULL calls to a destination server, can proxy callback traffic over the client's connection, and can inject XML-described errors before forwarding.

## Important APIs, Types, And Functions
- `NFS4Proxy(rpc.Server)` is the proxy server.
- Inner `Channel` stores request/response/cache/ops/requests channel caps used to clamp `CREATE_SESSION` attrs.
- Inner `ProxyClient(rpc.Client)` maintains the downstream or callback connection and sends raw forwarded calls.
- `start`, `start_cb_proxy`, `forward_call`, `handle_0`, `handle_1`, `handle_cb_0`, and `handle_cb_1` are the RPC entry points.
- `op_create_session(arg, cred, direction=0)` rewrites fore/back channel attributes and initializes callback proxying.
- `scan_options()` parses command-line destination/listen options.

## Control Flow
Construction binds the proxy RPC server, creates a `ProxyClient` connected to the destination NFS server, assigns the reverse reference, and loads an `ErrorParser`. For NULL calls, the proxy forwards an empty NULL request to either downstream or callback side and returns success if it receives a response.

COMPOUND handling unpacks request XDR into normal or callback args, creates `CompoundState`/`CBCompoundState`, scans operations, invokes matching proxy override methods, consults `errorhandler.get_error`, and if an injected status is returned, immediately packs a one-operation error reply and returns without forwarding. If no injected error stops the request, it repacks possibly mutated args, forwards raw XDR to the selected client, unpacks the downstream response, runs post-processing override hooks, repacks, and returns to the original caller.

`CREATE_SESSION` pre-processing starts a callback proxy using the client's connection and clamps requested fore/back channel attrs to the proxy's smaller configured channel caps. Callback calls use `handle_cb_*` and `cb_client` to forward traffic back to the original client.

## State And Persistence Behavior
Proxy state is in process memory: downstream client pipe, optional callback client, callback program/version, error parser, channel limits, tag, and RPC server state. It persists no traffic. Error injection can mutate in-flight request objects before forwarding; those mutations only live for that request.

## Dependencies And Integration Points
The module depends on `rpc.rpc`, generated NFSv4 constants/types, SCTRL packers, `nfs4lib`, `nfs4commoncode`, `nfs4client`, `locking`, `errorparser`, logging, traceback, random/hmac/struct/time, and command-line `optparse`. It sits between client tests and an NFSv4 server, including callback traffic.

## Risks And Edge Cases
- Callback request unpacking uses `unpack_CB_COMPOUNDargs`, while other code uses `unpack_CB_COMPOUND4args`; this naming mismatch can break callback proxying.
- Identity checks use `is 0` and `is 1` for integers.
- `ErrorParser(None)` may fail before proxy startup if no error file is supplied.
- Override function results are assigned but mostly ignored unless error injection returns a code.
- `_adjust_channel_values` misspells `ca_maxresponsesize_cached` as `ca_maxresposnesize_cached` in one assignment.
- The proxy supports only one downstream connection and one callback client at a time.
- `forward_call` catches timeouts but not decode/pack errors or connection resets beyond retry loop.
- The injected error reply uses the current operation name and current result accumulator; multi-op prefix behavior is minimal.

## Test Signals
Signals include transparent forwarding of NULL and COMPOUND calls, `CREATE_SESSION` channel clamping, callback proxy setup and callback forwarding, XML error injection returning encoded NFS errors without forwarding, function-based argument mutation, downstream timeout handling, and response repacking preserving server results.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.1/nfs4proxy.py -->
