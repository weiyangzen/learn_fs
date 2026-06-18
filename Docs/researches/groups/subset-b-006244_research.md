# Research: subset-b-006244

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_main.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_main.c

## Purpose
This file implements the H.323 conntrack helper module. It understands the H.323 signaling stack enough to discover dynamic call-control and media endpoints and then installs conntrack expectations for related flows: RAS over UDP, Q.931/H.225 call signaling over TCP, H.245 control, RTP/RTCP media, and T.120 data channels. It also exposes the RCU-protected `nfct_h323_nat_hook` hook table so the NAT companion can rewrite embedded H.225/H.245 addresses when the master connection is NATed.

## Important APIs, Types, And Functions
The public integration points are `nfct_h323_nat_hook`, exported `get_h225_addr()`, the registered helpers `nf_conntrack_helper_h245`, `nf_conntrack_helper_q931[]`, and `nf_conntrack_helper_ras[]`, and the module init/exit functions `nf_conntrack_h323_init()` / `nf_conntrack_h323_fini()`. Runtime state is kept in `struct nf_ct_h323_master` through `nfct_help_data(ct)`, especially `tpkt_len[]`, `sig_port[]`, and `timeout`.

Packet parsing starts with `get_tpkt_data()` for TCP TPKT framing and `get_udp_data()` for RAS. Address extraction is split between `get_h245_addr()` for H.245 `TransportAddress` and `get_h225_addr()` for H.225 `TransportAddress`. Expectation creation is handled by `expect_rtp_rtcp()`, `expect_t120()`, `expect_h245()`, `expect_callforwarding()`, `expect_q931()`, plus RAS helpers such as `process_gcf()`, `process_rcf()`, `process_acf()`, and `process_lcf()`.

## Control Flow
The H.245 and Q.931 helpers only inspect established traffic in either direction. Both take `nf_h323_lock` because they use shared static decode buffers/objects and the global `h323_buffer`. They iterate over all TPKTs in the skb, decode with generated decoders such as `DecodeMultimediaSystemControlMessage()` or `DecodeQ931()`, and pass decoded objects to `process_h245()` or `process_q931()`. Decode failures are logged at debug level and accepted, but expectation/NAT failures drop the packet via `nf_ct_helper_log()`.

`process_h245()` recognizes open logical channel requests and acknowledgements. `process_olc()` and `process_olca()` inspect H.2250 logical channel parameters, creating RTP/RTCP UDP expectations for media and TCP expectations for T.120 separate stacks. Q.931 processing handles setup/call proceeding/connect/alerting/facility/progress messages, opening H.245 control expectations, processing tunneled H.245 controls, NAT-rewriting call signal addresses, and optionally filtering call forwarding by route comparison.

RAS is UDP-oriented and processed for each packet. `process_ras()` dispatches gatekeeper, registration, unregistration, admission, location, and info messages. Registration requests create permanent Q.931 expectations and set the RAS timeout from the RRQ TTL or `default_rrq_ttl`; registration confirms refresh the master connection and update expectation timers. Unregistration clears expectations and shortens the master timeout.

## State And Persistence
There is no disk persistence. State persists in conntrack entries, helper extensions, and expectation timers. The module parameters `default_rrq_ttl`, `gkrouted_only`, and `callforward_filter` change behavior at runtime. Expectations may be permanent for Q.931/T.120/multiple-call paths, but they still live only inside conntrack state and are removed when the master connection/helper is destroyed or RAS unregistration occurs.

## Dependencies And Integration Points
The file depends on the generated H.323 type decoders from `nf_conntrack_h323_types.c` and declarations in `linux/netfilter/nf_conntrack_h323.h`. It integrates with core conntrack helpers, expectations, zones, ecache logging, IPv4/IPv6 routing, and optional NAT via `struct nfct_h323_nat_hooks`. Helper registration ties names `RAS`, `Q.931`, and `H.245` to nf_conntrack's helper lookup and expectation assignment.

