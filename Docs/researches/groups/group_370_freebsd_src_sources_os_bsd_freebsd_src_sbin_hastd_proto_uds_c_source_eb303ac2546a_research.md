# Group Research: group_370_freebsd_src_sources_os_bsd_freebsd_src_sbin_hastd_proto_uds_c_source_eb303ac2546a

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/freebsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_uds.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_uds.c

`proto_uds.c` implements the `uds` protocol backend for HAST's generic `proto` abstraction using UNIX domain stream sockets. It registers itself with `proto_register()` from a constructor.

The file parses `uds://`, `unix://`, and bare absolute-path addresses into `sockaddr_un`, creates client and server sockets, binds/listens with pre-bind `unlink()`, accepts worker connections, and exposes descriptor/local/remote address helpers. Data transfer is delegated to `proto_common_send()` and `proto_common_recv()`, so ancillary file-descriptor passing is preserved through the common protocol layer.

Important lifecycle detail: listening sockets record an owner PID and only unlink their socket path during close when still in the owning process and still on the server-listen side. Client timeout hooks are mostly placeholders: `uds_connect()` ignores the timeout except for assertions, and `uds_connect_wait()` returns success.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_uds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.c

`rangelock.c` provides a small in-memory range lock table for HAST. It stores locked byte ranges as `struct rlock` entries in a `TAILQ`, protected only by caller-side synchronization.

The API allocates/frees a `struct rangelocks`, adds exact ranges as `[offset, offset + length)`, removes an exact matching range, and tests overlap with `rl_start < end && rl_end > offset`. Assertions check the container magic value and that deletes find an existing range.

This is a simple conflict-detection helper, not a blocking lock manager: it does not sleep, merge ranges, sort entries, validate overflow, or provide internal mutex protection.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.h

`rangelock.h` declares the opaque range-lock API used by HAST code. It forward-declares `struct rangelocks` and exports init/free/add/delete/islocked functions using `off_t` offsets and lengths.

The header deliberately exposes no synchronization primitive or range internals, so callers own concurrency and lifetime discipline around the table.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/refcnt.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/refcnt.h

`refcnt.h` defines a lightweight atomic reference counter type and inline operations for HAST. `refcnt_t` is an unsigned int; initialization is a direct store, acquire uses `atomic_add_acq_int()`, and release uses `atomic_fetchadd_int(count, -1)`.

`refcnt_release()` returns the decremented value and asserts the old count was nonzero. A comment notes an unresolved question about whether release should include a release memory barrier.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/refcnt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/secondary.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/secondary.c

`secondary.c` implements the worker process for a HAST resource running in secondary role. The parent creates control/event socketpairs, forks, keeps parent-side descriptors, and the child initializes logging, descriptors, local metadata, request pools, privilege dropping, the control thread, remote handshake, and then the receive/disk/send pipeline.

The remote initialization exchanges resource size, extent size, counters, resource UID, synchronization source, and active map data. It detects first-use resources, resource UID mismatch, primary-out-of-date, secondary-out-of-date, in-sync, impossible-counter cases, and split-brain. Split-brain sends an error response, emits `EVENT_SPLITBRAIN`, and exits.

Runtime I/O uses a fixed pool of 256 `struct hio` entries, each with a `MAXPHYS` data buffer. Three queues are coordinated by mutexes and condition variables: free, disk, and send. `recv_thread()` validates protocol headers, receives write data, counts stats, handles keepalives, and clones memsync write requests so the primary can get an early "received" reply plus the later disk-completion reply. `disk_thread()` clears the local active map on the first real request after the primary has received it, then performs `pread()`, `pwrite()`, `g_delete()`, and `g_flush()`. `send_thread()` serializes replies, includes read data only on successful reads, reports per-command errors, and recycles requests.

Security and correctness checks include sector-size alignment, nonzero length, `MAXPHYS` write/read limit, datasize bounds, command validation, privilege drop before steady-state service, and disconnect events on fatal protocol errors.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/secondary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/subr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/subr.c

`subr.c` contains HAST support routines: append-style `snprintf` wrappers, local provider probing, role string conversion, and privilege dropping.

`provinfo()` opens the configured local path if needed and accepts only character devices and regular files. Character devices are treated as GEOM providers queried with `DIOCGMEDIASIZE` and `DIOCGSECTORSIZE`; regular files use file size and a hardcoded 512-byte sector size.

`drop_privs()` resolves the `hast` user, jails or chroots into that user's home directory, switches to `/`, clears supplementary groups, sets gid/uid, optionally enters Capsicum, and limits capabilities/ioctls for local provider and primary ggate descriptors. It verifies real/effective/saved uid/gid and no supplementary groups before reporting success.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/subr.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/subr.h

