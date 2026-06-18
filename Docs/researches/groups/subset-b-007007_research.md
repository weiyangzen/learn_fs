# subset-b-007007 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repio.cc -->
# sources/distributed-fs/coda/coda-src/librepair/repio.cc

Purpose: implements serialization, parsing, and printing of directory repair operation lists used by Coda manual/automatic repair. It supports a binary transfer format (`repair_putdfile`, overloaded `repair_getdfile`) and an ASCII command format (`repair_parseline`, `repair_parsefile`, `repair_printline`, `repair_printfile`).

APIs and flow: binary output writes replica count, per-replica volume/repair counts, then each `struct repair` opcode, newline-terminated names, new names, and `REPAIR_MAX` network-order parameters. Binary input reverses that into allocated `listhdr` arrays. ASCII parsing recognizes create/remove/ACL/status/replica/rename opcodes, unquotes names via `urlquote`, decodes ACL rights, and grows replica/repair arrays one element at a time.

State and dependencies: depends on `repio.h`, `vice.h`, RPC2/PRS rights, and Coda assertions. It allocates caller-owned arrays and mutates parse input lines. Risks include unchecked `fwrite` paths, debug-looking `perror` calls on success paths, possible underflow when stripping newlines from empty `fgets` results, and no cleanup of partially allocated data on parse/read errors. Test signal is mostly indirect through repair tools and `restest.cc`; no local unit test covers malformed binary input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repio.h -->
# sources/distributed-fs/coda/coda-src/librepair/repio.h

Purpose: defines the repair operation wire/in-memory contract shared by librepair parsers, resolution code, and repair executors. `struct repair` carries an opcode, name, optional rename target, and five overloaded integer parameters.

Important types/APIs: opcodes cover file/directory/symlink/link creation, removal, positive/negative ACL updates, mode/owner/mtime changes, ASCII-only replica markers, and rename. `struct listhdr` groups repair operations per replica FID. Prototypes expose binary I/O, ASCII parsing, and printing.

State and integration: no state is stored in the header, but the constants and field overloading are a cross-module ABI. `resolve.cc` fills `listhdr` arrays; `repio.cc` serializes them; repair clients/servers interpret the opcode/parameter layout. Risks are typical of untagged unions: consumers must know which parameter indexes are meaningful for each opcode, and `MAXNAMELEN` is locally defined if absent. Test signals come from any parser/repair workflow that round-trips `listhdr` content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/resolve.cc -->
# sources/distributed-fs/coda/coda-src/librepair/resolve.cc

Purpose: bridges Coda conflict replicas on disk with the resolution subsystem. It reads replica directories, gathers FIDs/version vectors/ACLs, groups entries by name and FID, classifies conflicts through predicate functions, and builds per-replica repair operation lists.

APIs and flow: `res_getfid`/`res_getmtptfid` call Venus pioctls, with symlink fallback for conflict roots. `getunixdirreps` walks replica directories into global `direntriesarr` and fills `resreplica` headers. `dirresolve` first handles name/name conflicts interactively or from a fixed directory, then sorts by FID/name and calls predicate/repair functions. `InitListHdr`, `InsertListHdr`, `InRepairList`, and `IsCreatedEarlier` maintain repair lists. `GetParent` maps child FIDs to parent path/FID via pioctls.

State and risks: uses process globals for directory entries, sorted arrays, total counts, and conflict count, so it is not reentrant. Memory ownership is manual; `InsertListHdr` leaks old repair arrays, and `resClean` skips freeing `lh[0].repairList`. Path assembly assumes replica paths and slash layout. Dependencies include Venus ioctls, `predicate.h`, `cure.h`, `repio.h`, ACL parsing, and parser prompts. Test signal is `restest.cc` plus repair integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/resolve.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/resolve.h -->
# sources/distributed-fs/coda/coda-src/librepair/resolve.h

Purpose: declares the directory-resolution data model and public helper functions for librepair. It defines ACL structures, user repair preferences, directory entry snapshots, replica metadata, conflict counters, and repair-list builders.

Important types/APIs: `Acl`/`AclEntry` model positive and negative ACLs; `repinfo` carries non-interactive repair choices; `resdir_entry` captures child name, FID, version vector, mount-point flag, replica index, and looked-at marker; `resreplica` captures a parent directory replica with entry range, FID, path, mode, ACL, and owner. Exports include `getunixdirreps`, `dirresolve`, `resClean`, `GetParent`, and repair-list manipulation helpers.

State and integration: exposes globals allocated/filled by `resolve.cc`, which couples callers to a single active resolution pass. Dependencies include Coda FID/version-vector types and `struct listhdr` from `repio.h`. Risk centers on global mutable state and opaque ownership of arrays/pointers. Tests should validate multi-replica grouping, ACL parsing, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/resolve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/restest.cc -->
# sources/distributed-fs/coda/coda-src/librepair/restest.cc

