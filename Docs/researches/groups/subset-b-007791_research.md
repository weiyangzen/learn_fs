# subset-b-007791 Research

Grouped research for OpenAFS platform-specific build/support files, the process-management library, and protection-server utilities. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/Makefile.in

## Purpose
Builds the Darwin `growlagent-openafs` helper, an Objective-C notification bridge for OpenAFS Venus Monitor events. The makefile compiles `main.o`, links it as an executable against Apple `Security`, `AppKit`, and `CoreFoundation`, and packages it into a `.app` layout for destination installs.

## Important APIs, Types, And Functions
The important targets are `all`, `growlagent-openafs`, `main.o`, `clean`, `install`, and `dest`. `main.o` depends on `GrowlDefines.h` and `GrowlPathway.h`, reflecting the source file's Growl bridge API surface. The `dest` target creates `Contents/MacOS`, `Contents/Resources/MacOS`, and `Contents/Resources`, then installs the executable, `Andy.icns`, and `Info.plist`.

## Control Flow
Normal build flow includes repository configuration and pthread rules, compiles `main.m` through the implicit rules, then runs `$(AFS_LDRULE)` with the required Cocoa/CoreFoundation frameworks. The packaging path is destination-only; `install` is intentionally empty, while `dest` stages an app bundle under `${DEST}/tools/growlagent-openafs.app`.

## State And Persistence
The only persistent artifacts are `main.o`, `growlagent-openafs`, and staged bundle contents. `clean` removes local objects and the executable but not installed bundles.

## Dependencies And Integration Points
Depends on top-level OpenAFS make configuration, Apple frameworks, and Growl headers/resources in the same directory. It integrates Darwin packaging with the broader OpenAFS `DEST` staging model.

## Risks And Test Signals
Risks are obsolete Growl framework assumptions, app bundle path correctness, and the empty `install` target differing from `dest`. Test signals are a successful Darwin build, correct framework linkage, bundle launchability, and presence of `Info.plist` and icon resources in the staged app.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/main.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/main.m

## Purpose
Implements a Darwin Growl notification agent for OpenAFS. It listens on UDP port `2106` for Venus Monitor messages, converts message prefixes such as `fetch$`, `store$`, and `warn$` into Growl notification metadata, and posts notifications either through `GrowlApplicationBridgePathway` or `NSDistributedNotificationCenter`.

## Important APIs, Types, And Functions
Key functions are `getPath`, `MyTransmit`, `BuildNotificationInfo`, `MySocketReadCallBack`, `readFile`, and `main`. The file uses CoreFoundation types (`CFNotificationCenterRef`, `CFDictionaryRef`, `CFDataRef`, `CFSocketRef`), Objective-C `NSConnection`/`NSDistantObject`, and Growl constants/protocols from `GrowlDefines.h` and `GrowlPathway.h`. `GrowlCBContext` carries the distributed notification center, registration dictionary, and icon data into the socket callback.

## Control Flow
`main` loads `Andy.icns`, constructs a Growl registration dictionary for the single `OpenAFS Venus Monitor` notification class, creates an IPv4 UDP socket bound to `INADDR_ANY:2106`, registers `MySocketReadCallBack` as a CoreFoundation read callback, adds the socket source to the current run loop, and blocks in `CFRunLoopRun`. On datagram receipt, the callback null-terminates the received buffer and calls `BuildNotificationInfo`, which chooses notification text, priority, and identifier based on the prefix. `MyTransmit` first tries direct Growl IPC and falls back to distributed notifications.

## State And Persistence
Runtime state is held in CoreFoundation objects, the UDP socket, and the callback context. There is no disk persistence beyond reading the bundled icon. Notifications are transient, with generated UUID click context values.

## Dependencies And Integration Points
Integrates OpenAFS cache-manager monitor output with macOS Growl. It depends on Foundation/AppKit/CoreFoundation, Mach-O executable path APIs, BSD sockets, and legacy Growl IPC/distributed notification contracts.

## Risks And Test Signals
Risks include legacy Growl availability, unchecked `recvfrom` return handling when `result <= 0`, possible CF object leaks for created description strings and UUIDs, and binding conflicts on UDP port 2106. Test signals are successful socket bind, correct notification registration, messages for all known prefixes, fallback behavior when Growl IPC is unavailable, and run-loop cleanup on termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/main.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DFBSD/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/DFBSD/Makefile.in

## Purpose
Provides the DragonFly BSD platform directory makefile placeholder. It declares that this platform has no platform-specific userland support objects in this subtree.

## Important APIs, Types, And Functions
The only targets are `all`, `install`, `dest`, and `clean`, each intentionally empty. `SHELL=/bin/sh` is set for consistency with other platform makefiles.

## Control Flow
When the top-level platform dispatcher enters this directory, all build/install/clean phases complete immediately without producing artifacts.

## State And Persistence
No build outputs, installed files, or generated state are created.

## Dependencies And Integration Points
This file is reached through `src/platform/Makefile.in` via `$(MKAFS_OSTYPE)`. Its presence keeps the platform dispatch stable even though DragonFly BSD has no specific code here.

## Risks And Test Signals
The main risk is false confidence: a successful target means only that no platform support is required here. Test signal is that DragonFly BSD platform builds do not fail due to a missing directory or makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DFBSD/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/FBSD/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/FBSD/Makefile.in

## Purpose
Provides the FreeBSD platform makefile placeholder for an otherwise empty platform-specific support directory.

## Important APIs, Types, And Functions
Defines no-op `all`, `install`, `dest`, and `clean` targets, plus `SHELL=/bin/sh`.

## Control Flow
Platform dispatch can `cd` into `FBSD` and run any standard target without building or staging files.

## State And Persistence
No artifacts or persistent state are produced.

## Dependencies And Integration Points
Integrated by `src/platform/Makefile.in` through `$(MKAFS_OSTYPE)`. It protects FreeBSD builds from missing-target failures while leaving actual FreeBSD support elsewhere in the tree.

## Risks And Test Signals
Risk is that future FreeBSD-specific files added to this directory would need real target wiring. Test signal is successful no-op execution under FreeBSD build configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/FBSD/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/HPUX/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/HPUX/Makefile.in

## Purpose
Declares an empty HP-UX platform-specific support directory.

## Important APIs, Types, And Functions
The makefile exposes standard no-op targets: `all`, `install`, `dest`, and `clean`.

## Control Flow
All standard invocations return successfully without compiling or installing anything.

## State And Persistence
No state, build outputs, or destination files are generated.

## Dependencies And Integration Points
Used by the platform dispatcher when `MKAFS_OSTYPE` selects `HPUX`. HP-UX-specific behavior in nearby code is handled through conditional compilation, not this makefile.

## Risks And Test Signals
Risk is target drift if platform artifacts are later added. Test signal is that HP-UX platform dispatch remains valid and no unexpected artifacts appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/HPUX/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/IRIX/Makefile.in