`subr.h` declares shared HAST helper functions and the `KEEP_ERRNO(work)` macro, which preserves `errno` across cleanup code.

The exported functions cover append-formatting, provider information discovery, role-name formatting, and privilege dropping. The header includes `hast.h`, so the helper API is tied to `struct hast_resource`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/synch.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/synch.h

`synch.h` wraps pthread mutexes, rwlocks, and condition variables in assertion-checked inline helpers for HAST. The wrappers include Clang thread-safety annotations such as `__locks_exclusive`, `__unlocks`, and `__requires_exclusive`.

Mutex and rwlock wrappers assert successful init/destroy/lock/unlock operations, `mtx_trylock()` accepts only success or `EBUSY`, and `mtx_owned()` uses FreeBSD's `pthread_mutex_isowned_np()`. Condition variables are initialized with `CLOCK_MONOTONIC`; `cv_timedwait()` treats timeout zero as an indefinite wait and otherwise returns whether `ETIMEDOUT` occurred.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/synch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/token.l -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/token.l

`token.l` is the flex lexer for HAST configuration parsing. It emits parser tokens for top-level config keywords, replication/checksum/compression values, boolean-like tokens, resource fields, numbers, strings, and braces.

It tracks global `depth` on `{`/`}` and global `lineno` on newlines. Numeric tokens use `atoi()`, string tokens are duplicated with `strdup()`, comments beginning with `#` and whitespace are ignored, and legal string characters are alphanumerics plus `.`, `-`, `_`, `/`, `:`, `[`, and `]`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/token.l -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/Makefile

This Makefile builds the FreeBSD `ifconfig` utility and controls which address-family and feature modules are compiled based on `src.opts.mk` knobs.

It always includes the base dispatcher plus link, clone, MAC, media, FIB, VLAN, VXLAN, GRE, GIF, IPsec, SFP, CARP, group, bridge, and lagg support. IPv4, IPv6, ND6/STF, wireless, pfsync, jail, and netlink/GENEVE pieces are conditional. The comments note that source order defines constructor order and therefore default status display order.

It links against `libifconfig`, `libm`, `libutil`, `libnv`, optional `lib80211`, and optional `libjail`, installs `ifconfig.8`, enables warning flags, and includes tests when requested.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet.c

`af_inet.c` implements IPv4 address-family support for `ifconfig`. It registers the `inet` family, status printing, address parsing/copying, tunnel display/setup, CARP VHID plumbing, and add/delete execution through either legacy ioctls or netlink.

Status output prints the IPv4 address, point-to-point destination, netmask in configured format (`cidr`, `dotted`, or hex), broadcast address, and VHID. Address parsing accepts numeric addresses, host names, network names, and `addr/prefix` syntax; setting a new non-loopback/non-point-to-point address without a mask is rejected.

In ioctl builds it fills `in_aliasreq`/`ifreq` structures and uses `SIOCAIFADDR`/`SIOCDIFADDR`. In netlink builds it builds `RTM_NEWADDR`/`RTM_DELADDR` messages with `IFA_LOCAL`, optional destination/broadcast, FreeBSD flags, and VHID. It also emulates legacy `SIOCDIFADDR` behavior by deleting the first IPv4 address when no explicit delete address was supplied.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet6.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet6.c

`af_inet6.c` implements IPv6 support for `ifconfig`, including address parsing, prefix handling, address flags, lifetimes, EUI-64 suffix filling, ND6 command registration, tunnel setup/display, and CARP VHID propagation.

Status output prints IPv6 address, point-to-point destination, prefix length, IPv6 address flags, scope ID, optional preferred/valid lifetime, and VHID. Commands include `prefixlen`, anycast/tentative/deprecated/autoconf/prefer_source, ND6 toggles, `pltime`, `vltime`, `eui64`, and the `-L` option for lifetime display.

The file supports both ioctl and netlink builds. Ioctl mode uses `in6_aliasreq`, `in6_ifreq`, `SIOCAIFADDR_IN6`, `SIOCDIFADDR_IN6`, and `SIOCSIFPHYADDR_IN6`; netlink mode builds IPv6 address messages with `IFA_LOCAL`, optional peer address, cacheinfo lifetime, FreeBSD flags, and VHID. If no prefix is explicit, post-processing defaults IPv6 prefixes to 64.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_link.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_link.c

`af_link.c` implements link-layer address handling for the `link`, `ether`, and `lladdr` address families. It registers three names that share the same status, parser, and `SIOCSIFLLADDR` execution path.

Status printing emits Ethernet addresses in the selected format (`colon`, `dash`, or `dotted`) or generic `lladdr` text from `link_ntoa()`. It also prints original hardware address when available and meaningfully different, and prints LAN PCP if configured.

