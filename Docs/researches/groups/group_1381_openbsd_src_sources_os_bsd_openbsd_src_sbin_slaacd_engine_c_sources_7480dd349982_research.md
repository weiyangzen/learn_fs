# Group Research: group_1381_openbsd_src_sources_os_bsd_openbsd_src_sbin_slaacd_engine_c_sources_7480dd349982

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/openbsd-src`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/engine.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/engine.c

Implements the `slaacd` engine process: the unprivileged policy/state-machine half of IPv6 SLAAC. It receives interface facts and router advertisements from the frontend, derives address/default-route/RDNS proposals, tracks proposal lifetimes, and asks the privileged main process to configure or withdraw kernel state.

Major structures:
- `struct slaacd_iface`: per-interface state, routing domain, flags, link-local address, hardware address, SOII key, current MTU, RA list, and address/default-route/RDNS proposal lists.
- `struct radv`, `radv_prefix`, `radv_rdns`: parsed router advertisement state with timestamps, lifetimes, prefixes, RDNSS servers, router preference, and MTU.
- `struct address_proposal`, `dfr_proposal`, `rdns_proposal`: pending/configured SLAAC outputs with event timers, monotonic timestamps, lifetimes, source router, interface ID, and state.

Process setup:
- `engine()` drops to `_slaacd`, unveils `/` with no access, pledges `stdio recvfd`, initializes libevent, and waits for imsg links.
- After receiving the frontend IPC socket from main, it reduces pledge to `stdio`.
- Uses OpenBSD `imsg`, libevent timers, `LIST_HEAD` queues, and signal handlers.

Core imsg handling:
- From frontend: handles RAs, interface removal, manual solicitation requests, address/route deletion notices, duplicate-address notices, RDNS reproposal, and control queries.
- From main: receives frontend IPC fd and interface-update messages.
- Sends configuration requests to main with `IMSG_CONFIGURE_ADDRESS`, `IMSG_WITHDRAW_ADDRESS`, `IMSG_CONFIGURE_DFR`, `IMSG_WITHDRAW_DFR`, and `IMSG_PROPOSE_RDNS`.

SLAAC state machines:
- Interface states: `IF_DOWN`, `IF_INIT`, `IF_BOUND`.
- Proposal states: `PROPOSAL_IF_DOWN`, `PROPOSAL_NOT_CONFIGURED`, `PROPOSAL_CONFIGURED`, `PROPOSAL_NEARLY_EXPIRED`, `PROPOSAL_WITHDRAWN`, `PROPOSAL_DUPLICATED`, `PROPOSAL_STALE`.
- `iface_state_transition()` sends router solicitations while initializing, stops after `MAX_RTR_SOLICITATIONS`, and moves proposals down or withdrawn as link state changes.
- Proposal transitions compute remaining lifetime from monotonic RA timestamps, solicit near expiry, withdraw stale state, and regenerate duplicated addresses.

Router advertisement parsing:
- `parse_ra()` validates ICMPv6 RA type/code, link-local sender, message and option lengths, prefix length, MTU minimum, and RDNSS layout.
- Parses prefix information, RDNSS, MTU, router lifetime, reachable/retransmit time, managed/other flags, and router preference.
- Ignores unsupported ND options such as DNSSL, route info, redirected header, and link-layer address options.
- `debug_log_ra()` provides verbose RA decoding in non-`SMALL` builds.

Address generation:
- `gen_addr()` constructs IPv6 addresses from advertised prefixes and either random IID for temporary addresses, SHA-512 stable opaque IID using prefix/MAC/DAD counter/SOII key, or link-local IID for non-SOII prefixes up to /64.
- Temporary lifetimes use RFC 8981 constants: 2-day valid, 1-day preferred, desync factor, and regeneration advance.
- Duplicate non-temporary SOII addresses increment the per-prefix DAD counter and generate a new proposal.

Proposal updates:
- `update_iface_ra()` replaces old RAs from the same router, preserves DAD counters, then updates default-route, address, and RDNS proposals.
- `update_iface_ra_prefix()` updates existing address proposals, creates stable and temporary proposals when enabled, removes disabled address kinds, and applies advertised MTU changes once.
- `update_iface_ra_dfr()` maps router lifetime into default-route proposals.
- `update_iface_ra_rdns()` aggregates RDNSS servers, truncates to `MAX_RDNS_COUNT`, and reproposes DNS through route proposals.

Resource/lifetime management:
- Free helpers remove list entries, delete timers, and withdraw configured kernel state when required.
- Timeout handlers move configured proposals to nearly-expired, stale, duplicated regeneration, or final free states.
- `real_lifetime()` converts RA-relative lifetimes using monotonic time.

Filesystem/storage relevance:
- No filesystem implementation. Relevant as OpenBSD daemon infrastructure: privilege separation, route-socket mediated kernel state, event/timer ownership, and long-lived resource cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/engine.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/engine.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/engine.h

Declares the engine-facing imsg payloads and public engine entry points.

Contents:
- `struct imsg_configure_address`: interface index, IPv6 address, source router/gateway, prefix mask, valid/preferred lifetimes, MTU, and temporary-address flag.
- `struct imsg_configure_dfr`: interface index, routing domain, gateway address, and router lifetime for default-route management.
- `engine(int, int)`: engine child-process entry point.
- `engine_imsg_compose_frontend(...)`: helper for sending imsgs from engine to frontend.

Role:
- Defines the contract between `engine.c` and `slaacd.c` for privileged address/route configuration.
- Keeps kernel mutation details out of the engine; the engine sends typed proposals and main performs syscalls/ioctls.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/engine.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.c

Implements the `slaacd` frontend process: observes interfaces, route-socket events, ICMPv6 router advertisements, and control connections, then forwards normalized facts to engine/main.

Process setup:
- Drops to `_slaacd`, unveils `/` with no access, pledges `stdio unix recvfd route`.
- Receives route socket, control socket, frontend-engine IPC socket, and ICMPv6 sockets by imsg fd passing.
- Maintains frontend `interfaces` and shared per-rdomain `icmp6_ev` receivers.

Interface discovery:
- `frontend_startup()` enables route-socket event handling and scans interfaces with `if_nameindex()`.
- `update_iface()` reads flags (`SIOCGIFFLAGS`), extended flags (`SIOCGIFXFLAGS`), routing domain (`SIOCGIFRDOMAIN`), link state, Ethernet address, link-local IPv6 address, autoconf/temp flags, and SOII flag.
- Defers solicitation until the link-local address is no longer tentative.

Route socket handling:
- `route_receive()` reads route messages, validates length/version, expands route socket addresses with `get_rtaddrs()`, and dispatches by message type.
- `handle_route_message()` handles `RTM_IFINFO`, `RTM_IFANNOUNCE`, `RTM_NEWADDR`, `RTM_DELADDR`, `RTM_CHGADDRATTR`, `RTM_DELETE`, and `RTM_PROPOSAL`.
- It notifies the engine about deleted IPv6 addresses, duplicated autoconf addresses, removed `slaacd`-labelled default routes, interface disappearance, and RDNS reproposal requests.

ICMPv6 handling:
- `get_icmp6ev_by_rdomain()` allocates one raw ICMPv6 receive event per routing domain and asks main to open the privileged socket.
- `set_icmp6sock()` attaches the passed raw socket to waiting interfaces.
- `icmp6_receive()` forwards only router advertisements with receiving interface metadata, hop limit 255, and bounded packet length.
- `send_solicitation()` sends ND router solicitations to `ff02::2` with packet info, hop limit 255, and source link-layer address.

Control relay:
- In non-`SMALL` builds, forwards control fd setup to `control_listen()` and relays engine control responses back to control clients.

Filesystem/storage relevance:
- No filesystem logic. Relevant as OpenBSD route-socket/raw-socket daemon frontend code with privilege separation and routing-domain aware resource sharing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.h

Declares the frontend process API:
- `frontend(int, int)`: child-process entry point.
- `frontend_dispatch_main(...)`: imsg dispatch from main.
- `frontend_dispatch_engine(...)`: imsg dispatch from engine.
- `frontend_imsg_compose_main(...)`: send imsg to main.
- `frontend_imsg_compose_engine(...)`: send imsg to engine with peer/pid metadata.

Role:
- Shared declaration boundary for `slaacd.c`, `frontend.c`, and control code.
- Captures the daemon’s three-process imsg topology.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/log.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/log.c

Small daemon logging implementation used by `slaacd`.

Behavior:
- `log_init()` chooses stderr logging in debug mode or syslog otherwise, initializes process name, and calls `tzset()`.
- `log_procinit()` changes the process label used in fatal messages.
- `log_setverbose()` and `log_getverbose()` manage runtime verbosity.
- `vlog()` preserves `errno`, writes to stderr in debug mode, or syslog otherwise.
- `log_warn()` appends `strerror(errno)` while preserving the original errno.
- `log_warnx()`, `log_info()`, and `log_debug()` are level-specific wrappers.
- `fatal()` and `fatalx()` log critical errors with process context and exit.

Robustness notes:
- Handles `asprintf()` failure with best-effort direct `vfprintf()`.
- Preserves `errno` across logging calls.

Filesystem/storage relevance:
- No filesystem logic; it is daemon support code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/log.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/log.h

Header for `slaacd` logging.

Contents:
- Declares logging, verbosity, and fatal APIs with printf-format attributes.
- Includes `stdarg.h` and `stdlib.h`.
- Under `SMALL`, compiles logging calls to no-ops and maps fatal exits to `exit(1)`.

Role:
- Allows the same source tree to build full daemon/control variants and reduced `SMALL` variants.
- Provides compile-time format checking for normal builds.

Filesystem/storage relevance:
- No filesystem logic; it is shared daemon logging API.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.c

Main `slaacd` supervisor and privileged executor. It starts frontend and engine children, wires imsg channels, owns privileged sockets/ioctls/route writes, and handles kernel state mutation requested by the engine.

Startup:
- Supports normal mode plus internal `-E` and `-F` child modes.
- Requires root, uses `/dev/slaacd.lock` with exclusive nonblocking lock, validates `_slaacd`, daemonizes unless `-d`.
- Creates socketpairs for main-frontend and main-engine, forks/execs child modes, then passes an additional frontend-engine socketpair via imsg.
- Opens route sockets, ioctl socket, and optional control socket; sets route message/table filters for frontend.
- Reads `/etc/soii.key` into the global SOII key in non-`SMALL` builds.
- Pledges `stdio inet sendfd wroute`.

Privileged operations:
- `open_icmp6sock()` opens raw ICMPv6 sockets per rdomain, enables packet info and hop-limit ancillary data, sets `SO_RTABLE`, and passes fds to frontend.
- `configure_interface()` performs `SIOCAIFADDR_IN6`, setting address, destination router, prefix mask, lifetimes, `IN6_IFF_AUTOCONF`, optional `IN6_IFF_TEMPORARY`, and optional MTU with `SIOCSIFMTU`.
- `delete_address()` removes IPv6 addresses with `SIOCDIFADDR_IN6`.
- `configure_gateway()` builds route messages for `::/0`, gateway, netmask, route label `slaacd`, and writes `RTM_ADD` or `RTM_DELETE`.
- `send_rdns_proposal()` writes `RTM_PROPOSAL` messages containing DNS server proposals.

Imsg topology:
- Main receives interface updates and socket-open requests from frontend.
- Main forwards interface updates to engine after filling the SOII key.
- Main receives address/route/RDNS proposals from engine and mutates kernel state.
- Helpers `imsg_event_add()`, `imsg_compose_event()`, and `imsg_forward_event()` integrate imsg buffers with libevent.

Shutdown:
- Closes child pipes, waits for children, logs abnormal child signals, frees imsgev state, and exits.

Utility functions:
- `sin6_to_str()` formats IPv6 sockaddr values.
- Hex parsing supports SOII key loading.
- `i2s()` maps imsg type constants to strings for diagnostics.

Filesystem/storage relevance:
- No filesystem implementation. Important OS plumbing: privilege separation, raw sockets, route messages, ioctl mutation, single-instance lock file, and configuration-key file reading.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.h

Shared `slaacd` protocol and control header.

Constants:
- `_PATH_LOCKFILE`, `_PATH_SLAACD_SOCKET`, `SLAACD_USER`, `SLAACD_RTA_LABEL`.
- `SLAACD_SOIIKEY_LEN` and `MAX_RDNS_COUNT`.

Core types:
- `struct imsgev`: wraps `imsgbuf`, libevent event, handler, and event mask.
- `enum imsg_type`: daemon protocol covering control commands, socket passing, startup, interface updates/removals, RAs, address/route/RDNS proposals, and duplicate-address notifications.
- `enum rpref`: router preference low/medium/high.

Control payloads:
- Non-`SMALL` structs expose interface info, RAs, RA prefixes, RA RDNS servers, address proposals, default-route proposals, and RDNS proposals.
- `struct imsg_propose_rdns`, `imsg_ifinfo`, `imsg_del_addr`, `imsg_del_route`, `imsg_ra`, and `imsg_dup_addr` define daemon-internal messages.

Declared helpers:
- imsg event helpers from `slaacd.c`.
- `sin6_to_str()` and `i2s()` in non-`SMALL` builds.

Filesystem/storage relevance:
- No filesystem logic; defines the daemon’s internal ABI.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/Makefile

Builds the `swapctl` utility.

Contents:
- `PROG=swapctl`.
- Sources are `swapctl.c` and `swaplist.c`.
- Links with `libutil`.
- Installs `swapctl.8`.
- Creates a hard/symlink-style install alias from `${BINDIR}/swapctl` to `${BINDIR}/swapon`.

Filesystem/storage relevance:
- Directly relevant to swap storage administration; builds both modern `swapctl` and compatibility `swapon` entry points.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.c

Implements the command-line frontend for OpenBSD swap device/file management.

Command modes:
- `-A`: add all `sw` entries from `/etc/fstab`.
- `-a path`: add one swap device/file.
- `-c -p priority path`: change swap priority.
- `-d path`: remove one swap device/file.
- `-l`: long listing.
- `-s`: summary listing.
- `-k`: report in 1K units.
- `-p priority`: priority for add/change/filtering.
- `-t blk|noblk`: with `-A`, include only block or non-block swap entries.

Compatibility mode:
- If invoked as `swapon`, `swapon_command()` emulates old `swapon(8)` behavior: `-a` processes fstab, otherwise path arguments are added.

Kernel interface:
- `change_priority()` calls `swapctl(SWAP_CTL, path, pri)`.
- `add_swap()` calls `swapctl(SWAP_ON, path, pri)` and ignores `EBUSY`.
- `del_swap()` calls `swapctl(SWAP_OFF, path, pri)`.

Fstab handling:
- `do_fstab()` scans `getfsent()` entries whose `fs_type` is `sw`.
- Parses mount options `priority=` and `nfsmntpt=`.
- For NFS-backed swap entries, mounts the NFS path with `/sbin/mount_nfs` before enabling swap.
- Filters block vs non-block swap candidates using `stat()`, DUID recognition via `isduid()`, and `/dev/` path checks.
- Rejects unsupported object types, allowing only regular files and block devices.
- Exits with failure if no fstab swap entries are successfully enabled.

Filesystem/storage relevance:
- Directly storage-related: manages active swap devices/files and fstab-defined swap resources, including NFS-backed swap setup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.h

Small shared header for `swapctl`.

Contents:
- Declares `list_swap(int pri, int kflag, int pflag, int dolong)`.
- Documents argument meaning: priority, 1K display flag, priority-filter flag, and long/short output mode.

Filesystem/storage relevance:
- Directly supports swap reporting shared between `swapctl.c` and `swaplist.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/swaplist.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/swaplist.c

