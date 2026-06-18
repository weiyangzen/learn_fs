# subset-b-009319 research

Grouped research report for strace's bundled Linux UAPI netlink-related headers. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_queue.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_queue.h

Purpose: defines the userspace ABI for nfnetlink queue messages on `NETLINK_NETFILTER`. It names queue message types, packet/verdict/config payload structs, netlink attributes for queued packet metadata, queue configuration attributes, and queue/SKB behavior flags consumed by userspace packet verdict daemons and by strace's netfilter netlink decoders.

Important APIs/types/functions: `enum nfqnl_msg_types` provides `NFQNL_MSG_PACKET`, `NFQNL_MSG_VERDICT`, `NFQNL_MSG_CONFIG`, and `NFQNL_MSG_VERDICT_BATCH`; `struct nfqnl_msg_packet_hdr` carries packet id, hardware protocol, and netfilter hook; `struct nfqnl_msg_verdict_hdr` carries verdict and packet id; `struct nfqnl_msg_config_cmd` and `struct nfqnl_msg_config_params` drive queue binding and copy mode. Attribute enums include `nfqnl_attr_type`, `nfqnl_vlan_attr`, and `nfqnl_attr_config`. Flag macros cover queue fail-open/conntrack/GSO/UID-GID/security-context behavior and skb checksum/GSO metadata.

Control flow: the header has no executable flow, but it describes the message lifecycle. The kernel emits `NFQNL_MSG_PACKET` with `NFQA_PACKET_HDR` plus optional metadata such as timestamps, ifindexes, hardware address, conntrack data, VLAN data, L2 header, UID/GID, security context, and payload. Userspace sends `NFQNL_MSG_VERDICT` or `NFQNL_MSG_VERDICT_BATCH` with a verdict header, or sends `NFQNL_MSG_CONFIG` with command/parameter attributes to bind queues, choose `NFQNL_COPY_NONE`, `NFQNL_COPY_META`, or `NFQNL_COPY_PACKET`, and adjust queue flags and length.

State/persistence behavior: there is no persistence in the header. The represented state is kernel queue configuration and transient packet queue entries; `packet_id` is the correlation key for later verdicts. Configuration flags alter kernel queue behavior for subsequent packets until changed or unbound.

Dependencies/integration: includes `<linux/types.h>` and `<linux/netfilter/nfnetlink.h>`. In this repository, `src/netlink.c` includes the header and maps `NFNL_SUBSYS_QUEUE` message types through generated `xlat/nf_queue_msg_types`, while `tests/nfnetlink_queue.c` and `tests/gen_tests.in` provide decode coverage. It also integrates with conntrack UAPI via `NFQA_CT`/`NFQA_EXP` attributes without defining those nested formats itself.

Risks: ABI decoding is sensitive to network byte order fields, packed structs, and attribute length/alignment. Adding attributes or flags in the bundled header requires matching xlat regeneration and decoder/test updates. `NFQA_CFG_MASK` and `NFQA_CFG_FLAGS` must be interpreted together; treating flags as absolute without the mask can misdescribe partial updates. `NFQA_SKB_CSUMNOTREADY` and `NFQA_SKB_CSUM_NOTVERIFIED` are easy to conflate.

Test signals: strace should print known nfqueue message names instead of numeric fallbacks, decode packet/config/verdict structures without over-reading short payloads, and preserve unknown attribute/flag fallback output. Existing signals are the `nfnetlink_queue` pure executable entry and netlink socket diagnostic test references.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netlink.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netlink.h

Purpose: provides the core Linux netlink userspace ABI: protocol numbers, socket address shape, message headers, message flags, alignment/access macros, error/extended ACK attributes, socket options, mmap ring descriptors, generic netlink attribute headers, bitfield attributes, and policy-description attribute types.