Purpose: small command-line harness for exercising directory resolution against Unix directory replicas. It expects a set of replica paths, converts them to `resreplica` structures, runs `dirresolve`, and prints generated repair lines.

APIs and flow: `main` calls `getunixdirreps(argc - 1, argv + 1, &dirs)`, then invokes `dirresolve` with a callback that prints strings and an output `listhdr **`. On success, it iterates each replica repair list and calls `repair_printline`.

State and dependencies: depends directly on `resolve.cc` globals and `repio` printing. It does not free all allocated state or provide scripted assertions; output is human-inspected. The visible prototype in this file is stale relative to the full `dirresolve` signature in `resolve.h`, so build coverage depends on conditional declarations or historical source skew. Risk is mainly bitrot as an old manual test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/restest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/rvol.cc -->
# sources/distributed-fs/coda/coda-src/librepair/rvol.cc

Purpose: manages repair-time remounting of a conflict volume. `repair_mountrw` asks Venus to mount a mutable replica view, records the generated mount point, and updates conflict bookkeeping; `repair_finish` unmounts and cleans temporary repair state.

APIs and flow: the mount path uses conflict metadata, `ViceIoctl`, and repair pathname helpers to issue Coda pioctls. On success it records mount path/FID state in `struct conflict`; cleanup paths remove temporary directories and unwind pioctl state. It treats mount failures as user-visible repair errors through `msg`/`msgsize`.

State/dependencies: integrates with `repcmds` conflict structures, Venus ioctls, Coda path helpers, and volume/FID types. State is persisted outside this file in Venus/server repair state rather than local files. Risks include many early exits with partially initialized conflict fields, dependence on exact pioctl behavior, and cleanup requiring correct conflict state. Test signals are repair command workflows rather than local tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/rvol.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/Makefile.am -->
# sources/distributed-fs/coda/coda-src/lka/Makefile.am

Purpose: automake recipe for the lookaside database library and `mklka` client utility. It builds `liblka.la` from the public/private LKA headers, runtime database manager, and SHA helpers.

Integration: `mklka` is built only under `BUILD_CLIENT`. Include paths pull in LWP, base helpers, and `rwcdb`; link dependencies include `liblka`, `librwcdb`, and `libbase`.

Risks/test signals: build coverage verifies that the C files remain C-compatible with the configured OpenSSL/SHA, LWP, and rwcdb APIs. There are no automake test targets here; functional validation comes from `mklka` and `testlka`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/lka.c -->
# sources/distributed-fs/coda/coda-src/lka/lka.c

Purpose: runtime manager for Coda lookaside databases. Venus can register one or more rwcdb databases mapping SHA-1 object hashes to local file paths, then use those paths to fill container files without fetching data remotely.

APIs and flow: `LKParseAndExecute` parses `cfs lka` commands (`--list`, `--clear`, `+db`, `-db`) and manages a global linked list of `lkdb` objects. `lkdb_BindDB` opens an absolute database path, validates the descriptor record, derives the database directory, and counts entries. `LookAsideAndFillContainer` scans databases for a SHA, avoids paths under the Coda prefix, copies the hit file to the container while recomputing SHA, and validates optional length.

State/persistence: global `lkdbchain` holds open rwcdb handles and per-db statistics. The database itself persists as rwcdb content with descriptor key zero. Risks include no duplicate registration checks, command parsing with fixed buffers, use of `open` result without checking before copy, and path prefix handling for relative records. Test signals include `testlka` and `mklka` round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/lka.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/lka.h -->
# sources/distributed-fs/coda/coda-src/lka/lka.h

Purpose: public interface for the lookaside subsystem. It exposes SHA helper routines and the two Venus-facing operations: fill a container from registered databases and parse/execute LKA control commands.

Important APIs: `ViceSHAtoHex`, `CopyAndComputeViceSHA`, `ComputeViceSHA`, and `IsZeroSHA` operate on `SHA_DIGEST_LENGTH` byte arrays. `LookAsideAndFillContainer` performs lookup/copy/verification. `LKParseAndExecute` implements command-string control.

Dependencies and risks: includes `coda_hash.h` for SHA definitions and expects `shaprocs.c`/`lka.c` implementations. The header makes SHA-1 a visible contract; any digest migration must change database format, helper lengths, and callers. Test signals are compile-time API compatibility plus `mklka`/`testlka`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/lka.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/lka_private.h -->
# sources/distributed-fs/coda/coda-src/lka/lka_private.h

Purpose: private data contract for LKA database handles. It defines `struct lkdb`, which links an rwcdb handle into Venus's lookaside list and tracks metadata/statistics.

State: `lkdb` stores list linkage, open rwcdb handle, allocated database name, allocated database directory, entry count, attempts, hits, and SHA verification failures. `LKA_VERSION_STRING` is the descriptor prefix used by both `mklka` and runtime binding.

