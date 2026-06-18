# subset-b-007014 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mgrp.cc -->
# sources/distributed-fs/coda/coda-src/venus/mgrp.cc

## Purpose
This file implements Venus multicast group (`mgrpent`) behavior for replicated server sets. It creates and tears down RPC2 multicast groups, manages per-server RPC handles for a VSG, reconciles multi-RPC return codes, chooses dominant/primary hosts, and records which replicas accepted mutating operations. It is a core communication layer between higher-level replicated volume/file code and Vice servers.

## Important APIs, Types, and Functions
`Mgrp_Wait()` and `Mgrp_Signal()` coordinate waiters looking for available multicast groups. `RepOpCommCtxt::RepOpCommCtxt()` initializes active handles, hosts, retcodes, primary host, multicast info pointer, and dying flags; `AnyReturned()` scans live hosts for a return code. `mgrpent::CreateMember()`, `KillMember()`, `GetHostSet()`, and `PutHostSet()` synchronize the current RPC2 group membership with the VSG host set. `CheckResult()`, `CheckNonMutating()`, `CheckCOP1()`, and `CheckReintegrate()` translate Vice/RPC2 results and collapse per-replica outcomes into Venus-level codes such as `EASYRESOLVE`, `ESYNRESOLVE`, `ERETRY`, and `EALREADY`. `RVVCheck()`, `PickDH()`, `DHCheck()`, and `GetPrimaryHost()` enforce version-vector and dominant-host policy.

## Control Flow
Callers obtain an mgrp, then `GetHostSet()` creates missing RPC2 connections via `srvent::Connect()`, adds them to the RPC2 mgrp, removes stale members, and ensures a primary host exists. After a multi-RPC, callers use one of the `Check*` routines. Those first invoke `CheckResult()` to convert server-specific failures and kill timed-out/retry hosts, then attempt unanimity under increasingly broad masks for tolerated errors. Mutating COP1 operations additionally populate `UpdateSet` for replicas where the operation succeeded. Dominant-host selection is based on hosts with successful retcodes and valid remote version vectors, with bandwidth used as a tie-breaker.

## State and Persistence Behavior
The file manages transient RPC state only: `rocc` holds live RPC2 handles, host addresses, return codes, primary host, multicast pointer, and dying flags. It does not directly write RVM state, but its `UpdateSet` and resolution decisions determine whether replicated persistent volume state can be trusted, retried, or must be resolved. Destructor cleanup can notify servers with `ViceDisconnectFS`, remove active members, unbind handles, and delete the RPC2 multicast group.

## Dependencies and Integration Points
It depends on RPC2 multicast APIs, VSG/server abstractions (`vsgent`, `srvent`), Vice error codes, version-vector helpers (`InitVV`, `VV_Check`, `FPrintVV` via callers), mariner logging, and Venus private error conventions. `fsobj`, `repvol`, `reintvol`, `volent`, `ClientModifyLog`, and `cmlent` are friends because they need direct access to the replicated operation context for multi-server operations.

## Risks and Test Signals
High-risk areas are return-code masking, bitmask constants, member lifetime while mgrp references are active, primary-host invalidation, and translation of retry/authentication failures. Tests should exercise unanimous success/failure, partial timeouts, mixed maskable/non-maskable errors, `EINCOMPATIBLE` handling for normal COP1 versus reintegration, dominant-host version-vector disagreement, all-members-lost behavior, and cleanup of dying members after an mgrp is put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mgrp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mgrp.h -->
# sources/distributed-fs/coda/coda-src/venus/mgrp.h

## Purpose
This header declares the Venus multicast group abstraction and the per-operation replicated communication context. It exposes the small API used by replicated file/volume code to manage server membership, inspect return codes, choose primary/dominant hosts, and coordinate waiters for free mgrp objects.

## Important APIs, Types, and Functions
`RepOpCommCtxt` stores `HowMany`, per-VSG-member RPC2 handles, host addresses, return codes, the primary host, multicast info pointer, and pending-death flags. `mgrpent` privately inherits `RefCountedObject` and stores immutable VSG/user/authentication identity plus dynamic `rocc` state. Public methods include lifecycle (`Put`, `Kill`, `InUse`, `IsAuthenticated`), membership (`CreateMember`, `KillMember`, `GetHostSet`, `PutHostSet`), result collation (`CheckResult`, `CheckNonMutating`, `CheckCOP1`, `CheckReintegrate`), and host/version-vector selection (`RVVCheck`, `DHCheck`, `PickDH`, `GetPrimaryHost`).

## Control Flow
The header establishes a lifecycle where a `mgrpent` starts with a single reference, is linked into a VSG list, is used by friends for multi-RPCs, and is returned through `Put()`. `InUse()` treats detached entries as protected during initialization/destruction. `Mgrp_Wait()` and `Mgrp_Signal()` are declared for global coordination.

## State and Persistence Behavior
All fields are transient VM state. The header intentionally exposes `rocc` to friend classes because replicated operation state must be shared across call setup, RPC execution, and result reconciliation. Persistence effects occur indirectly through callers that use `UpdateSet` and return codes to decide whether replicated mutations reached stable storage.

## Dependencies and Integration Points
It includes RPC2, Coda inconsistency/version-vector definitions, dllist support, and `refcounted.h`. Integration is intentionally broad via friend declarations for filesystem objects, volumes, VSGs, modify logs, and CML entries.

## Risks and Test Signals
The main risks are friend-heavy coupling, raw arrays indexed by `VSG_MEMBERS`, and refcount/list invariants. Tests should verify that headers compile for all friend users, copied `RepOpCommCtxt` objects cannot be accidentally used, and `InUse()` protects both linked and detached lifecycle states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mgrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/nt_util.cc -->
# sources/distributed-fs/coda/coda-src/venus/nt_util.cc

## Purpose
This Cygwin-only file implements Windows/NT support routines for Venus pseudo-mount management and kernel-to-Venus IPC. When `__CYGWIN32__` is not defined, it compiles to no runtime behavior.

## Important APIs, Types, and Functions
`nt_mount()` and `nt_umount()` wrap `nt_do_mounts()` to mount or dismount a pseudo volume using Windows device-control calls. `nt_initialize_ipc()` opens the Coda kernel device, starts the `listen_kernel` thread, and records the socket used to pass kernel messages into the normal Venus path. `nt_msg_write()` sends responses back to the kernel through `CODA_FSCTL_ANSWER`. `nt_stop_ipc()` terminates and closes the monitor thread. The local `wcslen()` and static `DEV_BROADCAST_VOLUME` support pseudo-device link creation and broadcast device-change notifications.

