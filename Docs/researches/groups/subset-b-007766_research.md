# subset-b-007766 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bos.c -->
# sources/distributed-fs/openafs/src/bozo/bos.c

`bos.c` is the OpenAFS `bos` administration client. It builds command syntaxes for process control, server configuration, key/user management, binary install/uninstall, pruning, log retrieval, restart scheduling, restricted mode, and salvage operations, then dispatches those commands through generated `BOZO_*` Rx stubs.

Important APIs include `GetConn`, which resolves the target server and selects Rx security from client or server config with `-cell`, `-noauth`, and `-localauth`; `Install`, `UnInstall`, `GetDate`, and `CopyBytes`, which stream files and compute canonical destination paths; `DoSalvage`/`SalvageCmd`, which create a temporary `cron` bnode named `salvage-tmp`; and `DoStat`, which composes the long status output from instance metadata, status text, command parameters, notifier, and timestamps.

Control flow is command-driven. `main` initializes Rx and error tables, registers many `cmd_CreateSyntax` entries, appends standard cell/auth parameters at offset `ADDPARMOFFSET`, then calls `cmd_Dispatch`. Most commands open a connection, validate option combinations locally, call one or more `BOZO_*` RPCs, and print user-facing errors. Salvage has the richest flow: it detects DAFS by probing `dafs`/`fs` instances, optionally shuts down the file service, builds a salvager or salvageserver command line with size checks, starts a one-shot cron bnode, polls until the temporary instance disappears, and optionally streams `SalvageLog`.

State and persistence are remote. The client mutates bosserver state through RPCs that update `BosConfig`, server config files, KeyFile, UserList, installed binaries, and log/core cleanup. Local state is limited to command options, temporary path strings, opened input files, and optional salvage log output files.

Dependencies and integration points are Rx, afsconf auth/configuration, kauth string-to-key support, volser/vsu volume-name lookup for single-volume salvage, ktime parsing/display, generated `bosint` RPC client stubs, and server path macros from dirpath configuration. Risks include privileged operations exposed through command-line UX, password/key material passed through buffers, path construction that must remain canonical-wire-format compatible with bosserver path translation, fixed-size salvage command buffers, and DAFS/manual-salvage safety. Test signals are mostly integration/manual: command syntax registration, mocked or live bosserver RPC behavior, install streaming size checks, restricted-mode salvage allowance, and option-conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bos_util.c -->
# sources/distributed-fs/openafs/src/bozo/bos_util.c

`bos_util.c` is a local server-side key-management utility for manipulating OpenAFS server keys without going through bosserver RPCs. It supports `add`, `adddes`, optionally `srvtab2keyfile`, `delete`, and `list`.

The primary API is `main`, which opens `AFSDIR_SERVER_ETC_DIR`, parses argv manually, prompts for passphrases with `UI_UTIL_read_pw_string`, converts them using `ka_StringToKey` or `DES_string_to_key`, and calls `afsconf_AddKey`, `afsconf_DeleteKey`, or `afsconf_GetKeys`. The list path prints raw key bytes in printable and octal forms.

Control flow is a straight opcode switch over `argv[1]`; all errors print to stdout/stderr and exit nonzero. State is persistent in the server configuration directory key files, with no network/Rx involvement. Dependencies are afsconf, hcrypto UI/DES, kauth utilities, and legacy Kerberos support when compiled.

Risks include direct display of secret key material in `list`, legacy DES handling, minimal input validation around numeric kvnos, and hard process exits that make it unsuitable as a library. Test signals are command-level: add/delete/list against a temporary afsconf dir, password mismatch behavior, and compile coverage for `KERBEROS` conditionals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bos_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bosoprocs.c -->
# sources/distributed-fs/openafs/src/bozo/bosoprocs.c

`bosoprocs.c` implements the server-side `SBOZO_*` RPC procedures used by the `bos` client. It is the authorization, auditing, path translation, configuration mutation, and bnode-control surface for bosserver.

Important APIs include restart time accessors, `SBOZO_Exec`, install/uninstall/date RPCs, cell host/cell name methods, superuser and key methods, bnode lifecycle methods, status/log enumeration methods, prune/restricted-mode calls, and `bozo_ShutdownAndExit`. Helper logic includes `SaveOldFiles`, `ZapFile`, `DirAccessOK`, `GetRequiredDirPerm`, and directory-entry permission metadata in `bozo_bosEntryStats`.