Dependencies and risks: depends on `rwcdb`, `dllist`, and public `lka.h`. The descriptor string is the format gate; changing it without migration rejects older databases. Ownership is manual and centralized in `delete_lkdb`. Tests should cover descriptor compatibility and stats behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/lka_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/mklka.c -->
# sources/distributed-fs/coda/coda-src/lka/mklka.c

Purpose: command-line builder for lookaside databases. It walks a tree, computes SHA-1 for each plain file, and inserts `sha -> path` records into a new rwcdb database with a descriptor record.

APIs and flow: `main` parses `-v` and `-r`, canonicalizes database and tree paths, computes relative prefixes when requested, initializes rwcdb, writes the descriptor through `SetDescriptor`, and calls `WalkTree`. `WalkTree` uses `fts_open`, skips non-regular files, computes SHA via `ComputeViceSHA`, and inserts either absolute or relative paths.

State/persistence: writes a persistent rwcdb file and reports progress through stdout. Globals carry options and entry counts. Risks include fragile relative-prefix mutation, `open(nextf->fts_name)` instead of full `fts_path` in non-current directories, and no duplicate-hash policy beyond rwcdb behavior. Test signals are verbose output, `testlka`, and runtime `LookAsideAndFillContainer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/mklka.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/shaprocs.c -->
# sources/distributed-fs/coda/coda-src/lka/shaprocs.c

Purpose: SHA helper implementation used by LKA creation, testing, and runtime verification. It converts SHA bytes to hex, copies files while hashing, and detects all-zero SHA values.

APIs and flow: `CopyAndComputeViceSHA` initializes SHA-1, reads 4096-byte chunks, updates the digest, optionally writes chunks to an output fd, and yields every 200 chunks through `LWP_DispatchProcess`. `ViceSHAtoHex` formats a 40-character hex digest if the destination is large enough. `IsZeroSHA` scans for nonzero bytes.

Dependencies and risks: depends on `coda_hash` SHA wrappers and LWP. Partial writes are treated as errors but not retried; read/write interruption handling is minimal. SHA-1 is the persistent lookup identity. Tests are indirect through `mklka` and `testlka`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/shaprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/testlka.c -->
# sources/distributed-fs/coda/coda-src/lka/testlka.c

Purpose: interactive harness for registering LKA databases and trying lookaside hits for user-entered files. It supplies a dummy `LWP_DispatchProcess` so SHA helpers can link outside Venus.

Flow: starts by passing the quoted command string to `LKParseAndExecute`, then loops prompting for filenames. For each file it computes SHA, creates a temporary container, calls `LookAsideAndFillContainer`, reports hit/miss/error text, and removes the temporary file.

Risks and test signals: useful for manual validation of database creation and lookup, but not an automated test. It uses `printf(em)` directly, which is a format-string risk if error text contains percent sequences. It does not compare copied container bytes itself, relying on LKA verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/lka/testlka.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/Makefile.am -->
# sources/distributed-fs/coda/coda-src/norton/Makefile.am

Purpose: automake recipe for the Norton server recovery tools. Under `BUILD_SERVER`, it builds `libnorton.la`, the interactive `norton` binary, the `norton-reinit` dump/load tool, and installs the `reinit` script/manpage.

Integration: `libnorton` contains setup, command, volume, vnode, directory, RVM heap, and recoverable-storage helpers. `norton` adds `norton.cc`, `norton.h`, and server dummy stubs; `norton-reinit` links reinit logic and the same stubs. Link dependencies span resolution, volume, volutil, version vectors, partition, ACL, directory, util, rwcdb, base, RVM/RPC2, readline, and termcap.

Risks/test signals: a visible missing line-continuation before one include path can affect generated Makefiles depending on automake parsing. Build coverage is the main signal; runtime tests require real Coda RVM state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/commands.cc -->
# sources/distributed-fs/coda/coda-src/norton/commands.cc

Purpose: defines the interactive Norton command tree and generic commands for help, memory examination, debug display/set, and unimplemented command stubs.

APIs and flow: command arrays wire parser tokens to handlers for delete/create/list/rename/show/set/examine. `InitParsing` initializes the prompt. `examine` validates an address/length, checks readable memory through platform-specific `address_ok`, then prints hex and ASCII lines. `set_debug`/`show_debug` manipulate global `norton_debug`.

Dependencies and risks: integrates with `parser.h`, platform VM APIs or `mprotect`, and handlers declared in `norton.h`. The Linux `address_ok` uses `mprotect`, which changes page protection and returns zero on success; the calling condition treats zero as failure, so behavior is platform-sensitive. `notyet` uses a fixed 80-byte buffer with repeated `strcat`. Test signal is interactive parser use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/commands.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/dummy.cc -->
# sources/distributed-fs/coda/coda-src/norton/dummy.cc

Purpose: supplies server-global symbols and aborting stubs needed to link Norton tools against libraries that normally expect a full file-server runtime.

APIs/state: defines `AllowResolution`, `DumpVM`, vnode cache sizing globals, `CodaSrvIp`, and `NullVV`. `PollAndYield`, `Die`, and `GetFsObj` assert if called, except `Die` prints first.

Dependencies and risks: depends on vnode/list types and Coda assertions. This intentionally narrows usable code paths: if linked libraries unexpectedly require server object lookup or polling, Norton aborts instead of pretending success. Tests should ensure normal Norton commands do not hit these stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/dummy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-dir.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-dir.cc

Purpose: implements Norton directory inspection and repair commands. It can list directory entries, delete a name from a directory, and create a name pointing at an existing child vnode.

APIs and flow: `SetDirHandle` resolves a directory vnode through volume index and directory cache. `show_dir` validates large vnode class, warns if `DH_DirOK` fails, and enumerates entries with existence markers from `testVnodeExists`. `delete_name` runs an RVM transaction, calls `DH_Delete`, optionally decrements parent link count, writes back the directory inode, marks the parent version vector inconsistent, and replaces the vnode. `create_name` similarly calls `DH_Create`, updates parent link count for directory children, adjusts child parent fields, and replaces both vnodes.

State/dependencies: mutates RVM vnode and directory-page state through vol/dir/recov APIs. Risks include operator-supplied FIDs, minimal semantic validation, link count drift, and destructive mutations on live metadata; `NortonInit` prevents server co-running. Test signal is manual Norton sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-dir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-print.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-print.cc

Purpose: legacy print helpers for version vectors and volume summaries. It overlaps with newer printing code in `norton-volume.cc`.

APIs: `PrintVV` formats raw version-vector fields, and `print_volume` prints ID, name, parent, group ID, partition, version vector, and small/large vnode list counts/pointers.

Dependencies and risks: includes older preprocessor syntax in `extern "C"` guards and uses fixed format assumptions for pointer-sized values. Because `norton-volume.cc` also defines `print_volume`, this file must not be linked into the same target unless duplicate definitions are intentionally avoided. Test signal is build/link success for any target that still references it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-print.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-rds.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-rds.cc

Purpose: minimal command wrapper for printing RDS/RVM heap information from Norton.

API and flow: declares external `print_heap()` and exposes `show_heap(int, char **)`, which ignores arguments and calls `print_heap`.

Dependencies and risks: depends on the RDS heap implementation providing `print_heap`. There is no input validation because none is needed. Test signal is the interactive `show heap` command successfully linking and printing heap state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-rds.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-recov.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-recov.cc

Purpose: provides thin accessors from Norton code to recoverable server volume storage.

APIs: `GetMaxVolId` masks `SRV_RVM(MaxVolId)` to 24 bits. `VolByIndex` bounds-checks an index against max ID and `MAXVOLS`, then returns `SRV_RVM(VolumeList[index])`. `VolHeaderByIndex` returns the embedded header for a valid volume.

State/dependencies: reads RVM-mapped globals initialized by `NortonInit`. Risks are stale/corrupt RVM data and reliance on magic checks by callers. Test signal is all volume/vnode commands that enumerate by index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-recov.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-reinit.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-reinit.cc

Purpose: dump and reload Coda server RVM state for destructive reinitialization. It serializes global volume ID state, volume headers, disk data, vnode records, directory pages, and resolution logs, then reconstructs them into a freshly initialized RVM heap.

APIs and flow: dump mode validates no unskipped backup volumes, writes global state, then iterates volumes and vnodes. Large vnodes include directory inode page counts/refcounts/pages and optional resolution logs. Load mode initializes partitions/server data, reads global state, creates volume headers, reads disk data and logs, attaches volumes, allocates vnodes, copies directory inodes into RVM, rebuilds resolution logs, restores original volume types, frees headers, and truncates the RVM log.

State/persistence: persistent artifact is a flat binary dump file with implicit structure and native in-memory layouts. It directly mutates RVM inside transactions. Risks are high: no portable format/versioning, many full-struct writes with pointers inside, skip logic depends on magic scanning, and load failures can leave partial RVM state. Test signal is successful dump/load under the `reinit` script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-reinit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-setup.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-setup.cc

Purpose: initializes enough of the Coda server runtime for Norton tools to inspect and mutate recoverable storage without starting the full server.

APIs and flow: `LoadRVM` verifies log/data devices, initializes per-thread rvmlib data, configures RVM options including optional private mapping, runs `RVM_INIT`, and loads the RDS heap. `InitLWP` initializes LWP and IOMGR. `NortonInitVolPackage` initializes server list, LRU, volume table, and vnode classes. `NortonInit` refuses to run while `/vice/srv/pid` exists, initializes LWP/RVM/directory cache, marks program type as salvager, and starts the volume package subset.

State/dependencies: sets globals `norton_debug`, `mapprivate`, and `camlibRecoverableSegment`. Depends on RVM/RDS, LWP, codadir, volume, partition, and parser infrastructure. Risks include hard-coded `/vice`, abrupt exits, and partial runtime initialization assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-setup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-vnode.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-vnode.cc

Purpose: implements vnode inspection and targeted vnode repair commands for Norton.

APIs and flow: `PrintVnodeDiskObject` prints vnode disk fields and version vectors. `show_vnode` either finds small vnodes by uniquifier or prints a specific vnode by volume/vnode/unique. `show_free` scans small/large RVM free lists for null, nonzero, and duplicate entries. `set_linkcount` wraps `setcount`, which starts an RVM transaction, extracts the vnode, changes `linkCount`, replaces the vnode, and commits.

State/dependencies: reads and mutates RVM vnode state through volume/index/recov APIs and resolution log printers. Risks include unsigned `count < 0` check being ineffective, no higher-level consistency checks when setting link counts, and free-list inspection relying on raw memory comparison. Test signal is manual `show vnode`, `show free`, and `set linkcount` usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-vnode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-volume.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton-volume.cc

Purpose: implements volume listing, lookup, display, delete marking, index lookup, detail printing, and rename commands for Norton.

APIs and flow: `GetVol` by ID/name and `GetVolIndex` scan `VolByIndex` up to `GetMaxVolId`/`MAXVOLS`, filtering by `VOLUMEHEADERMAGIC`. Display functions print header and `VolumeDiskData` fields. `delete_volume` sets `destroyMe` to `0xD3` in an RVM transaction. `rename_volume` writes a fixed-size zero-padded name in an RVM transaction. Parser wrappers choose ID vs name based on `Parser_uint`.

State/dependencies: depends on recoverable volume storage and `norton-recov.cc`. Mutations persist in RVM. Risks include destructive operator commands, no duplicate-name checks on rename, no transaction status handling beyond minimal reporting, and date formatting using `tm_year` directly. Test signal is interactive volume commands and reinit workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton-volume.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton.cc -->
# sources/distributed-fs/coda/coda-src/norton/norton.cc

Purpose: main entry point for the interactive Norton recovery shell.

Flow: parses optional `-mapprivate`, requires log device, data device, and length, initializes `/vice` directory handling, calls `NortonInit`, initializes command parsing, enters `Parser_commands`, then terminates RVM and reports its return status.

State/dependencies: sets global `mapprivate` and relies on `NortonInit` to refuse concurrent server use. Dependencies include parser, RVM, and Coda vice directory setup. Risks are minimal argument validation, hard-coded `/vice`, and high privilege/destructive potential once the shell starts. Test signal is startup against valid RVM devices and clean `rvm_terminate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton.h -->
# sources/distributed-fs/coda/coda-src/norton/norton.h