## Control Flow
Mounting first dismounts any existing drive mapping, creates a DOS device alias for `\\Device\\codadev`, opens `\\\\.\\codadev`, fills `OW_PSEUDO_MOUNT_INFO`, and issues either mount or dismount FSCTLs. A successful mount/dismount broadcasts a Windows `WM_DEVICECHANGE` message. IPC initialization opens or attempts to start the Coda service, then launches `listen_kernel`, which repeatedly issues `CODA_FSCTL_FETCH`, writes message length and payload to the Venus socket, and exits only when `doexit` is set or the thread is terminated.

## State and Persistence Behavior
State is transient and process-local: static `drive`, `mount`, `sockfd`, `doexit`, `kerndev`, and `kernelmon`. The only persistent external effects are Windows device namespace changes, service startup attempts, and kernel-driver mount state. Fatal mount/setup failures kill Venus because the kernel bridge is required for this platform path.

## Dependencies and Integration Points
It depends on Windows APIs (`DefineDosDevice`, `CreateFile`, `DeviceIoControl`, `CreateThread`, `BroadcastSystemMessage`), OSR pseudo-mount control structures from `nt_util.h`, Coda kernel message sizes, and Venus logging/error helpers. It integrates with `venus.cc` shutdown through `nt_stop_ipc()`.

## Risks and Test Signals
Risks include hard-coded device names, static argument passing to a thread, unsafe `TerminateThread`, incomplete cleanup of DOS device aliases, and FSCTL constants noted as broken in the header. Tests should run mount/unmount cycles, device-change observation, kernel fetch/answer loops, missing service startup, and failure paths where `CreateFile` or FSCTL calls fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/nt_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/nt_util.h -->
# sources/distributed-fs/coda/coda-src/venus/nt_util.h

## Purpose
This header declares Cygwin/Windows-only pseudo-mount and kernel IPC support for Venus. On non-Cygwin builds it contributes no declarations.

## Important APIs, Types, and Functions
It defines pseudo filesystem control codes `OW_FSCTL_MOUNT_PSEUDO` and `OW_FSCTL_DISMOUNT_PSEUDO`, the `OW_PSEUDO_MOUNT_INFO` structure passed to the Windows filesystem device, and Coda-specific control codes `CODA_FSCTL_ANSWER`, `CODA_FSCTL_FETCH`, and `CODA_FSCTL_PIOCTL`. It declares `nt_mount`, `nt_umount`, `nt_initialize_ipc`, `nt_msg_write`, and `nt_stop_ipc`.

## Control Flow
The header has no runtime flow, but it defines the contract implemented by `nt_util.cc`: mount/dismount are drive-name calls, IPC initialization accepts a socket descriptor, message writes return byte counts on success, and shutdown stops the kernel monitor.

## State and Persistence Behavior
No state is declared here. Implementations use these declarations to mutate Windows kernel-device state and pseudo-drive mount state.

## Dependencies and Integration Points
It depends on Windows headers and `winioctl.h` for `CTL_CODE`. It integrates with Venus startup/shutdown only under the Cygwin build path.

## Risks and Test Signals
The header itself calls out mismatched/broken FSCTL definitions that must match the NT filesystem driver. Build tests should verify Cygwin-only inclusion, and integration tests should confirm the FSCTL numbers still match the installed Coda driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/nt_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/persistent.h -->
# sources/distributed-fs/coda/coda-src/venus/persistent.h

## Purpose
This file is a template, intentionally disabled by `#error`, for RVM-backed persistent reference-counted objects. It documents a pattern later open-coded by classes such as `Realm`: separate recoverable reference counts from transient VM reference counts and destroy an object only when both reach zero inside a transaction.

## Important APIs, Types, and Functions
`PersistentObject` defines RVM allocation/deallocation operators, constructor initialization of `rec_refcount` and `refcount`, `ResetTransient()`, `Rec_GetRef()`, `Rec_PutRef()`, `GetRef()`, and `PutRef()`. The persistent methods use `RVMLIB_REC_OBJECT` and transaction annotations, while transient methods can run outside transactions.

## Control Flow
Creation allocates from recoverable memory and starts with one transient reference. Recovery calls `ResetTransient()` to drop transient references after restart and potentially delete objects that have no persistent references. Persistent reference changes are transaction-protected. Transient `PutRef()` can delete only when already inside an RVM transaction, otherwise destruction is deferred.

## State and Persistence Behavior
`rec_refcount` is recoverable and must be logged before mutation; `refcount` is transient. This is exactly the kind of split needed when persistent objects can be referenced from both RVM data structures and active in-memory users. The file is not meant to be compiled because RVM inheritance and virtual functions are called out as problematic.

## Dependencies and Integration Points
It depends on `rvmlib`, `venusrecov.h`, and Coda assertions. Its integration role is architectural guidance rather than direct inclusion.

## Risks and Test Signals
The visible risks are misspelled annotation macros (`REQUIRES_TRANSACION`) and the explicit `#error`, both reinforcing that it is not production code. Any class copied from this template should be tested for transaction correctness, restart-time `ResetTransient()` cleanup, and delayed deletion outside transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/persistent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realm.cc -->
# sources/distributed-fs/coda/coda-src/venus/realm.cc

## Purpose
This file implements the persistent `Realm` abstraction: a Coda administrative namespace with a realm id, name, root volume name, cached root server addresses, and refcounts that bridge RVM state and transient runtime use. It also provides administrative server connection setup and root-server replacement.

## Important APIs, Types, and Functions
The constructor allocates recoverable strings for `name` and `rootvolname`, initializes the persistent list link, and sets a temporary recoverable reference while transient state is reset. The destructor removes the realm from the persistent list, drops root-server references, removes the realm mount entry from the local fake root, frees recoverable strings, and kills the fake mountlink object. `ResetTransient()`, `Rec_PutRef()`, `PutRef()`, `ReplaceRootServers()`, `GetAdmConn()`, `SetRootVolName()`, and `print()` are the main operations.

## Control Flow
During recovery, `ResetTransient()` clears cached root servers and transient refcount; if called inside a transaction with no recoverable references, it deletes the realm. `GetAdmConn()` resolves realm servers when unknown or stale, reorders cached addresses on retries, tries each IPv4 server as `ANYUSER_UID`, and on first successful discovery creates the realm mount entry under local `/coda` in a recovery transaction. `SetRootVolName()` replaces the recoverable string inside a transaction.

## State and Persistence Behavior
Persistent state includes `realmid`, `rec_refcount`, `name`, `rootvolname`, and list linkage. Transient state includes `refcount`, `generation`, and `rootservers`. `ReplaceRootServers()` pins `srvent` objects for new IPv4 roots and drops refs for old ones, then frees old RPC2 addrinfo. Realm deletion mutates persistent directory entries and frees RVM allocations.