Control flow usually checks `afsconf_SuperUser`, optional restricted-mode constraints, logs privileged operations when `DoLogging` is enabled, mutates state, audits with `osi_auditU`, and returns a bos error code. Bnode operations hold `BNODE_LOCK`, find/hold/release instances, and delegate to generic bnode APIs. `SBOZO_ReBozo` shuts down children, finalizes Rx, and re-execs bosserver. `SBOZO_GetLog` streams a NUL-delimited file over Rx after translating canonical log paths.

State and persistence include `BosConfig` rewrites through `WriteBozoFile`, KeyFile and UserList changes through afsconf, CellServDB-style host data, installed server binaries with `.NEW`/`.BAK`/`.OLD` rotation, noauth flag, restricted mode, directory permission status, and live bnode state. Restricted mode blocks shell execution, installation, pruning, deletion, and generic bnode creation, but allows a tightly shaped `salvage-tmp` cron bnode.

Dependencies and integration points are generated `bosint` server stubs, Rx call/connection security inspection, rxkad encryption checks for key disclosure and key changes, afsconf server configuration, dirpath path constructors (`ConstructLocalBinPath`, `ConstructLocalLogPath`), audit, ktime, and the bnode subsystem. Risks include high-privilege filesystem mutation, shell execution when unrestricted, reliance on caller-provided names after path translation, key disclosure in noauth/encrypted cases, global locking around operations that may wait, and correctness of restricted-mode exceptions. Test signals should cover authorization failures, restricted-mode denials/allowances, install rollback and size mismatch, log path restrictions, directory permission flagging, and bnode state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bosoprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bosprototypes.h -->
# sources/distributed-fs/openafs/src/bozo/bosprototypes.h

`bosprototypes.h` centralizes internal prototypes shared by bosserver, bnode operation modules, and bos RPC procedures. It exposes the bnode management surface, bosserver helpers, bosoprocs helpers, and an inline key-structure cast.

Important declarations include `bnode_*` instance/process operations, `bozo_ReBozo`, `WriteBozoFile`, pid-file helpers, restricted-mode getters/setters, `GetRequiredDirPerm`, `bozo_ShutdownAndExit`, `initBosEntryStats`, and `DirAccessOK`. `ktc_to_bozoptr` casts a `ktc_encryptionKey` to the wire `bozo_key` structure used by bos RPCs.

This header has no runtime control flow or persistence, but it fixes cross-module contracts that affect `BosConfig` persistence, process supervision, pid files, and RPC key handling. Dependencies are `rx/rxkad.h` and types from included bnode/bos headers in consumers.

Risks are ABI/API drift between prototypes and implementation, especially for pointer ownership (`char **` outputs), lock preconditions (`WriteBozoFile`, `DirAccessOK`), and the inline cast assuming layout compatibility. Test signals are compile-time: all bozo objects must build with warnings enabled, and callers should be checked for lock and allocation ownership conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bosprototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bosserver.c -->
# sources/distributed-fs/openafs/src/bozo/bosserver.c

`bosserver.c` is the bosserver daemon entry point and global coordinator. It initializes server directories, logging, auth configuration, the bnode subsystem, registered bnode types (`fs`, `dafs`, `simple`, `cron`), Rx services, audit, pid files, restricted mode, and scheduled restarts.

Important APIs include `bozo_IsRestricted`/`bozo_SetRestricted`, `bozo_insecureme`, `bozo_rxstat_userok`, `bozo_ReBozo`, directory helpers `MakeDirParents`/`MakeDir`/`CreateDirs`, `ReadBozoFile`, `WriteBozoFile`, `BozoDaemon`, pid-file helpers, `bozo_CreateRxBindFile`, `GetRxBindAddress`, `CreateLocalCellConfig`, and `main`. `ReadBozoFile` parses `restrictmode`, `restarttime`, `checkbintime`, and `bnode`/`parm`/`end` records. `WriteBozoFile` atomically writes a `.NBZ` file and renames it into place.

