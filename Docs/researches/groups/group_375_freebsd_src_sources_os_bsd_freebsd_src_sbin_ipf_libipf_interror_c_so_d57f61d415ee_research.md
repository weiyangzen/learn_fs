# Group Research: group_375_freebsd_src_sources_os_bsd_freebsd_src_sbin_ipf_libipf_interror_c_so_d57f61d415ee

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/freebsd-src`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/interror.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/interror.c

IPFilter internal error-number translation table. It maps kernel/internal IPFilter error codes to stable text for filter, auth, frag, lookup, NAT, pool, proxy, scan, state, sync, destination-list, and FreeBSD ioctl/security failures.

Key behavior:
- `ipf_errors[]` is explicitly append-only; comments prohibit reusing gaps because numeric codes are external diagnostics.
- `find_error()` binary-searches the sorted table by `iee_number`.
- `ipf_geterror()` fetches the current internal error with `SIOCIPFINTERROR`; `ipf_strerror()` translates a supplied number.

Notable dependencies:
- `ipf.h`, `SIOCIPFINTERROR`, caller-supplied `ioctlfunc_t`.

Research notes:
- Correct ordering of `ipf_errors[]` is required for `find_error()` to work.
- Unknown or failed lookups return static fallback strings, so the API is not thread-safe.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/interror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ionames.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ionames.c

Static IPv4 option-name table for IPFilter rule parsing and printing.

Key behavior:
- Defines `ionames[]`, mapping option numeric values to bitmask bits, minimum lengths, and rule text names.
- Includes legacy/RFC options such as `rr`, `ts`, `lsrr`, `ssrr`, `sec`, `cipso`, `rtralrt`, and `ah`.
- Provides both `sec` and `sec-class` names for `IPOPT_SECURITY`.

Research notes:
- The duplicate security option entry is intentionally handled by printers that skip the second table row after printing normal security.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ionames.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_dotuning.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_dotuning.c

Command helper for listing, reading, and setting IPFilter tunables through ioctl objects.

Key behavior:
- Builds an `ipfobj_t` wrapping `ipftune_t` with type `IPFOBJ_TUNEABLE`.
- Parses comma-separated tuning arguments.
- `list` iterates with `SIOCIPFGETNEXT`; `name=value` uses `SIOCIPFSET`; bare `name` uses `SIOCIPFGET`.
- Prints results with `printtunable()` and reports ioctl errors through `ipf_perror_fd()`.

Research notes:
- `strtok()` mutates the caller-provided tuning string.
- Values are parsed as unsigned long only.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_dotuning.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_perror.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_perror.c

IPFilter-aware error reporting wrapper.

Key behavior:
- `ipf_perror()` prints a message with an internal IPFilter error string when available.
- `ipf_perror_fd()` preserves `errno`, asks the device for `SIOCIPFINTERROR`, prints the internal code prefix, and returns the internal error or saved `errno`.
- `ipferror()` chooses IPFilter error retrieval for valid file descriptors and normal `perror()` otherwise.

Research notes:
- Output goes directly to `stderr`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_perror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_hx.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_hx.c

Hexadecimal packet-input backend for IPFilter test tooling.

Key behavior:
- Exports `iphex` as an `ipread` provider with open, close, and packet-read callbacks.
- Reads packet bytes from text hex, ending a packet at a blank line.
- Supports optional leading metadata like `[ifname]` or `[in/out,ifname]`.
- Parses `+mcast`, `+bcast`, and `+mbcast` flags into `mb_t`.

Research notes:
- Maintains static file state and rewinds on repeated opens.
- `ifn` sometimes receives a direct pointer into the local line buffer in the no-direction bracket case, which is fragile after return.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_hx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_pc.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_pc.c

Classic pcap packet-input backend for IPFilter test tooling.

Key behavior:
- Exports `pcap` as an `ipread` provider.
- Reads the pcap file header, detects byte-swapped captures, and supports a small set of DLT/link types.
- Reads packet records, strips configured link-layer header/type bytes, and returns packet payload into `mb_t`.

Research notes:
- Only a few link-layer types are understood.
- Allocated static packet buffer is resized but not freed by this module.
- The IP protocol type bytes are copied into `ty` but the filtering loop is disabled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_pc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_tx.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_tx.c

Text packet-description backend for IPFilter test tooling.

Key behavior:
- Exports `iptext` as an `ipread` provider with checksum recomputation requested.
- Parses lines into synthetic IPv4 or IPv6 packets.
- Supports direction, optional interface, protocol, source/destination addresses, ports, TCP flags, TCP sequence/ack, ICMP types/codes, and IPv4 options.
- Resolves hostnames and service names through helper APIs.

Research notes:
- Parser mutates token strings in place with `strtok()` and comma splitting.
- IPv6 support is conditional on `USE_INET6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_tx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipoptsec.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipoptsec.c

IPv4 security classification lookup helpers.

Key behavior:
- Defines `secclass[]` mapping textual IPSO classes to option values and match bits.
- `seclevel()` converts a text name to the IPSO class value.
- `secbit()` converts a class value to the corresponding bit.

Research notes:
- Unknown classes print diagnostics and return zero.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipoptsec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmem.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmem.c

Userland kernel-memory read adapter built on `kvm(3)`.

Key behavior:
- `openkmem()` opens kernel/core state with `kvm_open()`.
- `kmemcpy()` copies bytes from a kernel virtual address into a user buffer, retrying partial reads.
- `kstrncpy()` reads a kernel string byte by byte until NUL or size limit.