Important APIs/types/functions: protocol constants include `NETLINK_ROUTE`, `NETLINK_SOCK_DIAG`, `NETLINK_NETFILTER`, `NETLINK_GENERIC`, `NETLINK_CRYPTO`, and others up to `MAX_LINKS`. `struct sockaddr_nl` defines `AF_NETLINK` addressing with `nl_pid` and multicast groups. `struct nlmsghdr` is the fixed message header. `NLM_F_*` macros describe request, multipart, ACK, dump, create/replace/delete, and extended ACK behavior. `NLMSG_ALIGN`, `NLMSG_LENGTH`, `NLMSG_SPACE`, `NLMSG_DATA`, `NLMSG_NEXT`, `NLMSG_OK`, and `NLMSG_PAYLOAD` are the parser/writer primitives. `struct nlmsgerr` and `enum nlmsgerr_attrs` define ACK/error payloads. `struct nlattr`, `NLA_F_NESTED`, `NLA_F_NET_BYTEORDER`, `NLA_ALIGN`, and `NLA_HDRLEN` define TLV attributes. `struct nla_bitfield32`, `enum netlink_attribute_type`, and `enum netlink_policy_type_attr` describe introspectable attribute policies.

Control flow: the header encodes generic parsing flow. A netlink buffer is walked with `NLMSG_OK` and `NLMSG_NEXT`; each `nlmsghdr` selects a subsystem-specific decoder via `nlmsg_type`; payload begins at `NLMSG_DATA`; multipart dumps carry `NLM_F_MULTI` and terminate with `NLMSG_DONE`; errors and ACKs use `NLMSG_ERROR`, `struct nlmsgerr`, and optional extended ACK TLVs when `NETLINK_EXT_ACK` is enabled. Attribute payloads are then walked using `struct nlattr`, the NLA alignment rules, and family-specific policy.

State/persistence behavior: no state is stored by this header. It defines transient socket message state, socket options, and mmap ring descriptors. The ring status enum (`NL_MMAP_STATUS_UNUSED`, `RESERVED`, `VALID`, `COPY`, `SKIP`) models per-frame handoff between kernel and userspace but persistence remains in the kernel socket buffers and mmap area, not in this file.

Dependencies/integration: includes `<linux/const.h>`, `<linux/socket.h>`, and `<linux/types.h>`. It is foundational for nearly all strace netlink decoding: `src/netlink.c` fetches `struct nlmsghdr`, chooses protocol-specific type tables using the `NETLINK_*` constants, decodes flags with xlat tables, and uses the alignment macros for nested payload boundaries. `src/nlattr.*` and many route, sock_diag, netfilter, generic-netlink, and sockaddr tests depend on these constants being in sync with the bundled UAPI snapshot.

Risks: malformed or truncated traced buffers make the alignment and length macros security-sensitive for decoders; callers must use `NLMSG_OK`-style guards before accessing payload. `NLMSG_PAYLOAD(nlh,len)` subtracts aligned nested header space and is easy to misuse with the wrong `len`. Flag values overlap across request classes (`NLM_F_ROOT` and `NLM_F_REPLACE` share a bit), so decoding must use operation context. Attribute type flags occupy high bits and must be masked with `NLA_TYPE_MASK` before indexing policy arrays.

Test signals: netlink tests should show correct protocol names, message flag names, control message names, ACK flag/TLV names, strict-check socket options, and robust behavior on short messages. Regressions usually appear as numeric fallbacks where an xlat should exist, bad payload offsets, missing extended ACK attributes, or decoder over-read failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netlink_diag.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netlink_diag.h

Purpose: defines the socket-diagnostic ABI for inspecting netlink sockets through `NETLINK_SOCK_DIAG`. It supplies request/response structs, ring configuration structs, optional diagnostic attributes, show masks, and socket flag bits.

Important APIs/types/functions: `struct netlink_diag_req` contains family, protocol selector, inode, `ndiag_show` bitmask, and cookie filter. `struct netlink_diag_msg` reports family, socket type, netlink protocol, connection state, source/destination port IDs, destination group, inode, and cookie. `struct netlink_diag_ring` mirrors mmap ring sizing. Attribute enum values cover memory info, multicast groups, RX/TX rings, and flags. `NDIAG_PROTO_ALL` selects all protocols; `NDIAG_SHOW_*` controls optional data; `NDIAG_FLAG_*` reports socket options such as packet info, broadcast error, no-ENOBUFS, listen-all-nsid, and cap-ack.

Control flow: a diagnostic client sends `netlink_diag_req`, often via sock_diag with `sdiag_family = AF_NETLINK`; the kernel replies with one or more `netlink_diag_msg` records and optional netlink attributes requested by `ndiag_show`. The strace decoder in `src/netlink_netlink_diag.c` first prints the fixed request/response fields, then uses `NLMSG_ALIGN(sizeof(msg))` to locate optional attributes and dispatches to decoders for meminfo, groups, ring config, and flags.