## Purpose
Builds IRIX authentication interposition shared libraries for remote shell/login integration. It links `sgi_auth.o` with AFS authentication libraries and helper objects (`ta-rauth.o`, `rcmd.o`, `herror.o`) to produce `afsauthlib.so` and Kerberos-flavored `afskauthlib.so`.

## Important APIs, Types, And Functions
Key variables are `AFSLIBS`, `KAFSLIBS`, `AUTHFILES`, `AUTHLIBS`, and `TARGETS`. Build products are installed into `${TOP_LIBDIR}` for in-tree use, `${DESTDIR}${libdir}` for install, or `${DEST}/root.client/usr/vice/etc` for legacy destination staging.

## Control Flow
`all` builds both shared libraries in the top library directory. The local shared-library targets invoke `$(LD) -shared -all` with either normal or Kerberos auth libraries. `install` and `dest` stage both libraries. Object rules are simple source-to-object dependencies.

## State And Persistence
Build state includes helper objects and the two `.so` files. Install/dest state persists shared libraries where IRIX client authentication mechanisms can load them.

## Dependencies And Integration Points
Depends on LWP-era OpenAFS libraries: kauth, prot, ubik, auth, rxkad, sys, rx, crypto, lwp, cmd, com_err, and util. Integrates IRIX login/rsh authentication paths with AFS tokens through `sgi_auth.c`, `ta-rauth.c`, and `rcmd.c`.

## Risks And Test Signals
Risks include very old IRIX linker flags, static library ordering, Kerberos/non-Kerberos variant drift, and the possibility that installing these libraries changes login behavior. Test signals are successful IRIX link, exported symbols expected by the OS authentication loader, and validated authenticated/unauthenticated remote login behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/herror.c -->
# sources/distributed-fs/openafs/src/platform/IRIX/herror.c

## Purpose
Provides a compatibility implementation of BSD `herror` and host lookup error strings for platforms that do not supply them, excluding Darwin.

## Important APIs, Types, And Functions
Defines `h_errlist`, `h_nerr`, and `herror(char *s)`. On Sun environments it defines `h_errno`; elsewhere it expects an external `h_errno`. `herror` emits an optional caller prefix, a host-error message, and newline using `writev` to file descriptor 2.

## Control Flow
`herror` builds a small `struct iovec` array. If the caller provided a non-empty prefix, it adds prefix and `": "`. It then indexes `h_errlist` when `h_errno` is in range, otherwise prints `"Unknown error"`, adds a newline vector, and calls `writev`.

## State And Persistence
Static/global state is limited to the error string table, count, and platform-dependent `h_errno`. The function writes only to stderr and persists nothing.

## Dependencies And Integration Points
Used by legacy remote command code such as `rcmd.c` when `gethostbyname` fails. Depends on BSD-ish `uio.h`, `writev`, `strlen`, and OpenAFS platform macros.

## Risks And Test Signals
Risks include K&R-style implicit `int` return, limited error table coverage, and potential mismatch with modern resolver thread-local `h_errno` semantics. Test signals are successful builds on target legacy platforms and correct diagnostics for failed remote host lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/herror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/rcmd.c -->
# sources/distributed-fs/openafs/src/platform/IRIX/rcmd.c

## Purpose
Implements BSD-compatible `rcmd`, `rresvport`, `ruserok`, and helper host/user validation routines with AFS remote-authentication support. It is used by IRIX/legacy remote shell integration to obtain reserved-port connections and optionally transfer AFS token authentication before falling back to classic rsh protocol behavior.

## Important APIs, Types, And Functions
Main APIs are `rcmd` (or `rmcd` on HP-UX 10.2), `rresvport`, `ruserok`, `_validuser`, and static `_checkhost`. `rcmd` coordinates `gethostbyname`, reserved-port sockets, `ta_rauth`, `connect`, secondary stderr-channel setup, and command/user string transmission. `ruserok` checks `/etc/hosts.equiv` and user `.rhosts` with ownership and mode validation.

## Control Flow
`rcmd` resolves the host, blocks `SIGURG`, creates a reserved local port, attempts AFS token remote auth via `ta_rauth` when a TCP service name exists, and otherwise connects to the requested remote service with retry/backoff for connection refusal and address-list fallback. If `fd2p` is requested, it opens another reserved port, sends that port number, accepts the reverse stderr connection, and verifies the peer uses a reserved port. It then writes local user, remote user, and command NUL-terminated strings and waits for the remote status byte. `ruserok` lowercases hosts, checks global and per-user trust files, temporarily switches effective uid/gid for `.rhosts`, and restores credentials.

## State And Persistence
State is mostly transient sockets and effective credential changes. `_check_rhosts_file` controls whether user `.rhosts` is consulted. `_checkhost` caches the local domain suffix.

## Dependencies And Integration Points
Depends on BSD sockets, reserved ports, resolver APIs, syslog, passwd/group APIs, and the OpenAFS `ta_rauth` token-transfer function. It plugs AFS token authentication into existing rsh/rlogin-style flows.

## Risks And Test Signals
Major risks are the inherent insecurity of r-commands, reserved-port trust assumptions, global resolver storage, credential-switch restoration on error paths, fixed-size buffers, and platform-specific signal-mask construction. Test signals are successful authenticated and fallback rsh connections, bad-host/address fallback behavior, stderr-channel validation, `.rhosts` permission rejection, and no leaked effective uid/gid after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/rcmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/sgi_auth.c -->
# sources/distributed-fs/openafs/src/platform/IRIX/sgi_auth.c

## Purpose
Provides IRIX-specific AFS password verification helpers for login/authentication integration.

## Important APIs, Types, And Functions
Exports `afs_verify` and `afs_gettktstring` when `AFS_SGI_ENV` is defined. `afs_verify` calls `ka_Init` and `ka_UserAuthenticateGeneral` with `KA_USERAUTH_DOSETPAG` to authenticate a user password and establish a PAG/token side effect. `afs_gettktstring` returns the cache/ticket path via `ktc_tkt_string`.

## Control Flow
`afs_verify` initializes kauth, calls the general user-authentication routine with username, password, default realm/cell, default lifetime, and an output expiration pointer. On failure it optionally prints the kauth reason and tells the caller to continue with local authentication by returning `1`; on success it returns `0`.

## State And Persistence
Successful authentication may establish process authentication group state and AFS tokens through the kauth/ktc layers. The file itself stores no static state.

## Dependencies And Integration Points
Depends on SGI platform macros, `kauth.h`, `kautils.h`, and the token-cache API. It is linked into IRIX authentication shared libraries by the sibling makefile.

## Risks And Test Signals
Risks include obsolete kauth password authentication, plaintext password handling, typoed `quite` parameter naming, and behavior that falls back to local auth after AFS failure. Test signals are correct return codes for valid/invalid AFS passwords, PAG/token creation, expiration output, and quiet/non-quiet diagnostic behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/sgi_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/ta-rauth.c -->
# sources/distributed-fs/openafs/src/platform/IRIX/ta-rauth.c

## Purpose
Transfers an existing local AFS token to a remote authentication service before an r-command connection proceeds. It is the token-authentication companion for `rcmd.c`.