Research notes:
- Uses a single static `kvm_t *`; not thread-safe.
- Error paths print kernel address context to `stderr`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmem.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmem.h

Header for the kernel-memory helper API.

Key contents:
- Declares `openkmem()`, `kmemcpy()`, and `kstrncpy()`.
- Defines `KMEM` from `_PATH_KMEM` when available, otherwise `/dev/kmem`.
- Includes NetBSD path handling when compiled there.

Research notes:
- Legacy `__P` compatibility macro remains present.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmemcpywrap.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmemcpywrap.c

Adapter that gives `kmemcpy()` a generic copy-function shape.

Key behavior:
- `kmemcpywrap(from, to, size)` calls `kmemcpy(to, (u_long)from, size)`.
- Used by printers that accept a `copyfunc_t` for either kernel-memory or local-memory traversal.

Research notes:
- Treats `from` as a kernel virtual address, not a normal source pointer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmemcpywrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kvatoname.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kvatoname.c

Kernel function-address to name resolver.

Key behavior:
- Fills `ipfunc_resolve_t` with a function pointer and calls `SIOCFUNCL`.
- Opens `IPL_NAME` unless `OPT_DONTOPEN` is set.
- Returns a static buffer containing the resolved name.

Research notes:
- Ignores ioctl failure and returns whatever name buffer contains.
- Static return storage is overwritten on each call.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kvatoname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlist.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlist.c

Destination-list table loader/remover for the IPFilter lookup device.

Key behavior:
- Builds an `iplookupop_t` of type `IPLT_DSTLIST`.
- Adds the table unless `OPT_REMOVE` is set.
- In verbose mode, prints the destination list before loading nodes.
- Loads each destination node with `load_dstlistnode()`.
- Deletes the table when `OPT_REMOVE` is set.

Research notes:
- Empty destination-list names are rejected.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlistnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlistnode.c

Destination-list node add/delete helper.

Key behavior:
- Allocates a `frdest_t` plus optional interface-name payload.
- Copies address, type, name offset/length, and appended name bytes.
- Uses `SIOCLOOKUPADDNODE` or `SIOCLOOKUPDELNODE` depending on `OPT_REMOVE`.

Research notes:
- Allocation size uses `sizeof(*dst) + node->ipfd_dest.fd_name`; negative `fd_name` values are handled for `op.iplo_size` but still influence allocation size.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlistnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_file.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_file.c

File-backed address-list loader.

Key behavior:
- Opens `filename + 7`, matching `file://` URI inputs.
- Reads one address/list item per line.
- Handles comments, leading/trailing whitespace, CRLF, and leading `!` negation.
- Builds an `alist_t` linked list with `alist_new()`.

Research notes:
- Lines without newline are treated as too long and abort parsing.
- Because it always skips seven bytes, callers passing plain paths must already account for that offset; `load_url.c` does not appear to.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hash.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hash.c

Hash lookup-table loader/remover.

Key behavior:
- Counts entries and chooses table size from `iph_size` or `n * 2 - 1`.
- Adds a lookup hash table with `SIOCLOOKUPADDTABLE` unless removing.
- Prints verbose hash output by temporarily creating a local table array.
- Loads each hash node with `load_hashnode()`.
- Deletes the table when `OPT_REMOVE` is set.

Research notes:
- Verbose printing converts listed IPv4 addresses/masks with `htonl()` after printing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hashnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hashnode.c

Hash lookup-table node add/delete helper.

Key behavior:
- Copies family, address, mask, group, and TTL into an `iphtent_t`.
- Uses lookup ioctls to add or delete a node.
- On failure, formats the address/mask into a detailed error message.

Research notes:
- IPv6 mask formatting is suppressed in the error message under `USE_INET6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hashnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_http.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_http.c

HTTP-backed address-list loader.

Key behavior:
- Accepts `http://` URLs up to 512 bytes.
- Sends a simple HTTP/1.0 GET with `Host:` header over `connecttcp()`.
- Requires a 2xx status line.
- Strips headers, then parses body lines like `load_file()`: comments, whitespace trimming, and `alist_new()` entries.

Research notes:
- Explicitly avoids truncating oversized URLs.
- Header/body buffer compaction is manual and sensitive to off-by-one mistakes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_http.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_pool.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_pool.c

Pool lookup-table loader/remover.

Key behavior:
- Builds `IPLT_POOL` lookup operation from an `ip_pool_t`.
- Supports anonymous pools when the name is empty.
- Adds the table, optionally prints it, loads each node with `load_poolnode()`, and deletes it in remove mode.

Research notes:
- Anonymous table names can be filled back from the kernel-created name.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_poolnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_poolnode.c

Pool node add/delete helper.

Key behavior:
- Copies address, mask, negation/info flag, TTL, and node name into a local `ip_pool_node_t`.
- Uses `SIOCLOOKUPADDNODE` or `SIOCLOOKUPDELNODE`.
- On error, prints the pool name and address/mask.

Research notes:
- Mask string buffer is only eight bytes, enough for IPv4 dotted masks only because IPv6 suppresses mask text.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_poolnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_url.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_url.c

Dispatcher for address-list loading by URL/path scheme.

Key behavior:
- Sends `file://` inputs to `load_file()`.
- Sends absolute or relative local paths to `load_file()`.
- Sends `http://` inputs to `load_http()`.

Research notes:
- `load_file()` opens `filename + 7`, so the plain path branches look inconsistent and likely skip the first seven path characters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_url.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mb_hexdump.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mb_hexdump.c

Hex dumper for `mb_t` packet chains.

Key behavior:
- Walks each mbuf-like segment.
- Prints bytes as two-byte hex groups separated by spaces.
- Ends output with a newline.