## Risks
The helper parses complex ASN.1/PER data from packets in softirq context, so bounds handling, shared buffer locking, and decode/object layout must stay exact. Incomplete or split TPKTs are mostly accepted without inspection; this avoids false drops but may miss expectations. NAT rewriting is IPv4-only in the checked paths. Call forwarding route filtering depends on current routing decisions and could misclassify unusual policy routing. Broad permanent expectations are necessary for H.323 but increase exposure if embedded addresses are forged; most expectation creation verifies that advertised addresses match the signaling source before accepting them.

## Test Signals
Useful tests include module load/unload with helper registration conflicts, H.323 calls with direct and gatekeeper-routed signaling, fragmented/separate TPKT header traffic, fastStart media offers in Q.931, standalone H.245 OLC/OLCA flows, RRQ/RCF TTL propagation, URQ cleanup, NATed IPv4 calls with embedded address rewriting, IPv6 non-NAT calls, forged embedded address rejection, and expectation table contents for RTP/RTCP port pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_types.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_types.c

## Purpose
This generated file describes the subset of H.225/H.245 ASN.1 structures that the H.323 helper decodes. It is a schema table collection, not normal procedural code: each `static const struct field_t` array maps PER fields onto C structure offsets, decode/skip/stop behavior, bounds, optionality, extension handling, and nested type tables. The decode engine included elsewhere consumes these tables to populate `Q931`, `RasMessage`, `MultimediaSystemControlMessage`, and related structures used by `nf_conntrack_h323_main.c`.

## Important APIs, Types, And Tables
The key type is `struct field_t` and the macros used inside table entries: `FNAME`, scalar kinds such as `INT`, `OCTSTR`, `BOOL`, `OID`, `SEQ`, `SEQOF`, `CHOICE`, size encodings such as `FIXD`, `BYTE`, `WORD`, `SEMI`, `CONS`, and actions/flags such as `DECODE`, `SKIP`, `STOP`, `OPT`, `EXT`, and `OPEN`. This file does not export symbols directly, but it provides the descriptor tables referenced by generated decoder entry points.

Important decoded tables include `_TransportAddress`, `_H245_TransportAddress`, `_H2250LogicalChannelParameters`, `_OpenLogicalChannel`, `_OpenLogicalChannelAck`, `_H323_UU_PDU`, `_H323_UserInformation`, and `_RasMessage`. These are the tables that expose embedded IPv4/IPv6 addresses, ports, H.245 addresses, media/control channel addresses, Q.931 message bodies, fastStart arrays, and RAS registration/admission/location fields to the runtime helper.

## Control Flow
Control flow is data-driven. A decoder begins at a top-level descriptor such as `_RasMessage`, `_H323_UserInformation`, or `_MultimediaSystemControlMessage`, reads PER bits, selects CHOICE arms, walks SEQUENCE fields in order, and either decodes data into the destination structure or skips/stops parsing for fields that are not relevant to conntrack. For example, `_Setup_UUIE` decodes `h245Address`, `destCallSignalAddress`, `sourceCallSignalAddress`, and `fastStart`; `_RegistrationRequest` decodes `callSignalAddress`, `rasAddress`, and `timeToLive`; `_AdmissionConfirm` decodes `destCallSignalAddress`.

The schema deliberately stops early for many complex or security-related fields after the addresses needed by conntrack are available. This keeps the helper focused on dynamic endpoint discovery rather than fully validating H.323 semantics.

## State And Persistence
All objects in this file are immutable static constants. No per-connection state is stored here. Persistence is only the compiled-in schema layout, which must remain ABI-consistent with the C structs declared in the H.323 header and with the generated decoder logic.

## Dependencies And Integration Points
The file depends on H.323 struct definitions and decoder macros usually included by the translation unit or generated companion. Its primary consumer is `nf_conntrack_h323_main.c`, whose processing functions rely on option bits, choice enums, decoded counts, and offset-filled address fields. Any mismatch between these tables and the struct definitions will corrupt parsed data or make the helper miss expectations.

## Risks
The dominant risk is generated-schema drift: offsets, count limits, extension flags, or decoded/skipped fields must match both the ASN.1 source and C structs. Because packet input is untrusted, malformed PER can exercise every bound and extension path. Many fields are skipped or stopped, so adding helper behavior for a new H.323 field requires changing the descriptor action from `SKIP`/`STOP` to `DECODE` and ensuring the destination structure has storage. Sequence-of bounds such as fastStart and address arrays are also security-relevant because they bound loops in the main helper.