## Important APIs, Types, And Functions
Exports `ta_rauth(int s, char *svc_name, struct in_addr raddr)` and `outtoken`. `ta_rauth` opens the client configuration, discovers the local cell, retrieves the `afs` service token with `ktc_GetToken`, connects the provided socket to `RAUTH_PORT` (default 601), sends token material with `outtoken`, and reads a one-byte allow/deny result. Global `ta_debug` enables syslog/perror diagnostics.

## Control Flow
The function returns `0` when no token or refused authenticator means the caller should continue without remote auth, `1` for successful remote authentication, `-1` for remote denial, `-2` for local/internal failures, and `-3` for remote connection failures. `outtoken` serializes service name, version, cell, token start/end times, session key, kvno, ticket length, and ticket bytes into a stack buffer, then writes it to the socket.

## State And Persistence
Reads local AFS client configuration and token-cache state but writes no persistent state. Network output includes sensitive token/session-key data.

## Dependencies And Integration Points
Depends on `afsconf`, `ktc`, socket APIs, syslog, and the remote auth daemon protocol expected on port 601. Called from `rcmd` before classic rsh fallback.

## Risks And Test Signals
Risks are cleartext token transfer unless protected externally, `sprintf`/fixed 1024-byte buffer sizing against ticket length, exit-on-short-read behavior, and stale kauth-era token assumptions. Test signals include no-token fallback, ECONNREFUSED fallback, timeout/unreachable error mapping, remote allow/deny handling, and protocol compatibility with the authenticator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/IRIX/ta-rauth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/LINUX/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/LINUX/Makefile.in

## Purpose
Declares that Linux has no buildable platform-specific files in this `src/platform` subdirectory.

## Important APIs, Types, And Functions
Defines no-op `all`, `install`, `dest`, and `clean` targets.

## Control Flow
The platform dispatcher can enter `LINUX` and run standard make targets without producing artifacts.

## State And Persistence
No files are generated or installed.

## Dependencies And Integration Points
This is selected by `src/platform/Makefile.in` for Linux platform dispatch. Linux-specific OpenAFS behavior is elsewhere in the source tree.

## Risks And Test Signals
Risk is only future drift if platform files are introduced here. Test signal is no-op success during Linux builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/LINUX/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/Makefile.in

## Purpose
Provides the common dispatcher makefile for `src/platform`, routing standard targets into the OS-specific subdirectory named by `$(MKAFS_OSTYPE)`.

## Important APIs, Types, And Functions
Targets are `all`, `clean`, `dest`, and `install`. Each target performs `cd $(MKAFS_OSTYPE) && $(MAKE) ...`, passing `DEST` or `DESTDIR` for staging/install targets.

## Control Flow
Top-level builds enter `src/platform`, include `Makefile.config`, and delegate work to exactly one platform directory. Version generation is included through `../config/Makefile.version`.

## State And Persistence
This file creates no artifacts directly; all state is produced by the selected platform child makefile.

## Dependencies And Integration Points
Depends on `MKAFS_OSTYPE` from OpenAFS configuration and on the existence of a matching subdirectory with compatible targets. It integrates Darwin, IRIX, Solaris, BSD, Linux, and other platform directories into the main build.

## Risks And Test Signals
Risks include unset or mismatched `MKAFS_OSTYPE`, missing platform directories, and target incompatibility in child makefiles. Test signals are successful target delegation for every configured OS type and correct propagation of destination variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/NBSD/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/NBSD/Makefile.in

## Purpose
Provides an empty NetBSD platform-specific makefile so platform dispatch has standard targets.

## Important APIs, Types, And Functions
Exposes no-op `all`, `install`, `dest`, and `clean` targets.

## Control Flow
All standard target invocations complete without invoking compilers or installers.

## State And Persistence
No persistent state or build output is created.

## Dependencies And Integration Points
Selected by the common platform dispatcher for NetBSD builds.

## Risks And Test Signals
Risk is future platform work not wired into these targets. Test signal is successful no-op dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/NBSD/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/OBSD/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/OBSD/Makefile.in

## Purpose
Provides an empty OpenBSD platform-specific makefile.

## Important APIs, Types, And Functions
Defines standard no-op `all`, `install`, `dest`, and `clean` targets.

## Control Flow
The common platform makefile can delegate into `OBSD` for any standard phase without doing work.

## State And Persistence
No artifacts are generated, installed, or removed.

## Dependencies And Integration Points
Serves the OpenBSD branch of `$(MKAFS_OSTYPE)` platform dispatch.

## Risks And Test Signals
Risk is only missing target updates if this directory gains real code. Test signal is successful OpenBSD build traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/OBSD/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/SOLARIS/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/SOLARIS/Makefile.in

## Purpose
Builds and stages the Solaris `fs_conv_sol26` utility, which converts AFS partition inode metadata between pre-SunOS 5.6 and SunOS 5.6-compatible formats.

## Important APIs, Types, And Functions
Important variables are `INCLS` and `LIBS`, covering AFS interfaces, command parsing, inode, sys, dir, LWP, and ACL libraries. Targets include `all`, `fs_conv_sol26`, `install`, `dest`, and `clean`. The executable depends on `fs_conv_sol26.o`, OpenAFS command/sys/dir libraries, roken, and component version generation.

## Control Flow
`all` builds `fs_conv_sol26`. The link rule invokes `$(AFS_LDRULE)` with `fs_conv_sol26.o`, `libcmd`, roken, other OpenAFS libraries, and `${XLIBS}`. `install` places the binary under `${afssrvsbindir}`; `dest` stages it under `root.server/usr/afs/bin`.

## State And Persistence
Build artifacts include `fs_conv_sol26.o`, `AFS_component_version_number.c`, and the executable. Install/dest targets persist a server administration binary.

## Dependencies And Integration Points
Depends on Solaris UFS/inode headers consumed by the C source and OpenAFS server tooling paths. It integrates a one-off filesystem migration utility into server install images.

## Risks And Test Signals
Risks include obsolete Solaris UFS layout assumptions, library-order sensitivity, and installing a destructive disk utility. Test signals are successful Solaris build, correct destination path, and controlled dry-run/force behavior in the tool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/SOLARIS/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/SOLARIS/fs_conv_sol26.c -->
# sources/distributed-fs/openafs/src/platform/SOLARIS/fs_conv_sol26.c

## Purpose
Implements `fs_conv_sol26`, a root-only Solaris utility that converts raw AFS partition inode metadata between pre-SunOS 5.6 and SunOS 5.6 encodings, with a reverse `unconvert` mode.

## Important APIs, Types, And Functions
Key routines are `main`, `ConvCmd`, `UnConvCmd`, `handleit`, `ProcessFileSys`, `ProcessAfsInodes`, `bread`, `vol_DevName`, `rawname`, `unrawname`, `blockcheck`, `EnsureDevice`, and `CheckMountedDevice`. Global flags `force`, `verbose`, and `unconv` control dry-run/output/direction. The utility uses `struct fs`, `struct dinode`, `vfstab`, `mnttab`, and OpenAFS `VICEMAGIC`, `UID_LONG`, and `GID_LONG` inode conventions.