Research notes:
- Similar logic is duplicated in `printpacket.c` for `OPT_HEX`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mb_hexdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/msgdsize.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/msgdsize.c

Message-chain byte counter.

Key behavior:
- `msgdsize()` walks an `mb_t` chain and sums `mb_len`.

Research notes:
- Used by packet printing assertions to compare logical IP length with mbuf-chain size.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/msgdsize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mutex_emul.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mutex_emul.c

Single-thread mutex emulation/debug checker.

Key behavior:
- Tracks magic value, owner string, held count, and source location.
- `eMmutex_enter()` aborts if uninitialized or already held.
- `eMmutex_exit()` aborts if not held exactly once.
- Init/destroy maintain a global `initcount`; `ipf_mutex_clean()` aborts if locks remain.

Research notes:
- This is not a real blocking mutex; it is misuse detection for userland/emulated builds.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mutex_emul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nametokva.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nametokva.c

Kernel function-name to address resolver.

Key behavior:
- Fills `ipfunc_resolve_t` with a function name and calls `SIOCFUNCL`.
- Opens `IPL_NAME` unless `OPT_DONTOPEN` is set.
- Returns `(ipfunc_t)-1` when the resolved address is still NULL.

Research notes:
- The name is copied with `strncpy()` without explicit forced NUL termination.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nametokva.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nat_setgroupmap.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nat_setgroupmap.c

NAT group-map port/address distribution calculator.

Key behavior:
- Computes `in_ippip`, `in_ppip`, `in_space`, and related fields based on original/new source masks.
- Handles equal masks, automatic port mapping, and explicit per-IP port allocation.

Research notes:
- Uses `USABLE_PORTS` and mask arithmetic in host byte order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nat_setgroupmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ntomask.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ntomask.c

Prefix-length to address-mask converter.

Key behavior:
- Supports IPv4 and IPv6/unspecified family.
- IPv4 prefixes produce a network-order `u_32_t` mask.
- IPv6 prefixes are delegated to `fill6bits()`.

Research notes:
- Enforces global `use_inet6` restrictions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ntomask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optname.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optname.c

IP option-name parser for rule text.

Key behavior:
- Parses comma-separated IPv4 option names into an option bitmask.
- Handles `sec-class` specially by consuming the following argument as security levels.
- Reports unknown option/security names with line numbers.