## Dependencies and Integration Points
It integrates with `RealmDB`, `FSDB`, local fake volumes, RPC2 address info, server entries, connection entries, `parse_realms`, recovery transactions, and user token lookup methods declared in `realm.h` but implemented in `user.cc`.

## Risks and Test Signals
Risks include refcount imbalance between `GetRealm()`, token-held realm refs, and root-server refs; stale address retries; deletion while fake mount entries are in use; and transaction boundaries around recoverable string/list updates. Tests should cover unknown realm discovery, server re-resolution after `ERETRY`/timeouts, root volume name persistence, realm removal from fake root, and restart scanning with zero/nonzero persistent refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realm.h -->
# sources/distributed-fs/coda/coda-src/venus/realm.h

## Purpose
This header defines `Realm`, the persistent Venus representation of a Coda realm. It exposes identity, root-volume naming, root-server replacement, administrative connection acquisition, and user-token entry points.

## Important APIs, Types, and Functions
`Realm` overloads `new` and `delete` to use `rvmlib_rec_malloc/free`. It declares transaction-aware constructor/destructor, `ResetTransient`, recoverable and transient refcount methods, `Name`, `Id`, `SetRootVolName`, `GetRootVolName`, `ReplaceRootServers`, `GetAdmConn`, `GetUser`, `NewUserToken`, and `print`. Private fields distinguish persistent (`realmid`, `rec_refcount`, `name`, `rootvolname`, `realms`) from transient (`refcount`, `generation`, `rootservers`) state.

## Control Flow
The API assumes creation and persistent refcount updates occur inside recovery transactions, while server lookups and administrative connections do not. User and token helpers let `Realm` own per-realm user table lookup even though the concrete `userent` implementation is transient.

## State and Persistence Behavior
The header encodes the RVM allocation contract and makes persistence visible through transaction annotations. Root server addresses are intentionally transient and refreshed from realm discovery; the root volume name and realm identity survive restart.

## Dependencies and Integration Points
It depends on `rvmlib`, authentication token types, `venusfid.h`, and forward declarations for connection/user classes. `RealmDB` and `fsobj` are friends for persistent database management and fake mount construction.

## Risks and Test Signals
Risks are incorrect transaction usage around recoverable fields and accidental external dependence on transient `rootservers`. Compile-time annotation checks and recovery tests should verify all persistent mutations happen inside transactions and that realm lookups return referenced objects that callers eventually release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realmdb.cc -->
# sources/distributed-fs/coda/coda-src/venus/realmdb.cc

## Purpose
This file implements the recoverable realm database, including initialization, restart-time transient reset, realm lookup/creation, periodic cleanup, and local fake-realm identification.

## Important APIs, Types, and Functions
`LocalRealm` is initialized from the special `LOCALREALM`. `RealmDB::RealmDB()` records the database object and initializes its persistent list and `max_realmid`. `ResetTransient()` scans all realms, resets each transient state, recomputes `max_realmid`, and obtains `LocalRealm`. `GetRealm(const char *)` looks up by name or creates a new persistent `Realm`; `GetRealm(RealmId)` looks up by id. `GetDown()` deletes realms with no transient or recoverable refs by briefly taking and dropping a recoverable reference. `RealmDBInit()` creates or recovers `REALMDB` and starts a periodic cleanup daemon. `FID_IsLocalFake()` checks whether a fid belongs to the local fake realm.

## Control Flow
Startup calls `RealmDBInit()`. If metadata is being initialized, it allocates a new `RealmDB` in an RVM transaction; then `ResetTransient()` repairs runtime fields after either fresh init or recovery. Normal lookup by name creates new realms in a transaction and adds them to the persistent list. Cleanup is scheduled with `FireAndForget` and runs outside transactions, opening a transaction only around possible deletion.

## State and Persistence Behavior
`REALMDB` is a persistent root under `RecovVenusGlobals`. The realm list and `max_realmid` are recoverable. `LocalRealm` is a transient global reference acquired during reset. Newly created realm ids increment `max_realmid` and persist with the new realm.

## Dependencies and Integration Points
It depends on `fso.h` for fake object interactions, `rec_dllist.h` for recoverable lists, and `venusrecov` globals through `REALMDB`. It is called by Venus startup after recovery and before volume/filesystem initialization can rely on realm ids.

## Risks and Test Signals
Risks include deleting a realm while hidden references still exist, name normalization limited to empty/null-to-`UNKNOWN`, and persistent id monotonicity after recovery. Tests should cover fresh init, dirty restart, repeated name lookup, id lookup miss, cleanup of unreferenced realms, and local fake fid detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realmdb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realmdb.h -->
# sources/distributed-fs/coda/coda-src/venus/realmdb.h

## Purpose
This header declares the persistent realm database and the special local realm used for fake/local volumes.

## Important APIs, Types, and Functions
`LOCALREALM` is `"localhost"`, `LocalRealm` is the transient pointer to that realm, and `REALMDB` maps to `rvg->recov_REALMDB`. `RealmDB` has RVM allocation operators, constructor/destructor, `ResetTransient`, name/id `GetRealm` overloads, `GetDown`, and print helpers. Private fields are the persistent realm list and `max_realmid`.

## Control Flow
The API is built around startup initialization via `RealmDBInit()`, followed by lookup/creation during realm discovery and periodic cleanup through `GetDown()`.

## State and Persistence Behavior
The class is recoverable and owned by the recovery globals. Its list links must be mutated with recoverable list helpers, and `max_realmid` is persistent so newly created realm ids do not collide after restart.

## Dependencies and Integration Points
It depends on `rvmlib`, `realm.h`, and recovery globals from `venusrecov.h` through the `REALMDB` macro. `fsobj` is a friend for fake realm object construction.

## Risks and Test Signals
Tests should validate that `RealmDB` is never destructed during normal shutdown, that fresh metadata init creates the persistent root, and that all callers can include the header without pulling in implementation-only dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/realmdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/rec_dllist.h -->
# sources/distributed-fs/coda/coda-src/venus/rec_dllist.h

## Purpose
This header provides small wrappers around intrusive doubly-linked list operations so list mutations are logged in RVM before they change recoverable memory.

## Important APIs, Types, and Functions
`rec_list_head_init()` records the list head and initializes it. `rec_list_add()` records the new node, the old first node, and the back-link before calling `list_add()`. `rec_list_del()` records the node and, when linked, the adjacent list links before calling `list_del()`.

## Control Flow
Each helper must be called inside a transaction. The control flow is deliberately one-level: mark affected recoverable ranges, then delegate to normal dllist primitives.

## State and Persistence Behavior
These functions directly protect persistent list consistency. Missing any adjacent pointer in the recorded range could corrupt recoverable lists across a crash.