Implements swap listing/reporting for `swapctl`.

Behavior:
- Uses `swapctl(SWAP_NSWAP)` to count configured swap entries.
- Allocates `struct swapent` array and fills it with `swapctl(SWAP_STATS)`.
- Supports priority filtering when `pflag` is set.
- Uses `getbsize()` for human display block size, or fixed 1024-byte units with `-k`.
- Long mode prints one row per swap entry: path, size, used, available, capacity, priority.
- Summary mode prints total allocated, used, and available.
- Prints a `Total` row in long mode when more than one entry is counted.

Filesystem/storage relevance:
- Directly storage-related: reports configured swap capacity and usage from kernel swap accounting.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/swapctl/swaplist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/sysctl/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/sysctl/Makefile

Builds the `sysctl` utility.

Contents:
- `PROG=sysctl`.
- Installs `sysctl.8`.
- `afterinstall` creates `/usr/sbin/sysctl` as a symlink to `../../sbin/sysctl` and sets symlink ownership.
- Includes `<bsd.prog.mk>`.

Filesystem/storage relevance:
- Build metadata only. The resulting tool exposes many kernel tunables, including VFS, mount, swap encryption, and name-cache stats.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/sysctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/sysctl/sysctl.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/sysctl/sysctl.c

Implements OpenBSD `sysctl(8)`: parses symbolic MIB names, lists known sysctl nodes, reads values, writes values, and formats special kernel structures.