Research notes:
- Mutates the current argument through `strtok()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprint.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprint.c

IPv4 option-match pretty-printer.

Key behavior:
- Prints positive `opt` matches from option mask/bits.
- Prints `sec-class` matches with named security levels.
- Prints negative `not opt` clauses for mask bits not present in match bits.

Research notes:
- Knows about the duplicate `IPOPT_SECURITY` rows in `ionames[]` and skips appropriately.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprintv6.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprintv6.c

IPv6 extension-header match pretty-printer.

Key behavior:
- Compiled only under `USE_INET6`.
- Prints positive `v6hdr` matches from `v6ionames[]`.
- Prints negative `not v6hdrs` matches when mask and bits differ.

Research notes:
- Accepts a `sec` parameter for signature parity but does not use IPv6 security-class data.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprintv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optvalue.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optvalue.c

IPv4 option lookup helpers.

Key behavior:
- `getoptbyname()` maps option text to its match bit.
- `getoptbyvalue()` maps numeric IP option value to its match bit.

Research notes:
- Returns `(u_32_t)-1` for not found.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optvalue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsefields.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsefields.c

Comma-separated output-field parser.

Key behavior:
- Parses requested field names against a `wordtab_t` table.
- Allows `field=header` overrides; empty header sets global `nohdrfields`.
- Produces a sentinel-terminated allocated `wordtab_t` list.

Research notes:
- Unknown fields call `exit(1)`.
- Uses `reallocarray()` and aborts on allocation failure after initial allocation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsefields.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parseipfexpr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parseipfexpr.c

Parser for IPFilter expression syntax into packed kernel expression arrays.

Key behavior:
- Supports operands such as `ip.addr`, `ip.src`, `ip.dst`, IPv6 variants, `ip.p`, TCP/UDP ports, TCP flags/state, and `idle-gt`.
- Removes all whitespace and requires semicolon-terminated expressions.
- Builds an integer array prefixed with total size and terminated with `IPF_EXP_END`.
- Encodes command metadata in `ipfexp_t` records followed by typed integer arguments.

Research notes:
- `arg < ops + 2` is evaluated before `arg == NULL`, making missing `=` handling fragile.
- Error strings may be static or allocated by `asprintf()`; ownership is not documented.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parseipfexpr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsewhoisline.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsewhoisline.c

WHOIS netrange line parser.

Key behavior:
- Searches for `(NET...)` or `(NET6...)` marker.
- Parses IPv4 or IPv6 start/end address ranges after the marker.
- Converts a contiguous range into base address plus mask.
- Rejects non-contiguous masks or addresses not aligned to the derived mask.

Research notes:
- IPv6 support depends on `USE_INET6`.
- IPv4 address/mask fields are stored in `addrfamily_t`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/parsewhoisline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/poolio.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/poolio.c

Shared open/ioctl/close wrapper for the IPFilter lookup device.

Key behavior:
- Lazily opens `IPLOOKUP_NAME` read-write unless `OPT_DONTOPEN` is set.
- `pool_ioctl()` calls the supplied ioctl function on the cached descriptor.
- Provides `pool_close()` and `pool_fd()`.

Research notes:
- Uses one static descriptor for the process.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/poolio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/portname.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/portname.c

Port-number to service-name formatter.

Key behavior:
- Honors `OPT_NORESOLVE`.
- With protocol `-1`, tries to return a name common to TCP and UDP.
- With a concrete protocol, resolves through `getprotobynumber()` then `getservbyport()`.
- Falls back to decimal text.

Research notes:
- Returns a static buffer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/portname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/prependmbt.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/prependmbt.c

Mbuf-chain prepend helper for emulated packet handling.

Key behavior:
- Inserts `m` at the front of `*fin->fin_mp`.
- Returns zero unconditionally.

Research notes:
- No validation of `fin`, `fin_mp`, or `m`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/prependmbt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/print_toif.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/print_toif.c

Printer for `to`, `dup-to`, and `reply-to` rule destinations.

Key behavior:
- Handles normal interface destinations, destination-list destinations, and unknown destination types.
- Prints unresolved interface markers with `(!)`.
- Appends IPv4/IPv6 next-hop addresses when present.

Research notes:
- Resolves names as offsets into the rule’s packed name buffer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/print_toif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactiveaddr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactiveaddr.c

Active NAT/state address printer.

Key behavior:
- For IPv4, formats through `inet_ntoa()` and caller-supplied format string.
- For IPv6, delegates to `printaddr()` when compiled with `USE_INET6`.

Research notes:
- Silently ignores unknown address versions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactiveaddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactivenat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactivenat.c

Printer for live NAT table entries.

Key behavior:
- Prints NAT type, clone/orphan markers, old/new endpoints, ports, protocol, and direction-specific layout.
- Handles rewrite, outbound map, and inbound redirect forms.
- Verbose mode prints TTL, use count, checksum deltas, hashes, flags, interfaces, byte/packet counters, and IP checksum delta.
- Debug mode prints internal linkage pointers and timer queue state.

Research notes:
- Assumes `getprotobynumber()` succeeds before dereferencing `pproto->p_name`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactivenat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaddr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaddr.c

Generic rule address printer.

Key behavior:
- Handles dynamic interface, broadcast, network, peer, lookup, normal, range, and split address types.
- Delegates concrete host/mask output to `printhostmask()`, `printhost()`, and `printlookup()`.
- Prints interface-derived suffixes such as `/bcast`, `/net`, and `/peer`.

Research notes:
- Unknown address types are printed numerically with a mask.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaps.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaps.c

Application proxy session printer.

Key behavior:
- Reads proxy session and proxy descriptor from kernel memory.
- Prints proxy label, protocol, refcount, flags, bytes/packets, and data presence.
- In verbose TCP mode, prints state/selection and sequence/ack adjustment data.
- Knows specific layouts for RealAudio, FTP, and IPSec proxy private data.

Research notes:
- Depends on `kmemcpy()` and kernel structure layout compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printbuf.c

Printable/escaped buffer printer.

Key behavior:
- Emits printable bytes directly.
- Emits non-printable bytes as octal escapes.
- Stops at NUL when `zend` is nonzero.

Research notes:
- Uses current locale’s `isprint()` behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstl_live.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstl_live.c

Live kernel destination-list printer.

Key behavior:
- Filters by name when requested.
- Prints destination-list metadata unless field output is requested.
- Uses `SIOCLOOKUPITER` with `IPLT_DSTLIST` to iterate nodes.
- Deletes the iterator token with `SIOCIPFDELTOK`.

Research notes:
- Allocates fixed extra 64 bytes for variable-sized destination nodes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstl_live.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlist.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlist.c

Destination-list printer for copied or kernel-readable lists.

Key behavior:
- Copies the destination-list header through a supplied copy function.
- Filters by name when requested.
- Prints list metadata and each node through `printdstlistnode()`.
- Handles empty lists with a bare semicolon.

Research notes:
- Allocates each variable-size node using its `ipfd_size`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistdata.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistdata.c

Destination-list metadata formatter.

Key behavior:
- Prints save/debug/normal forms for destination-list headers.
- Includes role/unit, name, policy, references, delete marker, and node-list pointer depending on options.
- Delegates policy names to `printdstlistpolicy()`.

Research notes:
- Uses `pool .../dstlist` syntax for save-style output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistnode.c

Destination-list node formatter.

Key behavior:
- Copies the fixed header, then copies the full variable-sized node.
- Field mode prints selected fields via `printpoolfield()`.
- Normal mode prints optional interface name, address, and semicolon.
- Debug mode prints interface, address, state/ref/name/uid details.

Research notes:
- On full-node copy failure, allocated memory is not freed before return.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistpolicy.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistpolicy.c

Destination-list policy name printer.

Key behavior:
- Maps `IPLDP_NONE`, `IPLDP_ROUNDROBIN`, `IPLDP_CONNECTION`, and `IPLDP_RANDOM` to text.

Research notes:
- Unknown policies print nothing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistpolicy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfieldhdr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfieldhdr.c

Field-header printer for tabular output.

Key behavior:
- Supports `"all"` sentinel value `-2` by recursively printing all positive fields.
- Prints caller-supplied header overrides as-is.
- Uppercases default field names for display.

Research notes:
- Duplicates the field name with `strdup()` only when using the default table word.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfieldhdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfr.c

Main IPFilter rule pretty-printer.

Key behavior:
- Reconstructs readable rule text from `frentry`.
- Prints action, return behavior, direction, logging, quick flag, interfaces, `to`/`dup-to`/`reply-to`, fastroute, family, protocol, addresses, ports, ICMP type/code, TCP flags, BPF, callfunc, and expression filters.
- Prints `with` clauses for packet flags and IPv4/IPv6 options.
- Prints keep-state/keep-frag settings, scan/group/head, tags, pps, comments, state counts, TTL, and debug refcounts.

Research notes:
- Calls `kvatoname()` to resolve kernel function pointers for call rules.
- Output is tightly coupled to packed name offsets inside `frentry`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfraginfo.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfraginfo.c

Fragment-cache entry printer.

Key behavior:
- Prints family, source, destination, fragment ID, TTL, protocol, packet/byte counters, seen-first-fragment flag, and refcount.

Research notes:
- Uses `hostname()` for address rendering.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfraginfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash.c

Hash lookup-table printer for copied/kernel-readable tables.

Key behavior:
- Copies the table header with a supplied copy function.
- Filters by name when requested.
- Prints table metadata and each linked entry through `printhashnode()`.
- Emits an empty semicolon block for empty lists.

Research notes:
- Allocates and copies the bucket table but visible iteration uses `iph_list`; the copied table is not otherwise used.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash_live.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash_live.c

Live kernel hash lookup-table printer.

Key behavior:
- Prints hash metadata unless field output is requested.
- Iterates nodes with `SIOCLOOKUPITER` using `IPLT_HASH`.
- Prints each node with `printhashnode()`.
- Deletes iterator token with `SIOCIPFDELTOK`.

Research notes:
- Reports an iterator-walk error if it exits before the final node.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash_live.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashdata.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashdata.c

Hash lookup-table metadata formatter.

Key behavior:
- Prints save, normal, and debug variants.
- Distinguishes lookup hash tables from group maps.
- Shows role/unit, name/number, size, seed, references, maskset, anonymous/delete state, and debug masks.

Research notes:
- Debug mask output converts mask bit positions with `ntomask()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashnode.c