## Control Flow
`main` requires root, defines `convert` and `unconvert` command syntaxes, and dispatches through the OpenAFS command package. `handleit` parses `-part`, `-device`, `-verbose`, and `-force`; it maps AFS partition names through `/etc/vfstab` or processes explicit raw devices after `CheckMountedDevice`. `ProcessAfsInodes` opens the raw device read-write, validates the UFS superblock, reads cylinder-group inode arrays, classifies AFS inodes by generation/flags/uid/gid fields, and when `-force` is present rewrites uid/gid/large-size fields to the target format.

## State And Persistence
Without `-force`, the utility only reports planned changes. With `-force`, it directly writes modified inode blocks to the raw filesystem device. It also reads `/etc/vfstab`, `/etc/mnttab`, and device nodes under `/dev`.

## Dependencies And Integration Points
Depends tightly on Solaris UFS on-disk structures and OpenAFS partition naming (`/vicep*`). It is an administrative migration tool, not a normal server runtime dependency.

## Risks And Test Signals
Risks are severe: raw-device writes can corrupt mounted or non-AFS filesystems, buffer sizes are fixed, some helpers use static small path buffers, and mounted-device checks allow interactive override. Test signals include dry-run counts, superblock validation, refusal without `-force`, mounted-device prompts, and validation on disposable UFS images before production use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/SOLARIS/fs_conv_sol26.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/Makefile.in -->
# sources/distributed-fs/openafs/src/procmgmt/Makefile.in

## Purpose
Builds and installs the OpenAFS process-management library and public process/signal compatibility headers.

## Important APIs, Types, And Functions
Targets build `${TOP_LIBDIR}/libprocmgmt.a`, install `${TOP_INCDIR}/afs/procmgmt.h`, and install `${TOP_INCDIR}/afs/procmgmt_softsig.h`. `libprocmgmt.a` is assembled from `procmgmt_unix.o` and `AFS_component_version_number.o` in this Unix build path. `buildtools` exposes only the public header.

## Control Flow
`all` ensures the library and headers are available in top-level build output. `install` stages the library under `${libdir}/afs` and headers under `${includedir}/afs`; `dest` mirrors that into `${DEST}/lib/afs` and `${DEST}/include/afs`. `clean` removes local archive/object/version artifacts.

## State And Persistence
Build artifacts are `libprocmgmt.a`, object files, and generated component version source. Install/dest persist a static library and public headers for other OpenAFS components.

## Dependencies And Integration Points
Includes OpenAFS config and LWP make fragments. The Unix archive exposes spawn wrappers used by portable OpenAFS code, while NT-specific sources are present for Windows builds outside this Unix make path.