Control flow in `main` parses options, requires root on Unix, creates required directories, daemonizes unless `-nofork`, initializes locks/signals/audit/logging, opens or creates cell config, initializes bnodes, reads `BosConfig` to instantiate and start configured services, initializes Rx, starts `BozoDaemon`, builds server security classes, creates the bos and rxstats services, and donates the process to `rx_StartServer`. `BozoDaemon` wakes every minute, handles restricted-mode signal notices, recomputes ktime schedules, triggers full reexec restarts, restarts bnodes whose binaries changed, and reopens logs for rotation.

State and persistence include global `bozo_confdir`, `bozo_fileName`, `bnode_glock`, logging flags, core/pid/log paths, restart ktime structures, restricted-mode atomics, rxbind file, pid files, and `BosConfig`. Dependencies include Rx/rxkad/rxstat, afsconf/authcon, audit, dirpath, bnode internals, soft signals, ktime, and platform-specific daemon/core handling.

Risks include global lock scope, root-only filesystem setup, persistence parser fragility for malformed `BosConfig`, direct reexec semantics, creating a default `localcell`, signal-based restricted-mode disable via `SIGFPE`, and security impact of running without restricted mode. Test signals include parser/round-trip tests for `BosConfig`, startup with missing config, directory permission checks, option parsing, Rx bind-file generation, and scheduled restart behavior with mocked bnodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bosserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/cronbnodeops.c -->
# sources/distributed-fs/openafs/src/bozo/cronbnodeops.c

`cronbnodeops.c` implements the `cron` bnode type: a bosserver-supervised command that runs once or periodically according to a `ktime` schedule. It is used for administrative scheduled jobs and by `bos salvage` for temporary one-shot salvager execution.

Important APIs are the `cronbnode_ops` vtable, `cron_create`, `ScheduleCronBnode`, `cron_timeout`, `cron_setstat`, `cron_procexit`, `cron_getstat`, `cron_getstring`, and `cron_getparm`. `struct cronbnode` stores the command, original schedule string, parsed `ktime`, next run time, process pointer, last start time, and shutdown/running flags.

Control flow parses the schedule at creation, translates the command from canonical bin path to local path, and computes `when`. For one-shot jobs (`when == 0`), `ScheduleCronBnode` starts the process immediately and deletes the bnode after it has run. For periodic jobs, it sets bnode timeouts until the next run. Shutdown sends SIGTERM and schedules a SIGKILL after `SDTIME`; process exit logs signal/nonzero status, clears state, recomputes the next run, and reschedules.

State is mostly in memory; persistence occurs indirectly because bosserver writes bnode type, command, and schedule string to `BosConfig`. Dependencies are bnode process APIs, `ktime`, path translation, LWP/procmgmt, and logging. Risks include schedule parser edge cases, one-shot self-deletion while active, fixed 60-second shutdown grace, command path translation constraints, and no binary-change restart support (`cron_restartp` returns 0). Test signals include one-shot lifecycle, periodic timeout computation, shutdown/kill behavior, status strings, and salvage-tmp compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/cronbnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/ezbnodeops.c -->
# sources/distributed-fs/openafs/src/bozo/ezbnodeops.c

`ezbnodeops.c` implements the `simple` bnode type: supervision for a single long-running command. It starts, stops, restarts after exits when the bnode goal is normal, detects core files, supports pid files, and reports simple status.

Important APIs are `ezbnode_ops`, `ez_create`, `ez_setstat`, `ez_timeout`, `ez_procexit`, `ez_restartp`, `ez_getstat`, `ez_getparm`, and pid-file hooks in `ez_procstarted`. The implementation uses `struct ezbnode` from bnode internals, with fields such as command, proc, running/shutdown flags, last start, and inherited bnode error state.

Control flow translates the canonical command path during creation, starts the process on `BSTAT_NORMAL`, sends SIGTERM and arms a 60-second timeout on shutdown, sends SIGKILL in `ez_timeout` if needed, and restarts automatically from `ez_procexit` if the desired goal remains normal. Error-stop retry uses `bnode_IsErrorRetrying` and `errorStopDelay`.

State is in-memory except for `BosConfig` persistence of the command and optional pid files under the configured pid directory. Dependencies are bnode APIs, path translation, procmgmt signals, pid-file helpers, and file stat checks for binary-change restarts. Risks include command parsing in `ez_restartp`, fixed shutdown grace, sparse auxiliary status text, and pid-file cleanup consistency on unusual exits. Test signals include start/stop/restart, ignored SIGTERM leading to SIGKILL, binary ctime restart detection, pid-file creation/removal, and error retry delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/ezbnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/fsbnodeops.c -->
# sources/distributed-fs/openafs/src/bozo/fsbnodeops.c