State/persistence behavior: diagnostic messages are snapshots of live netlink sockets. There is no durable state; cookies and inode fields let userspace correlate a returned socket with kernel socket identity at the moment of the dump. Ring attributes expose current mmap RX/TX ring configuration if requested.

Dependencies/integration: includes `<linux/types.h>` and relies on the generic sock_diag/netlink infrastructure. In strace it integrates with `netlink_sock_diag.h`, `src/netlink_sock_diag.c`, `src/socketutils.c`, and generated xlats `netlink_diag_attrs`, `netlink_diag_show`, `netlink_socket_flags`, and `netlink_states`. Tests include `tests/netlink_sock_diag.c`, `tests/netlink_netlink_diag.c`, and `tests/nlattr_netlink_diag_msg.c`.

Risks: request and response structs share similar field names but different semantics; decoders must not treat `sdiag_protocol` and `ndiag_protocol` identically when printing `NDIAG_PROTO_ALL`. Group attributes are word-size dependent, so 32-bit and 64-bit decoding can differ. `NDIAG_SHOW_RING_CFG` is deprecated but still part of the ABI and xlat coverage. Optional attributes require strict length checks to avoid reading past short diagnostic payloads.

Test signals: expected output should decode `NDIAG_SHOW_*` masks, `NETLINK_DIAG_*` attributes, `NDIAG_FLAG_*` flags, ring fields, cookies, and `NDIAG_PROTO_ALL`. Short-message tests should show ellipses or raw addresses rather than corrupt field output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netlink_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/nexthop.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/nexthop.h

Purpose: defines the rtnetlink ABI for standalone nexthop objects and nexthop groups. It covers the `nhmsg` fixed header, group entries and weight encoding, group type constants, top-level nexthop attributes, resilient-group nested attributes, bucket attributes, group statistics, and operation flags.

Important APIs/types/functions: `struct nhmsg` carries address family, returned scope, installing routing protocol, reserved byte, and `RTNH_F` flags. `struct nexthop_grp` names a member nexthop id and an encoded two-byte weight; the inline `nexthop_grp_weight()` converts `weight` plus `weight_high` to the public one-based weight. Group types are `NEXTHOP_GRP_TYPE_MPATH` and `NEXTHOP_GRP_TYPE_RES`. `NHA_*` attributes cover IDs, groups, group type, blackhole, output interface, gateway, lightweight tunnel encapsulation, dump filters, bridge FDB nexthops, resilient group/bucket nests, operation flags, group stats, and hardware stats state.

Control flow: route netlink messages for nexthop operations carry an `nhmsg` header followed by `NHA_*` attributes. A single nexthop uses attributes such as `NHA_ID`, `NHA_OIF`, `NHA_GATEWAY`, `NHA_ENCAP_TYPE`, and `NHA_ENCAP`; a group uses `NHA_GROUP` plus optional `NHA_GROUP_TYPE`, and resilient groups add `NHA_RES_GROUP`/`NHA_RES_BUCKET` nests. Dump requests can filter by output interface, groups-only, or master device, and operation flags request software/hardware stats. In strace, `src/rtnl_nh.c` decodes the fixed header, then dispatches attributes based on this enum and the header family.

State/persistence behavior: the header defines persistent kernel routing objects as seen through rtnetlink, but stores no state itself. Nexthop IDs are stable handles until deleted. Resilient group attributes expose timers, bucket assignments, idle time, unbalanced time, and stats snapshots; hardware-stat enable/use fields describe state shared with drivers.

Dependencies/integration: includes `<linux/types.h>` and references route concepts such as address families, routing scopes/protocols, `RTNH_F` flags, ifindexes, gateways, and lightweight tunnel encapsulation. In this repository it is consumed by `src/rtnl_nh.c`, `tests/nlattr_nhmsg.c`, `tests/netlink_route.c`, and xlat inputs for top-level nexthop, group type, resilient group, and bucket attributes.