## Dependencies and Integration Points
It depends on `dllist.h` and `rvmlib.h`. It is used by persistent structures such as `Realm`/`RealmDB` to maintain RVM-backed intrusive lists.

## Risks and Test Signals
Risks are incomplete logging of pointer fields and using non-recoverable list helpers on persistent lists. Crash-recovery tests should add/delete nodes inside transactions and verify list integrity after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/rec_dllist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/refcounted.h -->
# sources/distributed-fs/coda/coda-src/venus/refcounted.h

## Purpose
This header defines a lightweight transient reference-counted base class for VM-only objects that should delete themselves when the last reference is released.

## Important APIs, Types, and Functions
`RefCountedObject` stores protected `refcount`, initializes it to one, asserts the destructor is reached only with `refcount <= 1`, and exposes `GetRef()`, `PutRef()`, and `PrintRef()`. `PutRef()` asserts a positive count, decrements, and `delete`s `this` at zero. A `TESTING` block defines a simple `RefObj` exerciser.

## Control Flow
Objects start with an implicit reference. Callers increment before sharing and call `PutRef()` when done. Deletion is synchronous on the final put.

## State and Persistence Behavior
The class is entirely transient and not thread-safe by itself. It should not be used for RVM-persistent objects because deletion and refcount changes are not transaction logged.

## Dependencies and Integration Points
It depends only on C stdio/assert headers. `mgrpent` privately inherits it, and other VM-only Venus objects can use the same pattern.

## Risks and Test Signals
Risks include non-atomic refcounting, deletion through base pointer expectations, accidental direct `delete` while references exist, and cyclic references. Unit tests should verify final-put deletion and assert behavior for over-release in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/refcounted.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/sighand.cc -->
# sources/distributed-fs/coda/coda-src/venus/sighand.cc

## Purpose
This file implements Venus signal setup and signal-triggered control actions: clean termination, control-file command processing, log/stat toggles, fatal-signal zombie state, mount completion notification, and ASR child cleanup.

## Important APIs, Types, and Functions
`SigInit()` installs handlers and moves Venus into its own process group. `SigControl()` reads `VenusControlFile` on `SIGHUP` and handles `DEBUG`, `SWAPLOGS`, `STATSINIT`, and `STATS` commands. `SigChoke()` records fatal signals, notifies mariner, closes worker mux state, and suspends with only termination signals unblocked. `SigExit()` sets `TerminateVenus`, flushes and terminates recovery, unmounts, and exits. `SigMounted()` calls `gogogo(parent_fd)` for daemonization synchronization. `SigASR()` handles `SIGCHLD` for ASR launcher completion and unlocks the associated replicated volume.

## Control Flow
Startup calls `SigInit()` after logging/daemon infrastructure is ready. The main loop checks `TerminateVenus`, but `SigExit()` also performs immediate cleanup and exits from the handler. `SIGHUP` either swaps logs when no control file exists or executes the single command in the control file and unlinks it. Fatal signals enter a suspended zombie state for debugger attachment, then exit when interrupted or terminated. ASR child completion uses global `ASRpid`, `ASRfid`, and `VDB`.

## State and Persistence Behavior
Global state includes `TerminateVenus` and `mount_done`. Signal paths call recovery flushing/termination and VFS unmount, which affect persistent clean-shutdown markers. ASR cleanup mutates volume ASR state by clearing process group and unlocking.

## Dependencies and Integration Points
It integrates with recovery (`RecovFlush`, `RecovTerminate`), volume database, worker mux handling, daemonizer parent notification, Venus logging/stat functions, mariner, and ASR globals from `venus.private.h`.

## Risks and Test Signals
Many handler paths are not async-signal-safe because they use stdio, allocation-adjacent helpers, and complex subsystem calls. Tests should focus on integration behavior: `SIGHUP` control commands, SIGTERM clean shutdown marker, fatal signal debug state, ASR child unlock, and daemonization mount-complete notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/sighand.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/sighand.h -->
# sources/distributed-fs/coda/coda-src/venus/sighand.h

## Purpose
This header declares the Venus signal handler initialization API and the small set of signal-related globals shared with the main process loop.

## Important APIs, Types, and Functions
It declares `SigInit()`, `TerminateVenus`, and `mount_done`. `TerminateVenus` is the shutdown flag checked by `venus.cc`; `mount_done` is exposed for mount signaling paths.

## Control Flow
Callers invoke `SigInit()` once during startup after logging support is available. Signal handlers then update globals or perform direct cleanup.

## State and Persistence Behavior
No persistent state is declared here. The globals are transient process flags, though handlers that use them may trigger persistent recovery cleanup.

## Dependencies and Integration Points
The header intentionally has no heavy includes. It is included by Venus startup code and any module needing shutdown status.

## Risks and Test Signals
Risk is limited to global-state coupling. Compile tests should confirm all users include the header cleanly, and runtime tests should confirm `TerminateVenus` ends the main loop when termination is routed through the non-immediate path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/sighand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/spool.cc -->
# sources/distributed-fs/coda/coda-src/venus/spool.cc

## Purpose
This file ensures Venus checkpoint/spool directories exist with expected ownership and permissions, including per-user spool subdirectories.

## Important APIs, Types, and Functions
`ValidateDir()` checks whether a path exists and is a directory, removes non-directory entries, creates the directory if needed, and fixes owner/group/mode. `MakeUserSpoolDir()` validates the global `SpoolDir`, constructs `SpoolDir/<uid>` into the caller-provided buffer, and validates the per-user directory.

## Control Flow
Callers pass a writable path buffer and owner uid. The function first guarantees the parent spool directory is owned by Venus (`V_UID`) and group `V_GID` with mode `0755`, then creates/fixes the user's private directory with owner uid and mode `0700`.

## State and Persistence Behavior
This file mutates the host filesystem, not RVM. It creates directories, unlinks non-directory collisions, changes ownership, and changes modes. These directories are used for CML checkpoints/snapshots configured by `SpoolDir`.

## Dependencies and Integration Points
It depends on POSIX `stat`, `mkdir`, `unlink`, `chown`, `chmod`, Venus uid/gid constants, and the `SpoolDir` configuration exported from `venus.private.h`.

## Risks and Test Signals
Risks include unsafe `sprintf()` into the caller buffer, unlinking a non-directory path without additional safety checks, ignored errors from `chown/chmod/stat`, and behavior under privilege restrictions. Tests should cover missing parent, file collision, wrong owner/mode repair, long spool paths, and unprivileged failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/spool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/tallyent.cc -->
# sources/distributed-fs/coda/coda-src/venus/tallyent.cc

## Purpose
This file implements a priority/user tally list used to accumulate available, unavailable, and unknown cache/task quantities. It groups counts by `(priority, uid)` in sorted order.

