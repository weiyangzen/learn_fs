# Group Research: group_385_freebsd_src_sources_os_bsd_freebsd_src_sbin_restore_dirs_c_sources_o_4b1afad0100c

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/dirs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/dirs.c

Purpose: builds and queries restore’s temporary directory database while reading dump tapes. It records dumped directory contents in `dirfile`, optional directory metadata and extended attributes in `modefile`, and maps directory inode numbers to offsets through a hashed `inotab`.

Key functions:
- `extractdirs()` consumes directory records from tape, writes normalized directory entries to a temporary database, optionally records `modeinfo`, and validates that the root directory exists.
- `treescan()` recursively walks the dump directory tree and calls a supplied callback for each pathname/inode.
- `pathsearch()`, `searchdir()`, `rst_opendir()`, `rst_readdir()`, and `rst_closedir()` provide a small directory API over the temporary dump-directory file.
- `setdirmodes()` replays directory ownership, mode, timestamps, flags, and extended attributes after extraction.
- `genliteraldir()` writes a literal copy of a dumped directory file when restore is running inode-number mode.
- `done()` closes tape input and removes temporary directory/mode files.

Integration: depends on `getfile()`, `skipfile()`, `curfile`, `dumpmap`, `lookupino()`, `myname()`, and `set_extattr()` from the rest of restore. It is central to name-based restore because later selection and extraction operate against this synthesized directory view.