## Test Signals
Decode tests should cover IPv4 and IPv6 `TransportAddress`, H.245 unicast media and media-control addresses, Q.931 setup/connect/alerting/facility/progress with fastStart and tunneled H.245 controls, RAS RRQ/RCF/URQ/ARQ/ACF/LRQ/LCF/IRR messages, extension fields before and after decoded fields, oversized sequence-of inputs, malformed CHOICE indexes, and out-of-bound PER lengths. Runtime tests should verify that the main helper sees decoded option bits and counts exactly as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_helper.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_helper.c

## Purpose
This file implements the core conntrack helper registry and helper lifecycle. Helpers are protocol-specific packet inspectors that can attach private helper extensions to conntracks, create expectations for related flows, and optionally coordinate with NAT helper modules. This file provides lookup, module reference handling, helper assignment, registration/unregistration, expectation callback registration, and helper extension allocation.

## Important APIs, Types, And Functions
Global registry state is `nf_ct_helper_hash`, `nf_ct_helper_hsize`, `nf_ct_helper_count`, guarded by `nf_ct_helper_mutex` for registration changes and RCU for readers. NAT helper modules are tracked in `nf_ct_nat_helpers` under `nf_ct_nat_helpers_mutex`. Important exported APIs include `__nf_conntrack_helper_find()`, `nf_conntrack_helper_try_module_get()`, `nf_conntrack_helper_put()`, `nf_nat_helper_try_module_get()`, `nf_nat_helper_put()`, `nf_ct_helper_ext_add()`, `__nf_ct_try_assign_helper()`, `nf_ct_helper_destroy()`, `nf_ct_helper_expectfn_register()`, `nf_ct_helper_expectfn_unregister()`, `nf_ct_helper_expectfn_find_by_name()`, `nf_ct_helper_expectfn_find_by_symbol()`, `nf_ct_helper_log()`, `nf_conntrack_helper_register()`, `nf_conntrack_helper_unregister()`, `nf_ct_helper_init()`, bulk register/unregister helpers, NAT helper register/unregister, and init/fini.

## Control Flow
Helper lookup scans the hash table under RCU, matching helper name, optional L3 family, and L4 protocol. `nf_conntrack_helper_try_module_get()` can request `nfct-helper-%s`, then takes both a module reference and a helper refcount. NAT lookup uses the helper's `nat_mod_name` and can request the NAT helper module before taking its module reference.

Assignment is template-driven in `__nf_ct_try_assign_helper()`: if a template conntrack has a helper, the real conntrack gets `IPS_HELPER_BIT`, a helper extension if needed, and an RCU pointer to that helper. Existing helper extensions may only be reused for helpers with the same help callback shape. Unregistration removes the helper from the hash, waits for RCU readers, destroys expectations referencing the helper, and unhelps live conntracks via `nf_ct_iterate_destroy()`.

## State And Persistence
Registry state is in memory only and initialized by `nf_conntrack_helper_init()`, which allocates the helper hash table. Each helper carries a refcount and module reference while in use. Per-connection state lives in `struct nf_conn_help`, added as a conntrack extension and initialized with an expectations hlist. Expectation callback registrations are also in-memory RCU list entries.

## Dependencies And Integration Points
This file integrates with conntrack extensions, expectations, event cache, sequence adjustment, netfilter logging, module loading, and conntrack table iteration. Protocol helper modules use `nf_ct_helper_init()` plus register APIs; nftables/ct target paths use helper lookup and assignment; NAT helper modules register by `nf_conntrack_nat_helper` and are loaded by name.

## Risks
The main risks are concurrency and lifecycle ordering. Registration uniqueness prevents helper hash ambiguity for automatic assignment; weakening it can produce unpredictable helper selection. Unregistration must remove expectations and clear helper pointers after RCU grace periods to avoid use-after-free. Refcount/module reference error paths must stay paired. Helper reassignment is intentionally constrained because helper extension private data cannot be resized for a different helper type.