Hash lookup-table node formatter.

Key behavior:
- Copies one `iphtent_t` through the supplied copy function.
- Field mode prints selected pool/hash fields.
- Debug mode prints hash bucket, address/mask, refs, group, hits, and bytes.
- Normal mode prints address/mask and optional group-map override.

Research notes:
- Hash bucket calculation uses the IPv4 hash macro even before family-specific printing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhost.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhost.c

Host address printer.

Key behavior:
- Prints `any` for unknown family or zero address.
- Prints IPv4 with `inet_ntoa()` or IPv6 with `inet_ntop()` when enabled.

Research notes:
- IPv6 path passes the supplied address pointer directly to `inet_ntop()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmap.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmap.c

NAT hostmap entry printer.

Key behavior:
- Prints old source/destination mapping to new source/destination.
- Prints use/ref count and optional hash value in verbose mode.

Research notes:
- Uses `printactiveaddress()` for v4/v6 address handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmask.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmask.c

Host-plus-mask printer.

Key behavior:
- Prints `any` when family is unknown or both address and mask are zero.
- Prints address through IPv4/IPv6 formatting and appends mask with `printmask()`.

Research notes:
- IPv6 formatting depends on `USE_INET6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printifname.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printifname.c

Interface-name formatter.

Key behavior:
- Prints a prefix format string and interface name.
- Adds `(!)` when the interface pointer is NULL and name is neither `-` nor `*`.

Research notes:
- Used to indicate unresolved interfaces in rule output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printifname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printip.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printip.c

IP address printer for pool/hash output.

Key behavior:
- IPv4 values below 256 are printed as decimal numbers; other IPv4 values as dotted quads.
- IPv6 values are printed with `inet_ntop()` when enabled.
- Unknown families print `?(family)?`.

Research notes:
- The small-IPv4 decimal behavior supports numeric table identifiers or compact address syntax.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printipfexpr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printipfexpr.c

Pretty-printer for packed IPFilter expression arrays.

Key behavior:
- Walks the size-prefixed expression array until `IPF_EXP_END`.
- Prints IP/IPv6 address predicates, protocol, TCP/UDP ports, TCP flags/state, and idle time predicates.
- Delegates ports, scalar values, IPv4 host/mask pairs, and IPv6 host/mask pairs to helper functions.

Research notes:
- TCP flags loop compares `j < array[4]`, which appears inconsistent with `ipfe->ipfe_narg`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printipfexpr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printiphdr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printiphdr.c

Compact IPv4 header debug printer.

Key behavior:
- Prints version, header length, total length, TOS, fragment offset, checksum, source, and destination in one line prefix.

Research notes:
- Does not close the opening `ip(`; callers likely append more fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printiphdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlog.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlog.c

Rule logging clause printer.

Key behavior:
- Prints `log` plus `body`, `first`, and `or-block` flags.
- Prints syslog facility/priority names when `fr_loglevel` is set.

Research notes:
- Unknown facility/priority names print as `!!!`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlookup.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlookup.c

Lookup-reference printer for rule addresses.

Key behavior:
- Prints lookup type prefixes for pool, hash, and destination list.
- Prints numeric lookup IDs or name offsets into the rule name buffer.

Research notes:
- Unknown lookup types are printed as `lookup(hex)=`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printmask.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printmask.c

Network mask printer.

Key behavior:
- IPv6 masks print as prefix length from `count6bits()`.
- IPv4 contiguous masks print as prefix length from `count4bits()`.
- Non-contiguous IPv4 masks print as dotted mask.

Research notes:
- Does not special-case invalid IPv6 masks beyond whatever `count6bits()` returns.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnat.c

NAT rule pretty-printer.