Risk notes: path handling uses fixed `MAXPATHLEN` buffers and some unchecked `strcpy()` paths, assuming caller-normalized input. Directory-entry validation attempts to skip malformed records, but corrupted dump input can still affect traversal and warnings. Temporary file failures are fatal through `fail_dirtmp()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/dirs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/extern.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/extern.h

Purpose: shared function prototype header for the `restore` program.

Contents:
- Declares restore workflow entry points such as `setup()`, `extractdirs()`, `createfiles()`, `createleaves()`, `createlinks()`, `setdirmodes()`, and `checkrestore()`.
- Declares symbol-table APIs including `addentry()`, `lookupino()`, `lookupname()`, `moveentry()`, `freeentry()`, `dumpsymtable()`, and `initsymtable()`.
- Declares tape I/O APIs including `setinput()`, `getvol()`, `getfile()`, `skipfile()`, `skipmaps()`, `extractfile()`, and byte-swapping helpers.
- Defines `enum set_extattr_mode` for setting extended attributes by file path, symlink path, or file descriptor.
- Includes optional remote tape prototypes from `../dump/dumprmt.c`.

Integration: binds together the mostly global-state restore modules. This header makes the program’s cross-file coupling explicit: tape state, directory database, symbol table, utility functions, and high-level restore algorithms are all mutually visible.

Risk notes: APIs are C-era global-state oriented and lack const-correctness in several pathname parameters. Function contracts are mostly implicit in implementation comments rather than types.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/interactive.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/interactive.c

Purpose: implements `restore -i`, an interactive shell for browsing dump contents and choosing files to extract.

Key functions:
- `runcmdshell()` dispatches commands: `add`, `cd`, `delete`, `extract`, `ls`, `pwd`, `quit`/`xit`, `verbose`, `setmodes`, `what`, and `Debug`.
- `getcmd()` parses input, handles multiple arguments over repeated calls, canonicalizes paths, and expands globs.
- Custom glob hooks `rst_opendir`, `glob_readdir`, `rst_closedir`, and `glob_stat` make globbing operate against dump directory contents rather than the live filesystem.
- `canon()` normalizes names to restore’s `./...` convention and removes duplicate slashes, `.`, and `..`.
- `printlist()`, `mkentry()`, `formatf()`, and `fcmp()` implement an `ls`-style listing with restore-specific markers.
- `onintr()` uses `setjmp`/`longjmp` to recover to the prompt on interrupt in interactive mode.

Integration: uses directory APIs from `dirs.c`, selection callbacks from `restore.c`, and symbol-table state from `symtab.c`. It triggers actual extraction by calling `createfiles()`, `createlinks()`, and `setdirmodes()`.

Risk notes: command parsing uses static buffers and manual quote/backslash handling. `canon()` assumes enough destination capacity after an explicit length check, but later transformations still rely on fixed-size buffers. Interrupt handling is non-local and depends on global shell state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/interactive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/main.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/main.c

Purpose: program entry point, global option state definition, argument parsing, and top-level mode orchestration for `restore`.

Key behavior:
- Defines global flags such as `bflag`, `dflag`, `Dflag`, `hflag`, `mflag`, `Nflag`, `uflag`, `vflag`, `yflag`, `command`, `dumpnum`, `volno`, maps, times, and `terminal`.
- Parses modern options with `getopt()` and converts obsolete compact restore syntax through `obsolete()`.
- Selects exactly one command mode: interactive `i`, resume `R`, full/incremental restore `r`, table/list `t`, or extract `x`.
- Calls `setinput()`, `setup()`, `extractdirs()`, `initsymtable()`, and the relevant high-level restore workflow.
- `usage()` prints mode-specific command forms and exits through `done()`.

Integration: this file sequences the entire restore pipeline. It decides when to initialize from an existing checkpoint symbol table, when to scan directories, when to build extraction lists, and when to checkpoint again.

Risk notes: the program is intentionally global-state heavy; command sequencing is critical. Resume mode relies on `restoresymtable` being consistent with the current tape. Obsolete argument rewriting allocates new argv strings and exits on malformed legacy syntax.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/restore.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/restore.c

Purpose: implements the core restore algorithms for listing, extraction selection, incremental reconciliation, file creation, link creation, and verification.

Key functions:
- `listfile()`, `addfile()`, and `deletefile()` are traversal callbacks used by list, extract, and interactive modes.
- `removeoldleaves()`, `nodeupdates()`, `findunreflinks()`, and `removeoldnodes()` implement incremental restore reconciliation against a previous filesystem symbol table.
- `createleaves()` extracts new or changed file contents for full/incremental restore and checkpoints after volume changes.
- `createfiles()` efficiently extracts only requested files for `-x` and `-i`, including volume skipping logic.
- `createlinks()` recreates whiteouts, hard links, and symbolic links for directory hard-link cases.
- `checkrestore()` and `verifyfile()` enforce that requested operations completed and no temporary names or flags remain.

Integration: heavily depends on symbol-table operations, tape position state, inode maps, directory traversal, and filesystem utility functions. `nodeupdates()` is the main state machine that classifies files by whether names/inodes are on tape, already known, or type-changed.

Risk notes: incremental reconciliation is complex and stateful. Directory deletion is deferred through `removelist`, and comments note `removeoldnodes()` can be slow for deep deletion sets. Incorrect flag combinations call `badentry()`/`panic()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/restore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/restore.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/restore.h

Purpose: central shared type and global-state declaration header for `restore`.

Contents:
- Declares command flags, dump maps, tape metadata, current command, terminal stream, byte-swap flags, and old inode format flag.
- Defines `struct entry`, the in-memory restore symbol-table node for files/directories/links.
- Defines entry types `LEAF`, `NODE`, `LINK` and flags such as `EXTRACT`, `NEW`, `KEEP`, `REMOVED`, `TMPNAME`, and `EXISTED`.
- Defines `struct context curfile`, describing the next file/header on tape with mode, ownership, timestamps, flags, device, size, extattr size, inode, and name.
- Defines `RST_DIR`, `FORCE`, inode bitmap macros `TSTINO`/`SETINO`, conditional `dprintf`/`vprintf`, and status constants.

Integration: every restore source file depends on this header for the shared model. The `entry` graph and `curfile` context are the main internal contracts between tape reading, directory scanning, symbol-table operations, and extraction.

Risk notes: global variables and macros make state dependencies implicit. Bitmap macros assume valid inode ranges and map allocation sized by `maxino`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/restore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/symtab.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/symtab.c