## Test Signals
Tests should cover duplicate helper registration rejection, named lookup with wildcard and specific L3 families, module autoload success/failure, helper assignment from templates, clearing helpers on unregister, expectation removal on helper unregister, NAT helper autoload, `nf_ct_helper_log()` formatting from a helper callback, and bulk registration rollback when one helper in an array fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_irc.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_irc.c

## Purpose
This module implements the IRC DCC conntrack helper. It inspects client-to-server IRC TCP payloads for `PRIVMSG ... :\001DCC ...` commands, validates the advertised IPv4 address and port, and creates TCP expectations so DCC data/chat connections can be classified as related to the IRC control connection. It also exposes `nf_nat_irc_hook` for the NAT companion to rewrite embedded DCC address text.

## Important APIs, Types, And Functions
Module parameters are `ports[]`, `max_dcc_channels`, and `dcc_timeout`. The registered helper array is `irc[MAX_PORTS]`, initialized by `nf_ct_helper_init()` for each configured server port. `irc_exp_policy` carries the per-master maximum and timeout. `parse_dcc()` extracts the numeric IPv4 address and port from a DCC command and returns pointers to the embedded address text. `help()` is the packet inspection callback.

## Control Flow
The helper ignores reply-direction packets, non-established connections, packets without a full TCP header, and packets with no payload. It copies at most `MAX_SEARCH_SIZE` bytes into a global `irc_buffer` under `irc_buffer_lock`, skips leading whitespace, optionally verifies `PRIVMSG `, then scans for the CTCP marker `" :\001DCC "`. It matches known DCC verbs (`SEND`, `CHAT`, `MOVE`, `TSEND`, `SCHAT`), parses address and port, and validates that the advertised address is either the original source address or the NAT-visible reply destination address. Forged or zero-port DCC commands are rate-limited warnings and ignored.

For valid DCC commands, it allocates an expectation on the reply-side destination address and advertised TCP port. If NAT is active and `nf_nat_irc_hook` is registered, NAT handles payload rewrite and expectation setup; otherwise `nf_ct_expect_related()` installs the expectation directly. Allocation or expectation insertion failures drop the packet with helper logging.

## State And Persistence
State is in memory: module parameters, the helper array, expectation policy, exported NAT hook pointer, and `irc_buffer`. Per-flow persistence is in conntrack expectations until timeout or use. The helper does not keep protocol state across packets, so DCC commands split across TCP segments can be missed.

## Dependencies And Integration Points
The module depends on IPv4 TCP conntrack helpers, expectations, helper registration, and optional NAT IRC support through `nf_nat_irc_hook`. It registers aliases for legacy `ip_conntrack_irc` and helper autoload name `irc`.

## Risks
The scanner is intentionally simple and bounded, but it can miss DCC commands beyond the first 4095 payload bytes or across segment boundaries. It is IPv4-specific because DCC address parsing uses decimal IPv4. The global buffer serializes parsing with a spinlock. The address validation is critical; without it, arbitrary DCC expectations could be injected.

## Test Signals
Tests should cover default port registration, multiple configured ports, invalid `max_dcc_channels`, normal DCC SEND/CHAT parsing, leading whitespace, forged address rejection, zero-port rejection, NAT hook invocation offsets, expectation timeout/max limits, no inspection on server-to-client packets, and segmented or oversized payload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_irc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_labels.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_labels.c

## Purpose
This file implements conntrack label bit replacement and per-network label-user accounting. Labels are stored in the conntrack extension area and exposed to netfilter users for classification. The code provides atomic masked replacement, event notification when labels change, and simple reference accounting to know whether label extensions are in use for a network namespace.

## Important APIs, Types, And Functions
`replace_u32()` is the internal cmpxchg loop for one 32-bit word. `nf_connlabels_replace()` is the exported label update API; it applies `data` under an optional mask to the label bitset and emits `IPCT_LABEL` through `nf_conntrack_event_cache()` if any word changes. `nf_connlabels_get()` validates the requested bit index and increments `net->ct.labels_used`. `nf_connlabels_put()` decrements that counter.

