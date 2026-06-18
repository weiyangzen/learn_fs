<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink.c -->
# sources/test-tools/strace/src/netlink.c

Purpose: central netlink message decoder for socket payloads, including `nlmsghdr` arrays, type/flag rendering, control messages, and dispatch into family-specific payload decoders.

Important APIs/types/functions: `decode_netlink`, `fetch_nlmsghdr`, `get_fd_nl_family`, `decode_nlmsg_type`, `decode_nlmsg_flags`, `decode_nlmsgerr`, `decode_payload`, `print_nlmsghdr`, `netlink_decoders`, and xlat tables for audit, crypto, generic, netfilter, route, SELinux, sock_diag, and xfrm families.

Control flow: `decode_netlink` infers the netlink family from fd inode/socket details, special-cases `NETLINK_KOBJECT_UEVENT`, iterates aligned `nlmsghdr` records with sequence truncation checks, prints each header, and passes payloads to reserved-control handling or family decoders. `NLMSG_ERROR` payloads are decoded as `struct nlmsgerr`, optionally followed by extended ack attributes.

State and persistence behavior: no durable state; it reads tracee memory and fd metadata. The only persisted information is external to this file, such as generic family mappings and tcb output/aux state.

Dependencies and integration points: integrates with `netlink.h`, `nlattr.h`, family decoders (`decode_netlink_crypto`, `decode_netlink_route`, etc.), fd inode/socket lookup helpers, `genl_families_xlat`, and many generated xlat tables.

Risks: fd-family inference depends on `/proc` socket detail strings and can fall back to generic decoding. Alignment, malformed `nlmsg_len`, capped errors, and family-specific flag tables are sensitive to kernel ABI changes.

Test signals: cover single and multi-message buffers, short headers, unknown families, `NLMSG_DONE`, `NLMSG_ERROR` with and without `NLM_F_CAPPED`, extended ack attributes, netfilter split types, and route/generic/sock_diag dispatch.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink.h -->
# sources/test-tools/strace/src/netlink.h

Purpose: shared netlink header helpers and normalized header-length macros for netlink decoders.

Important APIs/types/functions: redefines `NLMSG_HDRLEN` and `NLA_HDRLEN` as unsigned aligned lengths and provides inline `is_nlmsg_ok`.

Control flow: `is_nlmsg_ok` validates that a buffer contains a full `struct nlmsghdr`, that `nlmsg_len` is at least the header size, and that the caller-provided length covers the message.

State and persistence behavior: no runtime state; it contributes constants and inline validation.

Dependencies and integration points: includes `<stdbool.h>`, `<sys/socket.h>`, and `<linux/netlink.h>`; used by netlink and nlattr decoders that need consistent alignment semantics.

Risks: changes to alignment macros or validation rules affect all netlink family decoders. The helper validates one message only and does not check multi-message overflow.

Test signals: malformed netlink header unit cases should exercise short buffers, too-small `nlmsg_len`, exact-length messages, and oversized messages.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_crypto.c -->
# sources/test-tools/strace/src/netlink_crypto.c

Purpose: decodes `NETLINK_CRYPTO` algorithm messages and their crypto report attributes.

Important APIs/types/functions: `decode_netlink_crypto`, `decode_crypto_user_alg`, report decoders for generic/hash/blkcipher/aead/rng/cipher payloads, and `crypto_user_alg_nla_decoders`.

Control flow: supported crypto message types (`NEWALG`, `DELALG`, `UPDATEALG`, `GETALG`) decode a leading `struct crypto_user_alg`; if aligned trailing data exists, `decode_nlattr` decodes `CRYPTOCFGA_*` attributes using report-specific structure printers.

State and persistence behavior: no persistent state. It copies tracee netlink payload structures and prints fields or raw short strings for undersized reports.

Dependencies and integration points: depends on `netlink.h`, `nlattr.h`, `<linux/cryptouser.h>`, `xlat/crypto_nl_attrs.h`, and the main `netlink.c` family dispatch.

Risks: crypto report structures evolve with kernel headers; short payloads intentionally fall back to string/hex output. C string fields rely on kernel-provided fixed buffers being printable.

Test signals: trace crypto algorithm dumps containing priority, hash, cipher, AEAD, RNG, generic report attributes, short attributes, unknown attributes, and all four supported crypto message types.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.c -->
# sources/test-tools/strace/src/netlink_generic.c

Purpose: generic netlink payload dispatcher that prints `genlmsghdr` and routes known generic families to specialized decoders.

Important APIs/types/functions: `decode_netlink_generic`, default `decode_genl_msg`, `genl_decoders`, `initialize_genl_decoders`, and `lookup_genl_decoder`.

Control flow: after rejecting too-short or `NLMSG_DONE` payloads, it fetches `struct genlmsghdr`, lazily resolves configured family names to dynamic ids via `genl_families_xlat`, selects a decoder by `nlmsg_type`, and falls back to printing generic attributes.

State and persistence behavior: process-local static initialization caches dynamic generic family ids, currently for `nlctrl`.

Dependencies and integration points: integrates with `netlink_generic.h`, `nlattr.h`, `genl_families_xlat`, and the main netlink dispatcher for `NETLINK_GENERIC`.

Risks: generic family ids are dynamic; stale or unavailable family xlat data causes fallback decoding. Only families listed in `genl_decoders` receive semantic attribute decoding.

Test signals: generic netlink tests should include known `nlctrl`, unknown family ids, short headers, reserved fields, attributes after `genlmsghdr`, and id initialization under multiple tracees.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.h -->
# sources/test-tools/strace/src/netlink_generic.h

Purpose: declares the generic netlink decoder signature and exported `nlctrl` decoder.

Important APIs/types/functions: `DECL_NETLINK_GENERIC_DECODER` macro and `decode_nlctrl` declaration.

Control flow: no runtime flow; the macro standardizes generic decoder prototypes that accept `struct genlmsghdr`, payload address, and payload length.

State and persistence behavior: no state.

Dependencies and integration points: includes `netlink.h` and `<linux/genetlink.h>`; consumed by `netlink_generic.c` and `netlink_nlctrl.c`.

Risks: signature drift would break generic family decoder registration. The macro hides the exact prototype, so compiler errors are the main guard.

Test signals: build coverage for every `DECL_NETLINK_GENERIC_DECODER` implementation and generic netlink dispatch tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_inet_diag.c -->
# sources/test-tools/strace/src/netlink_inet_diag.c

Purpose: decodes AF_INET/AF_INET6 sock_diag requests and responses, including legacy inet_diag requests, v2 requests, TCP metrics, ULP info, and nested diagnostic attributes.

Important APIs/types/functions: `print_inet_diag_sockid`, `decode_inet_diag_req`, `decode_inet_diag_msg`, bytecode decoders, `decode_tcpvegas_info`, `decode_tcp_dctcp_info`, `decode_tcp_bbr_info`, `decode_tcp_md5sig`, TLS/MPTCP ULP decoders, BPF storage decoders, and `decode_diag_sockopt`.

Control flow: request decoding chooses legacy `inet_diag_req` for `TCPDIAG_GETSOCK`/`DCCPDIAG_GETSOCK` and `inet_diag_req_v2` otherwise, then decodes request attributes. Response decoding prints `inet_diag_msg` fields and then aligned `INET_DIAG_*` attributes with nested dispatch for ULP, BPF storage, socket arrays, congestion info, and sockopt bitfields.

State and persistence behavior: no durable state; all work is tracee-memory fetch plus output formatting. Sparse bitfields are omitted in abbrev mode unless nonzero.

Dependencies and integration points: used by `netlink_sock_diag.c`; depends on Linux `inet_diag`, `tcp`, `tls`, `mptcp`, shared `nlattr` helpers, socket address printers, xlat tables, and `print_inet_diag_sockid` exported through `netlink_sock_diag.h`.

Risks: many structures are kernel-version dependent. Optional field printing via payload length must track ABI additions; unsupported `INET_DIAG_INFO` remains raw. Bytecode and nested attributes need correct length alignment to avoid misleading output.