Purpose: shared declaration hub for Norton modules. It exposes global debug/mapping flags and all command/utility functions implemented across setup, commands, volume, vnode, recovery, directory, and RDS files.

Integration: keeps parser command files loosely coupled by declaring overloads for volume/vnode/directory functions and recoverable-storage accessors. It includes Coda volume/vnode/index/recov/camprivate headers so consumers share exact server types.

Risks: broad header coupling means small type changes in server internals ripple into all Norton files. Several declarations, such as `undelete_volume`, are present without implementation in this subset, so command availability and link targets must stay aligned. Test signal is full Norton build/link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/norton.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/reinit -->
# sources/distributed-fs/coda/coda-src/norton/reinit

Purpose: Bourne shell orchestration script for server RVM reinitialization using `norton-reinit`, `rvmutl`, and `rdsinit`.

Flow/state: prompts for confirmation, ensures backup volumes are purged or acknowledged, blocks server startup by writing `/vice/srv/pid`, gathers skip-volume and RVM geometry parameters, dumps state to a user-provided file, asks at point of no return, reinitializes the RVM log/data heap, reloads the dump, removes the pid blocker, and leaves dump cleanup to the operator.

Dependencies and risks: assumes `/vice`, `VolumeList`, optional `skipsalvage`, and required tools in `PATH`. It is intentionally interactive and destructive. Risks include manual input mistakes, pid-file based server exclusion, no shell quoting around many variables, and partial failure requiring manual cleanup. Test signal is full operator rehearsal in a disposable server environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/norton/reinit -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/Makefile.am -->
# sources/distributed-fs/coda/coda-src/partition/Makefile.am