Risks: attribute combinations have ABI constraints documented in comments: `NHA_GROUP` excludes non-group attributes, `NHA_BLACKHOLE` excludes OIF/GATEWAY/ENCAP, and `NHA_FDB` excludes OIF/BLACKHOLE/ENCAP. The encoded group weight is one-based, so displaying raw `weight` alone can mislead even though strace currently prints raw struct fields. Newer attributes such as `NHA_OP_FLAGS`, `NHA_GROUP_STATS`, `NHA_HW_STATS_ENABLE`, and `NHA_HW_STATS_USED` need decoder and xlat support or they fall back to unknown `NHA_???` output.

Test signals: route-netlink tests should decode `nhmsg` family/scope/protocol/flags, arrays of `struct nexthop_grp`, group type names, gateway address according to `nh_family`, resilient group and bucket nested attributes, and unknown or truncated attributes safely. Hardware-stat and group-stat attributes are important future coverage points if the local decoder lags the bundled header.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/nexthop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/nfc.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/nfc.h

Purpose: defines Linux userspace ABI constants and socket address structures for NFC generic netlink control, NFC target/device/secure-element attributes, NFC protocol identifiers, raw packet pseudo-headers, socket protocols, and LLCP socket options.

Important APIs/types/functions: generic netlink identifiers are `NFC_GENL_NAME`, `NFC_GENL_VERSION`, and multicast group `NFC_GENL_MCAST_EVENT_NAME`. `enum nfc_commands` covers device get/up/down, DEP link up/down, poll start/stop, target discovery/loss events, target-mode activation events, LLC parameter get/set, secure-element enable/disable/events/I/O, firmware download, vendor commands, and target activation/deactivation. `enum nfc_attrs` names device, target, protocol, RF mode, LLC, secure-element, firmware, ISO15693, vendor, and ATS attributes. `struct sockaddr_nfc` and `struct sockaddr_nfc_llcp` define AF_NFC raw and LLCP socket addresses. Constants define protocol IDs/masks, secure-element types/states, raw header direction/payload type, socket protocols, and LLCP option names.

Control flow: NFC management is modeled as generic netlink commands and multicast events: userspace enumerates devices, powers adapters, starts polling with protocol masks, receives target events, configures LLCP, manages secure elements, and sends vendor or firmware commands using the listed attributes. Socket flow uses `AF_NFC` addresses: raw sockets bind/connect with device, target, and protocol, while LLCP adds DSAP/SSAP plus an optional service name and length. Raw monitor packets carry a two-byte pseudo-header with adapter index and direction/payload-type bits.

State/persistence behavior: the header stores no state. It names live kernel NFC device state such as powered devices, polling mode, discovered targets, active/deactivated target mode, LLCP parameters, firmware download status, and secure-element availability/connectivity. Those states are exposed through transient generic-netlink messages and AF_NFC socket operations.

Dependencies/integration: includes `<linux/types.h>` and `<linux/socket.h>`. In strace it is used by `src/sockaddr.c` to print `sockaddr_nfc` and `sockaddr_nfc_llcp`, by `src/net.c` to decode `socket(AF_NFC, ..., NFC_SOCKPROTO_*)` and NFC LLCP socket options, and by xlat inputs `nfc_protocols.in`, `nfc_sockaddr_protocols.in`, and `sock_nfcllcp_options.in`. `tests/sockaddr_xlat.c` exercises AF_NFC sockaddr formatting.

Risks: the LLCP sockaddr includes `__kernel_size_t service_name_len`, so layout and size differ between 32-bit and 64-bit personalities; strace handles this with parallel local layouts. Service names are fixed 63-byte arrays and must be printed using the provided length without trusting it beyond the array. Protocol IDs and protocol masks are different namespaces; mixing `NFC_PROTO_*` with `NFC_PROTO_*_MASK` can produce wrong output. Generic-netlink command/attribute enums are not necessarily decoded by strace unless matching xlat/decoder support exists.

Test signals: sockaddr tests should decode known NFC protocols such as `NFC_PROTO_JEWEL` and `NFC_PROTO_ISO15693`, preserve numeric fallback for unknown protocols, handle short `addrlen`, and print LLCP DSAP/SSAP/service-name fields correctly on 32-bit and 64-bit personalities. Socket tests should show `NFC_SOCKPROTO_RAW`, `NFC_SOCKPROTO_LLCP`, and `NFC_LLCP_*` option names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/nfc.h -->