`fsbnodeops.c` implements `fs` and `dafs` bnode types, coordinating the multi-process OpenAFS file service: fileserver, volserver, salvager, optional scanner, and for DAFS the salvageserver. It encodes startup ordering, shutdown ordering, salvage-after-crash behavior, binary-change restart detection, status strings, pid files, and core detection.

Important APIs are `fsbnode_ops`, `dafsbnode_ops`, `fs_create`, `dafs_create`, `NudgeProcs`, `SetSalFlag`, `RestoreSalFlag`, `SetNeedsClock`, `fs_timeout`, `fs_procexit`, `fs_restartp`, `fs_getstat`, `fs_getstring`, `fs_getparm`, and `dafs_getparm`. `struct fsbnode` stores command strings, process pointers, last starts, running/shutdown/kill flags, `needsSalvage`, and clock scheduling state.

Control flow validates and translates all command paths at creation, checks that binaries exist, restores `needsSalvage` from `AFSDIR_SERVER_LOCAL_DIRPATH/SALVAGE.<instance>` for non-DAFS, and sets a poll timeout. `NudgeProcs` is the state machine: when goal is normal it starts file/vol/scanner/salvageserver if safe, or stops file/vol/scanner and runs salvager if `needsSalvage` is set. On shutdown it SIGQUITs fileserver and SIGTERMs the other processes, with `fs_timeout` escalating to SIGKILL after grace periods. `fs_procexit` clears process state, updates salvage flags when fileserver exits cleanly or salvager completes, and re-enters `NudgeProcs`.

State and persistence are split between in-memory process flags, optional pid files, `BosConfig` command persistence, and the salvage flag file that survives host crashes. Dependencies include bnode APIs, path translation, server dirpath constants, procmgmt signals, LWP/Rx includes, pid-file helpers, and file stat metadata for restart detection.

Risks include a complex hand-written lifecycle state machine, crash-safety dependence on correct `SALVAGE.*` creation/removal, DAFS differences where salvage flags are ignored, fixed shutdown windows, emergency shutdown if salvager and fileserver run together, command-token parsing for ctime checks, and optional scanner/salvageserver branches. Test signals should cover clean vs killed fileserver exit, salvager completion clearing flags, DAFS startup, scanner optionality, status strings, ctime restart detection, pid-file cleanup, and timeout escalation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/fsbnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/test/Makefile.in -->
# sources/distributed-fs/openafs/src/bozo/test/Makefile.in

This makefile builds the `testproc` helper used for bos/bnode process supervision tests. It includes the top-level OpenAFS make configuration and defines `all`, `testproc`, `clean`, empty `install`, and empty `dest` targets.

The only build API is the `testproc: testproc.c` rule, invoking `$(CC)` with `$(AFS_LDFLAGS)` and `$(AFS_CFLAGS)`. No libraries are linked beyond the platform defaults implied by compiler flags.

There is no runtime state. Persistence is limited to generated `testproc`, object/core files, and clean removal. Dependencies are the configured compiler variables and `testproc.c`. Risks are low, but `MODULE_CFLAGS=$(LDIRS) $(LIBS)` appears unused and install/dest intentionally do nothing, so downstream tests must run from the build directory. Test signals are successful build and `make clean` removing generated artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/test/testproc.c -->
# sources/distributed-fs/openafs/src/bozo/test/testproc.c

`testproc.c` is a small controllable process for exercising bosserver bnode supervision. It can sleep, ignore termination, reload behavior from a file, return normally, exit with error, or intentionally crash.

Important APIs are `main`, `readfile`, `trim`, `sigproc`, and `sigreload`. Options are `-ignore`, `-sleep <n>`, and `-file <file>`. A control file can contain `sleep N`, `run`, `return`, `exit`, or `crash`; SIGHUP reloads it, while SIGTERM/SIGQUIT either exit or are ignored depending on `-ignore`.

Control flow parses options, installs signal handlers, and loops while `run` is true, optionally reading the control file and sleeping. State is process-local globals (`ignore`, `sleepTime`, `run`, `file`) plus the external control file. Dependencies are standard C/POSIX signal, sleep, stdio, and AIX full-core handling.