## Important APIs, Types, and Functions
`TallyList` is the global sorted `dlist`. `tallyent` stores priority, uid, available/unavailable block and file counts, and an incomplete flag. `tallyentPriorityFN()` orders entries by priority then uid. `InitTally()` resets the list and deletes existing entries. `Find()` locates an entry. `Tally()` creates or updates an entry for a status. `TallyPrint()` logs per-uid entries, and `TallySum()` aggregates total blocks/files across the list.

## Control Flow
Callers must initialize `TallyList` with `InitTally()`. Each `Tally()` call finds an existing `(priority, uid)` entry or inserts a new one, then increments counts depending on `TSavailable`, `TSunavailable`, or `TSunknown`. Deleting a `tallyent` removes its dlist link. The `TESTING` block provides a standalone exerciser.

## State and Persistence Behavior
All state is transient. The tally does not write RVM or filesystem state; it summarizes availability information for later reporting or notification. `TSunknown` preserves incomplete state without adding block/file counts.

## Dependencies and Integration Points
It depends on `dlist`, Coda assertions, `vcrcommon`, and Venus logging when not under `TESTING`. The header exposes `NotifyUsersTaskAvailability()` as a friend, indicating task availability notification code reads private fields.

## Risks and Test Signals
Risks include global mutable state, no synchronization, mandatory initialization, destructor assertions when `TallyList` is null, and a likely logging typo in `TallySum()` where pointer values are printed for total size/unknown fields. Tests should cover sorted insertion, repeated updates, unknown status, list reset deletion, sum accuracy, and per-uid print filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/tallyent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/tallyent.h -->
# sources/distributed-fs/coda/coda-src/venus/tallyent.h

## Purpose
This header declares the tally entry structure and tally-list API for summarizing available/unavailable work or cache quantities by priority and user.

## Important APIs, Types, and Functions
`TallyStatus` has `TSavailable`, `TSunavailable`, and `TSunknown`. `tallyent` stores a dlist link, priority, uid, available/unavailable block/file counts, and an incomplete flag. It declares `InitTally`, `Find`, `Tally`, `TallyPrint`, `TallySum`, and global `TallyList`.

## Control Flow
The intended lifecycle is initialize the global list, feed entries with `Tally()`, optionally print or sum, then reset by calling `InitTally()` again.

## State and Persistence Behavior
The declared state is transient and process-local. Counts are derived summaries and do not persist across Venus restarts.

## Dependencies and Integration Points
It depends on `dlist.h`. Friend declarations show integration with tally functions and user task notification code that inspects private counters.

## Risks and Test Signals
Risks are the exposed global pointer and private-data friend coupling. Tests should compile all consumers, verify initialization before use, and validate that `TallySum()` and `TallyPrint()` remain consistent with field semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/tallyent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/user.cc -->
# sources/distributed-fs/coda/coda-src/venus/user.cc

## Purpose
This file implements transient Venus user entries, token management, authorization checks, per-user connection reset, server binding, and the periodic token-expiry warning daemon.

## Important APIs, Types, and Functions
`UserInit()` creates the global `userent::usertab` and starts `USERD`. `Realm::GetUser()` and `Realm::NewUserToken()` allocate/find per-realm user entries and install tokens. `AuthorizedUser()` and `ConsoleUser()` decide whether a uid can perform privileged local operations. `userent` methods include `SetTokens`, `GetTokens`, `TokensValid`, `CheckTokenExpiry`, `Invalidate`, `Reset`, `CheckFetchPartialSupport`, `Connect`, `GetWaitForever`, `SetWaitForever`, and print helpers. `user_iterator` wraps the global olist. `UserDaemon()` periodically scans users for token expiry warnings.

## Control Flow
Token installation copies secret/clear tokens, pins the realm while tokens are valid, resets cached user state, and marks dirty owned replicated volumes for reintegration. Invalidation drops the token-held realm reference, clears token memory, notifies the user, and resets kernel/HDB/connection/mgrp state. `Connect()` either creates an RPC2 multicast group for `INADDR_ANY` or binds to a specific server; it chooses authenticated or unauthenticated security based on requested auth and token validity, calls `ViceNewConnectFS`, then probes `ViceFetchPartial` support with retries.

## State and Persistence Behavior
User entries are transient and kept in `usertab`; tokens are stored in memory and zeroed on invalidation. Token validity holds a transient realm reference, but does not directly persist. Resetting a user purges kernel data, demotes HDB bindings, suicides connections for the uid, and kills user mgrp entries, which invalidates runtime access state across Venus subsystems.

## Dependencies and Integration Points
It depends on RPC2, Vice/auth protocols, LKA, Coda service lookup, server/connection/mgrp databases, HDB, kernel purge helpers, worker retry signaling, replicated volume iteration, and mariner/RPC statistics macros. Platform-specific console-user logic depends on utmp/passwd or defaults to allowed on Cygwin/FreeBSD.

## Risks and Test Signals
Risks include token/realm refcount imbalance, platform-dependent console authorization, using expired tokens until servers reject them, partial-fetch probing side effects, fixed-size username buffer, and retry/unbind correctness on connection failure. Tests should cover token set/get/invalidate, authenticated and unauthenticated binds, `RPC2_NOTAUTHENTICATED` invalidation, fetch-partial unsupported/supported/error paths, wait-forever retry signaling, and user reset cleanup across connections and mgrps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/user.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/user.h -->
# sources/distributed-fs/coda/coda-src/venus/user.h

## Purpose
This header declares Venus user entries, token operations, authorization helpers, and the user daemon interface.

## Important APIs, Types, and Functions
`userent` stores its list handle, realm id, uid, token validity/warning state, secret and clear tokens, wait-forever flag, and demand-hoard timestamp. Public methods cover token set/get/validity/expiry, invalidation/reset, server connection, fetch-partial support probing, wait-forever state, uid access, and printing. `user_iterator` iterates over the static user table. Free functions include `UserInit`, `PutUser`, `UserPrint`, `AuthorizedUser`, `ConsoleUser`, `USERD_Init`, and `UserDaemon`.

## Control Flow
The header makes `Realm` responsible for constructing users and setting tokens while other modules interact through public methods and iterators. `PutUser()` currently has no reference-counting behavior, so returned user pointers are effectively table-owned.

## State and Persistence Behavior
All fields are transient. Tokens are process memory only, while their presence can hold runtime references to persistent realms and invalidate caches when changed.

## Dependencies and Integration Points
It depends on RPC2, auth token definitions, `olist`, communication/server declarations, and Venus private constants. Friends include FSDB and Realm so they can allocate and inspect user entries.