Purpose: automake recipe for the server partition/inode abstraction library and `inoder` utility.

Integration: under `BUILD_SERVER`, builds `libpartition.la`, `inoder`, and the `vicetab.5` manpage. Library sources include vicetab parsing, partition registry, inode operation dispatch, simple/ftree/backup backends, and inode metadata headers. Include/link dependencies cover RPC2 flags, base/util, vicedep, and LWP.

Risks/test signals: build confirms backend method tables and headers stay compatible. The partition tests have their own `tests/Makefile.am`; this file does not install runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/backupifs.c -->
# sources/distributed-fs/coda/coda-src/partition/backupifs.c

Purpose: dummy partition backend for backup-system entries. It registers an `inodeops_backup` table with only `init` implemented; all inode methods are null.

Flow/state: `b_init` stats the configured partition directory and returns its device number, storing no private data. This lets backup partitions participate in the partition registry without supporting normal inode file operations.

Dependencies/risks: depends on `Partent` accessors, `partition.h`, and Coda assertions. Any caller that tries to invoke null inode methods on a backup partition will crash; type checks must happen before operation dispatch. Test signal is `DP_Init` accepting backup entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/backupifs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/ftreeifs.c -->
# sources/distributed-fs/coda/coda-src/partition/ftreeifs.c