Purpose: maintains restore’s in-memory symbol table and serializes/deserializes it for checkpoint and restart.

Key functions:
- `lookupino()` and `lookupname()` provide inode and pathname lookup.
- `addentry()`, `freeentry()`, `moveentry()`, `deleteino()`, and internal `removeentry()` maintain the tree, inode hash chains, and hard-link chains.
- `myname()` reconstructs a full pathname by walking parent pointers.
- `savename()` and `freename()` implement a small free-list allocator for path component strings.
- `dumpsymtable()` writes string data, pointer-indexed `entry` records, hash table indices, and a trailing `symtableheader`.
- `initsymtable()` either initializes a new root table or reads a checkpoint and converts serialized indices back into pointers.

Integration: consumed by incremental restore and interactive/extract modes. Checkpoint data includes volume number, string size, entry table size, dump times, `maxino`, and tape block count so `restore -R` can resume extraction.

Risk notes: serialization stores pointer fields as integer-like indices through casts, so format is tightly coupled to `struct entry` layout and native ABI. The string allocator assumes `NAME_MAX`-bounded component sizes. Path reconstruction uses one static buffer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/symtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/tape.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/tape.c

Purpose: tape/input I/O core for `restore`, including dump header validation, volume changes, block buffering, file extraction, extended attributes, and byte swapping.

Key functions:
- `setinput()` configures local file, stdin pipe, pipe command, or optional remote tape input and drops privileges to the real UID.
- `setup()` opens volume 1, detects block size, validates dump headers, initializes `usedinomap` and `dumpmap`, and sets dump metadata.
- `getvol()` prompts/opens later volumes, validates dump dates and volume numbers, and resumes active file extraction when needed.
- `extractfile()` creates filesystem objects for regular files, symlinks, directories, FIFOs, devices, sockets, and applies metadata.
- `set_extattr()` restores UFS extended attributes and has ACL-specific fallback paths.
- `getfile()` walks dump block maps, dispatching data, extattr, and sparse-hole callbacks.
- `readtape()`, `gethead()`, `findinode()`, and `findtapeblksize()` manage buffered reads, errors, EOT, resynchronization, and header normalization.
- `swabst()` and helpers support opposite-endian or old-format dumps.

Integration: drives `curfile` and `spcl`, feeding all higher-level restore logic. It calls into directory extraction, file creation, maps, volume checkpointing, and external remote tape functions when compiled with `RRESTORE`.

Risk notes: this is the most error-sensitive module. It uses `setjmp`/`longjmp` for volume continuation, many globals for tape position, and manual buffer management. Corrupt media paths rely on `Dflag`/`yflag` recovery choices and checksum/header validation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/tape.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/utilities.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/utilities.c

Purpose: filesystem operation helpers and diagnostics used across restore.

Key functions:
- `pathcheck()` ensures parent directory entries exist in the symbol table and creates missing directories when extracting by name.
- `mktempname()` and `gentempname()` generate and apply collision-safe temporary names for rename/deletion choreography.
- `renameit()`, `newnode()`, `removenode()`, `removeleaf()`, `linkit()`, `addwhiteout()`, and `delwhiteout()` perform filesystem mutations with `Nflag` dry-run support.
- `lowerbnd()` and `upperbnd()` locate the next/last inode needing extraction.
- `badentry()`, `flagvalues()`, `dirlookup()`, `reply()`, and `panic()` provide diagnostics, prompting, and recoverable/fatal consistency handling.

Integration: called by restore reconciliation, extraction, directory mode replay, and interactive selection. It is the abstraction layer between symbol-table decisions and live filesystem effects.

Risk notes: helpers often continue after filesystem warnings to support best-effort restore. `panic()` returns instead of exiting when `yflag` is set, so callers must tolerate continuing after inconsistencies.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/utilities.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/route/Makefile