Risks are intentional because this is a test helper: `crash` dereferences NULL, file parsing only reads one line, and invalid control files can terminate the process. Test signals are exactly its behaviors under bnode supervision: normal return, ignored SIGTERM leading to SIGKILL, SIGHUP reconfiguration, nonzero exit, and core generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/test/testproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bu_utils/Makefile.in -->
# sources/distributed-fs/openafs/src/bu_utils/Makefile.in

This makefile builds and installs the backup utility `fms`, a filemark-size measurement program for tape devices. It includes OpenAFS config and LWP make fragments and defines `all`, `fms`, `install`, `dest`, `clean`, and version-generation integration.

Important build variables are `FMSLIBS`, which links `libcmd.a`, `libusd.a`, `util.a`, `libopr.a`, roken, and `XLIBS`; `fms.o`, which depends on `fms.c` and `AFS_component_version_number.o`; and install destinations under `${sbindir}` or `${DEST}/etc`.

There is no runtime state in the makefile, but it produces `fms`, object files, and component version C. Dependencies are OpenAFS build macros, USD tape support, command parsing, util/opr, and roken. Risks include platform tape-library availability and old-style `dest` install path divergence from modern `install`. Test signals are successful build/link and clean removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bu_utils/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bu_utils/fms.c -->
# sources/distributed-fs/openafs/src/bu_utils/fms.c

`fms.c` implements the `fms` utility, which estimates tape capacity and filemark size by writing data blocks and file marks until the tape reports an error/end condition. It is operational tooling for configuring backup tape characteristics.

Important APIs include `main`, `tt_fileMarkSize`, `fileMarkSize`, `rewindTape`, `fileMark`, `dataBlock`, and `quitFms`. It uses the OpenAFS `cmd` package for `-tape`, USD device handles for open/write/ioctl/close, and writes progress plus `fms.log`.

Control flow opens the tape read/write with write lock, rewinds, writes 16 KiB data blocks until failure to estimate capacity, closes/reopens/rewinds, then alternates data blocks and file marks until failure to estimate filemark cost. `dataBlock` caches a static zeroed buffer sized to the requested block and stores an incrementing integer at its start.

State and persistence include tape device contents, `fms.log` in the current directory, static data buffer/count, and global `eotEnabled`/`tapeDevice` values that are mostly unused. Dependencies are `afs/cmd.h`, `afs/usd.h`, tape ioctls (`USDTAPE_REW`, `USDTAPE_WEOF`), signals, and component version generation. Risks are destructive writes to the target tape, simplistic error handling where any write failure ends loops, possible division by zero if no file marks are written, SIGINT exiting without explicit cleanup beyond process teardown, and assumptions about 16 KiB block behavior. Test signals are hard to automate without a tape/mock USD layer; practical checks are command parsing, mocked USD write/ioctl behavior, log creation, and handling open/rewind/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bu_utils/fms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/Makefile.in -->
# sources/distributed-fs/openafs/src/bubasics/Makefile.in

This makefile builds `libbubasics.a` and generated backup/tape interface headers and sources. It is the build bridge from `.xg` Rx definitions and `.et` error tables to installed backup headers used by bucoord, butc, and tape modules.

Important targets include `generated`, `libbubasics.a`, generated `butc`, `bumon`, `butm`, `tcdata`, and `butx` headers/sources, plus install/dest/clean. RXGEN produces client/server/XDR/header code for `butc.xg` and `bumon.xg`; COMPILE_ET produces error C and headers; `tcdata.h` is generated from `butc_errs.et`, `tcdata.p.h`, and `butm.h`.

State is build-output state: generated C/header files, objects, archive library, installed headers, and component version source. Dependencies are top-level OpenAFS make config, LWP config, RXGEN, COMPILE_ET, archiver/ranlib, and source `.xg`/`.et`/`.p.h` files.

Risks include generated-header ordering, consumers depending on installed include names rather than private `.p.h` files, stale generated artifacts, and clean removing generated files required before regen. Test signals are deterministic regeneration, archive contents, installed headers matching generated outputs, and downstream bucoord/butc build success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/bubasics.h -->
# sources/distributed-fs/openafs/src/bubasics/bubasics.h

`bubasics.h` defines common backup-system constants, version numbers, ports, name lengths, dump result states, expiration encodings, tape-name helper macros, a double-linked queue node type, queue invariants, and the shared `statusS` task-status structure.