Purpose: inode backend that maps synthetic inode numbers into a fixed-depth hex directory tree and stores inode metadata in a central `FTREEDB` resource file.

APIs and flow: `f_init` validates partition options (`depth`, `width`), opens `FTREEDB`, builds a free bitmap from nonzero header records, and records geometry. `f_inotostr` derives payload paths. `f_icreate` allocates a free bitmap slot, creates parent directories via `mkpath`, creates the payload file, writes the header to `FTREEDB`, and fsyncs it. `f_iinc`/`f_idec` update link counts through `f_change_lnk`, deleting payload and clearing bitmap at zero. Read/write/open operate on payload files; list scans headers and stats payload paths.

State/persistence: persistent state is payload file tree plus `FTREEDB`; in-memory state is open fd and free bitmap. Risks include bitmap not set on successful `f_icreate` in the visible code, option validation typo (`i != 10`), central fd seek races, and no locking despite a `Lock` field. Tests are partition test programs and server inode scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/ftreeifs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/ftreeifs.h -->
# sources/distributed-fs/coda/coda-src/partition/ftreeifs.h

Purpose: private option/state structure for the ftree partition backend.

State: defines `RESOURCEDB` as `FTREEDB` and `struct part_ftree_opts` with depth, width, computed logwidth, resource fd, next counter, free bitmap, and lock.

Dependencies/risks: depends on LWP locks and bit vectors. The structure is embedded in `union PartitionData`, so layout matters to `partition.h` and `ftreeifs.c`. The lock field is not meaningfully used in the implementation, which is a concurrency risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/ftreeifs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/inodeops.c -->
# sources/distributed-fs/coda/coda-src/partition/inodeops.c

Purpose: compatibility dispatch layer that exposes inode operations by `Device` number rather than requiring callers to hold a `DiskPartition *`.

APIs and flow: `icreate`, `iopen`, `iinc`, `idec`, `iread`, and `iwrite` call `DP_Find(devno)` and then dispatch through the partition's `inodeops` table. `get_header` and `put_header` dispatch directly from an already known `DiskPartition *`.

State/dependencies: depends on global `DiskPartitionList` populated by `DP_Init` and backend method tables. Risks include null method pointers for backup partitions, silent `0`/`-1` returns when a device is missing, and no validation of backend capabilities. Test signal is any partition test using legacy inode APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/inodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/inodeops.h -->
# sources/distributed-fs/coda/coda-src/partition/inodeops.h

Purpose: declares the legacy inode operation wrappers and direct header/list APIs for callers outside the partition backend implementation.

Important APIs: exports create/open/read/write/increment/decrement by device/inode, header get/put by `DiskPartition *`, and `ListCodaInodes` signature. It includes partition, vicetab, and inode metadata types.

Risks/integration: header couples callers to both legacy `Device` lookup and newer partition structures. The declared `ListCodaInodes` wrapper is not implemented in `inodeops.c` in this subset, so link usage must be checked. Test signal is build/link coverage and backend tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/inodeops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/inoder.c -->
# sources/distributed-fs/coda/coda-src/partition/inoder.c

Purpose: command-line utility for manual partition inode operations: create inode, read header, increment/decrement link count, and overwrite header metadata.

Flow: initializes partitions from a supplied vicetab and host name, finds a partition by directory, then dispatches based on command string. `icreate` takes volume/vnode/unique/version; `header` prints `i_header`; `iinc`/`idec` adjust link counts; `setheader` writes a new header using the backend magic.

Dependencies/risks: depends on `DP_Init`, `DP_Get`, legacy inode wrappers, and backend `magic`. It is operator-facing and can corrupt metadata if pointed at production partitions. Test signal is successful command-line operations on test vicetab/simple/ftree directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/inoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/partition.c -->
# sources/distributed-fs/coda/coda-src/partition/partition.c