## Control Flow
`nf_connlabels_replace()` first looks up `struct nf_conn_labels` with `nf_ct_labels_find(ct)`. If the extension is absent, it returns `-ENOSPC`. It clamps the caller's word count to the extension size, applies each word with `replace_u32()`, and then pads remaining words by clearing them with another `replace_u32()` pass. If any update changed bits, it queues a conntrack label event. The mask semantics are inverted for the helper: `replace_u32(address, mask ? ~mask[i] : 0, data[i])` preserves masked-out bits and toggles in the new value according to the implementation's XOR-style composition.

## State And Persistence
Label state lives in each conntrack's label extension and lasts for the conntrack lifetime. The namespace-level `labels_used` atomic tracks active label users but is not persisted. No disk state exists.

## Dependencies And Integration Points
The file depends on `nf_conntrack_labels.h` for extension lookup and maximum size, and on conntrack ecache for `IPCT_LABEL` notifications. Netlink conntrack code calls `nf_connlabels_replace()` when handling `CTA_LABELS` and `CTA_LABELS_MASK`.

## Risks
Concurrency correctness depends on the cmpxchg loop because labels may be updated without taking the conntrack lock. Mask interpretation is subtle and must match userspace API expectations. Missing label extensions return `-ENOSPC`, so callers must ensure extensions are enabled/attached before updating. Bit range validation in `nf_connlabels_get()` protects the fixed extension size.

## Test Signals
Tests should cover unmasked replacement, masked replacement preserving other bits, no event when data is unchanged, event on change, truncation when `words32` exceeds extension size, padding behavior for shorter writes, absent-extension `-ENOSPC`, out-of-range `nf_connlabels_get()` returning `-ERANGE`, and balanced get/put accounting warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_labels.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netbios_ns.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netbios_ns.c

## Purpose
This small helper tracks locally originating NetBIOS name service broadcast requests on UDP port 137. It uses the generic broadcast helper to create a short-lived expectation for replies from the destination network, allowing broadcast name service responses to be related to the originating conntrack.

## Important APIs, Types, And Functions
The module parameter is `timeout`, defaulting to 3 seconds. `exp_policy` allows one expected reply. `netbios_ns_help()` delegates all packet-specific behavior to `nf_conntrack_broadcast_help(skb, ct, ctinfo, timeout)`. The single registered `helper` is named `netbios-ns`, IPv4-only, UDP, source port 137, and uses `exp_policy`.

## Control Flow
On module init, `nf_conntrack_netbios_ns_init()` sets `exp_policy.timeout` from the module parameter and registers the helper. When a matching packet invokes the helper, the generic broadcast helper handles direction checks, expectation creation, and timeout behavior. Module exit unregisters the helper.

## State And Persistence
The only module state is the timeout parameter, expectation policy, and helper registration. Runtime state is in conntrack expectations and expires quickly. There is no persistent storage.

## Dependencies And Integration Points
The file depends on core conntrack, helper registration, expectations, and `nf_conntrack_broadcast_help()`. It is IPv4-specific and registers legacy/helper aliases for autoload.

## Risks
The helper trusts the generic broadcast helper for safety. The short timeout limits exposure, but overly broad broadcast expectations can still admit unexpected replies during the window. Timeout changes are read-only after module load because the parameter is mode `0400`.

## Test Signals
Tests should verify helper registration on UDP/IPv4 port 137, correct timeout propagation to `exp_policy`, expectation creation for local broadcast queries, expiry after the configured timeout, no IPv6 registration, unload cleanup, and behavior with timeout values at low/high extremes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netbios_ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netlink.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netlink.c

## Purpose
This file implements the nfnetlink userspace API for listing, creating, modifying, deleting, and receiving events for conntrack entries and expectations. It is the kernel side of ctnetlink: it serializes conntrack state into netlink attributes, parses userspace requests back into tuples and mutable fields, exposes per-CPU/global stats, bridges conntrack metadata into nfqueue glue when enabled, and registers per-netns event notifiers.