## Risks and Test Signals
Risks include table-owned lifetime without real `PutUser()`, broad friend access, and direct token storage. Tests should verify iteration safety, connection method declarations under transaction annotations, and no accidental copying because copy/assignment abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venus.cc -->
# sources/distributed-fs/coda/coda-src/venus/venus.cc

## Purpose
This file is the Venus process entry point and startup orchestrator. It parses command-line/configuration values, sets defaults, daemonizes, initializes every major subsystem in a strict order, mounts the Coda filesystem when enabled, runs the main select/daemon dispatch loop, and performs orderly shutdown.

## Important APIs, Types, and Functions
Important exported globals include root fid/node id, cache/log/spool/config paths, cache sizes, primary user, mariner settings, ASR state, codatunnel flags, and zone limits. `MUX_add_callback()` lets modules add/remove fd callbacks to the main select loop; `_MUX_FD_SET()` and `_MUX_Dispatch()` service them. `ParseSizeWithUnits()`, `power_of_2()`, and `ParseCacheChunkBlockSize()` parse size options. `main()` performs process startup. `ParseCmdline()`, `DefaultCmdlineParms()`, `CalculateCacheFiles()`, `CdToCacheDir()`, `CheckInitFile()`, `UnsetInitFile()`, and `SetRlimits()` handle configuration and environment setup.

## Control Flow
Startup parses command line first, then `venus.conf`, daemonizes if configured, writes pid/control paths, moves into the cache directory, handles INIT metadata wiping, raises data rlimits, tests the kernel device, optionally starts codatunnel, then initializes LWP/vproc, logging, daemon registry, stats, signals, directory storage, recovery, communication, users, VSGs, realms, volumes, FS objects, HDB, mariner, workers, and callbacks. The main loop builds an fd set from registered callbacks, waits through `VprocSelect()` with daemon expiry, dispatches ready callbacks, checks `TerminateVenus`, and fires ready daemons.

## State and Persistence Behavior
Most globals are process configuration. Persistent behavior is driven by `InitMetaData`, `InitNewInstance`, RVM path/size options, cache directory `INIT` file handling, and recovery initialization. `CdToCacheDir()` creates `CACHEDIR.TAG`; `CheckInitFile()` translates the presence of `INIT` into metadata reinitialization; `UnsetInitFile()` removes the marker after successful startup. Shutdown flushes/terminates recovery and unmounts the VFS.

## Dependencies and Integration Points
It integrates every Venus subsystem: recovery, communication, users, VSGDB, RealmDB, volume DB, FSDB, HDB, mariner, kernel worker, callbacks, signal handlers, daemonizer, codatunnel, codaconf, and optional Cygwin IPC. Initialization order is explicitly documented as important, especially `RecovInit < VSGInit < VolInit < FSOInit < HDB_Init`.

## Risks and Test Signals
Risks include initialization-order regressions, config/command-line precedence bugs, size parsing overflow/truncation, invalid cache chunk block sizes, fd-callback removal callbacks, daemonization synchronization, and shutdown paths called both from main loop and signal handlers. Tests should cover config defaults, command-line overrides, INIT file semantics, no-codafs/nofork modes, codatunnel toggles, callback add/update/remove, and startup failure for invalid cache/RVM sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venus.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venus.private.h -->
# sources/distributed-fs/coda/coda-src/venus/venus.private.h

## Purpose
This private umbrella header defines Venus-wide constants, error codes, uid/gid/mode defaults, lock/timing/logging macros, utility declarations for source files without dedicated headers, and exported globals shared by many Venus modules.

## Important APIs, Types, and Functions
It defines replica-control rights, internal errors (`ESYNRESOLVE`, `EASYRESOLVE`, `ERETRY`, `EASRSTARTED`), default paths and minimum cache dimensions, special uids/gids, fid lookup flags, logging/timing macros, lock-level helpers, cache event/stat structures, string case macros, `CHOKE`, and `MRPC_common_params`. It declares many functions implemented in `venusutil.cc`, daemon helpers, `MUX_add_callback`, and globals from `venus.cc`, recovery, stats, and ASR state.

## Control Flow
The header has no runtime flow, but its macros shape control flow throughout Venus: `LOG` compiles away without `VENUSDEBUG`, `ObtainLock`/`ReleaseLock` dispatch by enum, `START_TIMING`/`END_TIMING` either measure or stub elapsed time, and `CHOKE` captures file/line for fatal handling.

## State and Persistence Behavior
It declares both transient process globals and structures that feed persistent behavior, such as `NullFid`, `NullVV`, `VFSStats`, `RPCOpStats`, cache sizing, ASR globals, and recovery-related configuration. It also defines `MRPC_common_params` used to pass multicast operation state.

## Dependencies and Integration Points
This is one of the broadest integration headers in Venus, depending on RPC2, util, Vice, version-vector definitions, stats, fid definitions, and Coda assertions. It is used by nearly every implementation file in this work item.

## Risks and Test Signals
Risks include namespace pollution, macro side effects, constants that must match kernel/protocol expectations, and declarations for functions without type-safe dedicated headers. Build tests across platforms and with/without `VENUSDEBUG`/`TIMING` are essential, as are protocol tests for error-code interpretation and cache-size boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venus.private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venuscb.cc -->
# sources/distributed-fs/coda/coda-src/venus/venuscb.cc

## Purpose
This file implements the Venus callback server subsystem. It exports the callback RPC2 subsystem, starts callback server vprocs, receives callback requests from servers, breaks file/volume callbacks, supports server backfetch of reintegration shadow data, and records callback connection ids.

## Important APIs, Types, and Functions
`CallBackInit()` sets `MaxCBServers`, exports `SUBSYS_CB`, and creates `callbackserver` instances. `callbackserver::main()` loops on `RPC2_GetRequest()`, validates callback connection state, handles bad clients, and dispatches generated callback RPC stubs through `cb_ExecuteRequest()`. `VENUS_CallBack()` handles callback breaks/probes. `VENUS_CallBackFetch()` transfers a shadow file to a server through SMARTFTP. `VENUS_CallBackConnect()` handles new callback connections and marks the server up. Globals include `MaxCBServers` and `cbbreaks`.

## Control Flow
Callback servers block waiting for RPC2 requests. RPC2 connection errors reset the associated server or unbind unknown handles. Normal callback packets are executed by generated callback dispatch. A break callback maps Vice fid plus server realm id to `VenusFid`, logs to mariner, ignores volume-zero probes, breaks FSDB file callbacks and VDB volume callbacks, and increments `cbbreaks` when a file break cannot find the fid. Backfetch finds the fsobj, ensures a shadow exists, verifies file/full-data state, opens the shadow container, initializes/checks SMARTFTP side effect transfer, and accounts transferred bytes on read-write volumes.