Startup and options:
- Supports `-A`, `-a`, `-f file`, `-n`, `-q`, and legacy no-op `-w`.
- Uses `unveil()` to restrict access to `_PATH_DEVDB`, `/dev`, and an optional config file.
- With no arguments, `-a`, or `-A`, initializes debug and VFS name tables and lists known nodes.
- With `-f`, reads non-comment tokens from a config file and parses them as sysctl assignments/queries.

Name parsing:
- `parse()` copies the input, separates optional `name=value`, resolves top-level and lower-level symbolic names into a MIB array, determines type, converts write values, calls `sysctl(2)`, and prints formatted output.
- `findname()` resolves one dotted path component against a `struct list`.
- `listall()` recursively lists known variables by constructing dotted names.
- `parse_hex_string()` supports hex-encoded string writes for selected nodes.

Supported top-level families:
- `kern`, `vm`, `net`, `hw`, `debug`, `machdep`, `ddb`, and `vfs`.
- Many data families have custom lower-level parsers: inet, inet6, unix, link, bpf, mpls, pipex, bios, swap encryption, fork stats, tty, name-cache stats, malloc stats, SysV sem/shm, watchdog, timecounter, sensors, audio, video, witness, battery.

Special formatting:
- Clock info, boot time, char/block devices, BIOS geometry/device IDs, unsigned ints, long arrays, timeout stats, sensors, kernel memory buckets/stats, and TCP/UDP bad-dynamic port bitmaps.
- For opaque or better-handled structures, redirects users to tools such as `netstat`, `vmstat`, `systat`, `fstat`, `ps`, `dmesg`, `pstat`, or `nfsstat`.