Purpose: FreeBSD build definition for the `route` utility.

Behavior:
- Builds `PROG=route` with `route.c` and generated `keywords.h`.
- Adds `-DINET` and `-DINET6` depending on build options.
- Adds `route_netlink.c` unless netlink support is disabled; otherwise defines `WITHOUT_NETLINK`.
- Adds jail support and `libjail` when enabled and not in rescue builds.
- Enables tests via `SUBDIR.${MK_TESTS}+= tests`.
- Generates `keywords.h` from the `keywords` file using `awk`.

Integration: controls whether `route.c` uses the netlink backend or legacy routing-socket backend. The generated keyword table is included directly by `route.c`.

Risk notes: feature set depends on FreeBSD build options; command behavior changes notably with `MK_NETLINK_SUPPORT`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/route.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/route/route.c

Purpose: main implementation of the FreeBSD `route` command: add/change/delete/get/show/flush/monitor routes.

Key functions:
- `main()` parses global flags, optional jail attachment, FIB defaults, and command dispatch.
- `newroute()` parses route modifiers, destination/gateway/netmask/FIB arguments, metrics, flags, and executes per-FIB mutations.
- `rtmsg()` abstracts backend dispatch to netlink or routing socket.
- Legacy routing-socket paths include `rtmsg_rtsock()`, `flushroutes_fib_rtsock()`, and `monitor_rtsock()` when built without netlink.
- `flushroutes()` and `flushroutes_fib()` purge gateway routes by FIB and address family.
- `getaddr()`, `prefixlen()`, `inet_makemask()`, and `inet6_makenetandmask()` parse CLI address forms.
- `routename()`, `netname()`, `print_getmsg()`, `print_rtmsg()`, `pmsg_common()`, `pmsg_addrs()`, `printb()`, and `sodump()` format output and diagnostics.
- `fiboptlist_csv()` and `fiboptlist_range()` parse single, comma, range, `all`, and `default` FIB selections.

Integration: compiled with generated `keywords.h`; calls netlink functions from `route_netlink.c` unless `WITHOUT_NETLINK` is set. Uses FreeBSD routing APIs, jails, FIB sysctls, `ifaddrs`, and address-family conditionals.

Risk notes: many global parser variables are reused per invocation. FIB parsing has strict validation against `net.fibs` when available. Address parsing mutates strings temporarily for CIDR syntax. Legacy backend has explicit read timeout for `RTM_GET`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/route.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/route_netlink.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/route/route_netlink.c

Purpose: netlink backend for the FreeBSD `route` command.

Key functions:
- `nl_init_socket()` opens `NETLINK_ROUTE`, attempting to load the `netlink` kernel module if needed.
- `rtmsg_nl_int()` translates route command requests into netlink route messages with destination prefix, table/FIB, gateway, output interface, route flags, metrics, expiration, priority, and weight.
- `rtmsg_nl()` wraps helper setup/teardown around one command.
- `print_getmsg()` and `print_nhop_getmsg()` display route lookup results, including next-hop view when `-o` is used.
- `monitor_nl()` subscribes to link, neighbor, nexthop, IPv4, and IPv6 route/address multicast groups and prints events.
- `print_nlmsg_route()`, `print_nlmsg_link()`, `print_nlmsg_addr()`, and `print_nlmsg_neigh()` format monitor events.
- `flushroutes_fib_nl()` dumps routes for a table/family and deletes gateway routes through `flushroute_one()`.

Integration: called from `route.c` through declared backend functions. Uses FreeBSD simple netlink (`snl_*`) route parsers and writers. Reuses `route.c` formatting helpers `routename()`, `netname()`, `printb()`, and `routeflags`.

Risk notes: route socket and netlink semantics are translated manually, especially around prefixes, gateways, link-local scope IDs, and route flags. Some monitor output is informational rather than a stable machine format. `flushroute_one()` contains unreachable warning code after an early return in one error branch.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/route_netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/route/tests/Makefile