Purpose: central partition registry for Coda server storage. It reads `vicetab`, initializes matching host partitions with the right backend, records them in `DiskPartitionList`, and exposes lookup/usage/lock helpers.

APIs and flow: `DP_Init` filters `Partent` records by hostname, resolves backend type, calls backend `init`, and inserts a `DiskPartition`. `DP_InitPartition` checks unique device numbers and sets usage. `DP_Find` and `DP_Get` search by device/name. `DP_SetUsage` uses `statvfs`/`statfs` to compute 1K free/usable/minfree values. `DP_ResetUsage` refreshes all partitions with LWP yields. Lock helpers are currently disabled.

State/dependencies: owns global list state and per-partition backend pointers/private data. Risks include assertions on config/runtime errors, questionable `DP_Get` behavior on empty lists, disabled locking, and free-space accounting being approximate. Test signal is vicetab-driven partition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/partition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/partition.h -->
# sources/distributed-fs/coda/coda-src/partition/partition.h

Purpose: public partition abstraction contract. It defines `DiskPartition`, backend private-data union, and the `inodeops` method table.

Important types/APIs: `DiskPartition` carries list linkage, mount/name/device/lock/free-space fields, backend operations, and private data. `inodeops` defines create/open/read/write/link/header/init/magic/list methods. Public functions initialize partitions, lock/unlock, find/get partitions, and report usage.

Integration/risks: includes backend headers, so the public abstraction knows both simple and ftree private types. Device numbers are persisted in RVM vnodes, making backend numbering stability important. Null method pointers are possible for backup partitions. Test signal is all server volume/inode code that compiles against this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/partition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/simpleifs.c -->
# sources/distributed-fs/coda/coda-src/partition/simpleifs.c

Purpose: simple userspace inode backend that stores each synthetic inode as a regular file named by inode number and a sidecar resource file named `.<inode>` containing `i_header`.

APIs and flow: `s_init` validates directory and stores device. `s_icreate` finds the next free numeric filename, creates the payload file, creates sidecar header with link count one and `VICEMAGIC`. `s_iopen`, `s_iread`, and `s_iwrite` operate on payload files. `s_iinc`/`s_idec` update header link count and delete payload/sidecar at final decrement. `s_list_coda_inodes` scans numeric directory entries and writes `ViceInodeInfo` records for valid headers.

State/persistence: persistent state is payload plus sidecar header files; in-memory state is only next inode hint. Risks include a bug in `set_link` comparing the pointer `count <= 0`, leaked file descriptors on lseek failure, no locking around inode allocation, and sidecar/header drift if creation fails mid-way. Tests are partition basic/create/delete/scan tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/simpleifs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/simpleifs.h -->
# sources/distributed-fs/coda/coda-src/partition/simpleifs.h

Purpose: constants and private state for the simple inode backend.

State/constants: defines filename/link limits, `FILEDATA`, `VICEMAGIC`, and `struct part_simple_opts` with the next-inode hint.

Dependencies/risks: included through `partition.h` and backend code. Constants are part of the sidecar header validation story; changing `VICEMAGIC` breaks existing partitions. `FNAMESIZE` is small relative to `MAXPATHLEN`, so long partition paths can overflow callers that format into this size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/simpleifs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/Makefile.am -->
# sources/distributed-fs/coda/coda-src/partition/tests/Makefile.am

Purpose: automake recipe for small partition backend test utilities.

Integration: builds `basic`, `setupvt`, `createmany`, `deletemany`, and `scaninodes`; distributes a sample `vicetab`; includes partition/util/vicedep/base paths; links against `libpartition`, `libutil`, and LWP.

Risks/test signals: these are command-line/manual tests rather than an automated harness. They are useful for exercising simple and ftree create/delete/list paths but may require directory setup and `makeftree` preparation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/basic.c -->
# sources/distributed-fs/coda/coda-src/partition/tests/basic.c

Purpose: basic manual smoke test for simple and ftree partition backends.

Flow: initializes partitions from local `vicetab`, gets `simpled`, creates an inode, opens it, writes a test string, prints ftree path names, then repeats create/open/write on `/tmp/f`.

Dependencies/risks: uses older API names (`InitPartitions`, `VGetPartition`) rather than current `DP_Init`/`DP_Get`, so it may reflect historical compatibility macros or bitrot. It requires test directories and ftree setup. Test signal is successful create/open/write across both backend types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/createmany.c -->
# sources/distributed-fs/coda/coda-src/partition/tests/createmany.c

Purpose: stress-style helper to create many synthetic inodes on a named test partition.

Flow: initializes local `vicetab`, expects directory and count arguments, finds the partition, then loops from 1 through count calling `icreate` with deterministic volume/vnode/unique/version values derived from the loop index.