## State and Persistence Behavior
The subsystem is transient but invalidates cached persistent filesystem state by breaking callbacks. `VENUS_CallBackFetch()` may create a missing shadow in a recovery transaction, then streams shadow file contents. Callback connection setup updates `srvent` runtime state via `ServerUp()`.

## Dependencies and Integration Points
It depends on RPC2 callback stubs, side-effect transfer, server database lookup by callback cid, FSDB/VDB callback-break methods, fsobj shadow/container APIs, reint volume accounting, mariner logging, and worker/vproc infrastructure.

## Risks and Test Signals
Risks include unauthenticated callback TODOs, unknown callback cid handling, callback break races around newly created files, shadow-file assumptions, SMARTFTP error translation, and server reset/unbind correctness. Tests should cover probe callbacks, file and volume callback breaks, unknown cid replies, backfetch success/failure/no-shadow cases, and callback new-connection updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venuscb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venuscb.h -->
# sources/distributed-fs/coda/coda-src/venus/venuscb.h

## Purpose
This header declares the Venus callback server vproc class and callback subsystem initialization globals.

## Important APIs, Types, and Functions
It defines `DFLT_MAXCBSERVERS` and `UNSET_MAXCBSERVERS`, declares `callbackserver : public vproc` with RPC2 request filter, handle, and packet fields, and exposes `MaxCBServers`, `cbbreaks`, and `CallBackInit()`.

## Control Flow
`CallBackInit()` is the external entry point. The private constructor starts callback server threads, and `main()` is overridden to service callback RPCs.

## State and Persistence Behavior
Declared state is transient callback server configuration and callback-break count. Persistent cache correctness is affected indirectly through callback breaks implemented in the `.cc` file.

## Dependencies and Integration Points
It depends on RPC2 and `vproc.h`. It is included by Venus startup and callback implementation code.

## Risks and Test Signals
Risks are configuration bounds and lifetime of packet buffers/handles. Build tests should verify generated callback stubs can link against the implementation and that configured `MaxCBServers` creates the expected number of vprocs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venuscb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusfid.h -->
# sources/distributed-fs/coda/coda-src/venus/venusfid.h

## Purpose
This header defines Venus-level fids, which extend Vice fids with a realm id, plus helper conversions among kernel fids, Vice fids, volume ids, and printable fid strings.

## Important APIs, Types, and Functions
`VenusFid` contains `Realm`, `Volume`, `Vnode`, and `Unique`; `Volid` contains `Realm` and `Volume`. Helpers include `VenusToKernelFid`, `KernelToVenusFid`, `MakeViceFid`, `MakeVolid`, `FID_EQ`, `FID_VolEQ`, `FID_IsVolRoot`, `FID_`, and `MakeVenusFid`. It defines `FakeRootVolumeId`, `FakeRepairVolumeId`, declares `FID_IsLocalFake`, and provides `FID_IsExpandedDir()` overloads.

## Control Flow
Most helpers are reinterpretation or inline field comparisons. `FID_()` alternates between two static buffers so two fid strings can appear in one expression. Fake/expanded directory helpers combine local fake realm checks with Vice fake-root tests.

## State and Persistence Behavior
Fids are value identifiers that are stored throughout persistent and transient Venus data structures. The helper casts rely on field layout: `Volume,Vnode,Unique` must match `ViceFid`, and the full struct must match `CodaFid` for kernel exchange.

## Dependencies and Integration Points
It depends on `codadir.h` for fid/realm/volume types and fake-root helpers. It integrates with kernel IPC, Vice RPC arguments, realm-aware FSDB/VDB lookups, callback conversion, and local fake volumes.

## Risks and Test Signals
Risks include strict layout assumptions, static buffer reuse in `FID_()`, and type-punning aliasing. Tests should assert struct sizes/field offsets against kernel/Vice definitions, check conversion round trips, and cover fake root/repair fids across local and non-local realms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusfid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusrecov.cc -->
# sources/distributed-fs/coda/coda-src/venus/venusrecov.cc

## Purpose
This file implements Venus recoverable storage management over RVM/RDS or VM mode. It validates and initializes persistent globals, creates/loads RVM log and data segments, manages transaction boundaries and no-flush persistence bounds, flushes/truncates logs, records clean shutdown, copies recoverable strings, starts the recovery daemon, and generates store ids for mutating operations.

## Important APIs, Types, and Functions
Globals include `RecovInited`, `rvg`, transaction counters, `MapPrivate`, initialization flags, RVM path/size/config parameters, and flush/truncate thresholds. `RecovVenusGlobals::validate/print` check persistent root integrity. `RecovInit()` drives VM or RVM initialization. Private helpers include `Recov_CheckParms`, `Recov_InitRVM`, `Recov_InitRDS`, `Recov_LoadRDS`, and `Recov_GetStatistics`. Public operations include `_Recov_BeginTrans`, `Recov_EndTrans`, `Recov_SetBound`, `RecovFlush`, `RecovTruncate`, `RecovTerminate`, `RecovPrint`, `Copy_RPC2_String`, `Free_RPC2_String`, `RECOVD_Init`, `RecovDaemon`, and `Recov_GenerateStoreId`.

## Control Flow
Startup calls `RecovInit()`, which fills defaults, handles VM mode as fresh in-memory metadata, or initializes RVM/RDS and loads the data segment. Fresh metadata zeroes and initializes `RecovVenusGlobals`; existing metadata validates heap bounds, magic/version, persistent roots, clean-shutdown state, and resets `recov_CleanShutDown` to dirty. Store identity is regenerated on init/new-instance or when replay-detection mode changes. The recovery daemon wakes every five seconds, observes worker idle time and RVM statistics, then truncates or flushes when thresholds are met.

## State and Persistence Behavior
Persistent root state lives in `RecovVenusGlobals`: magic/version, last init, clean shutdown, FSDB/VDB/REALMDB/HDB roots, heap bounds, UUID, and store id. Transactions are begun with `no_restore` and ended with `no_flush`; `Recov_SetBound()` bounds how long committed no-flush data may remain unflushed. `RecovTerminate()` writes a clean-shutdown marker only when there are no uncommitted transactions.

## Dependencies and Integration Points
It depends on RVM/RDS libraries, recovery annotations/macros, FSDB/VDB/HDB/RealmDB types, worker idle-time reporting, mariner/logging, RPC2 random generation for store identity, and Venus configuration from `venus.private.h`. Many persistent modules depend on `Recov_BeginTrans`/`Recov_EndTrans` and `RVMLIB_REC_OBJECT` semantics.

## Risks and Test Signals
Risks include RVM address assumptions per platform, data/log size calculations, dirty-shutdown validation, unflushed transaction windows, signal-handler use of RVM primitives, store-id overflow/replay detection behavior, and VM mode bypassing persistence. Tests should cover fresh init, restart validation, version/magic mismatch, clean versus dirty shutdown, explicit `-init`, private mapping, flush/truncate thresholds, recoverable string copy/free, and monotonic store id generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusrecov.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusrecov.h -->
# sources/distributed-fs/coda/coda-src/venus/venusrecov.h