VFS/filesystem handling:
- Includes `sys/mount.h`, UFS/FFS, FUSEFS, and NFS headers.
- `vfsinit()` queries `CTL_VFS.VFS_GENERIC.VFS_MAXTYPENUM` and `VFS_CONF`, builds dynamic filesystem name tables, records type numbers, and attaches known per-filesystem variable tables for FFS, NFS, and FUSEFS.
- Adds synthetic `vfs.mounts` listing behavior: `sysctl_vfsgen()` prints mounted instance counts by filesystem type.
- `sysctl_vfs()` maps symbolic filesystem names to kernel VFS type numbers and per-filesystem ctl names.
- Struct-valued NFS stats are intentionally not printed here; users are directed to `nfsstat`.

Name-cache and VM/storage-adjacent handling:
- `sysctl_nchstats()` reads `struct nchstats` once and prints individual vnode/name-cache counters.
- VM `swapencrypt` is delegated to `sysctl_swpenc()`.
- VM pages such as `VM_VNODEMIN`, `VM_ANONMIN`, `VM_VTEXTMIN`, `VM_NKMEMPAGES`, and malloc configuration are permitted through normal parsing; other VM stats are redirected to `vmstat`/`systat`.

Network handling:
- Large static protocol tables map inet/inet6 protocols to ctl names.
- Stats-heavy nodes are redirected to `netstat`.
- TCP/UDP bad-dynamic/root-only port lists support full replacement or incremental `+`/`-` port/range updates.