Risks/test signals: useful for allocation/free-map behavior and scalability. It has unused variables and older include paths/API names. It exits on first failed `icreate` but does not verify headers or file contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/createmany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/deletemany.c -->
# sources/distributed-fs/coda/coda-src/partition/tests/deletemany.c

Purpose: companion helper to decrement/delete a range of synthetic inodes from a test partition.

Flow: initializes local `vicetab`, expects directory, first inode, and last inode. It finds the partition, loops through the inclusive range, calls `idec`, prints each result, and fails on the first nonzero return.

Risks/test signals: exercises link-count decrement and payload/header deletion paths after `createmany`. It returns an uninitialized `rc` on success and uses historical API names. No post-delete scan is performed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/deletemany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/scaninodes.c -->
# sources/distributed-fs/coda/coda-src/partition/tests/scaninodes.c

Purpose: manual test for backend `ListCodaInodes` support.

Flow: initializes local `vicetab`, expects a partition directory argument, gets the partition, and calls `dp->ops->ListCodaInodes(dp, "/tmp/inodeinfo", NULL, 0)`.

Risks/test signals: writes a fixed output path and has a bad usage print referencing `argv[1]` when `argc != 2`. It does not inspect the output file, but success/failure exercises backend scanning of resource headers and payload files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/scaninodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/setupvt.c -->
# sources/distributed-fs/coda/coda-src/partition/tests/setupvt.c

Purpose: creates a local test `vicetab` with one simple and one ftree partition entry.

Flow: gets host name, creates `Partent` records for `simpled` and `/tmp/f` with `width=8,depth=5`, recreates `vicetab`, appends both records, frees entries, and prints a reminder to run `makeftree` before continuing.

Risks/test signals: local destructive behavior is limited to unlinking/recreating `vicetab`. It assumes `/tmp/f` and `simpled` setup are handled externally. It validates `Partent_create/add/end` enough for test use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/tests/setupvt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/viceinode.h -->
# sources/distributed-fs/coda/coda-src/partition/viceinode.h

Purpose: defines inode metadata records shared by partition backends, inode scans, and volume/salvage code.

Important types: `i_header` is the backend resource-header format with link count, volume, vnode, unique, data version, and magic. `ViceInodeInfo` is the scan output record with inode number, byte count, link count, volume/vnode/unique/version, and magic. `INODESPECIAL` reserves an impossible vnode number.

State/integration: persisted by simple sidecar files and ftree `FTREEDB`; emitted by list operations. Risks include native struct layout/endian assumptions in persisted headers and scan files. Tests are backend create/header/list paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/viceinode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/vicetab.c -->
# sources/distributed-fs/coda/coda-src/partition/vicetab.c

Purpose: parser/writer for `/vice/vicetab` partition entries. It hides the `Partent` structure and exposes fstab-like operations.

APIs and flow: `Partent_set/end` open/close files; `Partent_get` skips comments/blanks and tokenizes host, dir, type, options; `Partent_create/add/free` allocate and append entries; accessors return host/type/dir; option helpers search comma/space-separated options and parse integers.

State/persistence: each file line persists one partition entry. `Partent_get` uses a static buffer and `strtok`, so it is not reentrant. Risks include substring option matches (`width` inside another token), fixed 256-byte fields, possible `strtok(NULL)` misuse in `Partent_intopt`, and no robust quoting for paths/options. Test signals come from `setupvt` and `DP_Init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/vicetab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/vicetab.h -->
# sources/distributed-fs/coda/coda-src/partition/vicetab.h

Purpose: public API and constants for Coda partition table parsing.

Contract: defines default path `/vice/vicetab`, max line/string length, supported partition type strings (`simple`, `ftree`), opaque `Partent`, file operations, constructor/destructor, add/get, option lookup, integer option parsing, and field accessors.

Integration/risks: consumed by partition initialization, tests, and backends. Because `Partent` is opaque, callers cannot accidentally depend on layout, but they do depend on simple whitespace tokenization semantics. Missing `backup` type constant despite backend support is a small documentation/API mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/partition/vicetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/Makefile.am -->
# sources/distributed-fs/coda/coda-src/repair/Makefile.am

Purpose: automake recipe for the client-side `repair` program.

Integration: when `BUILD_CLIENT` is enabled, builds `repair` from `repair.cc`/`repair.h`, installs `repair.1`, and includes base, kerndep, util, vicedep, partition, auth, vv, and librepair headers. Link dependencies include client repair libraries (`libclnrepair`, `librepio`), version vectors, auth, kerndep, base, readline, and termcap.

Risks/test signals: ties the `repair` CLI to the librepair outputs researched in this subset. Build/link coverage catches API drift between `repair`, `repio`, and resolve/auth/vv dependencies; behavioral tests require actual Coda conflict scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/Makefile.am -->
