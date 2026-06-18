# sources/distributed-fs/lustre-release/lnet/lnet/config.c

## Purpose

`config.c` is the kernel-side LNet configuration parser and local network object constructor. It turns legacy module strings such as `networks`, `routes`, and `ip2nets` into `struct lnet_net`, `struct lnet_ni`, route, and interface-selection state, and it exposes helpers that LNDs and dynamic configuration paths use to allocate/free NIs, bind interfaces, check link status, and select an enumerated inet interface for a configured NID.

The file is mostly initialization/configuration code rather than packet fast path. Its persistent state is in the live `the_lnet` topology: net lists, NI lists, CPT restrictions, route table entries, per-NI net namespace references, health/fatal-link flags, and route/NI allocation side effects.

## Important APIs, Types, and Functions

- `struct lnet_text_buf` is a temporary parser allocation used for route and `ip2nets` token expansion. Global `lnet_tbnob` bounds cumulative scratch allocation to `LNET_MAX_TEXTBUF_NOB`, and `LNET_SINGLE_TEXTBUF_NOB` bounds each token.
- `lnet_net_unique()` and `lnet_ni_unique_net()` enforce duplicate-network and duplicate-interface checks within supplied lists.
- `lnet_net_append_cpts()` and `lnet_net_remove_cpts()` maintain `net->net_cpts`, `net->net_ncpts`, and `the_lnet.ln_cpt_restricted_count` as NIs with restricted CPT arrays are added and removed.
- `lnet_net_alloc()`, `lnet_net_free()`, `lnet_ni_alloc()`, `lnet_ni_alloc_w_cpt_array()`, `lnet_ni_free()`, and `lnet_ni_add_interface()` create and destroy `lnet_net`/`lnet_ni` objects, allocate per-CPT NI refs and TX queues, capture the current net namespace, and attach new NIs to `net_ni_added`.
- `lnet_parse_networks()` parses the legacy `networks` string grammar: network name, optional interface list in parentheses, optional CPT expression in brackets on either the net or individual interface.
- `lnet_parse_routes()` parses legacy route strings into calls to `lnet_add_route()`. It supports comments/separators, bracket expansion, optional hop count, and per-gateway selection priority after `:`.
- `lnet_parse_ip2nets()` enumerates local inet devices, matches address expressions from `ip2nets`, then returns a synthesized networks string through `lnet_match_networks()`.
- `lnet_set_link_fatal_state()`, `lnet_get_link_status_locked()`, `lnet_get_link_status()`, and `lnet_inet_select()` expose link/inet helpers to LNDs.

## Control Flow

Network allocation starts with `lnet_net_alloc()`, which either returns an existing matching net or initializes a new net object with NI lists, route preference list, tunables set to undefined, `net_last_alive`, and max selection priority. NI allocation flows through `lnet_ni_alloc_common()`: it checks interface uniqueness on the pending list, allocates the NI, initializes locks/lists/handles, allocates per-CPT refs and TX queues, sets the NID or leaves the LND to fill in the address portion, takes a reference to the current or init net namespace, and appends to `net_ni_added`. The public allocation variants then interpret CPT restrictions either from a `cfs_expr_list` or a caller-provided array and append that CPT coverage to the parent net.

`lnet_parse_networks()` is a destructive parser over a private copy of the string. For each network token it parses name, optional interface list, and optional net-level CPT expression, rejects bad delimiters, converts the name with `libcfs_str2net()`, ignores explicit loopback, allocates/gets the net, and either creates a default NI or walks the interface list and optional interface-level CPT expressions. On syntax or allocation failure it emits `lnet_syntax()` diagnostics, frees any partially built nets/NIs, frees expression lists, and returns `-EINVAL`.

Route parsing first splits the input with `lnet_str2tbs_sep()` by newline, carriage return, or semicolon while honoring comments. Each route command is tokenized by `lnet_parse_route()`: first token is one or more destination nets with bracket expansion, optional second token can be hops, remaining tokens are gateway NIDs with optional `:priority`. Local gateways set `*im_a_router`; remote gateways call `lnet_add_route()` and tolerate existing/unreachable routes. All text buffers must drain back to `lnet_tbnob == 0`.