Important types and macros include `BUTM_MAJORVERSION`, `CUR_BUTC_VERSION`, `CUR_TAPE_VERSION`, backup database magic/version constants, `BC_MESSAGEPORT`, `BC_TAPEPORT`, `AFSCONF_BUDBPORT`, dump result codes, `BU_MAX*` sizing constants, `NEVERDATE`/`cTIME`, `tc_MakeTapeName`, `struct dlqlink`, `DLQ_*` types, task flags such as `STARTING`, `ABORT_REQUEST`, `TASK_DONE`, `CONTACT_LOST`, `TASK_ERROR`, and `struct statusS`/`statusP`.

There is no executable control flow, but the header governs binary and wire compatibility across backup coordinator, tape coordinator, backup database, and tape modules. State represented here includes queued task status, dump progress counters, current volume name, scheduled command line, and job metadata.

Dependencies are OpenAFS integer types and `ctime` consumers; queue function prototypes are implemented elsewhere. Risks include fixed-width name buffers, macro side effects (`tc_MakeTapeName`, `cTIME`), legacy version constants that must not change casually, typo-prone flag semantics shared between client/server, and `statusS` ownership of `cmdLine`. Test signals are compile coverage across backup components, queue invariant tests, and status flag interop between bucoord and butc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/bubasics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/butm.p.h -->
# sources/distributed-fs/openafs/src/bubasics/butm.p.h

`butm.p.h` is the private template for the generated public `butm.h` tape module interface. It defines tape block layout, tape operation vtables, tape state/config structures, tape status/flag bits, tape labels, naming macros, and vtable call macros.

Important types include `struct blockMark`, `struct butm_tapeInfo` with its `ops` function pointers, `struct tapeConfig`, and `struct butm_tapeLabel`. Constants define 16 KiB physical tape blocks, header/data sizes, tape status bits (`OFFLINE`, `TAPEERROR`, `EOF`, `EOD`), and flags (`READONLY`, `SEQUENTIAL`). Macros include `TNAME`, `TAPENAME`, `LABELNAME`, and `butm_*` dispatch wrappers.

There is no direct control flow; runtime dispatch happens through the function pointers in `butm_tapeInfo`. State includes tape position, byte/KByte/record/file counters, capacity model coefficients, mounted tape name, read-only/sequential flags, module-private rocks, error code, label metadata, expiration, dump id, use count, size, and dump path.

Dependencies are `afs/auth.h`, `afs/bubasics.h`, generated error table inclusion in the final header, and implementations that populate the ops table. Risks include ABI compatibility of function pointers, fixed-size label fields, macro buffer assumptions, a suspicious `butm_remainingSpace` reference to `(i)->Bytes` even though the structure defines `nBytes`, and unit ambiguity across historical version flags. Test signals are compile checks of generated `butm.h`, tape-module vtable conformance, label round trips, and capacity accounting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/butm.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/tcdata.p.h -->
# sources/distributed-fs/openafs/src/bubasics/tcdata.p.h

`tcdata.p.h` is the private template for generated `tcdata.h`, defining tape-coordinator shared data structures and constants for dump/restore task management and volume headers/trailers on tape.

Important types include `struct dumpNode`, which ties a task id to dump/restore arrays, tape set descriptors, parent/level metadata, append mode, and status node; `struct deviceSyncNode`, which wraps a lock and device flags; `struct volumeHeader`, which records volume identity, server/partition, clone/from dates, magic values, continuation, dump set/name/id/level/parent/end/version fields; and small RPC/interface payloads `labelTapeIf`, `scanTapeIf`, `saveDbIf`, and `deleteDumpIf`.

There is no executable control flow. State modeled here is in-memory tape coordinator task state and serialized tape volume metadata. Dependencies include generated `butc.h`, `budb.h`, `bubasics.h`, and `butm.h`.

Risks include fixed magic constants and string sizes, compatibility of on-tape `volumeHeader`, comments noting temporary values, concurrency correctness around `deviceSyncNode.lock`, and alignment/endianness expectations for serialized headers. Test signals are generated header build, dump/restore interop tests that read old tape formats, task abort/done flag behavior, and scan/label/save-db RPC structure compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bubasics/tcdata.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/Makefile.in -->
# sources/distributed-fs/openafs/src/bucoord/Makefile.in