Sensors:
- `sysctl_sensors()` supports scanning all devices, one device, one sensor type, or one numbered sensor.
- `print_sensor()` formats many sensor types and statuses, including drive status, temperature, voltage, watts, amperage, humidity, pressure, acceleration, and timestamps.

Filesystem/storage relevance:
- Strongly relevant as a kernel control/reporting tool. It exposes VFS type information, mount instance counts, FFS/NFS/FUSE sysctl namespaces, name-cache statistics, swap encryption nodes, vnode VM thresholds, and device-name formatting.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/sysctl/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ttyflags/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/ttyflags/Makefile

Builds the `ttyflags` utility.

Contents:
- `PROG=ttyflags`.
- Installs `ttyflags.8`.
- Includes `<bsd.prog.mk>`.

Filesystem/storage relevance:
- Build metadata for a terminal device configuration utility; no filesystem implementation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ttyflags/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ttyflags/ttyflags.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ttyflags/ttyflags.c

Implements `ttyflags`, which applies or prints device-specific tty flags from `/etc/ttys`.

Options:
- `-a`: process all tty entries.
- `-p`: print current kernel tty flags instead of setting from `/etc/ttys`.
- `-v`: verbose diagnostics.
- `-n`: undocumented dry-run behavior that skips opening/ioctl changes.