## Risks And Test Signals
Risks include platform divergence between Unix and NT implementations and consumers expecting NT-only APIs from a Unix archive. Test signals are archive creation, header installation, and successful consumers using `spawnprocve`/`spawnprocv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/afskill.c -->
# sources/distributed-fs/openafs/src/procmgmt/afskill.c

## Purpose
Implements an AFS-aware `kill` command front-end that uses the process-management `kill` abstraction. It is intended especially for Windows NT, where non-`SIGKILL` signaling works only for processes linked with the OpenAFS process-management library.

## Important APIs, Types, And Functions
Defines `signal_map_t`, static `signalMap`, `PrintSignalList`, `SignalArgToNumber`, `PrintUsage`, and `main`. It recognizes names such as `HUP`, `INT`, `TERM`, `KILL`, `USR1`, `CHLD`, and `TSTP`, plus numeric signals parsed by `strtol`.

## Control Flow
`main` derives the program basename, handles no-argument usage, `-l` signal listing, or signal delivery. A leading `-signal` argument changes the default signal from `SIGTERM`. Remaining arguments are parsed as positive pids and passed to `kill((pid_t)pid, signo)`. Errors are mapped to user-facing diagnostics for invalid signal, no such process, permission, or generic errno.

## State And Persistence
No persistent state. The only external effect is process signaling or termination through the platform `kill` implementation.

## Dependencies And Integration Points
Depends on `procmgmt.h` for portable signal constants and `kill` macro/function behavior. On NT this routes to named-pipe or `TerminateProcess`; on Unix it is the native signal API.

## Risks And Test Signals
Risks include sending unintended signals, platform-specific support gaps for non-AFS Windows processes, and accepting numeric signals outside the named table until lower layers reject them. Test signals include `-l`, invalid pid handling, self-signal tests, non-existent pid mapping, and SIGKILL fallback behavior on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/afskill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/pmgtprivate.h -->
# sources/distributed-fs/openafs/src/procmgmt/pmgtprivate.h

## Purpose
Declares private process-management support that should not be exported through public `procmgmt.h`, primarily for Windows NT signal emulation internals.

## Important APIs, Types, And Functions
For `AFS_NT40_ENV`, defines `PMGT_SIGSTATUS_ENCODE`, `PMGT_IS_SIGSTATUS`, and `PMGT_SIGSTATUS_DECODE`, which encode a Unix-like signal termination into a Windows process exit status. Declares `pmgt_SignalRaiseLocalByName`, `pmgt_RedirectNativeSignals`, and `pmgt_RestoreNativeSignals`.

## Control Flow
The macros are used by NT signal/default-action code to translate process exit codes back into wait statuses. Native signal redirection code raises library signals by name to avoid including `procmgmt.h` where it would redefine `signal`/`raise`.

## State And Persistence
The header declares no storage. It defines an exit-status encoding contract that persists across parent/child process boundaries until `waitpid` decodes it.

## Dependencies And Integration Points
Integrated by `procmgmt_nt.c` and `redirect_nt.c`. It is intentionally separated from public headers to avoid exposing NT implementation details.

## Risks And Test Signals
Risks are encoding collisions with real process exit codes and drift between encoder/decoder users. Test signals are Windows `waitpid` reporting `WIFSIGNALED`/`WTERMSIG` correctly for default signal actions and abort/native signal redirection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/pmgtprivate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt.h -->
# sources/distributed-fs/openafs/src/procmgmt/procmgmt.h

## Purpose
Provides OpenAFS portable process spawning, waiting, and signal APIs. On Windows NT it emulates a Unix-like `pid_t`, `wait`, `waitpid`, `signal`, `sigaction`, `raise`, `kill`, signal sets, and wait-status macros; on Unix it maps spawn wrappers to native fork/exec semantics and includes native signal/wait headers.

## Important APIs, Types, And Functions
Windows definitions include `pid_t`, `WIFEXITED`, `WIFSIGNALED`, `WEXITSTATUS`, `WTERMSIG`, `WNOHANG`, `SIGHUP` through `SIGTSTP`, `NSIG`, `sigset_t`, `struct sigaction`, `pmgt_ProcessSpawnVEB`, `pmgt_ProcessWaitPid`, `pmgt_SigactionSet`, `pmgt_SignalSet`, `pmgt_SignalRaiseLocal`, and `pmgt_SignalRaiseRemote`. Public spawn macros include `spawnprocveb`, `spawnprocve`, `spawnprocve_sig`, and `spawnprocv`. Unix exposes `pmgt_ProcessSpawnVE`.

## Control Flow
Consumers include this header and use familiar Unix names. On NT, macros redirect calls into the process-management DLL/library. On Unix, only spawn helpers are wrapped while native wait/signal behavior remains intact.

## State And Persistence
Declares NT exported `pmgt_spawnData` and `pmgt_spawnDataLen`, a buffer delivered from parent to spawned child. Wait status encodings are part of the cross-process contract.

## Dependencies And Integration Points
Central integration header for `afskill`, procmgmt implementations, and OpenAFS code needing portable process handling. On Windows it must be included before `signal.h`, which it deliberately blocks.

## Risks And Test Signals
Risks include macro substitution surprises, incompatible Windows signal semantics, `NSIG <= 33` assumptions in bitsets, and public ABI drift. Test signals include compiling consumers on Unix and NT, spawn/wait tests, signal handler install/reinstall behavior, and child data buffer delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt_nt.c -->
# sources/distributed-fs/openafs/src/procmgmt/procmgmt_nt.c

## Purpose
Implements the Windows NT process-management library that emulates Unix process spawning, waiting, and software signals for OpenAFS processes.

## Important APIs, Types, And Functions
Major public functions are `pmgt_SigactionSet`, `pmgt_SignalSet`, `pmgt_SignalInit`, `pmgt_SignalRegister`, `pmgt_SignalRaiseLocal`, `pmgt_SignalRaiseLocalByName`, `pmgt_SignalRaiseRemote`, `pmgt_ProcessSpawnVEB`, and `pmgt_ProcessWaitPid`. Important private helpers include `SignalIsDefined`, `DefaultActionHandler`, `ProcessSignal`, `RemoteSignalListenerThread`, `StringArrayToString`, `StringArrayToMultiString`, `ComputeWaitStatus`, `CreateChildDataBuffer`, `ReadChildDataBuffer`, `ChildMonitorThread`, `PmgtLibraryInitialize`, and `DllMain`. Global state includes a signal disposition table, child process table, mutexes, condition variable, named signal pipe, and exported spawn data.

## Control Flow
DLL attach initializes locks, default signal dispositions, child-process table, optional parent-provided spawn data, a per-process named pipe for remote signals, a listener thread, and native signal redirection. Local signals run through `ProcessSignal`; remote signals are delivered with `CallNamedPipe`, ACKed, and executed on a new thread so `SIGKILL` is not blocked behind a stuck handler. Spawning converts argv/envp to Windows command-line/environment strings, optionally creates shared memory for spawn data, starts the child suspended, registers a process-table entry, starts a monitor thread, resumes the child, and waits briefly for data consumption. `waitpid` blocks on `childTermEvent` or returns `0` for `WNOHANG`, then converts Windows exit/exception/signal status to Unix wait status.

## State And Persistence
Runtime persistence is in process-global tables, named pipes (`TransarcAfsSignalPipe<PID>`), named shared memory/events for spawn data, child process handles, and encoded exit statuses. No disk state is written.

## Dependencies And Integration Points
Depends on Win32 process, pipe, event, shared-memory, and signal APIs; pthread mutex/cond wrappers; NT error mapping; security utility ACL updates; and private status encoding in `pmgtprivate.h`. It backs `procmgmt.h` macros and `afskill`.

## Risks And Test Signals
Risks include command-line quoting that rejects embedded quotes, fixed `PMGT_CHILD_MAX`, signal serialization not fully matching POSIX masks, races before a child creates its signal pipe, named-pipe ACL/security behavior, and 10-second spawn-data timeout. Test signals are the `pmgttest` suite, remote/local signal delivery, `SIGKILL` fallback to `TerminateProcess`, exception-to-signal wait decoding, spawn with env/data, and wait/waitpid `ECHILD`/`WNOHANG` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt_softsig.h -->
# sources/distributed-fs/openafs/src/procmgmt/procmgmt_softsig.h

## Purpose
Adapts OpenAFS `opr/softsig.h` soft-signal APIs to the Windows process-management signal implementation.

## Important APIs, Types, And Functions
When `AFS_NT40_ENV` is defined, maps `opr_softsig_Init()` to `pmgt_SignalInit()` and `opr_softsig_Register(sig, handler)` to `pmgt_SignalRegister(sig, handler)`, with declarations for both process-management functions.

## Control Flow
Consumers can include this header after `opr/softsig.h` and call the standard soft-signal names. On NT, macro substitution routes calls to procmgmt; on non-NT platforms the header has no effect.

## State And Persistence
No state is defined here. Runtime state is managed by `procmgmt_nt.c` signal tables.

## Dependencies And Integration Points
Bridges Unix-oriented soft-signal call sites to the NT process-management library without scattering conditional compilation across users.

## Risks And Test Signals
Risks are include-order dependency and signature drift between `opr_softsig` and `pmgt` handlers. Test signals are successful NT compilation of soft-signal consumers and runtime registration/delivery of handlers through procmgmt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt_softsig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt_unix.c -->
# sources/distributed-fs/openafs/src/procmgmt/procmgmt_unix.c

## Purpose
Implements the Unix process-spawn wrapper used by `procmgmt.h`, giving OpenAFS code a consistent `spawnprocve`/`spawnprocv` API.

## Important APIs, Types, And Functions
Exports `pmgt_ProcessSpawnVE(const char *spath, char *sargv[], char *senvp[], int estatus, sigset_t *mask)`. It depends on native `fork`, `execv`, `execve`, `sigprocmask`, `close`, and `exit`.

## Control Flow
The function forks. In the child, it closes file descriptors 3 through 63, applies the supplied signal mask with `SIG_SETMASK`, executes `spath` with either explicit environment or inherited environment, and exits with `estatus` if exec fails. The parent returns the child pid or `-1` from failed `fork`.

## State And Persistence
No in-process persistent state is retained. External state is the spawned child process and inherited stdio descriptors.

## Dependencies And Integration Points
Used by Unix `procmgmt.h` spawn macros and any OpenAFS code needing child process creation with controlled environment and signal mask.

## Risks And Test Signals
Risks include hard-coded closure of only descriptors below 64, calling `sigprocmask` with a possibly NULL mask, lack of close-on-exec awareness above fd 63, and silent child `exec` failure represented only by `estatus`. Test signals are spawning with/without environment, signal-mask inheritance, exec failure exit status, and descriptor inheritance checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/procmgmt_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/redirect_nt.c -->
# sources/distributed-fs/openafs/src/procmgmt/redirect_nt.c

## Purpose
Redirects native Microsoft C runtime signals on Windows into the OpenAFS process-management signal system.

## Important APIs, Types, And Functions
Key functions are `NativeSignalHandler`, `pmgt_RedirectNativeSignals`, and `pmgt_RestoreNativeSignals`. The handler maps native `SIGINT`, `SIGILL`, `SIGFPE`, `SIGSEGV`, `SIGTERM`, and `SIGABRT` names into `pmgt_SignalRaiseLocalByName`. For abort, it exits with `PMGT_SIGSTATUS_ENCODE(libSigno)`.

## Control Flow
`pmgt_RedirectNativeSignals` installs `NativeSignalHandler` for supported CRT signals. The handler reinstalls itself because NT CRT signals are unreliable, translates the native signal to a string, raises the matching procmgmt signal, and handles abort specially so `waitpid` observes a signal-style termination rather than CRT exit code 3. `pmgt_RestoreNativeSignals` resets handlers to `SIG_DFL`.

## State And Persistence
Persistent runtime state is the process CRT signal-disposition table. `dummyDouble` exists to ensure floating-point support for `SIGFPE` trapping.

## Dependencies And Integration Points
Used by `procmgmt_nt.c` library initialization and cleanup. It deliberately avoids `procmgmt.h` because that header redefines signal-related APIs.

## Risks And Test Signals
Risks include incomplete native signal coverage, reentrant signal handling, comment typo naming restore as redirect, and reliance on CRT-specific behavior. Test signals are abort reporting as `SIGABRT`, native access violation/floating-point exceptions mapping to wait status, and restore-on-DLL-detach behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/redirect_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/test/Makefile.in -->
# sources/distributed-fs/openafs/src/procmgmt/test/Makefile.in

## Purpose
Builds the process-management test executable `pmgttest`.

## Important APIs, Types, And Functions
Defines `LIBPMGT=DEST/lib/afs/libprocmgmt.a`, a `pmgttest` link target using `pmgttest.o`, `libprocmgmt.a`, `-lm`, and `${XLIBS}`, plus `test`/`tests` aliases and `clean`.

## Control Flow
`test` or `tests` builds `pmgttest`; it does not run the test. The link uses `$(AFS_LDRULE)`. `clean` removes objects, executable, and core files.

## State And Persistence
Build artifacts are `pmgttest.o` and `pmgttest`.

## Dependencies And Integration Points
Depends on OpenAFS config/LWP make fragments and the process-management archive from `DEST/lib/afs`. The test source exercises the library's public API.

## Risks And Test Signals
Risks include the suspicious `DEST/lib/afs/libprocmgmt.a` literal relative path and test target not executing the binary. Test signals are successful link and manual execution showing all tests pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/test/pmgttest.c -->
# sources/distributed-fs/openafs/src/procmgmt/test/pmgttest.c

## Purpose
Provides an end-to-end test program for the process-management library. It self-spawns into parent and child modes to validate signal set manipulation, signal handler semantics, process spawning, wait/waitpid behavior, WNOHANG, signal termination, abort handling, environment passing, and NT-only spawn data buffers.

## Important APIs, Types, And Functions
Important helpers are `TimedSleep`, `Bailout`, `ChildTableLookup`, `ChildTableClear`, `SignalCatcher`, `BasicAPITest`, `SingleThreadMgmtTest`, `BehaveLikeAParent`, `BehaveLikeAChild`, and `main`. It uses `spawnprocve`, `spawnprocv`, NT-only `spawnprocveb`, `wait`, `waitpid`, `sigaction`, `signal`, `raise`, `kill`, `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, and `WTERMSIG`.