This makefile builds the backup coordinator command (`backup`), support archive `libbxdb.a`, generated `bc.h`/`bucoord_errs.c`, installed `bucoord_prototypes.h`, and the `btest` helper. It wires bucoord against backup database, tape, volume, vldb, kauth, ubik, Rx, LWP, cmd, util, opr, and crypto libraries.

Important build variables are `LIBS`, `BACKSRCS`, `BACKOBJS`, generated-header dependencies, and targets `libbxdb.a`, `backup`, `btest`, `install`, `dest`, and `clean`. `bc.h` is generated from `bucoord_errs.et` plus `bc.p.h`; `bucoord_errs.c` comes from COMPILE_ET.

State is build-output state: generated error/header files, object files, archive, executable, component version source, and installed artifacts. Dependencies are top-level config, LWP config, COMPILE_ET, many OpenAFS libraries, and generated bubasics headers. Risks include library ordering sensitivity, broad transitive dependency surface, `CFLAGS_commands.o=@CFLAGS_NOERROR@` suppressing strict warnings for commands, legacy `dest` path, and generated `bc.h` staleness. Test signals are clean generated rebuild, link success for `backup` and `btest`, install layout, and downstream inclusion of `bc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bc.p.h -->
# sources/distributed-fs/openafs/src/bucoord/bc.p.h

`bc.p.h` is the template for generated `bc.h`, defining core backup coordinator configuration and scheduling data structures. It models database/tape hosts, global config, volume sets, volume entries, concrete volumes to dump, dump schedules, and queued dump/restore tasks.

Important types include `bc_hostEntry`, `bc_config`, `bc_opstatus`, `bc_volumeSet`, `bc_volumeEntry`, `bc_volumeDump`, `bc_dumpSchedule`, and `bc_dumpTask`. Constants define config file names (`dbasehosts`, `tapehosts`, `dumpschedule`, `volumeset`), `VSFLAG_TEMPORARY`, `BC_MAXSIMDUMPS`, `BC_MAXPORTS`, and an empty `afs_dprintf` macro.

There is no runtime control flow in this file, but its structures carry persistent config parsed from bucoord text files and runtime job state used to initiate dump/restore operations. Dependencies include `budb_client.h`, `afsutil.h`, stdio conditionals, string, socket address types, and generated error content added when `bc.h` is produced.

Risks include pointer ownership across config structures, fixed port-count limits, fields marked obsolete/unused, generated-header drift, and no active debug logging due to `afs_dprintf` being compiled away. Test signals include parsing/saving config text, dump schedule parent/child construction, temporary volume set lifecycle, and dump task execution with multiple port offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bc.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bc_status.c -->
# sources/distributed-fs/openafs/src/bucoord/bc_status.c

`bc_status.c` implements backup coordinator status watching for scheduled and active tape coordinator tasks. It maintains a global queue of `statusS` nodes, polls butc task status, sends abort requests, starts scheduled dumps, reports completion, and exposes wait/job-number helpers.

Important APIs include `statusWatcher`, `cmdDispatch`, `bc_jobNumber`, `waitForTask`, and helper `nextItem`. Globals include `statusHead`, `statusQueueLock`, `cmdLineLock`, `lastTaskCode`, and `cmdLine`. Macros `SET_FLAG` and `CLEAR_FLAG` update the current status node under lock.

Control flow in `statusWatcher` loops forever, cycling through status nodes. It sleeps if the queue is empty, handles pre-start aborts, starts scheduled dumps by moving `cmdLine` into a new LWP `cmdDispatch`, handles local abort/contact-lost cases, connects to butc through `bc_GetConn`, validates `CheckTCVersion`, sends `TC_RequestAbort` when needed, polls `TC_GetStatus`, updates local flags and progress, reports task completion/abort/error, calls `TC_EndStatus`, and deletes or preserves nodes based on `NOREMOVE`. `waitForTask` sleeps and polls local queue flags until the requested task is done or removed.

State and persistence are in-memory queue state plus scheduled command lines; durable backup metadata lives in downstream budb/butc services, not here. Dependencies include LWP, Rx, bubasics status flags, tcdata/butc RPCs, command parser/dispatcher, `bc_globalConfig`, locks, and bucoord internal prototypes.

Risks include concurrency on global `cmdLine`, queue-node lifetime while locks are dropped, contact-lost retry behavior, output from background watcher interleaving with command output, and apparent `delaytime`/`delayTime` case mismatch in pthread branches that would matter when `AFS_PTHREAD_ENV` is enabled. Test signals include scheduled dump dispatch, abort before start, abort after start, TC_NODENOTFOUND cleanup, CONTACT_LOST recovery, `NOREMOVE` behavior, and `waitForTask` completion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bc_status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/btest.c -->
# sources/distributed-fs/openafs/src/bucoord/btest.c

`btest.c` is a tiny Rx client test for the backup coordinator monitor/message service. It sends a `BC_Print` RPC to localhost on `BC_MESSAGEPORT` using null Rx security and prints the returned code.

The only API is `main`: initialize Rx, create `rxnull` client security, connect to `127.0.0.1:BC_MESSAGEPORT` service id `1`, call `BC_Print(tconn, 1, 2, argv[1])`, print completion, and exit.

State is process-local; it does not persist data. Dependencies are LWP/Rx, `bubasics.h` for `BC_MESSAGEPORT`, generated `bumon.h` for `BC_Print`, generated `bc.h`, and component version inclusion.

Risks include no argument count validation for `argv[1]`, hard-coded localhost/service/security, no connection/security cleanup, and suitability only as a developer smoke test. Test signals are successful compile/link and a live backup coordinator accepting `BC_Print`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/btest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bucoord_internal.h -->
# sources/distributed-fs/openafs/src/bucoord/bucoord_internal.h

`bucoord_internal.h` declares internal cross-module functions and globals for the `backup` command implementation. It is broader than the public prototype header and covers command handlers, config parsing, dump/restore orchestration, text-database operations, tape host and volume set persistence, VLDB interaction, status management, regex, and globals.

Important API groups include status watcher/job/wait functions; command utility and command handler prototypes; config host operations; volume set and dump schedule CRUD/parsing; butc connection and dump/restore/tape commands; update/save functions for dump schedules, tape hosts, and volume sets; ubik backup database wrappers; VLDB/volume helpers; and globals `localauth`, `nobutcauth`, `tcell`, and `tokenExpires`.

There is no runtime control flow or persistence in the header, but it defines contracts for modules that read/write bucoord config text, interact with budb/ubik/vldb/butc, and manage status queues. Dependencies include many structs from generated `bc.h`, `budb`, `ubik_client`, `rx_connection`, `cmd`, socket, FILE, and status types.

Risks include a large shared namespace, duplicate declarations also present in `bucoord_prototypes.h`, pointer ownership ambiguity, historical regex prototypes, and difficulty enforcing module boundaries. Test signals are compile/link coverage across all bucoord objects, generated-header ordering, and warnings for prototype mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bucoord_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bucoord_prototypes.h -->
# sources/distributed-fs/openafs/src/bucoord/bucoord_prototypes.h

`bucoord_prototypes.h` is the installed/public-ish prototype header for backup coordinator support library functions. It exposes double-linked queue utilities, status queue operations, VLDB lookup, backup database text/dump/tape/volume wrappers, client initialization, and single-server BUDB ubik call wrappers.

Important declarations include `dlqEmpty`, `dlqInit`, `dlqUnlink`, `dlqLinkb`, `dlqLinkf`, `dlqTraverseQueue`; status functions `initStatus`, `findStatus`, `lock_Status`, `unlock_Status`, `deleteStatusNode`, `createStatusNode`; `bc_GetEntryByID`; multiple `bcdb_*` wrappers; `udbClientInit`; `vldbClientInit`; and `ubik_Call_SingleServer_BUDB_GetVolumes`/`DumpDB`.

The header has no direct control flow or persistence. Its contracts mediate persistent backup database operations, text-file locks/saves, dump/tape/volume records, and status queue ownership. Dependencies are `dlqlinkP`, `statusP`, `udbClientTextP`, `budb_*` types, `ubik_client`, `vldbentry`, and token/time types supplied by consumers.

Risks include installed API stability, overlap with `bucoord_internal.h`, callback typing for `dlqTraverseQueue`, and ownership/error-code conventions not visible in prototypes. Test signals are external consumer builds, archive symbol availability, queue operation unit tests, and integration tests for BUDB wrapper calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bucoord/bucoord_prototypes.h -->