`ip2nets` parsing enumerates local IPv4 addresses via `lnet_inet_enumerate()`, converts to host-order addresses, filters each text entry by address expressions, splits matched network specs while preserving interface groups in parentheses, rejects duplicate networks, and returns the comma-joined matched networks. Empty match is `-ENOENT`.

## State and Persistence Behavior

This file persists configuration into in-memory LNet objects only. `struct lnet_net` owns live NI lists (`net_ni_list`, `net_ni_added`, `net_ni_zombie`), CPT restrictions, tunables, health-derived timestamps, and route preference data. `struct lnet_ni` owns per-CPT refs/queues, interface string, current net namespace reference, CPT restrictions, state, selection priority, health/fatal flags, and recovery-related handles initialized elsewhere.

CPT restriction accounting is subtle: `NULL net_cpts` with `net_ncpts == LNET_CPT_NUMBER` means unrestricted. Transitions between restricted and unrestricted update `ln_cpt_restricted_count`. OOM during CPT rebuild intentionally degrades to unrestricted behavior to preserve function at lower NUMA efficiency.

Text parser allocations are intentionally temporary and globally counted. `lnet_parse_routes()` and `lnet_match_networks()` assert the counter returns to zero, making leaks visible in debug builds.

## Dependencies and Integration Points

The file depends on kernel networking (`struct net_device`, rtnl locking, ethtool `get_link`, net namespaces), Lustre/LNet core types from `lib-lnet.h`, libcfs expression/range parsers, NID/net conversion helpers, route-table APIs such as `lnet_add_route()`, interface enumeration through `lnet_inet_enumerate()`, NI status propagation via `lnet_push_update_to_peers()`, and per-CPT allocation through `cfs_percpt_alloc()`.

It integrates with LND startup: LNDs consume allocated NIs, may fill unspecified NID address bits, call `lnet_inet_select()` against enumerated devices, and use link-status helpers. It also integrates with dynamic configuration because `lnet_net_alloc()` can be called against arbitrary net lists and because CPT accounting affects global scheduling/NUMA behavior.

## Risks and Edge Cases

- Legacy string parsing is destructive and delimiter-sensitive; malformed parentheses/brackets, empty interface names, duplicated nets in `ip2nets`, or unexpected delimiters all collapse to `-EINVAL`.
- `lnet_parse_networks()` returns `-EINVAL` for all failures after cleanup, including some allocation failures, so callers may lose exact `-ENOMEM` detail.
- `lnet_tbnob` is a static global parser counter and the route parser comments assume single-threaded use. Concurrent parser use would make the allocation limit/accounting unsafe.
- Interface uniqueness is checked only against `net_ni_added` during common allocation; comments say LNDs own broader interface conflict checks.
- `lnet_get_link_status_locked()` dereferences `dev->ethtool_ops->get_link` without first checking `dev->ethtool_ops`, so callers must pass devices with operations initialized or this path can fault.
- CPT counter transitions are easy to imbalance if future callers manipulate `net_cpts` outside the helpers.
- `ip2nets` currently records only `li_ipaddr` into `ipaddrs`, so IPv6 matching depends on lower helper behavior and the local representation available to this older code path.

## Test Signals

Useful tests should cover successful and failing `networks` strings, including net-level CPTs, interface-level CPTs, duplicate interface names, loopback suppression, malformed delimiters, and full cleanup of partially allocated nets. Route tests should exercise separators, comments, bracket expansion, optional hops, gateway priorities, local gateway router detection, duplicate route tolerance, and `lnet_tbnob` returning to zero. `ip2nets` tests should cover match/no-match, duplicate networks, interface groups in parentheses, malformed address tokens, and long strings. Allocation tests should validate restricted/unrestricted CPT transitions and `ln_cpt_restricted_count`. Link helper tests should cover no device, down device, missing `get_link`, and `lnet_inet_select()` matching by interface name, IPv4/IPv6 address, and default first interface.