Test signals: cover legacy/v2 requests, IPv4 and IPv6 sockids, bytecode host/mark/dev conditions, all implemented response attributes, TLS and MPTCP ULP nests, BPF storage, sockopt nonzero/abbrev behavior, short payloads, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_inet_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.c -->
# sources/test-tools/strace/src/netlink_kobject_uevent.c

Purpose: decodes `NETLINK_KOBJECT_UEVENT` payloads, especially libudev monitor headers followed by property strings.

Important APIs/types/functions: `decode_netlink_kobject_uevent`, `PRINT_FIELD_HTONL_X`, and `struct udev_monitor_netlink_header`.

Control flow: if verbose mode, successful syscall state, valid address/length, and `"libudev"` prefix all match, it prints the libudev header fields and trailing property string data. Otherwise it prints the payload as a string buffer.

State and persistence behavior: no persistent state; it decodes one payload buffer.

Dependencies and integration points: called directly from `decode_netlink` when the fd family is `NETLINK_KOBJECT_UEVENT`; depends on `netlink_kobject_uevent.h`, tracee memory fetch, and network byte-order formatting.

Risks: non-libudev kernel uevents are intentionally string-only. Header validation is prefix based; malformed or short libudev-like payloads fall back rather than partially decoding.

Test signals: cover raw kernel uevent strings, valid libudev headers with properties, short buffers, failed syscalls, nonverbose mode, and big-endian formatted filter hashes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.h -->
# sources/test-tools/strace/src/netlink_kobject_uevent.h

Purpose: defines the libudev monitor header layout used by the kobject uevent decoder.

Important APIs/types/functions: `struct udev_monitor_netlink_header` with `prefix`, `magic`, `header_size`, property offsets/lengths, and filter hash/bloom fields.

Control flow: no runtime control flow.

State and persistence behavior: no state; structure definition only.

Dependencies and integration points: consumed by `netlink_kobject_uevent.c` and aligned with libudev netlink monitor payload format.

Risks: the layout is not a generic kernel `nlmsghdr`; changing it would break libudev payload rendering. Field endian expectations live in the decoder.

Test signals: compile-time structure use plus runtime uevent tests for `libudev` prefix and property payload offsets.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netfilter.c -->
# sources/test-tools/strace/src/netlink_netfilter.c

Purpose: decodes `NETLINK_NETFILTER` payload headers and generic netfilter attributes.

Important APIs/types/functions: `decode_netlink_netfilter`, `struct nfgenmsg`, `netfilter_versions`, and netfilter subsystem/type xlats.

Control flow: skips `NLMSG_DONE`, prints `nfgen_family`, `version`, and `res_id` from `nfgenmsg`; then decodes trailing attributes unless the message is a batch control or reserved type, in which case it prints raw hex. It includes workarounds for historical nftables `res_id` endianness.

State and persistence behavior: no durable state; per-payload only.

Dependencies and integration points: invoked by main netlink dispatcher for `NETLINK_NETFILTER`; uses `nlattr`, `<linux/netfilter/nfnetlink.h>`, and network byte-order helpers.

Risks: netfilter subsystems have many nested formats that are not decoded here beyond generic attributes. The `res_id` workaround is protocol-specific and must remain accurate for nftables.

Test signals: cover nfgenmsg printing, batch begin/end, nftables res_id endian variants, short payloads, raw reserved payloads, and generic trailing attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netlink_diag.c -->
# sources/test-tools/strace/src/netlink_netlink_diag.c

Purpose: decodes AF_NETLINK sock_diag request and response payloads.

Important APIs/types/functions: `decode_netlink_diag_req`, `decode_netlink_diag_msg`, `decode_netlink_diag_groups`, `decode_netlink_diag_ring`, `decode_netlink_diag_flags`, and `netlink_diag_msg_nla_decoders`.

Control flow: request decoding prints `netlink_diag_req` including protocol, inode, show flags, and cookie. Response decoding prints `netlink_diag_msg` fields, then aligned `NETLINK_DIAG_*` attributes for meminfo, group masks, RX/TX rings, and socket flags.

State and persistence behavior: no durable state. Group attributes are interpreted in current tracee word size.

Dependencies and integration points: registered through `netlink_sock_diag.c`; depends on `<linux/netlink_diag.h>`, shared `nlattr` decoders, `netlink_protocols`, `socktypes`, and generated diag xlat tables.

Risks: group mask element width varies with personality word size. Unknown protocols and newly added attributes fall back to generic hex if xlat/decoder tables lag.

Test signals: cover `NDIAG_PROTO_ALL`, protocol-specific requests, group arrays for 32/64-bit personalities, ring attributes, flags attributes, and short messages.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netlink_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_nlctrl.c -->
# sources/test-tools/strace/src/netlink_nlctrl.c

Purpose: specialized decoder for the generic netlink controller (`nlctrl`) family, including family metadata, operations, multicast groups, and policy descriptions.

Important APIs/types/functions: `decode_nlctrl`, `family_names`, `decode_nla_ctrl_attr_family_name`, operation and policy nested decoders, and xlat mappings for known generic families such as devlink, ethtool, ioam6, mptcp_pm, netdev, nl80211, taskstats, tcp_metrics, and thermal.

Control flow: prints `genlmsghdr` command/version/reserved, then decodes `CTRL_ATTR_*` attributes. The family-name attribute updates an opaque index so operation ids can be rendered with the family-specific command table, including send/receive tables for ethtool.

State and persistence behavior: no global state; a per-message `family_names_idx` is passed through nested attribute decoding.

Dependencies and integration points: called from `netlink_generic.c`; uses `nlattr` nested decoding and many generated generic-family xlat tables.

Risks: semantic command rendering depends on seeing `CTRL_ATTR_FAMILY_NAME` before nested operation attributes and on the hardcoded family-name table staying current. Unknown policy attributes fall back to raw output.

Test signals: cover `CTRL_CMD_*` messages with family names, ops, mcast groups, policy and op-policy nests, ethtool receive/send command rendering, unknown families, and missing family-name ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_nlctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_packet_diag.c -->
# sources/test-tools/strace/src/netlink_packet_diag.c

Purpose: decodes AF_PACKET sock_diag requests and response attributes.

Important APIs/types/functions: `decode_packet_diag_req`, `decode_packet_diag_msg`, `decode_packet_diag_info`, multicast list/ring/filter decoders, and `packet_diag_msg_nla_decoders`.

Control flow: request decoding prints family, protocol, inode, show flags, and cookie. Response decoding prints `packet_diag_msg`, then decodes `PACKET_DIAG_*` attributes for socket info, multicast list arrays, RX/TX rings, fanout, uid, meminfo, and classic BPF filters.

State and persistence behavior: no persistent state; filter attributes are printed as socket filter programs with an unsigned-short instruction-count guard.

Dependencies and integration points: registered in `netlink_sock_diag.c`; uses `nlattr`, `print_sock_fprog`, `print_ifindex`, ethernet protocol and packet xlat tables.

Risks: AF_PACKET protocol support is documented as currently zero-only in the request path. Multicast address length is capped to the embedded address array; longer kernel formats would need updates.

Test signals: AF_PACKET request/response dumps with info, mclist, rings, fanout, meminfo, uid, valid/invalid filter lengths, short messages, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_packet_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.c -->
# sources/test-tools/strace/src/netlink_route.c

Purpose: dispatches `NETLINK_ROUTE` payloads to RTM message-specific route decoders.

Important APIs/types/functions: `decode_netlink_route`, local `decode_family`, `route_decoders`, and `DECL_NETLINK_ROUTE_DECODER` function pointers.

Control flow: skips `NLMSG_DONE`, fetches the first family byte, computes `nlmsg_type - RTM_BASE`, and calls a registered decoder for link, address, route, neighbor, rule, qdisc/class/filter/action, netconf, mdb, nsid, stats, nexthop, and related RTM messages. Unknown types fall back to printing family plus raw data.

State and persistence behavior: no persistent state.

Dependencies and integration points: invoked by `netlink.c`; depends on `netlink_route.h`, `<linux/rtnetlink.h>`, `addrfams`, and route decoder implementations in other strace source files.