## Important APIs, Types, And Functions
The main callback tables are `ctnl_cb[]` for `NFNL_SUBSYS_CTNETLINK` and `ctnl_exp_cb[]` for `NFNL_SUBSYS_CTNETLINK_EXP`. The module registers `ctnl_subsys`, `ctnl_exp_subsys`, and `ctnetlink_net_ops`. Serialization is centered on `ctnetlink_fill_info()`, tuple dump helpers, extension dump helpers for accounting/timestamps/helper/labels/seqadj/synproxy, and expectation dump helpers such as `ctnetlink_exp_fill_info()`.

Parsing uses netlink policies `ct_nla_policy`, `tuple_nla_policy`, `proto_nla_policy`, `help_nla_policy`, `exp_nla_policy`, and optional NAT/seqadj/synproxy policies. Request handlers include `ctnetlink_get_conntrack()`, `ctnetlink_new_conntrack()`, `ctnetlink_del_conntrack()`, stats handlers, `ctnetlink_get_expect()`, `ctnetlink_new_expect()`, and `ctnetlink_del_expect()`. Event delivery uses `ctnetlink_conntrack_event()` and `ctnetlink_expect_event()`.

## Control Flow
Dumping a conntrack walks the hash table under bucket locks in `ctnetlink_dump_table()`, skips expired/nonmatching/non-original-direction entries, applies optional family/zone/mark/status/tuple filters, and emits netlink messages through `ctnetlink_fill_info()`. Single-entry get/delete parses an original or reply tuple plus zone and uses `nf_conntrack_find_get()`. Delete without a tuple flushes entries through `nf_ct_iterate_cleanup_net()` with the same filter machinery.

Creating a conntrack requires original and reply tuples, matching L4 protocol, and `CTA_TIMEOUT`. `ctnetlink_create_conntrack()` allocates the entry, optionally attaches helper/NAT/acct/timestamp/ecache/labels/seqadj/synproxy extensions, sets confirmed status and timeout, applies status/protoinfo/seqadj/synproxy/mark, optionally links a master conntrack, inserts into the hash, and reports events. Existing entries are modified by `ctnetlink_change_conntrack()`, which intentionally disallows NAT and master changes after creation.

Expectation control mirrors conntrack control. `ctnetlink_new_expect()` parses tuple, mask, master, zone, class, flags, optional NAT, helper assignment, and optional expectfn. It requires a helper-bearing master because expectations are helper-scoped. Dumps can list all expectations or only those attached to a master conntrack. Deletes can remove one expectation by tuple/id, all expectations for a helper name, or all expectations.

## State And Persistence
No disk state is used. Persistent runtime state is the conntrack table, expectation table, per-net event notifier registration, per-CPU stats, timers, labels, timestamps, helper extensions, and optional NAT/seqadj/synproxy extensions. Netlink dump cursors persist only in `netlink_callback` args/context during a multipart dump.

## Dependencies And Integration Points
This file is deeply integrated with conntrack core, expectations, helpers, L4 protocol plugins, accounting, zones, timestamps, labels, synproxy, NAT, security secctx, nfnetlink, module autoloading, per-netns registration, and optional `CONFIG_NETFILTER_NETLINK_GLUE_CT` for nfqueue metadata build/parse/expect attach/seq-adjust hooks.

## Risks
The risk profile is high because this is a privileged mutation API over shared conntrack state. Attribute validation must reject incomplete tuples, unsupported zones, impossible masks, invalid status masks, missing protocol numbers for protocol-specific filters, invalid label masks, and invalid expectation classes. Dump code must handle hash resize, expired entries, and skb space exhaustion without skipping or looping forever. Creation order matters: extensions must be attached before confirmation/insertion, helper and NAT autoload paths must handle `-EAGAIN`, and master references must be dropped on insertion failure. Event allocation failures are reported as netlink buffer pressure rather than crashing.

## Test Signals
Tests should cover multipart dump resume with filters, filtered flush, tuple get/delete by original and reply directions, zones and tuple zones, mark/status masks, create/update/delete conntracks, required timeout enforcement, helper attach and helper-private netlink data, NAT setup autoload failures, label attach with mask length validation, sequence-adjust and synproxy updates, event delivery for new/update/destroy/related, dying-list dump, stats dumps, expectation create/update/delete/dump with id checks, helper-name expectation flush, and nfqueue glue build/parse when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netlink.c -->