## Control Flow
Without arguments the program acts as parent: it runs API-only signal tests, then repeatedly spawns children with special argv markers for spawn, wait, WNOHANG, signal, and abort scenarios. Children validate argv/env/data buffer contents or sleep forever until signaled, then exit with expected statuses. The parent records pids, kills lingering children on bailout, and checks exact wait statuses.

## State And Persistence
State is in volatile signal-catcher flags, a fixed child pid table, environment variable `PMGT_SPAWNTEST`, and NT-only `spawnDatap`/`spawnDataLen`. No disk state is written except possible core/crash artifacts.

## Dependencies And Integration Points
Depends on public `afs/procmgmt.h` and platform runtime behavior. It is the primary behavioral signal for both Unix wrappers and NT emulation.

## Risks And Test Signals
Risks include timing sleeps hiding races, interactive/debug dialogs on NT abort tests, fixed `TEST_CHILD_MAX`, and no multithreaded stress coverage. Passing output `All tests completed successfully.` is the key signal; failures identify API, signal, spawn, or wait-status regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/procmgmt/test/pmgttest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/Makefile.in -->
# sources/distributed-fs/openafs/src/ptserver/Makefile.in

## Purpose
Builds the OpenAFS protection server, client tools, database utilities, generated Rx interfaces, and protection client libraries.

## Important APIs, Types, And Functions
Major targets are `ptserver`, `pts`, `pt_util`, `prdb_check`, `ptclient`, `readgroup`, `readpwd`, `testpt`, `liboafs_prot.la`, `libprot_pic.la`, and `libprot.a`. Generated interface files come from `ptint.xg` via `RXGEN` (`ptint.cs.c`, `ptint.ss.c`, `ptint.xdr.c`, `ptint.h`, plus kernel variants). Error files are generated from `pterror.et`. Installed headers include `prclient.h`, `prerror.h`, `print.h`, `prserver.h`, `ptclient.h`, `ptuser.h`, `pterror.h`, `ptint.h`, and `ptserver.h`.

## Control Flow
`all` builds server/tools/libraries and runs `depinstall`. Object dependencies enforce generated headers and version source. The server links ptserver core, utility, RPC server stub, xdr, map, and OpenAFS auth/rx/ubik/cmd/audit libraries. Install/dest skip installing LWP server tools when pthreaded ubik is enabled but still install libraries/headers.

## State And Persistence
Build state includes generated C/header/error files, archives, libtool libraries, executables, objects, and component version source. Install/dest persist server binaries, user tools, libraries, and headers.

## Dependencies And Integration Points
This makefile is the central build integration point for the protection service, Rx RPC generation, Ubik replication, authentication, audit, and command-line tooling.

## Risks And Test Signals
Risks include generated-file ordering, strict-aliasing exceptions for supergroups, library-order sensitivity, and pthreaded-Ubik install conditionals. Test signals are successful generation, all binaries/libraries linked, installed headers present, and functional `pts`, `ptclient`, `pt_util`, and `prdb_check` tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/display.c -->
# sources/distributed-fs/openafs/src/ptserver/display.c

## Purpose
Formats protection database entries and continuation entries for diagnostics and tooling.

## Important APIs, Types, And Functions
Exports `pr_PrintEntry` and `pr_PrintContEntry`. Private `pr_TimeToString` formats timestamps using a shorter current-year format. Macros `PRINT_COMMON_FIELDS` and `PRINT_IDS` print common header fields, reserved fields, IDs, and PRBADID markers while honoring caller-selected host/network byte order through `host(a)`.

## Control Flow
`pr_PrintEntry` detects continuation entries accidentally passed as regular entries and redirects to `pr_PrintContEntry`. Otherwise it prints flags, id, next pointer, create/add/remove/change times, membership IDs, hash chain pointers, owner/creator, quota/count fields, owned/parent/sibling/child pointers, supergroup-specific fields when enabled, and the bounded name. `pr_PrintContEntry` prints common fields, legacy timestamp-like reserved fields, and continuation IDs.