Key behavior:
- Prints map, map-block, redirect, bimap, rewrite, encap, and divert rule forms.
- Handles interface lists, family, protocol, optional filter `from/to`, translated source/destination, port maps, proxy settings, round-robin, frag, age, sticky, MSS clamp, tags, purge, and debug internals.
- Uses `printnataddr()`, `printportcmp()`, `printproto()`, and `portname()`.

Research notes:
- In rewrite destination-list output, the numeric destination branch prints `in_nsrc.na_num` while handling `in_ndst`, which looks like a copy/paste mistake.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnataddr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnataddr.c

NAT address formatter.

Key behavior:
- Handles IPv4 zero-address normal form as `0/prefix`.
- Delegates other IPv4 and IPv6 NAT address forms to `printaddr()`.
- Prints unknown versions as `{v=n}`.

Research notes:
- Includes `kmem.h` but does not use kernel-memory helpers directly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnataddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatfield.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatfield.c

Tabular NAT-entry field definitions and printer.

Key behavior:
- Defines `natfields[]` with names for interfaces, MTUs, checksums, counters, protocols, hashes, refs, addresses, ports, age, and direction.
- `printnatfield()` prints one selected field or all positive fields for sentinel `-2`.

Research notes:
- Field `v1` prints `nat_v[0]`, likely intended to be `nat_v[1]`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatfield.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatside.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatside.c

NAT per-side statistics printer.

Key behavior:
- Prints counters for proxy failures, bad NAT cases, buckets, clone failures, decapsulation, divert, drops, exhaustion, ICMP handling, insert/lookup misses, memory failures, translations, wraps, and null/existing translations.
- Verbose mode prints the table pointer.

Research notes:
- `ns_memfail` is printed twice with different labels.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatside.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket.c

Packet summary/hex printer for test traffic.

Key behavior:
- Computes IPv4 or IPv6 packet length and asserts it matches `msgdsize()`.
- `OPT_HEX` dumps raw mbuf-chain bytes.
- IPv6 packets are delegated to `printpacket6()`.
- IPv4 summary prints direction, interface, ID, length/header length, protocol, fragment offset, endpoints, ports, and TCP flags.

Research notes:
- Assumes transport header is present for non-fragmented TCP/UDP summaries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket6.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket6.c

IPv6 packet summary printer.

Key behavior:
- Parses IPv6 header bytes manually.
- Prints direction, interface, version, payload length, flow label, next-header protocol, source/destination addresses, and TCP/UDP ports when payload length permits.

Research notes:
- Avoids reliance on IPv6 header library availability, but does not parse extension headers before TCP/UDP ports.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpacket6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool.c

Pool lookup-table printer for copied/kernel-readable pools.

Key behavior:
- Copies the pool header, filters by name, and prints metadata.
- Copies the node list into local allocated nodes before printing.
- Prints nodes with `printpoolnode()` and frees local copies.

Research notes:
- Does not check allocation/copy failures robustly inside the node-copy loop.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool_live.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool_live.c

Live kernel pool lookup-table printer.

Key behavior:
- Prints metadata unless field output is requested.
- Iterates pool nodes with `SIOCLOOKUPITER`.
- Prints save, normal, or debug block syntax.
- Deletes the iterator token with `SIOCIPFDELTOK`.