## Purpose
This header defines the recoverable storage contract for Venus: RVM/VM defaults, persistent global root layout, transaction helpers, flush/truncate APIs, and pointer validation.

## Important APIs, Types, and Functions
It declares constants for default/unset RVM type, data/log sizes, RDS chunk/list counts, flush/truncate periods and sizes, magic/version numbers, and `RecovVenusGlobals`. `RecovVenusGlobals` stores persistent roots for FSDB, VDB, RealmDB, and HDB plus heap bounds, clean-shutdown state, UUID/store id, and validation/print methods. It declares global recovery configuration and functions including `Recov_BeginTrans`, `_Recov_BeginTrans`, `Recov_EndTrans`, `Recov_SetBound`, `RecovInit`, `RecovFlush`, `RecovTruncate`, `RecovTerminate`, `RecovPrint`, RPC2 string helpers, `RECOVD_Init`, `RecovDaemon`, and `Recov_GenerateStoreId`.

## Control Flow
The macro `Recov_BeginTrans()` captures caller file/line and delegates to `_Recov_BeginTrans`. Callers bracket persistent mutations with begin/end, then pass a flush bound to `Recov_EndTrans()`. Recovery initialization must precede modules that dereference `rvg` persistent roots.

## State and Persistence Behavior
This header is the authoritative layout for persisted Venus globals. `RecovVersionNumber` changes are format changes. `VALID_REC_PTR` enforces that persistent root pointers lie inside the loaded RDS heap. `VenusGenID` aliases part of `recov_UUID`.

## Dependencies and Integration Points
It depends on RPC2, rvmlib, Venus private declarations, and forward declarations of persistent database types. It is included by almost every module that touches RVM state.

## Risks and Test Signals
Risks include format-version drift, macro aliasing of UUID fields, and pointer validation only checking heap bounds rather than object type. Tests should verify fresh and recovered `RecovVenusGlobals` layouts, valid/invalid pointer detection, and that persistent root fields are initialized before dependent subsystem init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusrecov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusstats.h -->
# sources/distributed-fs/coda/coda-src/venus/venusstats.h

## Purpose
This header defines Venus statistics structures for VFS operations, filesystem objects, volumes, communication components, RPC operations, and RPC/SFTP packet counters.

## Important APIs, Types, and Functions
`VFSStat` stores operation name, success/retry/timeout/failure counts, and timing sums; `VFSStatistics` contains `NVFSOPS` entries. Placeholder structs exist for FSO, volume, connection, mgrp, server, and VSG stats. `RPCOpStat` stores per-RPC success/failure/timing and retry counts for unicast and multicast operations. `RPCPktStatistics` mirrors RPC2 and SFTP sent/received packet stats. `CommStatistics` and `VenusStatistics` aggregate subsystem stats.

## Control Flow
No functions are defined. Runtime initialization and printing occur in `venusutil.cc` through `StatsInit()`, `VFSPrint()`, `RPCPrint()`, and packet stat helpers.

## State and Persistence Behavior
These structures are transient runtime counters. They are not persisted, but they expose operational signals through Venus print/control paths and possibly pioctl status.

## Dependencies and Integration Points
It depends on RPC2 and Vice definitions, including `srvOPARRAYSIZE`, `SStats`, `RStats`, and `sftpStats`. `venus.private.h` declares global instances using these types.

## Risks and Test Signals
Risks include fixed `NVFSOPS`, fixed name buffer lengths, and protocol array size coupling. Tests should ensure VFS operation tables in `venusutil.cc` match `NVFSOPS`, RPC op initialization matches `srvOPARRAYSIZE`, and printed timing avoids divide-by-zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusstats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusutil.cc -->
# sources/distributed-fs/coda/coda-src/venus/venusutil.cc

## Purpose
This file implements general Venus utility behavior: debug logging, fatal error handling, state dumps, operation/error stringification, statistics initialization/printing, RPC packet-stat snapshots, malloc/RDS tracing hooks, log swapping, lock-level names, current time, and fid comparison.

## Important APIs, Types, and Functions
Globals include `logFile`, `LogLevel`, `MallocTrace`, `NullFid`, `NullVV`, `VFSStats`, and `RPCOpStats`. `dprint()` writes stamped debug logs. `choke()` prints a fatal message, dumps state, flushes/terminates recovery, unmounts, and asserts. `VenusPrint()` dispatches module-specific printers. `VenusOpStr()`, `IoctlOpStr()`, and `VenusRetStr()` map operation numbers and returns to strings. `VVPrint()`, `binaryfloor()`, `LogInit()`, `DebugOn()`, `DebugOff()`, `Terminate()`, `DumpState()`, `RusagePrint()`, `VFSPrint()`, `RPCPrint()`, `GetCSS()`, `SubCSSs()`, `MallocPrint()`, `StatsInit()`, `ToggleMallocTrace()`, `rds_printer()`, `SwapLog()`, `lvlstr()`, `Vtime()`, and `FAV_Compare()` round out utility support.

## Control Flow
Logging is inert until `LogInit()` sets `LogInited`. `dprint()` prefixes messages with the current vproc stamp and inserts blank lines when vproc/sequence changes. `VenusPrint()` parses requested module names and invokes the relevant printers. `StatsInit()` zeroes VFS/RPC stats and copies static operation names. `RPCPrint()` snapshots RPC2/SFTP counters and prints unicast/multicast stats. Fatal paths funnel through `choke()`, which performs best-effort persistent flush and unmount before invoking Coda assertion handling.

## State and Persistence Behavior
Most state is transient logging/statistics. `choke()` and `Terminate()` can force recovery flushing and clean termination side effects. `SwapLog()` reopens log and console files. `ToggleMallocTrace()` changes RDS heap tracing state.

## Dependencies and Integration Points
It depends on nearly all Venus subsystems for printing and cleanup: recovery, FSDB, VDB, HDB, users, connections, servers, VSG/mgrp, callbacks, workers, mariner, RPC2/SFTP counters, RDS tracing, and ioctl constants. `venus.private.h` declares many of its functions for broad use.

## Risks and Test Signals
Risks include fixed-size buffers in logging/string conversion, varargs declarations in old style, divide-by-zero possibilities in stat means if counters and times disagree, stale operation tables, and fatal cleanup reentrancy. Tests should cover log initialization, control-triggered stats dump, ioctl/op string mappings, RPC stat subtraction, malloc tracing toggles, and `FAV_Compare()` ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/venusutil.cc -->