## State And Persistence
Uses static buffers and cached current year in `pr_TimeToString`. Writes formatted output to a caller-supplied `FILE *`; no database state is changed.

## Dependencies And Integration Points
Used by `ptclient` and `prdb_check` for dumping entries. Depends on `ptserver.h`, `contentry`, `prentry`, and byte-order conventions.

## Risks And Test Signals
Risks include static time buffer reuse, assuming `FILE *` is valid, and layout drift with protection database structures. Test signals are readable dumps for regular, continuation, and supergroup entries in both host and network order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/display.h -->
# sources/distributed-fs/openafs/src/ptserver/display.h

## Purpose
Declares protection database display helpers for regular and continuation entries.

## Important APIs, Types, And Functions
Exports `pr_PrintEntry(FILE *f, int hostOrder, afs_int32 ea, struct prentry *e, int indent)` and `pr_PrintContEntry(FILE *f, int hostOrder, afs_int32 ea, struct contentry *e, int indent)`.

## Control Flow
Callers pass an output stream, byte-order flag, database address, entry pointer, and indentation. Implementations perform all formatting in `display.c`.

## State And Persistence
No state is declared. The API only writes diagnostics to a stream.

## Dependencies And Integration Points
Included by `ptclient.c`, `prdb_check.c`, and other protection database diagnostic tools. Requires surrounding includes to define `FILE`, `afs_int32`, `struct prentry`, and `struct contentry`.

## Risks And Test Signals
Risk is declaration drift with `display.c` or missing prerequisite type includes. Test signals are successful compilation and formatted database-entry output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/error_macros.h -->
# sources/distributed-fs/openafs/src/ptserver/error_macros.h

## Purpose
Defines a convenience macro for audited process exit in protection tools.

## Important APIs, Types, And Functions
`PT_EXIT(evalue)` calls `osi_audit(PTS_ExitEvent, evalue, AUD_END)` and then `exit(evalue)`.

## Control Flow
Any caller using the macro records an audit event before terminating the process with the supplied status.

## State And Persistence
Persistent state is external audit output produced by `osi_audit`; process termination follows immediately.

## Dependencies And Integration Points
Depends on audit symbols `PTS_ExitEvent` and `AUD_END`, plus `osi_audit` and `exit`. It integrates command/tool exits with OpenAFS auditing.

## Risks And Test Signals
Risks include macro multi-statement behavior, hidden control flow, and missing audit definitions. Test signals are audited exits with expected status and clean compilation at use sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/error_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/map.c -->
# sources/distributed-fs/openafs/src/ptserver/map.c

## Purpose
Implements in-memory sparse bitmap maps for supergroup support. Maps can represent positive sets or complemented sets by stealing the low bit of the map pointer as a negation flag.

## Important APIs, Types, And Functions
When `SUPERGROUPS` is enabled, exports `in_map`, `free_map`, `add_map`, `and_map`, `or_map`, `not_map`, `copy_map`, `count_map`, `next_map`, `first_map`, `prev_map`, `last_map`, `negative_map`, `bic_map`, and optional `print_map`, `read_map`, `write_map`. Internal `struct bitmap` stores a linked list of pages, each with `MDATA` integer bit words. Macros map node numbers to page/index/bit and toggle negation.

## Control Flow
Membership checks locate the node's page and return the stored bit XOR complement flag. Adding allocates a page when needed, initializes it to all zeroes or all ones depending on map polarity, then sets or clears the bit. Boolean operations destructively combine bitmap page lists, freeing consumed right-hand pages. Iterators scan pages/words/bits to find next or previous set nodes and reject negative maps.

## State And Persistence
State is heap-allocated bitmap linked lists. Many operations consume/free input map pages, so ownership is part of the API contract. No disk state is written.

## Dependencies And Integration Points
Used by protection-server supergroup logic through `map.h`. Depends on OpenAFS debug globals only for optional diagnostics.

## Risks And Test Signals
Risks include pointer-tagging portability, destructive boolean operation ownership surprises, negative map count returning one's complement, allocation failure handling bug that calls `free_map` on the newly failed pointer path, and lack of code when `SUPERGROUPS` is disabled. Test signals are set algebra identities, iteration order, complement behavior, large sparse IDs, and memory leak/error-path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/map.h -->
# sources/distributed-fs/openafs/src/ptserver/map.h

## Purpose
Declares the opaque map API used by protection-server supergroup code.

## Important APIs, Types, And Functions
Forward-declares `struct map` and declares membership, allocation/free, boolean set operations, copying, counting, iteration, complement inspection, subtraction, and printing functions.

## Control Flow
Callers create/update maps with `add_map`, combine them with `and_map`, `or_map`, `not_map`, and `bic_map`, query with `in_map` and `count_map`, iterate with first/next/last/prev helpers, and release with `free_map`.

## State And Persistence
The header hides representation and stores no state. Implementation state is heap-backed sparse bitmaps in `map.c`.

## Dependencies And Integration Points
Included by supergroup-aware ptserver code when `SUPERGROUPS` is enabled.

## Risks And Test Signals
Risks are hidden destructive ownership semantics not visible in declarations and no const-correctness. Test signals are compilation against `map.c` and supergroup membership tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/prdb_check.c -->
# sources/distributed-fs/openafs/src/ptserver/prdb_check.c

## Purpose
Implements `prdb_check`, an offline consistency checker and optional rebuild-script generator for the protection database (`ptdb.DB0`).

## Important APIs, Types, And Functions
Major routines are `printheader`, `pr_Read`, `ReadHeader`, `IDHash`, `NameHash`, `readUbikHeader`, `ConvertDiskAddress`, `PrintEntryError`, `PrintContError`, `WalkHashTable`, `WalkNextChain`, `WalkOwnedChain`, `WalkChains`, `GC`, `QuoteName`, `DumpRecreate`, `CheckPrDatabase`, `WorkerBee`, and `main`. Under `SUPERGROUPS`, `zeromap`, `inccount`, and `idcount` track large sparse ID reference counts. `misc_data` accumulates counts, max/min ids, chain lengths, verbosity flags, and the rebuild output stream.

## Control Flow
`main` registers command options for database path, header display, entry display, verbose mode, and hidden rebuild output. `WorkerBee` opens the database read-only, reads Ubik and protection headers, optionally prints them, opens rebuild output, and calls `CheckPrDatabase`. The checker validates EOF alignment, walks name and ID hash tables, computes ID ranges, walks entry membership chains, continuation chains, free list, owner/orphan chains, checks unreferenced entries and membership counts, generates recreate commands, and compares observed counts/max IDs against header values.

## State And Persistence
Reads the database file directly using `lseek`/`read`; it does not use Ubik transactions. Optional `-rebuild` writes a command script capable of recreating entries and memberships. In-memory maps mark whether each entry was seen in hashes, continuation/free/owned chains, or recreate output.