Main flow:
- Opens tty database with `setttyent()`.
- Processes either all entries with `all()` or named entries with `ttys()`.
- Closes tty database with `endttyent()`.

Flag application:
- `ttyflags()` builds `/dev/<ttyname>`.
- Converts `ttyent` status bits to ioctl flags: `TTY_LOCAL`, `TTY_RTSCTS`, `TTY_SOFTCAR`, `TTY_MDMBUF`.
- Opens devices `O_RDONLY | O_NONBLOCK`.
- Sets flags with `TIOCSFLAGS` or reads them with `TIOCGFLAGS`.
- Ignores pseudo/network entries and tolerates some absent/off devices.

Filesystem/storage relevance:
- Uses `/etc/ttys` and `/dev` paths but is terminal-device administration, not filesystem/storage logic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ttyflags/ttyflags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/tunefs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/tunefs/Makefile

Builds the `tunefs` utility.

Contents:
- `PROG=tunefs`.
- Installs `tunefs.8`.
- Links with `libutil`.

Filesystem/storage relevance:
- Directly relevant: builds the UFS/FFS filesystem tuning utility.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/tunefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/tunefs/tunefs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/tunefs/tunefs.c

Implements `tunefs`, a UFS/FFS superblock tuning utility.

Options:
- `-A`: update all alternate superblocks in every cylinder group.
- `-F`: open the provided path directly instead of resolving a filesystem/device through fstab/opendev.
- `-N`: no-write/current-settings mode.
- `-e maxbpg`: maximum blocks per file in a cylinder group.
- `-g avgfilesize`: average file size.
- `-h avgfpdir`: expected files per directory.
- `-m minfree`: minimum free-space percentage.
- `-o space|time`: optimization preference.

Filesystem handling:
- Opens target read-only for `-N`, read-write otherwise.
- `openpartition()` maps a mounted filesystem path through fstab to a raw device path when possible, then uses `opendev()`.
- `getsb()` searches known superblock locations from `SBLOCKSEARCH`, supports UFS1 and UFS2 magic, and checks `fs_sblockloc` when applicable.
- Reads and writes with `pread()`/`pwrite()` at device-block offsets.

Tuning behavior:
- Updates selected fields in `struct fs`: `fs_maxbpg`, `fs_minfree`, `fs_optim`, `fs_avgfilesize`, and `fs_avgfpdir`.
- Warns when requested values are unchanged.
- Warns when minfree and optimization preference are inconsistent with `MINFREE` conventions.
- In `-N` mode, prints current settings and exits without writing.
- Writes the primary superblock; with `-A`, writes alternate superblocks at `cgsblock()` locations.

Safety/error behavior:
- Numeric arguments are validated with `strtonum()`.
- After opening and reading the superblock, pledges `stdio`.
- Read/write errors are fatal with block/byte-offset diagnostics.

Filesystem/storage relevance:
- Directly relevant to local filesystem metadata: edits UFS/FFS superblock tunables on raw devices.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/tunefs/tunefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/umount/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/umount/Makefile

Builds the `umount` utility.

Contents:
- `PROG=umount`.
- Installs `umount.8`.
- Links with `libutil`.

Filesystem/storage relevance:
- Directly relevant: builds the unmount utility for filesystem mount lifecycle management.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/umount/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/umount/umount.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/umount/umount.c

Implements `umount`, including single target unmounts, bulk unmounts, type filtering, forced unmounts, and NFS mountd notification.

Options:
- `-a`: unmount all selected filesystems except root.
- `-f`: force unmount via `MNT_FORCE`.
- `-h host`: with all-mode, limit NFS unmounts to a host; implies `-a` and defaults type filter to NFS.
- `-t type[,type]` or `-t no...`: include/exclude filesystem types.
- `-v`: verbose output.

Main flow:
- Calls `sync()` early.
- Parses options, builds type list if needed, then calls either `umountall()` or `umountfs()` for each argument.

