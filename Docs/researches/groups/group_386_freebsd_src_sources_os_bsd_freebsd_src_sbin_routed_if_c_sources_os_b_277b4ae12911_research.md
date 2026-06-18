# Group Research: group_386_freebsd_src_sources_os_bsd_freebsd_src_sbin_routed_if_c_sources_os_b_277b4ae12911

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/freebsd-src`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/if.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/if.c

Interface discovery, lifecycle, lookup, health monitoring, and direct-route installation for FreeBSD `routed`.

Key responsibilities:
- Maintains global local/remote interface lists plus address, broadcast, and name hash tables.
- Resolves interfaces by address, name, index, and likely packet ingress network.
- Computes classful/RIPv1 masks, checks destination sanity, duplicate interfaces, and remote-gateway reachability.
- Periodically reads kernel interface state via routing sysctl `NET_RT_IFLIST`.
- Adds, changes, deletes, sickens, and restores interfaces, including aliases and multicast group membership.
- Detects bad/off/disappeared links through interface flags and packet/error counters.
- Installs connected routes, loopback host routes for point-to-point local ends, multihomed host routes, and synthetic RIPv1 network routes.
- Applies configured interface parameters through `get_parms()` and enables RIP/router-discovery state.

Dependencies:
- Uses `defs.h`, `pathnames.h`, routing table helpers, radix walking, router discovery hooks, RIP socket state, kernel routing sockets/sysctls, multicast group socket options, and `/etc/gateways` path constants.

Notable risks:
- Interface deletion recursively removes aliases while walking shared lists, so traversal safety is important.
- Broken/sick state drives route deletion and rediscovery timing; subtle counter wrap or timing bugs can destabilize routes.
- RIPv1 classful/subnet synthesis logic can create or remove daemon routes that differ from kernel route aggregation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/if.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/input.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/input.c

RIP packet receive path, request/response processing, authentication validation, and route-update ingestion.

Key responsibilities:
- Reads RIP datagrams from global or per-interface UDP sockets.
- Determines the authenticated/expected incoming interface using source address or `SO_PASSIFNAME` interface metadata.
- Validates RIP versions, lengths, commands, source ports, enabled input policy, and router trust.
- Answers full-table and specific-route RIP requests, including query-specific security controls.
- Handles trace on/off RIP commands from privileged ports and known routers.
- Processes RIP responses with metric, mask, next-hop, default-route, and trusted-gateway filtering.
- Deaggregates received RIPv2 routes when RIPv1 output requires more specific routes.
- Updates primary/spare route slots through `input_route()`.
- Validates cleartext and MD5 RIPv2 authentication with key lifetimes and key IDs.

Dependencies:
- Uses route table APIs (`rtget`, `rtfind`, `rtadd`, `rtchange`, `rtswitch`), interface lookup/state, output buffers from `output.c`, auth structures, MD5, and rate-limited logging.

Notable risks:
- Authentication deliberately accepts unauthenticated RIPv2 when no secrets are configured, matching historic behavior but not strong security.
- The code contains many compatibility choices for RIPv1/RIPv2 interoperability that affect route masks and aggregation.
- Incorrect source-interface classification can cause legitimate routes to be rejected or malicious routes to be accepted.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/main.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/main.c

Main daemon entry point, option parsing, socket setup, signal handling, timer scheduling, and event loop.

Key responsibilities:
- Parses daemon flags for supplier/quiet mode, default-route advertisement, multihomed host routes, tracing, auth behavior, fake routes, and parameter overrides.
- Checks root privileges and kernel IP forwarding state, disabling supplier behavior when forwarding is off.
- Daemonizes unless debugging, opens syslog, routing socket, RIP sockets, trace output, buffers, and radix table state.
- Initializes timing epoch and randomizes broadcast/router-discovery intervals.
- Reads `/etc/gateways`, discovers interfaces, sends initial RIP queries, and sends router-discovery solicitations.
- Runs a single-threaded `select()` loop over routing, RIP, per-interface RIP, and router-discovery sockets.
- Drives interface rescans, kernel route flush checks, periodic RIP broadcasts, flash updates, route aging, kernel sync, and router discovery.
- Provides helpers for select fd rebuilding, socket option setup, RIP socket on/off behavior, allocation, random intervals, timeval math, and logging.

Dependencies:
- Coordinates nearly every routed subsystem: interface manager, route table, RIP input/output, router discovery, trace, parameters, and kernel routing socket.

Notable risks:
- Time monotonicity is simulated with a microsecond fudge; timer ordering depends on this invariant.
- Signal handlers only set simple state, but shutdown triggers final RIP/router-discovery advertisements.
- Main loop behavior changes substantially depending on `supplier`, router discovery, forwarding, and interface counts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/output.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/output.c

RIP packet construction, route-table export, split horizon, route aggregation, authentication emission, broadcasts, and queries.

Key responsibilities:
- Initializes shared RIPv1/RIPv2-compatible and RIPv2-only packet buffers.
- Sends RIP packets as query replies, unicasts, broadcasts, or multicasts with correct sockets and interface selection.
- Chooses outgoing authentication keys and emits cleartext or MD5 RIPv2 authentication records.
- Walks the daemon route table and converts routes into advertisement entries.
- Applies supplier/quiet policy, fake default routes, multihomed host retention, host-route suppression, split horizon, poison reverse, outgoing metric adjustments, and route tags.
- Aggregates or deaggregates routes based on RIPv1/RIPv2 compatibility, subnet/supernet policy, and query mode.
- Sends full or flash broadcasts to all eligible interfaces.
- Sends one-time RIP table requests on eligible interfaces.

Dependencies:
- Uses route radix walking, aggregation helpers (`ag_check`, `ag_flush`), interface state, auth config, MD5, global timers, and socket output from `main.c`.

Notable risks:
- Advertisement semantics differ between RIPv1-compatible and full RIPv2 buffers; fields such as mask/tag/next-hop must be zeroed for old listeners.
- Split-horizon and poison-reverse state mutates per-route poison tracking while generating output.
- Multicast interface selection is global per socket and must track the selected outgoing interface correctly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/output.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/parms.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/parms.c

Configuration parsing and application for `/etc/gateways`, command-line `-P` options, auth keys, synthetic networks, RIPv1 masks, and trusted gateways.

Key responsibilities:
- Applies matching parameter records to interfaces by name, all interfaces, or address/net match.
- Reads legacy `/etc/gateways` remote/passive/external gateway entries and creates remote interface records.
- Parses parameter lines for RIP, RIPv1/RIPv2, aggregation, router discovery, passive mode, fake defaults, metric adjustment, redirect policy, trusted gateways, and passwords.
- Supports `subnet=` authority routes and `ripv1_mask=` classful compatibility overrides.
- Parses cleartext and MD5 passwords with optional key ID and validity timestamps, accepting MD5 only from secure files.
- Checks parameter conflicts and stores records in operator-specified order.
- Resolves host and network names/numeric forms with optional prefix lengths.

Dependencies:
- Uses `defs.h`, `pathnames.h`, host/network resolver APIs, interface insertion, route mask helpers, and global config lists consumed by interface and RIP logic.

Notable risks:
- Password parsing depends on secure ownership/mode checks only for file-sourced MD5 parameters.
- `parse_quote()` implements custom escaping and delimiter handling used for secrets and parameter values.
- Conflicting overlapping parameter records are allowed only where explicit consistency checks pass; ordering affects final interface state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/parms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/pathnames.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/pathnames.h

Path constants for `routed` configuration and remote trace control.

Key responsibilities:
- Defines `_PATH_GATEWAYS` as `/etc/gateways`.
- Defines `_PATH_TRACE` as `/etc/routed.trace`.
- Includes `<paths.h>` for platform path definitions.
- Documents the security model for remotely requested trace files: requests must match the startup trace file or use the configured trace prefix.

Dependencies:
- Consumed by daemon configuration parsing, remote gateway handling, and trace command logic.

Notable risks:
- Remote trace control is intentionally enabled through a fixed `/etc` path; safety depends on trace implementation checks and filesystem permissions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/radix.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/radix.c

Userland BSD radix tree implementation used for routing table lookup, insertion, deletion, mask handling, and traversal.

Key responsibilities:
- Implements compressed binary radix search over variable-length keys.
- Supports exact lookup, longest-prefix match, masked lookup, and mask-aware search.
- Interns masks in a separate mask radix tree and annotates route subtrees with radix masks.
- Handles normal contiguous masks and non-contiguous masks.
- Inserts routes, duplicate-key entries, and mask chains ordered by specificity/refinement.
- Deletes routes while maintaining duplicate-key chains, parent links, and subtree mask annotations.
- Walks the tree safely even when callback functions delete current nodes.
- Initializes zero/one root keys, mask tree, and radix node-head function pointers.

Dependencies:
- Includes `defs.h`; uses `rtmalloc`, syslog-style logging, and structures declared in `radix.h`.

Notable risks:
- Pointer manipulation is dense and deletion mutates tree topology in place; dangling mask annotations are explicitly treated as serious consistency errors.
- Duplicate-key and non-contiguous-mask ordering rules are subtle and central to correct route selection.
- `max_keylen` must be set before `rn_init()` or initialization cannot allocate proper key buffers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/radix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/radix.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/radix.h

Radix tree public structures, macros, and function declarations for the userland routing table implementation.

Key responsibilities:
- Defines `struct radix_node` for internal and leaf nodes with parent, bit index, bit mask, flags, key, mask, and duplicate-key chain fields.
- Defines `struct radix_mask` for masks attached to subtrees and normal-route annotations.
- Defines `struct radix_node_head` with tree root, key sizes, operation callbacks, and embedded root nodes.
- Provides mask allocation/free-list macros and memory wrapper macros.
- Declares `rn_init()`, `rn_inithead()`, and `rn_walktree()`.

Dependencies:
- Includes `sys/cdefs.h`; expects `rtmalloc`, `free`, `memmove`, and `memset` availability through including translation units.

Notable risks:
- Exposes internal layout used by route entries and tree manipulation code; ABI/layout changes must match `radix.c`.
- Allocation macros rely on a global free list and have side effects, so callers must treat them carefully.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/radix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/rdisc.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/rdisc.c

ICMP Router Discovery Protocol support for client solicitation, router advertisement, default-route selection, and multicast group management.

Key responsibilities:
- Defines local ICMP router advertisement and solicitation packet layouts.
- Opens and configures a raw ICMP socket for router discovery.
- Joins/leaves all-hosts and all-routers multicast groups per interface based on supplier/client mode and policy.
- Switches the daemon to supplier mode when multiple RIP interfaces make route supply necessary.
- Maintains a fixed table of discovered routers with interface, gateway, lifetime, and preference.
- Ages discovered routers, removes stale/bad defaults, chooses the best default route, and toggles RIP on/off depending on router discovery success.
- Sends router advertisements as supplier and solicitations as client with randomized timers.
- Parses incoming advertisements and solicitations, validates packet shape, source/interface, address size, lifetime, preferences, and reachable gateways.
- Responds to valid solicitations with unicast advertisements.

Dependencies:
- Uses raw sockets, ICMP/IP headers, multicast group socket options, route-table default-route operations, interface state, timers, and RIP socket control.

Notable risks:
- Deliberately departs from RFC 1256 in aging bad routers quickly to avoid black holes.
- Preference conversion uses signed/unsigned transforms and metric biasing; errors can invert route choice.
- Packet interface attribution is limited without `SO_PASSIFNAME`, especially for source address zero solicitations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/rdisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/rtquery/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/rtquery/Makefile

Build recipe for the `rtquery` routed diagnostic tool.

Key responsibilities:
- Builds program `rtquery`.
- Installs manual page `rtquery.8`.
- Places the tool in the `runtime` package.
- Links against `libmd` for MD5 support.
- Sets warning level default to `3` and disables array-bounds warning handling through `NO_WARRAY_BOUNDS`.
- Includes FreeBSD `bsd.prog.mk`.

Dependencies:
- Requires the FreeBSD bsd.prog.mk build system and MD library.

Notable risks:
- `NO_WARRAY_BOUNDS` suggests the source intentionally uses packet unions or flexible indexing patterns that may otherwise trigger compiler diagnostics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/rtquery/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/rtquery/rtquery.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/rtquery/rtquery.c

Standalone RIP query and trace-control utility for probing `routed` instances and printing RIP responses.

Key responsibilities:
- Parses options for numeric output, gated-style poll requests, RIPv1 mode, wait timeout, specific target route, trace commands, and cleartext/MD5 authentication.
- Builds RIP request, poll, trace-on, trace-off, and trace-dump packets.
- Sends queries to one or more hosts on the RIP UDP port and waits for distinct responders.
- Supports full-table requests or single-route requests with host/network/prefix parsing.
- Emits RIPv2 cleartext or MD5 authentication records in outgoing requests.
- Prints response source names/addresses, packet version/size, route destination, mask/prefix, metric, name, next-hop, tag, and authentication contents.
- Verifies displayed MD5 response trailers against the supplied password.
- Provides local helpers for printable secret strings, classful mask guessing, network parsing, and escaped password parsing.

Dependencies:
- Uses `<protocols/routed.h>`, UDP sockets, resolver APIs, MD5 functions from `libmd` or NetBSD `<md5.h>`, and RIP packet constants shared with routed.

Notable risks:
- Trace commands require UID 0 and bind to a reserved UDP port, matching daemon-side trust checks.
- MD5 query generation uses packet-length-sensitive trailer construction; incorrect length math breaks authentication.
- Response display is diagnostic, not strict validation; it reports malformed lengths, unusual masks, and auth records while continuing to parse what it can.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/rtquery/rtquery.c -->