Purpose: test build definition for `sbin/route`.

Behavior:
- Registers shell ATF test `basic`.
- Marks `basic` as exclusive because tests reuse jail names.
- Installs `utils.subr` as a test support file.
- Includes `bsd.test.mk`.

Integration: pairs with `basic.sh`, which relies on VNET jail helper functions and route lookup helpers from `utils.subr`.

Risk notes: tests require root, jails, and `jq`; exclusive metadata prevents parallel jail-name collisions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/tests/basic.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/route/tests/basic.sh

Purpose: ATF shell tests for basic `route` add/change/delete and interface route behavior.

Test cases:
- `basic_v4`: creates an epair/VNET jail, adds an IPv4 route, verifies gateway, changes it, verifies again, deletes it, and checks absence.
- `basic_v6`: same lifecycle for IPv6 with `-6` and `no_dad`.
- `interface_route_v4`: adds an IPv4 interface route using `-iface`.
- `interface_route_v6`: adds an IPv6 interface route using `-iface`.
- Each test cleans up through `vnet_cleanup`.

Integration: sources `utils.subr` for jail/network helpers such as `vnet_mkepair`, `vnet_mkjail`, `check_route`, and cleanup. Exercises actual `route` command behavior inside a jail.

Risk notes: tests require root, `jail`, and `jq`. They verify gateway presence/value, not full route flags or backend-specific monitor/get output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/route/tests/basic.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/Makefile

Purpose: FreeBSD build definition for the `routed` RIP daemon.

Behavior:
- Builds `PROG=routed` in package `rip`.
- Uses source files `if.c`, `input.c`, `main.c`, `output.c`, `parms.c`, `radix.c`, `rdisc.c`, `table.c`, and `trace.c`.
- Installs `routed.8`.
- Links against `libmd`.
- Builds `rtquery` as a subdirectory.
- Includes `bsd.prog.mk`.

Integration: this makefile ties the shared definitions in `defs.h` to the daemon modules that implement interface discovery, RIP input/output, router discovery, route table management, tracing, and parameter parsing.

Risk notes: warning level is `WARNS?=3`, reflecting older C code style. Build is specific to FreeBSD’s system make infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/Makefile.inc -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/Makefile.inc

Purpose: small include file for routed-related subdirectories.

Behavior:
- Sets `PACKAGE=rip`.
- Includes parent `../Makefile.inc`.

Integration: shares package classification and parent build settings with `routed` subcomponents such as `rtquery`.

Risk notes: minimal file; behavior depends entirely on the parent include.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/defs.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/defs.h

Purpose: central shared definitions for the FreeBSD `routed` RIPv2 routing daemon.

Contents:
- Includes system networking, routing, socket, radix, sysctl, and RIP protocol headers.
- Defines routing constants, timer intervals, packet buffer sizes, router discovery constants, and helper macros.
- Defines `struct rt_entry`, route state flags, route spares/alternate gateways, and route selection macro `BETTER_LINK`.
- Defines `struct interface` with address/mask data, flags, RIP state, authentication keys, statistics, and router discovery state.
- Defines extensive interface state flags for aliases, remote/passive/external interfaces, RIP input/output policy, multicast, router discovery, aggregation, and health.
- Defines aggregation structures `ag_info`, parameter structures `parm`, internal-network/trusted-router lists, output buffers, global state externs, tracing globals, and radix root.
- Declares cross-module functions for sockets, RIP I/O, logging, parameters, tracing, router discovery, route aging/table operations, address masks, interface lookup/health, and authentication.

Integration: included by most `routed` daemon implementation files. It is the daemon’s shared ABI: route table, interface inventory, timers, authentication, tracing, RIP output, and kernel route synchronization all meet here.

Risk notes: very high coupling through global externs and macros. Many bit flags interact, so behavior depends on consistent flag interpretation across modules. The daemon is IPv4/RIP-focused and uses FreeBSD-specific routing and interface APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/defs.h -->