Research notes:
- Only iterates when `pool->ipo_list != NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool_live.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpooldata.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpooldata.c

Pool metadata formatter.

Key behavior:
- Prints save, normal, and debug representations of a pool table.
- Shows role/unit, name/number, anonymous/delete state, references, hits, and node-list pointer.

Research notes:
- Save output uses `pool .../tree` syntax.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpooldata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolfield.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolfield.c

Tabular field printer shared by pool, hash, and destination-list nodes.

Key behavior:
- Defines `poolfields[]`: address, mask, interface name, packets, bytes, and family.
- Prints selected fields according to object type `IPLT_POOL`, `IPLT_HASH`, or `IPLT_DSTLIST`.
- Handles `all` sentinel `-2`.

Research notes:
- Destination-list packet/byte fields are hardcoded as zero.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolfield.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolnode.c

Pool node formatter.

Key behavior:
- Field mode delegates to `printpoolfield()`.
- Normal mode prints optional negation, address, and mask.
- Debug mode prints address, mask, hits, bytes, name, and refcount.

Research notes:
- Returns the node’s `ipn_next` pointer to drive callers’ list traversal.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printportcmp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printportcmp.c

Port comparison clause printer.

Key behavior:
- Maps comparison enum values to text operators.
- Prints in/out range, inclusive range, and simple comparison forms.
- Resolves simple port names with `portname()`.

Research notes:
- Assumes `frp_cmp` indexes the local operator table safely.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printportcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printproto.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printproto.c

Protocol-name printer.

Key behavior:
- For NAT rules, honors aggregate flags such as `tcp/udp`, `tcp`, `udp`, and `icmp`.
- Prints `ip` for protocol zero in NAT context.
- Otherwise prints `protoent` name or numeric protocol.

Research notes:
- NAT context prefers rule flags over the supplied protocol number.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printproto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printsbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printsbuf.c

IPFilter scan-buffer printer.

Key behavior:
- When `IPFILTER_SCAN` is enabled, prints `ISC_TLEN` bytes with printable characters direct and others as octal escapes.
- Otherwise provides a no-op stub.

Research notes:
- Keeps builds working when scan support is disabled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printsbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstate.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstate.c

Live state-table entry pretty-printer.

Key behavior:
- Prints version/protocol, source/destination endpoints, TCP state, remaining lifetime, clone/orphan flags, and protocol-specific details.
- Prints packet/byte counters for forward/reverse and in/out directions.
- Reconstructs pass/block/log/count/auth action flags.
- Prints interface names/pointers, verbose packet-match metadata, and synchronization status read through `kmemcpy()`.

Research notes:
- Uses `hostname()` and optional protocol-name resolution.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstatefields.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstatefields.c

Tabular state-entry field definitions and printer.

Key behavior:
- Defines `statefields[]` for interfaces, counters, TCP states, ages, refs, sequence deltas, addresses, ports, ICMP type, pass flags, protocol, version, hash, tag, flags, rule number, group, flags/options/security/auth masks, and ICMP counters.
- `printstatefield()` prints one selected field or all positive fields.

Research notes:
- The `"-"` field has value 31 but no print case, acting as a blank/separator field.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstatefields.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtcpflags.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtcpflags.c

TCP flags/mask formatter.

Key behavior:
- Prints known TCP flags as letters using global `flagset`/`flags`.
- Prints hex for unknown flag bits.
- Appends `/mask` when a mask is supplied.

Research notes:
- Relies on global flag arrays defined elsewhere in libipf.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtcpflags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtqtable.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtqtable.c

TCP state timeout-queue count printer.

Key behavior:
- Prints state indexes from `0` to `IPF_TCP_NSTATES - 1`.
- Prints `ifq_ref - 1` for each queue.

Research notes:
- The subtraction implies one internal reference is not counted as an entry.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtqtable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtunable.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtunable.c

IPFilter tunable formatter.

Key behavior:
- Prints name, min, max, and current value.
- Chooses current-value member based on `ipft_sz`.

Research notes:
- Unknown sizes are printed as `sz = n`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtunable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printunit.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printunit.c

IPFilter unit/minor-name printer.

Key behavior:
- Maps log/unit constants for ipf, nat, state, auth, sync, scan, lookup, count, and all.
- Prints unknown numeric units as `unknown(n)`.

Research notes:
- Used across pool/hash/destination-list metadata output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hash.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hash.c

Hash lookup-table removal helper.

Key behavior:
- Builds `IPLT_HASH` lookup operation from an `iphtable_t`.
- Handles anonymous hash names.
- Calls `SIOCLOOKUPDELTABLE`.

Research notes:
- `op.iplo_arg` is only assigned in the anonymous case; otherwise it is left uninitialized.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hashnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hashnode.c

Hash lookup-table node removal helper.

Key behavior:
- Copies address and mask from the supplied node.
- Calls `SIOCLOOKUPDELNODE`.
- Debug mode prints the address and mask being removed.

Research notes:
- Removal key does not copy family/group fields, unlike `load_hashnode()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hashnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_pool.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_pool.c

Pool lookup-table removal helper.

Key behavior:
- Builds an `IPLT_POOL` lookup operation from an `ip_pool_t`.
- Calls `SIOCLOOKUPDELTABLE`.
- Reports failures through `ipf_perror_fd()` unless `OPT_DONOTHING`.

Research notes:
- Includes `ip_htable.h` even though it removes pools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_poolnode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_poolnode.c

Pool node removal helper.

Key behavior:
- Copies address, mask, info flag, and node name into a local `ip_pool_node_t`.
- Calls `SIOCLOOKUPDELNODE`.
- Reports failures through `ipf_perror_fd()` unless `OPT_DONOTHING`.

Research notes:
- Does not copy TTL/death time because it is irrelevant to deletion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_poolnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/resetlexer.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/resetlexer.c

Global lexer-state reset helper.

Key behavior:
- Defines global `string_start`, `string_end`, `string_val`, and `pos`.
- `resetlexer()` restores them to initial values.

Research notes:
- This is shared mutable parser state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/resetlexer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/rwlock_emul.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/rwlock_emul.c

Single-thread read/write lock emulation/debug checker.

Key behavior:
- Tracks magic value, owner, read/write hold counts, and source location.
- Read/write enter abort if already held.
- Downgrade converts one write hold to one read hold.
- Exit requires exactly one read or write hold.
- Init/destroy maintain a global `initcount`; `ipf_rwlock_clean()` aborts on leaks.

Research notes:
- `eMrwlock_try_upgrade()` currently aborts if a read lock is held, so it does not model a normal upgrade from read to write.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/rwlock_emul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_execute.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_execute.c

`ipmon` saver backend that pipes log messages to an external command.

Key behavior:
- Registers `executesaver`.
- Parses a command path/string.
- `execute_send()` opens the command with `popen(..., "w")`, writes the formatted message, and closes it.

Research notes:
- Executes a shell command for each message; command string trust is entirely caller/configuration dependent.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_execute.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_file.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_file.c

`ipmon` file saver backend.

Key behavior:
- Registers `filesaver`.
- Parses `raw://path` for binary append and `file://path` for text append.
- Supports matching and reference-counted duplication for shared file contexts.
- Writes raw data or formatted message text in `file_send()`.

Research notes:
- `file_destroy()` frees path/context but does not close `fp`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_nothing.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_nothing.c

`ipmon` discard saver backend.

Key behavior:
- Registers `nothingsaver`.
- Parses by allocating a tiny dummy context.
- `nothing_send()` deliberately ignores messages.

Research notes:
- `nothing_opts_t` is defined but unused.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_nothing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_syslog.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_syslog.c

`ipmon` syslog saver backend.

Key behavior:
- Registers `syslogsaver`.
- Parses optional `facility.priority`, `.priority`, or `facility.` override.
- Sends messages to `syslog()` using either configured facility/priority or the message log level.

Research notes:
- Invalid facility or priority names reject parser setup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_syslog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v1trap.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v1trap.c

`ipmon` SNMPv1 trap saver backend.