Mount lookup:
- `umountall()` uses `getmntinfo(MNT_NOWAIT)` and iterates mounted filesystems in reverse order.
- `getmntname()` maps from device/spec to mount point or from mount point to mounted-from name and returns filesystem type.
- `umountfs()` accepts DUIDs, paths, special devices, and mount points, using `realpath()`, `stat()`, `isduid()`, and mount table lookup.

Unmount behavior:
- Filters by filesystem type using `selected()`.
- Calls `unmount(mntpt, fflag)`.
- Verbose mode prints source and mount point.

NFS behavior:
- Parses `host:path` or `path@host` forms.
- `namematch()` compares requested host against canonical and alias names, with short-name handling.
- Unless forced, sends `RPCMNT_UMOUNT` to the remote mount daemon after successful local unmount.

Filesystem/storage relevance:
- Directly relevant to VFS mount lifecycle: resolves mount table entries, invokes `unmount(2)`, supports type-filtered bulk unmounts, and handles NFS cleanup RPCs.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/umount/umount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/Makefile

Builds the `unwind` DNS resolver daemon.

Contents:
- `PROG=unwind`.
- Sources include `control.c`, `resolver.c`, `frontend.c`, `log.c`, `unwind.c`, `parse.y`, `printconf.c`, and `dns64_synth.c`.
- Includes bundled `libunbound/Makefile.inc`.
- Adds include paths for daemon and libunbound headers.
- Enables warning flags such as `-Wall`, strict prototypes, missing prototypes/declarations, shadow, pointer arithmetic, and sign comparison.
- Links with `libevent`, `libutil`, `libssl`, and `libcrypto`.
- Explicitly avoids static linking by default with `LDSTATIC=`.

Filesystem/storage relevance:
- Build metadata for network resolver daemon; no filesystem/storage implementation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/control.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/control.c

Implements the local control socket server for `unwind`.

Control socket setup:
- `control_init()` creates a nonblocking close-on-exec Unix stream socket, unlinks any existing path, binds with a restrictive temporary umask, chmods the socket to user/group/other read-write, and returns the fd.
- `control_listen()` installs the listening fd, calls `listen()`, sets the libevent accept event, and prepares a timeout event for accept backoff.

Connection management:
- Accepted connections are wrapped in `struct ctl_conn`, which contains an `imsgev`.
- Connections are stored in a `TAILQ`.
- `control_connbyfd()` and `control_connbypid()` find active control clients.
- `control_close()` clears imsg state, removes events, closes the fd, removes the connection, and resumes accepts after descriptor pressure.

Accept behavior:
- `control_accept()` accepts with `accept4(... SOCK_CLOEXEC | SOCK_NONBLOCK)`.
- On `ENFILE`/`EMFILE`, pauses accepting for one second to avoid a busy event loop.
- Other transient accept errors are ignored; unexpected errors are logged.

Control imsg dispatch:
- `control_dispatch_imsg()` reads/writes imsgs, validates peer credentials with `getpeereid()`, and restricts reload/log-verbose commands to root.
- Handles:
  - `IMSG_CTL_RELOAD`: forwards to frontend/main.
  - `IMSG_CTL_LOG_VERBOSE`: forwards to main and resolver, and updates local verbosity.
  - `IMSG_CTL_STATUS`, `IMSG_CTL_AUTOCONF`, `IMSG_CTL_MEM`: forwards to resolver.
- Unknown or malformed messages are logged or ignored.

Relay:
- `control_imsg_relay()` sends a response imsg back to the control client whose stored imsg pid matches the response pid.

Filesystem/storage relevance:
- No filesystem/storage implementation. Relevant as OpenBSD daemon control-plane code using Unix sockets, imsg, credentials, and libevent.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/control.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/control.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/control.h

Declares the `unwind` control socket API.

Functions:
- `control_init(char *)`: create and bind a control socket.
- `control_listen(int)`: begin listening on the control socket.
- `control_accept(int, short, void *)`: libevent accept callback.
- `control_dispatch_imsg(int, short, void *)`: per-client imsg callback.
- `control_imsg_relay(struct imsg *)`: relay daemon responses to control clients.

Filesystem/storage relevance:
- No filesystem/storage logic; header for daemon control socket plumbing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/control.h -->