Address setting accepts `random`, generating a locally administered non-multicast Ethernet address, or parses a supplied link address with `link_addr()`. It rejects attempts to set link-level netmask or broadcast values.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_link.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_nd6.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_nd6.c

`af_nd6.c` provides IPv6 Neighbor Discovery option handling used by the IPv6 module. It gets/sets ND6 interface flags with `SIOCGIFINFO_IN6` and `SIOCSIFINFO_IN6`, and manages the default IPv6 interface with `SIOCGDEFIFACE_IN6`/`SIOCSDEFIFACE_IN6`.

`nd6_status()` opens an IPv6 datagram socket, reads ND6 flags, checks whether the interface is the default interface, and prints `nd6 options=` only when options or default-interface state are present. The bit-name table covers NUD, router-advertisement, source preference, disabled, route suppression, auto-linklocal, RADR, DAD, stable-address, and default-interface state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/af_nd6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/carp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/carp.c

`carp.c` implements CARP and VRRP configuration/status integration for `ifconfig` using `libifconfig`. It registers CARP/VRRP commands and an `AF_UNSPEC` status hook.

Status reads up to `CARP_MAXVHID` entries and prints CARP state, VHID, advbase, advskew, optional key, IPv4/IPv6 peers, or VRRP state, VRID, priority, and interval. Setters collect command-line values in file-scope state and defer application via `setcarp_callback()` registered when `vhid` is set.