## Dependencies And Integration Points
Depends on exact on-disk `prheader`, `prentry`, `contentry`, Ubik header size/magic, protection error tables, command parser, and `display.c`. It complements `pt_util` and `ptclient` as an offline diagnostic/recovery tool.

## Risks And Test Signals
Risks include stale reads if the database changes during checking, index math tied to struct size, large non-supergroup ID ranges causing big allocations, rebuild ordering edge cases for owner cycles, and diagnostics that continue after some corruption. Test signals include clean output for a known-good database, intentional hash/continuation/owner/free-list corruption detection, header count mismatch reporting, and valid rebuild script generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/prdb_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/pt_util.c -->
# sources/distributed-fs/openafs/src/ptserver/pt_util.c

## Purpose
Implements `pt_util`, an offline dump/load utility for the OpenAFS protection database. It reads the Ubik database file directly and can dump users, groups, and memberships to text or rebuild/update the database from text input.

## Important APIs, Types, And Functions
Key routines are `main`, `CommandProc`, `display_entry`, `add_group`, `display_groups`, `display_group`, `fix_pre`, `id_to_name`, `checkin`, and `check_core`. Globals include database file descriptor, data stream, cached `prheader`, `ubik_version`, hash table `hat`, group/user lists, `nflag`, `wflag`, and display flags (`DO_USR`, `DO_GRP`, `DO_MEM`, `DO_SYS`, `DO_OTR`).

## Control Flow
Command options choose write mode, display classes, hash traversal by name or id, prdb file, and data file. The utility opens `<prdb>.DB0` by default, reads the Ubik header and protection header, warns on bad magic, initializes ptserver database helpers, and either imports records or dumps chains. In write mode it parses base records and indented membership records, creates entries via ptutils helpers, fixes group counts/flags, and handles deferred foreign users. In dump mode it walks hash chains, prints selected users, accumulates groups, then prints group base records and optionally continuation-block members.

## State And Persistence
Read mode writes only text output. Write mode opens the database read-write/create, may initialize a zero Ubik version to epoch 2, and mutates protection entries through direct ptserver utility calls. It caches ID-to-name mappings in memory.

## Dependencies And Integration Points
Depends on Ubik internals, protection database structures, ptserver utility functions (`Initdb`, `FindByID`, `CreateEntry`, `AddToEntry`, `pr_ReadEntry`, `pr_WriteEntry`), command parsing, and pterror tables.

## Risks And Test Signals
Risks are direct database access while ptserver is active, text format parsing fragility, destructive write mode, memory leaks in helper lists, and version-change warning only after work is done. Test signals include stable dumps of known databases, import into disposable databases, version-change detection, name/id hash traversal parity, and member continuation handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/pt_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptclient.c -->
# sources/distributed-fs/openafs/src/ptserver/ptclient.c

## Purpose
Provides an interactive low-level protection-server client for testing and administration. It connects through the protection library/Ubik client and exposes compact commands for entry creation, deletion, membership, ID/name translation, hash repair, and database entry dumping.

## Important APIs, Types, And Functions
Important helpers are `osi_audit`, `GetToken`, `GetString`, `CodeOk`, `PrintEntry`, `PrintHelp`, `skip`, and `main`. Commands call `ubik_PR_INewEntry`, `ubik_PR_SetFieldsEntry`, `ubik_PR_ChangeEntry`, `ubik_PR_WhereIsIt`, `ubik_PR_DumpEntry`, `ubik_PR_AddToGroup`, `ubik_PR_IDToName`, `ubik_PR_NameToID`, `ubik_PR_Delete`, `ubik_PR_RemoveFromGroup`, `ubik_PR_GetCPS`, `ubik_PR_GetHostCPS`, `ubik_PR_ListSuperGroups`, `ubik_PR_ListElements`, `ubik_PR_NewEntry`, `ubik_PR_ListMax`, `ubik_PR_SetMax`, `ubik_PR_UpdateEntry`, and high-level `pr_*` helpers.

## Control Flow
Startup parses configuration directory, server/client mode, security level, rxgk level, ignore-exist mode, and target cell. It initializes protection errors and `pr_Initialize2`, then repeatedly reads a line, tokenizes an opcode, parses typed arguments, invokes the matching RPC/library call, and prints results or errors. `PrintEntry` compensates for old byte-swapped continuation dump behavior before delegating to display formatting.

## State And Persistence
Persistent external state is the live protection database changed through server RPCs. Local state includes command buffer, parser cursor, security/confdir globals, and optional `ignoreExist`.

## Dependencies And Integration Points
Depends on Rx, Ubik protection stubs, ptuser library, pterror, display helpers, CellServDB/config files, and optional rxgk security level. It is useful for exercising ptserver operations below the polished `pts` interface.

## Risks And Test Signals
Risks include terse/unsafe commands, duplicate `fih`/`fnh` command blocks under supergroups, fixed input buffers, partial quoted-string handling, and direct hash repair operations. Test signals are successful connection at each security mode, create/change/delete/member operations, ID/name translation, CPS listing, host CPS, dump entry formatting, and hash repair on a test database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptclient.h -->
# sources/distributed-fs/openafs/src/ptserver/ptclient.h

## Purpose
Provides a small public include shim for protection client code.

## Important APIs, Types, And Functions
Includes `afs/afs_lock.h`, `ubik.h`, `ptint.h`, and `ptserver.h`, then defines `pr_ErrorMsg` as `afs_error_message`.

## Control Flow
There is no runtime flow. Including this header pulls in the core protection RPC/database types and gives callers the legacy `pr_ErrorMsg` name for error formatting.

## State And Persistence
No state is declared or modified.

## Dependencies And Integration Points
Used by `ptclient.c` and installed as both `prclient.h` and `ptclient.h` aliases through the makefile. It bridges callers to Ubik and generated protection interfaces.

## Risks And Test Signals
Risks are broad transitive includes and macro alias drift if error-message APIs change. Test signals are successful compilation of protection clients and correct error string formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptclient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptopcodes.h -->
# sources/distributed-fs/openafs/src/ptserver/ptopcodes.h

## Purpose
Defines numeric opcode constants for the protection-server RPC interface.

## Important APIs, Types, And Functions
Defines `LOWEST_OPCODE` as 500, opcodes from `PRINEWUSER` through `PRLISTSUPERGROUPS`, and `HIGHEST_OPCODE` as 530. Constants cover create, lookup, dump, membership, ID/name translation, delete, CPS, list/set max, change entry, list elements/entries/owned/supergroups, host CPS, and update entry operations.

## Control Flow
There is no runtime behavior. Generated or hand-written RPC dispatch code uses these numeric constants to identify protection operations.

## State And Persistence
The file defines protocol constants only. These values are persistent wire/API contract state and must remain stable for compatibility.

## Dependencies And Integration Points
Integrated with `ptint.xg`, ptserver RPC stubs, and clients that need explicit operation numbers.

## Risks And Test Signals
Risks are opcode collisions, changing existing values, or failing to update `HIGHEST_OPCODE` when adding operations. Test signals are RPC compatibility between clients and servers and generated interface consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptopcodes.h -->