Key behavior:
- Registers `snmpv1saver`.
- Parses `community address`, opens a connected UDP socket to port 162, and supports IPv4 plus optional IPv6 destination parsing.
- Manually BER-encodes an SNMPv1 enterprise trap for IPFilter enterprise OID `1.3.6.1.4.1.9932`.
- Includes IPFilter version and message text variable bindings.

Research notes:
- Reference-counted contexts share sockets/community strings.
- `writeint()` contains a typo in the 32768 branch divisor (`327678`), also present in v2.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v1trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v2trap.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v2trap.c

`ipmon` SNMPv2 trap saver backend.

Key behavior:
- Registers `snmpv2saver`.
- Parses `community address`, opens a connected UDP socket to port 162, and supports IPv4 plus optional IPv6 destination parsing.
- Manually BER-encodes an SNMPv2 trap PDU.
- Emits sysUpTime, IPFilter version, and message text variable bindings.

Research notes:
- Structure closely mirrors `save_v1trap.c`.
- Contains unused `server` field in the context struct.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_v2trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcp_flags.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcp_flags.c

TCP flags plus mask parser.

Key behavior:
- Parses `flags` or `flags/mask`, accepting symbolic letters or numeric values starting with `0`.
- Defaults mask to all TCP flags except ECN, and also except CWR for bare SYN.
- Returns parsed flags and writes parsed/default mask.

Research notes:
- `linenum` parameter is unused.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcp_flags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpflags.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpflags.c

Symbolic TCP flag-string converter.

Key behavior:
- Converts characters from global `flagset` into TCP flag bits from global `flags`.
- Handles `W` explicitly as `TH_CWR`.
- Provides fallback definitions for ECN, CWR, and AE flag constants.

Research notes:
- Unknown flag characters make the whole conversion return zero.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpflags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpoptnames.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpoptnames.c

TCP option-name table.

Key behavior:
- Defines `tcpoptnames[]` for NOP, MSS, window scale, SACK permitted, SACK, and timestamp.
- Each entry maps TCP option value to bit, expected length, and text name.

Research notes:
- Sentinel row terminates the table.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpoptnames.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6ionames.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6ionames.c

IPv6 extension-header name table.

Key behavior:
- Compiled under `USE_INET6`.
- Defines `v6ionames[]` mapping protocol numbers to match bits and text names for hopopts, ipv6, routing, frag, ESP, AH, none, dstopts, and mobility.

Research notes:
- All lengths are zero because these are extension-header identifiers, not fixed option lengths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6ionames.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6optvalue.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6optvalue.c

IPv6 extension-header lookup helpers.

Key behavior:
- `getv6optbyname()` maps extension-header text to bit.
- `getv6optbyvalue()` maps protocol value to bit.
- Both return `(u_32_t)-1` when not found or IPv6 support is not compiled.

Research notes:
- Entire lookup body is conditional on `USE_INET6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6optvalue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/var.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/var.c

Simple variable store and `$variable` expansion engine for IPFilter config parsing.

Key behavior:
- Maintains a linked list of name/value variables.
- `set_variable()` creates or replaces variables and strips matching single/double quotes around values.
- `get_variable()` parses `$name` or `${name}` references and recursively expands the stored value.
- `expand_string()` replaces embedded variables, supports `$$` escaping, and allocates expanded strings when needed.

Research notes:
- No cycle detection for recursive variables.
- `set_variable()` mutates quoted input values by writing a NUL before the closing quote.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/var.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/verbose.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/verbose.c

Verbose-output helpers.

Key behavior:
- `verbose()` prints through `vprintf()` when global `opts` includes `OPT_VERBOSE`.
- `ipfkverbose()` attempts to route verbose kernel-style messages through `verbose()`.

Research notes:
- `ipfkverbose()` passes a `va_list` as a normal variadic argument to `verbose()`, so it does not actually forward formatting arguments correctly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/verbose.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/vtof.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/vtof.c

IP version to address-family converter.

Key behavior:
- Maps version 4 to `AF_INET`.
- Maps version 6 to `AF_INET6` when IPv6 support is compiled.
- Maps version 0 to `AF_UNSPEC`.
- Returns `-1` for unknown versions.

Research notes:
- Small utility used where structures store IP version instead of socket family.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/vtof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/Makefile

FreeBSD build file for the `ipfw` command.

Key behavior:
- Builds `ipfw` and links `dnctl` to the same binary.
- Includes core source files for ipfw, dummynet, IPv6, NAT, tables, NAT64 variants, and NPTv6.
- Adds `altq.c` and `-DPF` when `MK_PF` is enabled.
- Links against `jail` and `util`; enables tests subdir when `MK_TESTS` is set.

Research notes:
- Suppresses `-Wcast-align` warnings after including `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/altq.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/altq.c

ALTQ integration support for the FreeBSD `ipfw` command through PF control ioctls.

Key behavior:
- `altq_set_enabled()` opens `/dev/pf` and starts/stops ALTQ with `DIOCSTARTALTQ` or `DIOCSTOPALTQ`.
- `altq_fetch()` lazily reads the PF ALTQ queue list with `DIOCGETALTQS`/`DIOCGETALTQ` and caches queue entries in a TAILQ.
- `altq_name_to_qid()` maps a queue name to PF ALTQ qid for rule parsing.
- `print_altq_cmd()` maps a qid back to a queue name when printing ipfw rules.

Research notes:
- Requires PF support and `PFIOC_USE_LATEST`.
- Missing queue names are fatal during name-to-qid parsing but print as `?<qid>` during reverse lookup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/altq.c -->