Risks: dispatcher coverage must track new RTM message numbers. Incorrect index arithmetic or missing entries lead to generic output for otherwise decodable route messages.

Test signals: route netlink tests for representative RTM families, unknown RTM types, short payloads, `NLMSG_DONE`, and correct fallback family rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.h -->
# sources/test-tools/strace/src/netlink_route.h

Purpose: declares the route-netlink decoder signature and all route message decoder entry points used by the route dispatcher.

Important APIs/types/functions: `DECL_NETLINK_ROUTE_DECODER` and extern declarations for link, address, route, neighbor, rule, tc, action, dcb, netconf, bridge mdb, nsid, stats, cache report, and nexthop decoders.

Control flow: no runtime flow; macro-generated prototypes enforce a consistent `(tcp, nlmsghdr, family, addr, len)` contract.

State and persistence behavior: no state.

Dependencies and integration points: consumed by `netlink_route.c` and implemented across route-related decoder files.

Risks: adding a route decoder requires both this declaration and `route_decoders` registration. Signature mismatch is compile-time visible.

Test signals: full strace build plus route-netlink dispatch tests that reference each declared decoder family.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_route.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_selinux.c -->
# sources/test-tools/strace/src/netlink_selinux.c

Purpose: decodes SELinux netlink notification payloads.

Important APIs/types/functions: `decode_netlink_selinux`, `struct selnl_msg_setenforce`, and `struct selnl_msg_policyload`.

Control flow: switches on `SELNL_MSG_SETENFORCE` and `SELNL_MSG_POLICYLOAD`, printing `val` or `seqno` respectively; unknown message types return false so the main netlink layer prints raw payload.

State and persistence behavior: no persistent state.

Dependencies and integration points: called by `netlink.c` for `NETLINK_SELINUX`; depends on `<linux/selinux_netlink.h>`.

Risks: only two SELinux message payload shapes are decoded. Future SELinux netlink messages require new cases.

Test signals: setenforce and policyload netlink messages, short payloads, unknown SELinux message types, and fetch failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_selinux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_smc_diag.c -->
# sources/test-tools/strace/src/netlink_smc_diag.c

Purpose: decodes AF_SMC sock_diag request and response payloads, including SMC connection, link group, DMB, fallback, and shutdown attributes.

Important APIs/types/functions: `decode_smc_diag_req`, `decode_smc_diag_msg`, `decode_smc_diag_conninfo`, `decode_smc_diag_lgrinfo`, `decode_smc_diag_dmbinfo`, `decode_smc_diag_fallback`, and `smc_diag_msg_nla_decoders`.

Control flow: request decoding prints `smc_diag_req` with extended flags and an AF_INET sockid. Response decoding prints `smc_diag_msg` state, mode, shutdown, sockid, uid, and inode, then aligned `SMC_DIAG_*` attributes. Optional newer DMB extended gid fields are printed only when present.

State and persistence behavior: no durable state.

Dependencies and integration points: registered in `netlink_sock_diag.c`; uses `<linux/smc_diag.h>`, shared inet sockid printing, `nlattr`, and SMC generated xlats.

Risks: SMC headers have evolved and some fallback reasons are from non-UAPI kernel headers, so xlat staleness is likely. AF_SMC uses AF_INET sock address fields, which is easy to mis-handle.

Test signals: AF_SMC request/response traces with conninfo, lgrinfo, shutdown, DMB old/new lengths, fallback reasons, short payloads, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_smc_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.c -->
# sources/test-tools/strace/src/netlink_sock_diag.c

Purpose: top-level `NETLINK_SOCK_DIAG` payload dispatcher across socket address families.

Important APIs/types/functions: `decode_netlink_sock_diag`, local `decode_family`, `diag_decoders`, and decoder pairs for AF_UNIX, AF_INET/AF_INET6, AF_NETLINK, AF_PACKET, and AF_SMC.

Control flow: skips `NLMSG_DONE`, reads the first family byte, selects request or response decoder based on `NLM_F_REQUEST`, and falls back to printing family plus raw data when no decoder exists.

State and persistence behavior: no persistent state.

Dependencies and integration points: invoked from `netlink.c`; depends on `netlink_sock_diag.h`, addrfams xlats, and family-specific diag files.

Risks: family dispatch assumes the first byte is the family and that `NLM_F_REQUEST` accurately distinguishes request from response. New sock_diag families need table entries.

Test signals: request and response messages for each registered family, unknown families, short buffers, `NLMSG_DONE`, and missing decoder fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.h -->
# sources/test-tools/strace/src/netlink_sock_diag.h

Purpose: declares sock_diag decoder signatures and shared inet sockid printing support.

Important APIs/types/functions: `DECL_NETLINK_DIAG_DECODER`, extern declarations for inet/netlink/packet/smc/unix request and message decoders, `print_inet_diag_sockid`, and `PRINT_FIELD_INET_DIAG_SOCKID`.

Control flow: no runtime flow; macro standardizes decoder prototypes.

State and persistence behavior: no state.

Dependencies and integration points: consumed by `netlink_sock_diag.c` and each family diag implementation.

Risks: all sock_diag family decoders depend on this prototype. The shared inet sockid printer assumes `struct inet_diag_sockid` layout from kernel headers.

Test signals: build coverage for each declared decoder plus inet sockid output in inet and SMC diag tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_unix_diag.c -->
# sources/test-tools/strace/src/netlink_unix_diag.c

Purpose: decodes AF_UNIX sock_diag requests and response attributes.

Important APIs/types/functions: `decode_unix_diag_req`, `decode_unix_diag_msg`, `decode_unix_diag_vfs`, `decode_unix_diag_inode`, `decode_unix_diag_rqlen`, and `unix_diag_msg_nla_decoders`.

Control flow: request decoding prints family, protocol, state mask, inode, show flags, and cookie. Response decoding prints `unix_diag_msg`, then aligned attributes for name, VFS dev/inode, peer, peer inode array, queue lengths, meminfo, shutdown, and uid.

State and persistence behavior: no persistent state.

Dependencies and integration points: registered in `netlink_sock_diag.c`; depends on `<linux/unix_diag.h>`, `nlattr`, TCP state xlats, unix diag show/attr xlats, and device-number printers.

Risks: `UNIX_DIAG_ICONS` is decoded as an array of 32-bit inodes; kernel layout changes would require adjustment. Names rely on string attribute semantics.

Test signals: AF_UNIX request/response traces with all implemented attributes, state/show flags, multiple peer inodes, short payloads, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_unix_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nice.c -->
# sources/test-tools/strace/src/nice.c

Purpose: syscall decoder for `nice`.

Important APIs/types/functions: `SYS_FUNC(nice)`.

Control flow: prints the single signed `increment` argument and marks the syscall decoded.

State and persistence behavior: no state.

Dependencies and integration points: integrated through strace syscall table and generic argument printing helpers from `defs.h`.

Risks: low; only sign formatting matters.

Test signals: trace positive, zero, and negative nice increments.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.c -->
# sources/test-tools/strace/src/nlattr.c

Purpose: generic netlink attribute iterator and library of reusable typed nla payload decoders.

Important APIs/types/functions: `decode_nlattr`, `decode_nlattr_with_data`, `fetch_nlattr`, `print_nlattr`, scalar `DECL_NLA` decoders, `decode_nla_xval`, `decode_nla_flags`, `decode_nla_af_spec`, and typed helpers for strings, fd, uid/gid, ifindex, hwaddr, inet addresses, byte-order integers, meminfo, protocols, and variable-sized integers.

Control flow: iterates aligned `struct nlattr` records with truncation checks, prints header length/type including `NLA_F_NESTED` and `NLA_F_NET_BYTEORDER`, dispatches payload by type index or no-type decoder mode, and falls back to hex when no decoder succeeds.

State and persistence behavior: no persistent state. It only reads tracee memory and uses caller-provided opaque context for xlat options or nested decoder state.

Dependencies and integration points: used by nearly every netlink family decoder; depends on `netlink.h`, `nlattr.h`, network byte-order helpers, socket diag meminfo xlats, address printers, and `print_ifindex`/`print_hwaddr`.