Commands cover `vhid`, password, advskew/base, state, peer/mcast IPv4, peer6/mcast6 IPv6, CARP/VRRP version, VRRP priority, and VRRP advertisement interval. The callback fetches an existing VHID entry if present, overlays requested fields, and writes it with `ifconfig_carp_set_info()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/carp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifbridge.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifbridge.c

`ifbridge.c` implements bridge interface status and configuration commands. It uses `SIOCSDRVSPEC`/`SIOCGDRVSPEC` driver-specific ioctls through `do_cmd()` for mutations and `libifconfig` for full bridge status.

Status prints bridge ID, priority, timers, STP protocol/root details, cache sizing, bridge flags, default untagged VLAN, member ports, member flags, STP role/state/protocol, VLAN protocol, untagged VLAN, and tagged VLAN ranges. It can also dump the forwarding cache with MAC, VLAN, interface, expiry, and flags.

Commands cover adding/removing members, span ports, member flags, STP settings, edge/ptp options, flushing dynamic/all cache entries, static cache entries and deletions, max address counts, bridge timers, priorities, path costs, VLAN filter/default VLAN/QinQ behavior, member tagged/untagged VLAN sets, and VLAN protocol. VLAN set parsing supports `none`, `all`, comma-separated values, and ranges while excluding reserved VLAN IDs for `all`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifbridge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifclone.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifclone.c

`ifclone.c` implements clone-interface creation/destruction commands and the `-C` cloner listing option. It uses `libifconfig` to list cloners and `SIOCIFDESTROY`/`SIOCIFCREATE2` for default create/destroy behavior.

The file maintains a list of default creation callbacks matched by interface-name prefix or custom filter. `ifclonecreate()` picks a matching callback when a clone type needs parameterized creation, otherwise it performs a bare create. It special-cases `ipfw`/`ipfwlog` names with a warning that explicit creation is unnecessary in FreeBSD 16.0.

Registered commands are clone-only `create`/`plumb` and normal `destroy`/`unplumb`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifclone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.c

`ifconfig.c` is the main dispatcher for FreeBSD `ifconfig`. It owns global option parsing, address-family and command registration lists, callback deferral, interface listing, status output, address add/delete sequencing, basic interface flags/capabilities, module autoloading, jail attachment, and build-time dispatch between ioctl and netlink backends.

The command model is plugin-based: constructors in feature modules register `struct afswtch`, `struct cmd`, and options. `main()` parses global flags, handles `IFCONFIG_FORMAT`, resolves single-interface versus list mode, handles clone creation before the interface exists, detects optional address family arguments, and invokes `ifconfig_ioctl()` or `ifconfig_nl()`. In ioctl listing builds it uses `getifaddrs()`, preserves kernel order, filters by interface/group/up/down/address family, and calls per-family status hooks. In netlink builds it delegates listing to `list_interfaces_nl()`.

`ifconfig_ioctl()` interprets commands, handles clone-only command transition, treats unknown command tokens as interface/destination addresses, runs address-family post-processing, executes deferred callbacks, then performs deferred delete/add address operations. Basic commands include up/down, arp/debug/promisc/allmulti, description, alias/delete, netmask/broadcast, tunnel setup/removal, jail vnet movement, link flags, many interface capabilities, PCP, MTU, and rename.

Support helpers include group matching with shell patterns, status bit formatting, `%b`-style bit printing, VHID printing from `ifaddrs`, tunnel status fanout, metric/status printing, capability-NV packing, and module autoload guessing with explicit aliases for tun/tap/vmnet/ipsec/enc.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.h

`ifconfig.h` defines the shared internal API for `ifconfig` modules. It declares the context object, command handler signatures, command registration macros, address-family switch table, parsed argument structure, option registration, global formatting variables, and cross-module helper functions.

The command table supports fixed integer parameters, one argument, two arguments, optional argument, string parameter, vector arguments, and clone-only commands. The address-family table abstracts status output, address parsing/copying, prefix parsing, post-processing, VHID propagation, kernel execution, add/delete request storage, tunnel status/setup, and ioctl/netlink differences.

The header also declares netlink entry points when available, clone default callback registration, SFP/media hooks, common status/format helpers, and sockaddr cast helpers. Its compile-time `WITHOUT_NETLINK` macros change callback signatures and mark netlink-only parameters as used or unused.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.c

`ifconfig_netlink.c` provides the netlink backend for `ifconfig`. It opens a `NETLINK_ROUTE` socket, attempts to load the `netlink` kernel module if needed, wraps single-interface configuration through `ifconfig_nl()`, and implements netlink-based interface listing/status.

The listing path builds an ifindex-indexed `ifmap` from `RTM_GETLINK`, resolves names with a targeted `RTM_GETLINK`, dumps addresses with `RTM_GETADDR`, attaches parsed addresses to interfaces, sorts interfaces in kernel-provided order, sorts addresses by family and original order, applies interface/name/group/up/down/address-family filters, and then prints either names or full status.

Status output prints flags, metric, MTU, description, capabilities, tunnel status, link-level address, address-family statuses, other status hooks, driver name, interface status text, and optional SFP data. Link and address parsing relies on `netlink_snl_route` parser structures shared with address-family modules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.h

`ifconfig_netlink.h` is a small conditional include wrapper for netlink support. When `WITHOUT_NETLINK` is not defined, it includes the core FreeBSD netlink headers, route netlink headers, simple-netlink helper API, route compatibility helpers, and route parsers.

Modules include this header to share netlink parser/writer types while keeping non-netlink builds free of those dependencies.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/iffib.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/iffib.c

`iffib.c` adds commands and status output for non-default interface and tunnel FIBs. Status queries `SIOCGIFFIB` and `SIOCGTUNFIB`, printing only values different from `RT_DEFAULT_FIB`.

The `fib` and `tunnelfib` setters parse unsigned integer values with `strtoul()`, reject trailing garbage and values above `UINT_MAX`, and apply them with `SIOCSIFFIB` and `SIOCSTUNFIB`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/iffib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgeneve.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgeneve.c

`ifgeneve.c` implements GENEVE interface support for netlink-enabled `ifconfig` builds. It registers clone creation for `geneve*` interfaces, GENEVE-specific configuration commands, GENEVE status output, and parser verification for nested netlink attributes.

Status fetches `RTM_GETLINK` data for a GENEVE interface, parses nested `IFLA_LINKINFO`/`IFLA_INFO_DATA`, prints mode (`l2` or `l3`), VNI, local/remote or multicast group endpoint, device for multicast, and in verbose mode prints port range, TTL, DSCP inheritance, DF behavior, external metadata mode, L2 forwarding-table state/counters, and offload statistics.

Configuration commands send `RTM_NEWLINK` messages with nested GENEVE attributes. They set clone-time mode, VNI, local address, remote address, multicast group, local/remote ports, source port range, forwarding-table timeout/max entries, multicast device, TTL or inherit, DF mode, DSCP inheritance, learning, flush behavior, external metadata mode, and GENEVE hardware checksum/TSO capabilities. Address validation distinguishes multicast-only group addresses from non-multicast local/remote endpoints.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgeneve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgif.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgif.c

`ifgif.c` adds GIF tunnel option status and commands. It reads options with `GIFGOPTS`, prints nonzero flags with names for `NOCLAMP` and `IGNORE_SOURCE`, and writes modified options with `GIFSOPTS`.

Registered commands toggle `noclamp` and `ignore_source` by reading the current option word, setting or clearing the requested bit, and writing it back.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgre.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgre.c

`ifgre.c` adds GRE tunnel key, UDP port, and option handling. Status prints a nonzero GRE key, optional UDP encapsulation port, and option bits for checksum, sequence, and UDP encapsulation.

Commands set `grekey` with `GRESKEY`, set `udpport` with `GRESPORT`, and toggle `enable_csum`, `enable_seq`, and `udpencap` by reading `GREGOPTS`, changing bits, and writing `GRESOPTS`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgre.c -->