Risks: invalid `nla_len`, address overflow, zero-size decoder semantics, and opaque-data misuse can produce wrong output. New kernel attribute scalar sizes may need new decoders.

Test signals: nested attributes, short headers, malformed lengths, unknown types, flags, xval with endian conversion, meminfo arrays, hardware addresses, AF_SPEC dispatch, and no-type nested arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.h -->
# sources/test-tools/strace/src/nlattr.h

Purpose: public interface for netlink attribute decoding and typed nla decoder declarations.

Important APIs/types/functions: `struct decode_nla_xlat_opts`, `struct ifla_linkinfo_ctx`, `nla_decoder_t`, `decode_nlattr`, `decode_nlattr_notype`, `DECL_NLA`, typed decoder declarations, `decode_nla_hwaddr_family`, `decode_nla_hwaddr_nofamily`, `struct af_spec_decoder_desc`, and `decode_nla_af_spec`.

Control flow: inline wrappers adapt `decode_nlattr` for special no-type and hardware-address cases; most behavior is implemented in `nlattr.c`.

State and persistence behavior: declares context structures but owns no state. `ifla_linkinfo_ctx` is caller-managed state for linkinfo decoding.

Dependencies and integration points: includes `xlat.h` and is consumed by route, sock_diag, generic, crypto, netfilter, and other netlink decoders.

Risks: the zero-size decoder convention passes `nla_type` through `opaque_data`, so callers must not also expect opaque context in that mode. Hardware family encoding uses `NLA_HWADDR_FAMILY_OFFSET` sentinel bits.

Test signals: compile all declared decoders, no-type nested decoding, AF_SPEC selection, hardware address family wrappers, and xlat option scalar/flags decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nsfs.c -->
# sources/test-tools/strace/src/nsfs.c

Purpose: decodes namespace filesystem ioctl commands.

Important APIs/types/functions: `nsfs_ioctl`, `print_mnt_ns_info`, `struct mnt_ns_info`, and `NS_*` ioctl constants.

Control flow: returns fd-formatted results for namespace fd getters, decodes `NS_GET_NSTYPE` return aux strings, prints owner uid, namespace ids, PID/TGID translations, and mount namespace info for variable-sized `NS_MNT_GET_*` ioctls.

State and persistence behavior: no persistent state in this file; it reads ioctl output buffers on exit and sets `tcp->auxstr` for namespace type names.

Dependencies and integration points: used by the generic ioctl dispatcher; depends on `<linux/nsfs.h>`, pid printers, uid printers, `setns_types`, and ioctl size macros.

Risks: many commands are exit-only because output buffers are valid after syscall completion. Size-gated mount namespace ioctls must track kernel structure versions.

Test signals: `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, owner uid, mount namespace info/prev/next, PID namespace id translations, short ioctl sizes, and syscall failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nsfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nsig.h -->
# sources/test-tools/strace/src/nsig.h

Purpose: normalizes `NSIG` availability and defines signal-set byte size.

Important APIs/types/functions: `NSIG` fallback/error checks and `NSIG_BYTES`.

Control flow: preprocessor-only logic warns and uses 32 if `NSIG` is missing, errors if it is less than 32, then defines `NSIG_BYTES`.

State and persistence behavior: no state.

Dependencies and integration points: includes `<signal.h>`; used by signal mask decoders and syscall wrappers that need kernel sigset sizing.

Risks: assumes `NSIG / 8` is an adequate byte count for kernel sigset operations in callers.

Test signals: build on platforms with and without `NSIG`, and ppoll/pselect sigset-size decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nsig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/numa.c -->
# sources/test-tools/strace/src/numa.c

Purpose: decodes NUMA policy and page migration syscalls.

Important APIs/types/functions: `print_nodemask`, `print_mode`, `SYS_FUNC(migrate_pages)`, `mbind`, `set_mempolicy`, `get_mempolicy`, `set_mempolicy_home_node`, and `move_pages`.

Control flow: nodemasks are printed as word arrays sized from `maxnode` and current word size. Policy modes are split into base `MPOL_*` and `MPOL_F_*` flags. Enter/exit phases differ for `get_mempolicy` and `move_pages` because output buffers and status arrays are only meaningful on exit.

State and persistence behavior: no persistent state.

Dependencies and integration points: depends on xlat tables for NUMA policy modes/flags and move flags, pid translation, array printers, and tracee memory fetch.

Risks: nodemask size arithmetic guards overflow but large user values can still be abbreviated by generic array truncation. Mode/flag split must track kernel additions.

Test signals: migration nodemask arrays, mbind flag combinations, get_mempolicy output mode/nodemask, move_pages page and status arrays, invalid pointers, and large `maxnode` edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/number_set.c -->
# sources/test-tools/strace/src/number_set.c

Purpose: implements dynamic bitset arrays used for syscall, signal, status, fd, pid, quiet, and injection qualifiers.

Important APIs/types/functions: opaque `struct number_set`, `is_number_in_set`, `is_number_in_set_array`, `add_number_to_set`, `clear_number_set_array`, `invert_number_set_array`, `is_complete_set`, `alloc_number_set_array`, and `free_number_set_array`.

Control flow: bit operations map numbers to 32-bit slots; insertion grows the slot vector; membership XORs the stored bit with the set-level inversion flag; completeness counts set bits or recognizes an inverted empty set as universal.

State and persistence behavior: number sets are heap-allocated mutable process state owned by qualifier parsing and global decoder configuration.

Dependencies and integration points: used by filtering, path tracing, fd decoding, PID decoding, injection, and quiet-option logic; depends on `xmalloc`, `static_assert`, and `popcount32`.

Risks: inverted semantics are easy to misuse. Completeness depends on caller-provided max counts. The implementation assumes `number_slot_t` is 32-bit.

Test signals: empty sets, add and membership, array index behavior, inversion, clear, complete sets, high-number growth, and allocation/free under sanitizer builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/number_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/number_set.h -->
# sources/test-tools/strace/src/number_set.h

Purpose: public declarations for qualifier number sets and related option enums.

Important APIs/types/functions: opaque `struct number_set`, membership/allocation functions, `enum status_t`, `enum quiet_bits`, `enum decode_fd_bits`, `enum decode_pid_bits`, and extern global sets such as `trace_set`, `signal_set`, `quiet_set`, `decode_fd_set`, and `inject_set`.

Control flow: no runtime flow; API declarations only.

State and persistence behavior: declares process-wide mutable qualifier state owned by other translation units.

Dependencies and integration points: included by path tracing, open fd formatting, injection, filters, and PID namespace translation.

Risks: enum ordering is part of option parsing and membership checks; changes require updating parsers and tests. Globals make initialization order important.

Test signals: qualifier parsing tests for quiet/decode-fd/decode-pid bits, syscall filter membership, and build coverage for all extern sets.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/number_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/oldstat.c -->
# sources/test-tools/strace/src/oldstat.c

Purpose: decodes legacy `oldstat` and `oldfstat` syscalls when `struct __old_kernel_stat` is available.

Important APIs/types/functions: `print_old_kernel_stat`, `SYS_FUNC(oldstat)`, `SYS_FUNC(oldfstat)`, `struct __old_kernel_stat`, and normalized `struct strace_stat`.

Control flow: on entry, `oldstat` prints pathname and `oldfstat` prints fd. On exit, both fetch the old kernel stat buffer, normalize fields with sign/zero extension into `strace_stat`, and call `print_struct_stat`.

State and persistence behavior: no persistent state.

Dependencies and integration points: depends on `asm_stat.h`, `stat.h`, old kernel stat configure probes, path/fd printers, and the shared stat structure printer.

Risks: compiled only on platforms exposing the old structure. Legacy field widths and sign extension must match historical ABI expectations.

Test signals: oldstat/oldfstat traces on supported architectures, bad output pointers, timestamp sign extension, device/inode formatting, and absence on unsupported builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/oldstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/open.c -->
# sources/test-tools/strace/src/open.c

Purpose: decodes `open`, `openat`, `openat2`, `creat`, and shared directory-fd/open-flag formatting.

Important APIs/types/functions: `print_dirfd`, `sprint_open_modes`, `tprint_open_modes`, `decode_open`, `print_open_how`, `SYS_FUNC(open)`, `openat`, `openat2`, and `creat`.

Control flow: open-like syscalls print path, flags, optional mode for `O_CREAT`/`__O_TMPFILE`, and return fd semantics. `openat` prints `dirfd` first. `openat2` fetches `struct open_how`, prints flags/mode/resolve flags, and emits nonzero trailing bytes for larger user-provided sizes.

State and persistence behavior: no durable state, except `print_dirfd` updates `tcp->last_dirfd` when SELinux context support is enabled and may read `/proc/<pid>/cwd` for associated info.

Dependencies and integration points: depends on `kernel_fcntl.h`, `<linux/openat2.h>`, open flag xlats, path/fd printers, number-set decode-fd options, and proc pid helpers.

Risks: open flag formatting must split access mode from other flags correctly. `openat2` structure size is user-provided and must avoid over-reading.

Test signals: all open variants, `AT_FDCWD` with cwd decoding, `O_CREAT`, `O_TMPFILE`, unknown flags, `open_how` short/extended sizes, resolve flags, and fd return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/or1k_atomic.c -->
# sources/test-tools/strace/src/or1k_atomic.c

Purpose: architecture-specific decoder for OpenRISC `or1k_atomic` syscall.

Important APIs/types/functions: `SYS_FUNC(or1k_atomic)`, `OR1K_ATOMIC_*` operation constants, and `atomic_ops` xlat.

Control flow: under `OR1K`, prints operation type and then prints one, two, or three value arguments depending on the atomic operation; returns decoded with hex return formatting.

State and persistence behavior: no state.

Dependencies and integration points: compiled only for OR1K builds; integrated through the architecture syscall table.

Risks: operation constants are local definitions and must match the kernel ABI. Unsupported operations print only the type.

Test signals: OR1K syscall tests for swap, cmpxchg, decpos, arithmetic/bitwise ops, unknown type, and hex return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/or1k_atomic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pathtrace.c -->
# sources/test-tools/strace/src/pathtrace.c

Purpose: implements path and fd matching for strace path filtering.

Important APIs/types/functions: `global_path_set`, `pathtrace_select_set`, `pathtrace_match_set`, `get_proc_pid_fd_path`, `getfdpath_pid`, `pathmatch`, `upathmatch`, `fdmatch`, `match_xselect_args`, and `storepath`.

Control flow: selected paths are stored literally and with realpath canonicalization. Matching dispatches by syscall semantic number (`sen`) to inspect the correct path and fd arguments for file, descriptor, network, mmap, poll/select, fanotify, mount, link/rename, and fsconfig cases; otherwise it falls back to arg0 based on syscall trace flags.

State and persistence behavior: `global_path_set` and caller-provided `path_set` arrays persist selected paths. It reads `/proc/<pid>/fd` links and detects `" (deleted)"` suffixes by comparing link and path stat data.

Dependencies and integration points: used by trace filtering; depends on syscall metadata flags, number sets, proc pid translation, largefile stat wrappers, fd/path printers, and quiet option state.

Risks: syscall-specific argument knowledge must stay synchronized with syscall decoders. `/proc` path resolution can fail under namespaces or permissions. Large fd sets are capped to limit work.

Test signals: path filters for openat/linkat/renameat/mmap/poll/select/fanotify/fsconfig, fd-set filters, deleted fd symlinks, canonical path logging, and fallback behavior for new trace-flagged syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pathtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/perf.c -->
# sources/test-tools/strace/src/perf.c

Purpose: decodes `perf_event_open` and shared `perf_event_attr` structures for syscall and ioctl paths.

Important APIs/types/functions: `fetch_perf_event_attr`, `print_perf_event_attr`, `SYS_FUNC(perf_event_open)`, `struct pea_desc`, `free_pea_desc`, and perf xlat tables for type, config, sample/read formats, branch samples, breakpoints, and flags.

Control flow: on syscall entry it fetches the user attr size and stores a copied `perf_event_attr` in tcb private data; on exit it prints fields as the kernel sees them, including E2BIG size changes, type-specific `config` decoding, bit flags, optional versioned fields, breakpoint config, branch/sample register fields, aux action fields, and trailing data marker.

State and persistence behavior: per-syscall tcb private data owns a heap copy of the attr and is freed by `free_pea_desc`.

Dependencies and integration points: used by `perf_event_open` and `perf_ioctl.c`; depends on `perf_event_struct.h`, many perf xlat tables, tcb private data, and syscall enter/exit sequencing.

Risks: perf attr is versioned and accepts partial structures; field availability checks must mirror kernel behavior. Bitfield layout and new flags require ongoing updates.

Test signals: perf_event_open for hardware/software/cache/raw/breakpoint types, abbrev/full output, E2BIG size update, versioned optional fields, unknown reserved bits, invalid sizes, and ioctl modify-attributes reuse.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/perf_event_struct.h -->
# sources/test-tools/strace/src/perf_event_struct.h

Purpose: local UAPI-compatible definitions for perf event structures used by decoders.

Important APIs/types/functions: `struct perf_event_attr`, `struct perf_event_query_bpf`, `PERF_PMU_TYPE_SHIFT`, and `PERF_HW_EVENT_MASK`.

Control flow: no executable flow; structure layout encodes versioned perf attr fields from ver0 through ver9 and query-bpf flexible array header.

State and persistence behavior: no state.

Dependencies and integration points: included by `perf.c` and `perf_ioctl.c`; layout must match kernel UAPI enough for tracee memory decoding across personalities.

Risks: bitfield order and structure growth are ABI-sensitive. Missing newer fields or wrong reserved widths causes incorrect perf output.

Test signals: compile-time structure size/offset expectations, perf attr version-size tests, and `PERF_EVENT_IOC_QUERY_BPF` id-array decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/perf_event_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/perf_ioctl.c -->
# sources/test-tools/strace/src/perf_ioctl.c

Purpose: decodes perf event ioctl commands.

Important APIs/types/functions: `perf_ioctl`, `perf_ioctl_query_bpf`, `perf_ioctl_modify_attributes`, `PERF_EVENT_IOC_*`, and `perf_ioctl_flags`.

Control flow: simple commands print flags, counts, fds, strings, ids, or numeric args. `QUERY_BPF` prints `ids_len` on entry and `prog_cnt` plus `ids` on exit. `MODIFY_ATTRIBUTES` reuses `fetch_perf_event_attr` and `print_perf_event_attr`.

State and persistence behavior: uses syscall phase and may rely on perf attr tcb private data through shared perf helpers.

Dependencies and integration points: personality-aware `MPERS_PRINTER_DECL` ioctl decoder; depends on `<linux/ioctl.h>`, `perf_event_struct.h`, and perf syscall attr helpers.

Risks: pointer-size-sensitive ioctls need mpers handling. Query BPF output count controls array length, so failed exits must preserve a syntactically closed partial struct.

Test signals: enable/disable/reset flags, refresh, period, set-output fd, set-filter string, id output, query-bpf success/error, and modify-attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/perf_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/personality.c -->
# sources/test-tools/strace/src/personality.c

Purpose: decodes the Linux `personality` syscall argument.

Important APIs/types/functions: `SYS_FUNC(personality)`, `personality_types`, and `personality_flags`.

Control flow: prints the low personality type bits with `PER_*` xlat and remaining behavior flags with `ADDR_*`/personality flag xlat semantics.

State and persistence behavior: no persistent state in the decoder; the syscall changes tracee execution personality in the kernel.

Dependencies and integration points: integrated through syscall table and generated personality xlat tables.

Risks: flag/type masks must match kernel UAPI. Unknown flags should remain visible numerically.

Test signals: known personalities, combined flags, unknown high bits, and `0xffffffff` query-style argument.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_getfd.c -->
# sources/test-tools/strace/src/pidfd_getfd.c

Purpose: decodes `pidfd_getfd`.

Important APIs/types/functions: `SYS_FUNC(pidfd_getfd)`, `pidfd_get_pid`, `printfd`, and `printfd_pid`.

Control flow: prints pidfd, then tries to resolve the pidfd target pid so the target fd can be rendered in that process context; otherwise prints target fd numerically. Flags are printed as hex and the return value is fd-formatted.

State and persistence behavior: no state.

Dependencies and integration points: depends on pidfd-to-pid lookup and fd printing helpers; integrated as a syscall decoder.

Risks: target fd path rendering depends on resolving pidfd and `/proc` access. Flags currently have no symbolic table here.

Test signals: valid pidfd target resolution, invalid pidfd fallback, flags zero/nonzero, and returned fd formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_getfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_ioctl.c -->
# sources/test-tools/strace/src/pidfd_ioctl.c

Purpose: decodes pidfd-specific ioctl commands, including namespace fd getters and `PIDFD_GET_INFO`.

Important APIs/types/functions: `pidfd_ioctl`, `pidfd_ioctl_is_namespace_fd`, `pidfd_ioctl_is_get_info`, `pidfd_ioctl_print_pidfd_info_fields`, `struct pidfd_info`, `pidfd_info_mask`, and `pidfd_coredump_mask`.

Control flow: namespace ioctls are rendered as fd-returning commands. `PIDFD_GET_INFO` prints the requested mask on entry, stores it in tcb private data if needed, then on exit fetches the structure, notes mask changes, and conditionally prints fields gated by returned mask bits and user-provided size.

State and persistence behavior: per-ioctl requested mask is stored in tcb private data or private ulong across enter/exit. No global state.

Dependencies and integration points: used by generic ioctl dispatch; depends on `<linux/pidfd.h>`, pid/uid/signal/wait-status printers, and xlat tables.

Risks: this is a 2026 kernel-facing area with evolving `pidfd_info` versions. Size and mask gating must match the kernel or fields may be omitted or over-read.

Test signals: all namespace fd ioctls, `PIDFD_GET_INFO` short sizes, each mask bit, changed returned mask, failed exits, coredump fields, credential fields, and supported-mask output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_open.c -->
# sources/test-tools/strace/src/pidfd_open.c

Purpose: decodes `pidfd_open`.

Important APIs/types/functions: `SYS_FUNC(pidfd_open)` and `pidfd_open_flags`.

Control flow: prints the target pid as a TGID with namespace translation support, prints flags symbolically, and marks the return value as an fd.

State and persistence behavior: no state.

Dependencies and integration points: uses pid printers, `kernel_fcntl.h`, and generated pidfd flag xlats.

Risks: new pidfd flags require xlat updates. PID printing depends on namespace translation settings.

Test signals: valid pid, pid zero/negative error cases, known and unknown flags, and fd return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidns.c -->
# sources/test-tools/strace/src/pidns.c

Purpose: translates and annotates PIDs across PID namespaces for decoded output.

Important APIs/types/functions: `pidns_init`, `translate_pid`, `get_proc_pid`, `printpid`, `printpid_tgid_pgid`, `get_ns_hierarchy`, `get_id_list`, trie caches `ns_pid_to_proc_pid` and `proc_data_cache`, and `struct proc_data`.

Control flow: initialization sizes trie caches from `/proc/sys/kernel/pid_max`. Translation first handles trivial same-namespace cases, then checks cached namespace/id mappings, validates cached process data, scans cached entries, and finally scans `/proc` and task directories. Namespace hierarchy is walked with `NS_GET_PARENT`; status files provide `NSpid`/`NStgid`/`NSpgid`/`NSsid` lists.

State and persistence behavior: process-wide trie caches persist namespace-to-proc-pid mappings and per-proc namespace/id hierarchies. `ns_get_parent_enotty`, `pid_max`, and cached namespace ids persist to avoid repeated expensive probes.

Dependencies and integration points: used by `printpid`, fd/path helpers, namespace ioctls, and decode-pid options; depends on `/proc`, nsfs ioctls, trie implementation, number sets, largefile wrappers, and tcb `pid_ns`.

Risks: heavy reliance on `/proc` visibility, permissions, kernel namespace ioctl support, and process liveness. Cache invalidation is best-effort and must handle disappearing processes.

Test signals: same namespace fast path, nested PID namespaces, proc-pid lookup, cache hits/invalidations, missing `NS_GET_PARENT`, permission failures, comm annotations, TGID/PGID/SID translation, and disabled decode-pid options.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pkeys.c -->
# sources/test-tools/strace/src/pkeys.c

Purpose: decodes memory protection key allocation and free syscalls.

Important APIs/types/functions: `SYS_FUNC(pkey_alloc)`, `SYS_FUNC(pkey_free)`, and `pkey_access` xlat.

Control flow: `pkey_alloc` prints raw flags and symbolic access rights; `pkey_free` prints the signed key id.

State and persistence behavior: no decoder state.

Dependencies and integration points: syscall table integration and generated protection-key access xlat.

Risks: allocation flags are printed raw because no symbolic table is used here. Access-right additions need xlat updates.

Test signals: pkey allocation with disable-access/disable-write combinations, unknown access bits, and freeing valid/invalid pkeys.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pkeys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/poke.c -->
# sources/test-tools/strace/src/poke.c

Purpose: stores and applies syscall tampering payloads that write bytes into tracee memory on syscall entry or exit.

Important APIs/types/functions: `alloc_poke_data`, `poke_add`, `poke_tcb`, `struct poke_payload`, `poke_data_vec`, and list helpers.

Control flow: allocation grows an arena of list heads and returns a 16-bit index. `poke_add` rejects duplicate `(is_enter,arg_no)` payloads per index. `poke_tcb` iterates payloads for the current phase, validates argument count, writes data to the pointer argument with `upoken`, logs failures, and marks `TCB_TAMPERED_POKED` if any write succeeds.

State and persistence behavior: process-wide `poke_data_vec` stores payload lists for the lifetime of strace.

Dependencies and integration points: used by fault/injection qualifier logic; depends on `list.h`, `upoken`, syscall metadata `n_args`, and tcb flags.

Risks: writes target tracee memory and can intentionally perturb behavior. Argument numbers are one-based in payloads but zero-based in `u_arg`; validation must remain correct. Index overflow is fatal.

Test signals: allocation growth, duplicate rejection, entry and exit pokes, invalid argument number, failed `upoken`, successful tamper flag, and multiple payloads per syscall.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/poke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/poke.h -->
# sources/test-tools/strace/src/poke.h

Purpose: declares poke payload storage and application APIs for syscall tampering.

Important APIs/types/functions: `struct poke_payload`, `alloc_poke_data`, `poke_add`, and `poke_tcb`.

Control flow: no implementation flow; callers create payloads, register them under an index, and apply by phase.

State and persistence behavior: `struct poke_payload` embeds list linkage and owns a data pointer supplied by callers.

Dependencies and integration points: included by injection parser and `poke.c`; requires `struct list_item` from surrounding includes.

Risks: ownership of `data` is external to the header and must be consistent with parser cleanup. `data_len` is 16-bit though comments document a maximum of 1024.

Test signals: compile-time users, parser-created payloads, and entry/exit application through `poke_tcb`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/poke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/poll.c -->
# sources/test-tools/strace/src/poll.c

Purpose: decodes `poll` and `ppoll` time32/time64 variants and produces concise return aux strings for ready fds and remaining timeout.

Important APIs/types/functions: `print_pollfd`, `decode_poll_entering`, `decode_poll_exiting`, `do_poll`, `do_ppoll`, `SYS_FUNC(poll_time32)`, `poll_time64`, `ppoll_time32`, and `ppoll_time64`.

Control flow: on entry, prints the `pollfd` array and nfds; `poll` prints integer timeout, `ppoll` prints timespec pointer and sigmask/size. On exit, successful calls scan the array for nonzero `revents`, build `tcp->auxstr`, and include timeout-left text when applicable.

State and persistence behavior: uses a static 1024-byte aux buffer inside `decode_poll_exiting`; no durable state across calls beyond `tcp->auxstr`.

Dependencies and integration points: syscall table time variants, poll flag xlats, array printers, timespec printers, sigset printers, and `xstring` bounded append helpers.

Risks: aux string truncation must remain syntactically understandable. Size arithmetic can overflow for huge nfds but is guarded by address range checks and fetch failures.

Test signals: ready fd arrays, timeout return, errors, negative fd entries, ppoll sigmask, time32/time64 paths, aux truncation, and modified timeout-left output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/prctl.c -->
# sources/test-tools/strace/src/prctl.c

Purpose: comprehensive decoder for `prctl` and x86 `arch_prctl`.

Important APIs/types/functions: `SYS_FUNC(prctl)`, `SYS_FUNC(arch_prctl)`, `print_prctl_args`, `print_get_uint_arg`, `print_set_kulong_arg`, SVE/SME/tagged-address/RISC-V value formatters, seccomp filter decoding, capability and architecture xlat tables.

Control flow: `prctl` prints the option then dispatches through a large option switch grouped by common decoding style. It handles no-arg getters, pointer-output getters on exit, setters with symbolic flags, seccomp filters, capabilities, securebits, timerslack, MCE, `PR_SET_MM`, vector length controls, speculation controls, PAC, tagged address, syscall user dispatch, sched core cookies, MDWE, RISC-V/PPC controls, VMA names, and ptracer ids. Getter results often return aux strings on exit. `arch_prctl` has x86-specific pointer-output and xfeature cases.

State and persistence behavior: no persistent global state; uses syscall enter/exit phase and `tcp->auxstr` for decoded return values.

Dependencies and integration points: integrates with syscall tables, seccomp BPF decoder, pid/signal/capability printers, architecture conditionals, and many generated prctl xlat tables.

Risks: prctl grows frequently and option-specific unused-argument rules differ. Some symbolic values are architecture-specific or not public UAPI. Return decoding must happen only on successful exits.

Test signals: representative option from each switch group, seccomp strict/filter, get/set aux-string options, SVE/SME/tagged/RISC-V formatting, sched core get cookie, VMA name, ptracer any, unknown option fallback, and x86 arch_prctl cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_dev_t.c -->
# sources/test-tools/strace/src/print_dev_t.c

Purpose: prints encoded device numbers in raw, abbreviated, or verbose `makedev` form.

Important APIs/types/functions: `print_dev_t`, `major`, `minor`, and xlat verbosity helpers.

Control flow: prints raw hex unless abbrev-only mode, returns early in raw mode, otherwise prints or comments `makedev(major, minor)` according to xlat verbosity.

State and persistence behavior: no state.

Dependencies and integration points: used by stat/statfs/VFS/socket diag decoders; depends on `<sys/sysmacros.h>` and print-field helpers.

Risks: major/minor extraction follows libc macros and must match Linux device encoding expected by decoded structures.

Test signals: raw, abbrev, and verbose xlat modes with representative device numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_dev_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_fields.h -->
# sources/test-tools/strace/src/print_fields.h

Purpose: shared inline output primitives and field/value macros used throughout strace and some tests.

Important APIs/types/functions: `tprint_struct_*`, `tprint_array_*`, `tprints_arg_*`, `tprint_comment_*`, `tprint_indirect_*`, `tprint_value_changed`, `tprint_unavailable`, `PRINT_VAL_*`, and many `PRINT_FIELD_*` macros.

Control flow: inline helpers emit punctuation, color sequences when `IN_STRACE` is defined, argument names when `Nflag` is enabled, and formatted scalar/field values. In non-strace test builds, macros map to stdio and no-op color constants.

State and persistence behavior: no owned state, but behavior depends on global formatting state such as color enablement, `Nflag`, and xlat verbosity through callers.

Dependencies and integration points: included by `defs.h` consumers across the decoder tree; bridges production strace output and test helper builds.

Risks: tiny punctuation/color changes affect golden output broadly. Macros evaluate arguments in C macro contexts, so callers must avoid side effects where a macro may reference fields multiple times.

Test signals: broad decoder golden tests, color/no-color output, named-argument mode, non-strace test compilation, and field macro coverage for signed, unsigned, hex, arrays, pointers, flags, and comments.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_fields.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_group_req.c -->
# sources/test-tools/strace/src/print_group_req.c

Purpose: mpers-aware printer for `struct group_req` socket multicast options.

Important APIs/types/functions: `print_group_req`, `struct_group_req`, `PRINT_FIELD_IFINDEX`, and `PRINT_FIELD_SOCKADDR`.

Control flow: if caller-provided length is shorter than the structure, prints the address; otherwise fetches and prints interface index plus group sockaddr.

State and persistence behavior: no state.

Dependencies and integration points: used by socket option decoders; depends on `<netinet/in.h>`, mpers definitions, interface-index printing, and sockaddr printing.

Risks: structure layout is personality-sensitive. Short lengths intentionally do not attempt partial decoding.

Test signals: native and compat `group_req`, short length fallback, invalid pointer, IPv4/IPv6 multicast sockaddrs, and interface-name rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_group_req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_ifindex.c -->
# sources/test-tools/strace/src/print_ifindex.c

Purpose: prints network interface indexes, optionally annotated with interface names.

Important APIs/types/functions: `get_ifname`, `print_ifindex`, `sprint_ifname`, `if_indextoname`, and string quoting helpers.

Control flow: when `HAVE_IF_INDEXTONAME` is available, resolves the index to an interface name, quotes it, and prints as `if_nametoindex("name")` using xlat formatting; otherwise prints the numeric index.

State and persistence behavior: uses static buffers for resolved names and formatted strings; no persistent cache.

Dependencies and integration points: used by netlink, socket, multicast, and NUMA-related printers; depends on `<net/if.h>` and xlat verbosity.

Risks: static buffers are overwritten on subsequent calls. Interface names depend on the strace process namespace, which may not match the tracee.

Test signals: existing and nonexistent ifindexes, quoted names with special characters, fallback builds without `if_indextoname`, and xlat verbosity modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_ifindex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_instruction_pointer.c -->
# sources/test-tools/strace/src/print_instruction_pointer.c

Purpose: prints the current tracee instruction pointer as a fixed-width output attribute.

Important APIs/types/functions: `print_instruction_pointer` and `get_instruction_pointer`.

Control flow: begins an attribute, fetches IP, prints 8 hex digits for 32-bit personalities or 16 for 64-bit, prints question marks if unavailable, then emits trailing space.

State and persistence behavior: no state.

Dependencies and integration points: used by syscall output prefixes when instruction pointer display is enabled; depends on current word size and architecture ptrace support.

Risks: unavailable IP must remain visually distinct and width-stable. Current word size controls formatting, not host pointer size.

Test signals: 32-bit and 64-bit tracees, failed IP fetch, and output prefix formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_instruction_pointer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_sigset.c -->
# sources/test-tools/strace/src/print_kernel_sigset.c

Purpose: mpers-aware printer for structures containing a signal-set pointer and size.

Important APIs/types/functions: `print_kernel_sigset`, `struct_sigset_addr_size`, and `print_sigset_addr_len`.

Control flow: fetches the two-field structure from tracee memory, prints `sigmask` by dereferencing the pointed-to sigset with the provided size, then prints `sigsetsize`.

State and persistence behavior: no state.

Dependencies and integration points: used by syscalls that pass a packed `{sigmask, sigsetsize}` pointer; depends on mpers pointer sizing and generic sigset printers.

Risks: pointer fields are personality-sensitive. Invalid outer or inner pointers must fall back cleanly.

Test signals: native and compat layouts, NULL sigmask, invalid pointers, different sigset sizes, and signal names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_sigset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_version.c -->
# sources/test-tools/strace/src/print_kernel_version.c

Purpose: prints packed Linux kernel version values.

Important APIs/types/functions: `print_kernel_version` and `KERNEL_VERSION`-style major/minor/patch extraction.

Control flow: prints raw hex unless abbrev-only mode; in non-raw modes also emits `KERNEL_VERSION(major, minor, patch)` as value or verbose comment.

State and persistence behavior: no state.

Dependencies and integration points: used by ioctl or syscall decoders that expose packed kernel version integers.

Risks: assumes the Linux `KERNEL_VERSION` packing layout `(major << 16) | (minor << 8) | patch`.

Test signals: raw/abbrev/verbose xlat modes and representative version values including high major/minor bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_kernel_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_mac.c -->
# sources/test-tools/strace/src/print_mac.c

Purpose: formats MAC and hardware addresses, including device-type-specific address lengths.

Important APIs/types/functions: `print_mac_addr`, `print_hwaddr`, `sprint_mac_addr`, `sprint_hwaddr`, and `hwaddr_sizes`.

Control flow: address bytes are formatted as colon-separated hex for supported sizes, with raw quoted hex also printed in raw/verbose modes or for oversized buffers. Hardware-address printing caps displayed bytes based on ARPHRD device type where known.

State and persistence behavior: uses static formatting buffers and a static hardware-size lookup table; no dynamic state.

Dependencies and integration points: used by netlink attribute decoders and link-layer printers; depends on ARP hardware type constants, xlat verbosity, and string formatting helpers.

Risks: `hwaddr_sizes` must track ARPHRD constants. Static buffers are overwritten by later calls. Unknown device types use a permissive length cap.

Test signals: Ethernet, loopback, InfiniBand-like, unknown types, oversized address buffers, and raw/abbrev/verbose xlat modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_mq_attr.c -->
# sources/test-tools/strace/src/print_mq_attr.c

Purpose: mpers-aware printer for POSIX message queue attributes.

Important APIs/types/functions: `printmqattr`, `mq_attr_t`, and `mq_attr_flags`.

Control flow: fetches `struct mq_attr`; prints `mq_flags` symbolically when requested or hex otherwise, then prints max messages, message size, and current message count.

State and persistence behavior: no state.

Dependencies and integration points: used by mqueue syscall decoders; depends on mpers, kernel mqueue headers, and open-flag style xlat tables.

Risks: layout is personality-sensitive. Callers must choose `decode_flags` according to syscall context.

Test signals: `mq_getsetattr`, `mq_open` attribute printing, native/compat layouts, flags decoded/raw modes, and invalid pointer fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_mq_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_msgbuf.c -->
# sources/test-tools/strace/src/print_msgbuf.c

Purpose: mpers-aware printer for SysV message buffers.

Important APIs/types/functions: `tprint_msgbuf`, `msgbuf_t`, and `MSG_H_PROVIDER`.

Control flow: fetches the message header, prints signed `mtype`, then prints `mtext` from immediately after `mtype` using the caller-provided byte count.

State and persistence behavior: no state.

Dependencies and integration points: used by SysV `msgsnd`/`msgrcv` decoders; depends on IPC header provider selection and mpers message-buffer layout.

Risks: text length is supplied by the caller and must match syscall semantics. Compat `mtype` layout matters.

Test signals: send/receive message buffers, zero-length text, invalid pointer, native/compat mtype widths, and truncated string output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_msgbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_sg_req_info.c -->
# sources/test-tools/strace/src/print_sg_req_info.c

Purpose: decodes `struct sg_req_info` for SCSI generic ioctl support.

Important APIs/types/functions: `decode_sg_req_info`, `struct_sg_req_info`, and `HAVE_SCSI_SG_H` gating.

Control flow: on entering returns without printing; on exit prints `argp` and decodes request state, orphan/ownership/problem flags, pack id, user pointer, and duration.

State and persistence behavior: no state.

Dependencies and integration points: used by SG ioctl decoder paths; depends on `<scsi/sg.h>` and mpers when available.

Risks: compiled only when SCSI SG headers are present. Output is exit-only because ioctl fills the structure.

Test signals: successful `SG_GET_REQUEST_TABLE`-style output, failed ioctl, invalid pointer, and builds without `<scsi/sg.h>`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_sg_req_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_sigevent.c -->
# sources/test-tools/strace/src/print_sigevent.c

Purpose: mpers-aware printer for `struct sigevent`.

Important APIs/types/functions: `print_sigevent`, `print_sigev_value`, `struct_sigevent`, and `sigev_value` xlat.

Control flow: fetches the structure, optionally prints non-null `sigev_value`, prints `sigev_signo` as a signal for signal/thread/thread-id notifications, prints notify type, and then prints thread id or thread callback/attribute pointers for relevant modes.

State and persistence behavior: no state.

Dependencies and integration points: used by timer, AIO, and message queue decoders; depends on mpers, `sigevent.h`, signal names, and generated notify xlats.

Risks: union field macros are layout-sensitive. Unknown notify modes print numeric signal and omit union-specific fields.

Test signals: SIGEV_SIGNAL, SIGEV_NONE, SIGEV_THREAD, SIGEV_THREAD_ID, non-null sigev_value, invalid pointer, and compat layouts.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_sigevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_statfs.c -->
# sources/test-tools/strace/src/print_statfs.c

Purpose: prints normalized `statfs` and `statfs64` structures.

Important APIs/types/functions: `print_struct_statfs`, `print_struct_statfs64`, `print_f_fsid`, `fetch_struct_statfs`, `fetch_struct_statfs64`, `fsmagic`, and `statfs_flags`.

Control flow: fetches the requested statfs variant into `struct strace_statfs`, prints filesystem type, block/file counts, optional fsid, name length, fragment size, and `f_flags` only when `ST_VALID` is set.

State and persistence behavior: no state.

Dependencies and integration points: used by statfs-family syscall decoders; depends on configure probes for structure fields and fetchers that normalize native/compat layouts.

Risks: optional fields vary by platform. Flag printing depends on `ST_VALID`; missing fetch support falls back to address.

Test signals: statfs/statfs64 success, magic type names, fsid layouts, flags with and without `ST_VALID`, invalid pointers, and platforms lacking statfs64.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_statfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_struct_stat.c -->
# sources/test-tools/strace/src/print_struct_stat.c

Purpose: prints normalized file status structures.

Important APIs/types/functions: `print_struct_stat`, `struct strace_stat`, device/inode/mode/uid/gid/time field printers, and macro remapping from `st_*` names to normalized fields.

Control flow: prints common stat fields including device, inode, mode, link count, uid/gid, rdev, size, block size, blocks, and timestamps. Nanosecond fields are printed when `has_nsec` is set; otherwise timestamps still get human-readable time comments.

State and persistence behavior: no state.

Dependencies and integration points: shared by old/new stat fetchers and syscall decoders; depends on `stat.h`, device/mode/uid/time printers, and field macros.

Risks: normalized `strace_stat` must be populated correctly by fetchers. Conditional nanosecond output affects golden traces.

Test signals: stat family syscalls with regular files/devices, nanosecond and non-nanosecond layouts, invalid pointers, large inode/size values, and mode/uid/gid formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_struct_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_syscall_number.c -->
# sources/test-tools/strace/src/print_syscall_number.c

Purpose: prints syscall numbers as fixed-width output attributes.

Important APIs/types/functions: `print_syscall_number` and `tcp->true_scno`.

Control flow: emits an attribute containing the true syscall number when known, otherwise prints unavailable marker, then emits a trailing space.

State and persistence behavior: reads per-tcb syscall state only.

Dependencies and integration points: used by output prefix logic when syscall number display is enabled.

Risks: `true_scno == -1` must be treated as unavailable rather than a huge unsigned value.

Test signals: known syscall number, unavailable syscall number, and output prefix alignment.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_syscall_number.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_time.c -->
# sources/test-tools/strace/src/print_time.c

Purpose: decodes the legacy `time` syscall and formats returned epoch seconds.

Important APIs/types/functions: `SYS_FUNC(time)`, mpers `kernel_time_t`, `sprinttime`, and `tcp->auxstr`.

Control flow: on exit, prints `tloc` and dereferenced time value if accessible. On successful return, sets aux string to human-readable return time.

State and persistence behavior: no persistent state; uses exit-phase syscall result and optional output pointer.

Dependencies and integration points: syscall table integration, mpers scalar sizing, tracee memory fetch, and time formatting helpers.

Risks: pointer output is only valid on exit. Time width is personality-sensitive.

Test signals: `time(NULL)`, valid `tloc`, invalid pointer, syscall failure, 32-bit/64-bit personalities, and aux return string formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_time.c -->
