# subset-b-006253 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_synproxy.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_synproxy.c

Purpose: implements the nftables `synproxy` expression and `NFT_OBJECT_SYNPROXY` object, allowing rules to terminate client SYNs, validate SYN cookies, and only let validated TCP handshakes proceed.

Important APIs/types/functions: `struct nft_synproxy` stores `nf_synproxy_info`; `nft_synproxy_do_init()` parses MSS, window scale, and option flags and enables conntrack plus IPv4/IPv6 synproxy hooks; `nft_synproxy_do_eval()` verifies TCP checksums, parses options, dispatches to v4/v6 handlers, and sets verdicts; `nft_synproxy_obj_update()` uses `WRITE_ONCE()` for object updates.

Control flow: init validates netlink attributes, obtains `nf_ct_netns_get()`, initializes per-net synproxy support for the rule family, then eval checks TCP protocol/checksum/options. SYN packets cause `synproxy_send_client_synack*()`, ACK packets call `synproxy_recv_client_ack*()`, and accepted synthetic handling consumes the skb with `NF_STOLEN`.

State and persistence: rule/object state is the synproxy option struct; per-net synproxy and conntrack references persist while the expression/object exists; stats are incremented in `synproxy_net`. Dependencies/integration include nf_tables expression/object registration, conntrack, synproxy core, TCP option parsing, and IPv4/IPv6 hook validation for LOCAL_IN/FORWARD. Risks: reference symmetry on mixed `NFPROTO_INET`, packet ownership after `consume_skb()`, checksum parsing on malformed TCP, and atomic visibility of object updates. Test signals: netlink init/dump round trips, IPv4/IPv6/inet family creation/destruction, SYN and ACK verdict paths, invalid flags, unsupported families, and module unload after active objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_synproxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_tproxy.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_tproxy.c

Purpose: provides the nftables `tproxy` expression for transparent proxy socket assignment in prerouting, optionally redirecting to address and/or port values loaded from nft registers.

Important APIs/types/functions: `struct nft_tproxy` records source registers and family; `nft_tproxy_eval_v4()` and `_v6()` perform established/listener lookups; `nft_tproxy_init()` validates family/register sizes and enables defragmentation; `nft_tproxy_destroy()` disables defrag; `nft_tproxy_validate()` restricts use to PRE_ROUTING.

Control flow: eval gates to TCP/UDP non-fragment packets, reads transport headers, searches for an existing socket, computes local target address/port, handles TCP TIME_WAIT reopening, then assigns transparent sockets through `nf_tproxy_assign_sock()` or breaks the nft rule path.

State and persistence: expression state is only register selectors and family; defrag enablement is a per-net side effect held for expression lifetime. Dependencies/integration include nf_tables registers, nf_tproxy IPv4/IPv6 socket lookup helpers, transparent socket policy, and nf_defrag modules. Risks: register length/family mismatch, stale defrag reference accounting after init failures, socket reference ownership because assignment consumes references, and fragment handling differences between nft and xt TPROXY. Test signals: IPv4, IPv6, and inet family rules; address-only/port-only validation; UDP/TCP listener lookup; TIME_WAIT reopening; non-transparent sockets causing `NFT_BREAK`; and defrag enable/disable balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_tproxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_tunnel.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_tunnel.c

Purpose: implements nftables tunnel metadata support: a netdev-family `tunnel` expression for reading path/id metadata and a `NFT_OBJECT_TUNNEL` object for attaching transmit tunnel metadata to packets.

Important APIs/types/functions: `struct nft_tunnel` describes read key/dreg/mode; `struct nft_tunnel_obj` stores `metadata_dst` plus parsed options; init helpers parse IPv4, IPv6, VXLAN, ERSPAN, and GENEVE nested attributes; `nft_tunnel_obj_eval()` installs the metadata dst on the skb; dump helpers serialize all key fields and options.

Control flow: get-expression init validates key and destination register length; eval reads `skb_tunnel_info()` and stores path bool or tunnel id only if mode matches RX/TX. Object init constructs `ip_tunnel_info`, requires an id and IP/IP6 destination, applies ports/flags/TOS/TTL/options, allocates `metadata_dst`, optionally initializes dst cache, and sets tunnel options.

State and persistence: object state persists as metadata dst and option bytes until object destroy frees it; expression state is register metadata only. Dependencies/integration include nf_tables netdev family, dst metadata, ip_tunnels, vxlan/erspan/geneve option formats, and netlink nested policies. Risks: option length and type exclusivity, GENEVE multi-option bounds, dst cache initialization failure cleanup, unconditional dump of optional ports/options, and mode semantics for RX/TX metadata. Test signals: read path/id with no metadata and wrong mode, object creation for IPv4/IPv6, each option family, invalid mixed options, dump/init round trips, and skb dst replacement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_xfrm.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_xfrm.c

Purpose: implements the nftables `xfrm` expression, extracting IPSec/XFRM state fields such as reqid, SPI, source address, and destination address into nft registers.

Important APIs/types/functions: `struct nft_xfrm` stores key, output register, direction, secpath number, and value length; `nft_xfrm_get_init()` validates netlink attributes and register size; `nft_xfrm_state_get_key()` copies selected state data; `_eval_in()` reads `skb_sec_path()`, while `_eval_out()` walks `xfrm_dst` chain.

Control flow: init restricts families to IPv4/IPv6/inet, maps key to data length, validates IN/OUT direction and `XFRM_MAX_DEPTH`, then registers a store. Eval chooses inbound secpath or outbound dst chain, selects the requested transform index, verifies address-family/mode compatibility for address keys, and stores data or breaks.

State and persistence: expression state is immutable rule metadata; no per-net references are held. Dependencies/integration include nf_tables, XFRM state/dst structures, secpath, and hook validation. Risks: address keys are valid only for BEET/TUNNEL/IPTFS with matching family; outbound traversal can miss absent dst/xfrm chains; register sizes must match IPv4/IPv6 fields; hook validation must reflect direction. Test signals: inbound/outbound policies, multiple `spnum` depths, reqid/SPI/address keys, unsupported families and directions, transport-mode address breaks, and netlink dump parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_xfrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/utils.c -->
# sources/distributed-fs/ceph-client/net/netfilter/utils.c

Purpose: supplies shared netfilter helpers for checksum validation, route lookup dispatch, and IPv6 hop-by-hop length checking.

Important APIs/types/functions: exports `nf_ip_checksum()`, `nf_ip6_checksum()`, `nf_checksum()`, `nf_checksum_partial()`, `nf_route()`, and `nf_ip6_check_hbh_len()`. Private partial helpers handle header-limited checksum validation.

Control flow: checksum helpers honor `CHECKSUM_COMPLETE` fast paths for PREROUTING/LOCAL_IN, construct pseudo-header checksums for TCP/UDP, and call skb checksum completion helpers. `nf_route()` dispatches to IPv4 or IPv6 route helpers. Hop-by-hop parsing pulls enough bytes, iterates TLVs, validates jumbo payload option shape/alignment, and returns errors on malformed lengths.

State and persistence: no persistent state; functions mutate skb checksum metadata and may update jumbo payload output length. Dependencies/integration include IPv4/IPv6 headers, skb checksum APIs, route helpers, and netfilter queue users. Risks: checksum metadata mutation affects later consumers, partial checksum pseudo-header length is subtle, and hop-by-hop parsing must avoid short-pull and malformed TLV overrun. Test signals: CHECKSUM_COMPLETE and CHECKSUM_NONE packets, non-TCP/UDP protocols, partial length checks, IPv4/IPv6 route dispatch, valid jumbo option, invalid TLV length/alignment, and too-short skb pulls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/x_tables.c -->
# sources/distributed-fs/ceph-client/net/netfilter/x_tables.c

Purpose: core backend for legacy x_tables users (`iptables`, `ip6tables`, `arptables`, and bridge variants), managing match/target registration, table lifetime, validation, replacement, compat layout, proc exposure, per-net storage, and exported helper APIs used by many xt modules.

Important APIs/types/functions: `xt_register_target(s)`, `xt_register_match(es)`, `xt_find_match()`, `xt_request_find_target()`, `xt_check_match()`, `xt_check_target()`, `xt_check_entry_offsets()`, `xt_alloc_table_info()`, `xt_replace_table()`, `xt_register_table()`, `xt_unregister_table_pre_exit()`, `xt_unregister_table_exit()`, `xt_hook_ops_alloc()`, `xt_register_template()`, `xt_proto_init()`, and compat/counter helpers. Key state types are `xt_af`, `xt_pernet`, `xt_template`, `xt_table_info`, and per-cpu `xt_recseq`.

Control flow: modules register match/target descriptors into per-family lists; rule load paths resolve modules, validate sizes, table/proto/hook constraints and entry offsets, call extension checks, and install table info. Table replacement allocates jumpstacks, swaps `table->private` under bottom-half exclusion with memory barriers, waits for in-flight readers via per-cpu sequence counts, then returns old table info for cleanup. Table registration duplicates metadata/hooks, publishes netfilter hooks, audits, and links the table into the namespace. Namespace teardown first moves tables to dead lists and unregisters hooks, then finalizes after family-specific cleanup.

State and persistence: global per-family lists hold registered matches, targets, and templates; per-net lists hold live/dead tables; compat offset tables are temporary under compat mutex; proc entries expose table/match/target names; static key `xt_tee_enabled` and per-cpu recursion sequence counters are exported. Dependencies/integration include module autoloading, procfs, audit, net namespaces, netfilter hook registration, user-copy, RCU/synchronization, and legacy compat ABI. Risks: user-supplied offsets and sizes, memory ordering during replacement, module ref leaks, compat delta overflow, dead-table teardown ordering, proc traversal mutex handoff, and large allocation caps. Test signals: module autoload success/failure, invalid match/target sizes, hook/proto/table mismatch, malformed jump offsets/verdicts, compat 32-bit translation, concurrent replacement under packet load, namespace exit, proc list reads, and table template lazy instantiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/x_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_AUDIT.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_AUDIT.c

Purpose: xtables target that emits audit records for packets and then continues traversal; supports IPv4, IPv6, bridge, and ARP aliases.

Important APIs/types/functions: `audit_tg()` creates `AUDIT_NETFILTER_PKT` records with skb mark and `audit_log_nf_skb()` details; `audit_tg_ebt()` adapts verdict to ebtables; `audit_tg_check()` validates `xt_audit_info.type`.

Control flow: target checks `audit_enabled`, allocates an atomic audit buffer, records packet fields, ends the audit log, and returns `XT_CONTINUE` or `EBT_CONTINUE`. Init registers two target descriptors, one generic and one bridge-specific.

State and persistence: no target-private persistent state beyond rule info; audit subsystem owns logs. Dependencies/integration include Linux audit, x_tables, bridge ebtables verdict constants, and skb family helpers. Risks: audit allocation failure silently continues, audit type is validated but not otherwise used by target body, and bridge verdict must differ from normal xt verdict. Test signals: disabled audit, allocation failure tolerance, type range validation, IPv4/IPv6/bridge/ARP registration aliases, and rule traversal continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_AUDIT.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CHECKSUM.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_CHECKSUM.c

Purpose: `CHECKSUM` target for filling partial checksums, mainly for mangle OUTPUT scenarios such as DHCP/UDP packets produced with partial checksum state.

Important APIs/types/functions: `checksum_tg()` calls `skb_checksum_help()` when `skb->ip_summed == CHECKSUM_PARTIAL` and skb is not GSO; `checksum_tg_check()` validates `XT_CHECKSUM_OP_FILL` and warns for non-UDP/non-OUTPUT-like usage.

Control flow: rule load rejects unsupported operations and empty operation masks. Runtime leaves GSO packets alone, completes eligible software checksums, and continues traversal.

State and persistence: no persistent state; mutates skb checksum data. Dependencies/integration include x_tables, IPv4/IPv6 iptables entry protocol metadata, and skb checksum helpers. Risks: broad use can hide checksum offload expectations, non-UDP use is only warned not rejected, and checksum helper failures are ignored because target always continues. Test signals: operation validation, UDP-restricted rules, CHECKSUM_PARTIAL non-GSO conversion, GSO no-op, IPv4/IPv6 registration, and warning behavior for broad rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CHECKSUM.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CLASSIFY.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_CLASSIFY.c

Purpose: `CLASSIFY` target sets `skb->priority` so qdiscs can classify matching packets.

Important APIs/types/functions: `classify_tg()` copies `xt_classify_target_info.priority` to the skb; registration covers IPv4, IPv6, and ARP with hook masks suited to output/forward/postrouting paths.

Control flow: runtime is a single field assignment followed by `XT_CONTINUE`. Module init/uninit registers or unregisters all supported targets.

State and persistence: no state outside rule info; the skb priority persists for downstream qdisc and networking decisions. Dependencies/integration include x_tables, mangle-like hooks, ARP support, and traffic-control classifiers. Risks: incorrect hook placement could set priority too early/late, priority overwrites previous classifiers, and ARP support has a different hook namespace. Test signals: priority value applied for IPv4/IPv6/ARP, hook mask enforcement by x_tables core, and continued traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CLASSIFY.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CONNSECMARK.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_CONNSECMARK.c

Purpose: target copies security marks between packets and conntrack entries, enabling SECMARK labels to persist across a connection.

Important APIs/types/functions: `secmark_save()` copies `skb->secmark` to `ct->secmark` and emits `IPCT_SECMARK`; `secmark_restore()` restores from conntrack to skb; `connsecmark_tg_check()` validates mode/table and obtains conntrack namespace support; destroy releases it.

Control flow: load accepts only mangle/security tables and SAVE/RESTORE modes. Runtime chooses mode, gets the associated conntrack entry, conditionally copies one direction, and continues traversal.

State and persistence: persistent state is in conntrack `secmark`; rule lifetime holds a conntrack netns reference. Dependencies/integration include nf_conntrack, conntrack event cache, x_tables, and LSM/security mark users. Risks: missing conntrack silently means no copy, SAVE refuses to overwrite existing connection secmark, RESTORE refuses to overwrite packet secmark, and netns references must balance on every loaded rule. Test signals: save and restore paths with/without conntrack, event emission on save, invalid modes/tables, IPv4/IPv6 rule lifetime, and destroy reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CONNSECMARK.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CT.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_CT.c

Purpose: implements `CT` and `NOTRACK` raw-table targets for attaching conntrack templates, helper/timeout/event/zone metadata, or marking packets untracked before normal conntrack.

Important APIs/types/functions: `xt_ct_target()` attaches a template or untracked marker; `xt_ct_tg_check()` allocates `nf_conn` templates and optional helper/ecache/timeout extensions; revision wrappers validate feature masks; destroy releases helper, timeout, conntrack, and netns references.

Control flow: check rejects invalid flags, obtains conntrack support unless NOTRACK, builds zone from id/direction/mark flags, allocates a template, attaches optional event cache, helper, and timeout, marks it confirmed, and stores the kernel pointer outside usersize. Runtime skips already-seen skbs, increments template refcount, and sets `_nfct`; NOTRACK sets `IP_CT_UNTRACKED`.

State and persistence: per-rule private `ct` template persists until rule destroy; helper modules and timeout policies may be pinned; conntrack netns refs persist per rule. Dependencies/integration include raw table, nf_conntrack templates/zones/helpers/timeouts/ecache, and queue dropping on helper/timeout removal. Risks: helper selection requires non-inverted L4 proto, cleanup unwinds several partially initialized resources, zone support is config dependent, and destroy drops queued hooks when helper/timeout state disappears. Test signals: revisions 0/1/2, NOTRACK, helper and timeout names including unterminated strings, zone direction/mark flags, existing `_nfct` skip, and cleanup after failed init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_CT.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_DSCP.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_DSCP.c

Purpose: mangle-table target for modifying IPv4/IPv6 DSCP and TOS/traffic-class fields while preserving or applying masks as requested.

Important APIs/types/functions: `dscp_tg()` and `dscp_tg6()` set DSCP preserving ECN bits; `tos_tg()` and `tos_tg6()` apply mask/xor semantics; `dscp_tg_check()` bounds DSCP to `XT_DSCP_MAX`.

Control flow: runtime reads current DS field, exits if unchanged, makes the IP header writable, updates IPv4 or IPv6 field, and continues or drops on write failure. Module registers DSCP and TOS revision targets for both families.

State and persistence: no persistent state; packet header changes persist through the stack. Dependencies/integration include x_tables, mangle table, IPv4/IPv6 DS field helpers, and skb writability checks. Risks: skb write failures drop packets, IPv6 TOS path ensures only `sizeof(struct iphdr)` bytes despite touching IPv6 header, and ECN preservation differs between DSCP and TOS modes. Test signals: DSCP bounds, unchanged fast path, IPv4 checksum update via helper, IPv6 traffic class update, skb clone write failure, and TOS mask/xor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_DSCP.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_HL.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_HL.c

Purpose: mangle-table target for changing IPv4 TTL and IPv6 hop-limit values by set, increment, or decrement operations.

Important APIs/types/functions: `ttl_tg()` adjusts IPv4 TTL and checksum via `csum_replace2()`; `hl_tg6()` adjusts IPv6 hop limit; check functions validate mode and nonzero increment/decrement operands.

Control flow: target makes the network header writable, calculates a saturated new TTL/hop limit according to mode, updates the field, and continues or drops on write failure. Registration exposes `TTL` for IPv4 and `HL` for IPv6.

State and persistence: no persistent state; header mutation affects subsequent routing and forwarding. Dependencies/integration include x_tables, mangle table, IPv4 checksum helpers, IPv6 header handling. Risks: decrement can force zero TTL/hop-limit, affecting later drop behavior; invalid mode defaults are guarded by checkentry; checksum update is IPv4-only by design. Test signals: set/inc/dec boundaries at 0 and 255, invalid zero operand for inc/dec, writable failure, IPv4 checksum delta, and IPv6 no-checksum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_HL.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_HMARK.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_HMARK.c

Purpose: `HMARK` target computes a deterministic hash from packet or conntrack tuple fields and writes the result to `skb->mark`, useful for load distribution and policy routing.

Important APIs/types/functions: `struct hmark_tuple`, `hmark_ct_set_htuple()`, IPv4/IPv6 packet tuple builders, `hmark_swap_ports()`, `hmark_hash()`, and `hmark_tg_check()`. It supports L3-only, conntrack-derived, port/SPI masks, modulus, and offset.

Control flow: runtime zeroes a tuple, populates it from conntrack original/reply tuples or packet headers, handles ICMP/ICMPv6 inner headers and fragments, normalizes address/port ordering, hashes with jhash and reciprocal scaling, then assigns `skb->mark`.

State and persistence: no module state; mark persists on skb and may drive later rules/routes. Dependencies/integration include optional conntrack, IPv4/IPv6 parsing, jhash, ICMP error parsing, and xt target registration. Risks: no conntrack or parse failure leaves packet unchanged, fragments omit ports, endian-independent hash must remain stable across architectures, and invalid flag combinations must be rejected. Test signals: IPv4/IPv6 packet hashing, conntrack hashing, ICMP error inner-header use, fragments, L3-only mode, modulus zero rejection, and incompatible SPI/port flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_HMARK.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_IDLETIMER.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_IDLETIMER.c

Purpose: `IDLETIMER` target creates named timers exposed under a sysfs device; matching packets reset the timer, and expiry notifies userspace.

Important APIs/types/functions: `struct idletimer_tg` tracks list entry, alarm/timer, work, sysfs attribute, refcount, and timer type; create/check/destroy helpers manage v0 jiffies timers and v1 alarm timers; target functions reset the timer/alarm on packet match.

Control flow: module init creates class/device and registers targets. Checkentry validates timeout/label/sysfs name, reuses existing timers by label with refcounting, or creates sysfs attributes and starts the timer. Runtime resets expiration. Expiry schedules work that calls `sysfs_notify()`. Destroy decrements refcount, removes list/sysfs entry, cancels timer/alarm/work, and frees memory.

State and persistence: global list of named timers, sysfs files, class/device, timers/alarms, and work items persist while rules exist. Dependencies/integration include x_tables, sysfs/kobject, timers, alarmtimer, workqueue, and `xt_check_proc_name()`. Risks: label collisions with different timer types, timer/work teardown races, sysfs reserved names, reference counting across multiple rules, and unsupported `send_nl_msg`. Test signals: v0/v1 creation, shared label refcounts, alarm and normal timers, sysfs read remaining time, expiry notification, invalid labels/timeouts/types, and module unload after active timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_IDLETIMER.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_LED.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_LED.c

Purpose: `LED` target triggers named LED subsystem triggers when packets match, with optional delay and always-blink behavior.

Important APIs/types/functions: `struct xt_led_info_internal` holds list node, refcount, trigger id, `led_trigger`, and timer; `led_tg_check()` creates or reuses triggers; `led_tg()` signals/blinks LEDs; `led_tg_destroy()` tears down when refcount reaches zero.

Control flow: check validates NUL-terminated id, locks the global trigger list, increments existing trigger refcount or allocates/registers a new trigger and timer, then stores the private pointer. Runtime emits LED_FULL, blink one-shot, or LED_OFF depending on delay policy. Destroy removes the trigger, shuts down timer, unregisters LED trigger, and frees memory.

State and persistence: global trigger list and LED triggers persist across rules sharing the same id; timer state persists until destroy. Dependencies/integration include x_tables, LED trigger core, timers, mutexes, and usersize-hidden kernel pointers. Risks: duplicate trigger names, timer callback after unregister, refcount correctness with shared rules, id validation, and semantic differences between negative/zero/positive delays. Test signals: shared id refcounts, always-blink with pending timer, zero delay immediate off, negative delay stay-on, invalid id, unregister cleanup, and IPv4/IPv6 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_LED.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_LOG.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_LOG.c

Purpose: `LOG` target logs IPv4/IPv6 packets through the nf_log infrastructure and continues traversal.

Important APIs/types/functions: `log_tg()` fills `nf_loginfo` and calls `nf_log_packet()` with the rule prefix; `log_tg_check()` validates family, level, prefix termination, and logger availability; destroy releases the logger.

Control flow: check attempts to get the syslog logger and, for non-nft compat callers, autoloads `nf_log_syslog` if needed. Runtime passes family/hook/in/out and log flags to nf_log. Module init registers family-specific targets.

State and persistence: per-rule logger reference is held while rule exists; no private data beyond user log info. Dependencies/integration include x_tables, nf_log, syslog logger soft dependency, and nft compat behavior. Risks: missing logger rejects rule load, prefix must be terminated, log volume can be high, and nft compat avoids request_module behavior. Test signals: level >= 8 rejection, unterminated prefix, logger autoload, IPv4/IPv6 log emission, destroy logger put, and traversal continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_LOG.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_MASQUERADE.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_MASQUERADE.c

Purpose: `MASQUERADE` NAT target performs automatic-source SNAT using the outgoing interface address for IPv4 and IPv6 postrouting.

Important APIs/types/functions: IPv4 `masquerade_tg()` converts legacy multi-range compat info to `nf_nat_range2`; IPv6 `masquerade_tg6()` passes range directly; check functions reject explicit mapped IPs and obtain conntrack; module init also registers masquerade netdevice/address notifiers.

Control flow: check validates one range for IPv4 or no MAP_IPS for IPv6 and pins conntrack. Runtime calls `nf_nat_masquerade_ipv4()` or `_ipv6()` using the output device. Module init registers xt targets then notifier support; failure unwinds target registration.

State and persistence: per-rule conntrack refs and global masquerade notifiers persist until unload; NAT mappings live in conntrack. Dependencies/integration include nat table POST_ROUTING, nf_nat_masquerade, conntrack, netdevice/address notifier cleanup. Risks: notifier registration ordering, conntrack ref symmetry, legacy IPv4 range translation, and no explicit address mapping allowed. Test signals: IPv4 range size validation, MAP_IPS rejection, IPv6 range validation, postrouting-only enforcement, notifier registration failure unwind, interface address change cleanup, and destroy netns put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_MASQUERADE.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_NETMAP.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_NETMAP.c

Purpose: `NETMAP` NAT target maps one subnet to another one-to-one by preserving host bits and replacing network bits.

Important APIs/types/functions: `netmap_tg4()` and `netmap_tg6()` compute netmask from min/max range, choose source or destination based on hook, create a single-address `nf_nat_range2`, and call `nf_nat_setup_info()`; check/destroy manage conntrack refs.

Control flow: check requires MAP_IPS and one IPv4 range, then obtains conntrack. Runtime gets conntrack, computes the translated address from packet source/destination and configured range, sets MAP_IPS, and applies NAT manipulation for the current hook.

State and persistence: NAT state is persisted in conntrack; rules hold conntrack netns refs. Dependencies/integration include nat table hooks, IPv4/IPv6 headers, nf_nat setup, conntrack, and hook-to-manip mapping. Risks: invalid ranges produce surprising masks, ct must be present, IPv6 target is always registered in this source, and hook direction decides whether source or destination is mapped. Test signals: DNAT hooks vs SNAT hooks, IPv4 and IPv6 subnet preservation, MAP_IPS/rangesize validation, conntrack absence handling through NAT core, and destroy ref release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_NETMAP.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_NFLOG.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_NFLOG.c

Purpose: `NFLOG` target sends packet log records to nfnetlink_log groups and continues traversal.

Important APIs/types/functions: `nflog_tg()` fills `NF_LOG_TYPE_ULOG` settings including copy length, group, threshold, and prefix; `nflog_tg_check()` validates flags/prefix and pins the ULOG logger; destroy releases it.

Control flow: check rejects unknown flags and unterminated prefixes, then finds or autoloads `nfnetlink_log` unless in nft compat mode. Runtime calls `nf_log_packet()` with ulog parameters.

State and persistence: per-rule nf_logger reference; userspace receives netlink log traffic. Dependencies/integration include x_tables, nf_log, nfnetlink_log, module autoloading, and IPv4/IPv6 registration. Risks: logger absence rejects rules, log copy length/threshold can affect performance, prefix validation is essential for user memory safety, and nft compat changes autoload path. Test signals: flag mask rejection, prefix termination, logger autoload, copy length flag behavior, group delivery, destroy logger put, and traversal continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_NFLOG.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_NFQUEUE.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_NFQUEUE.c

Purpose: `NFQUEUE` target returns queue verdicts to send packets to userspace netfilter queues, supporting queue ranges, hash fanout, bypass, and CPU fanout across revisions.

Important APIs/types/functions: revision targets `nfqueue_tg()`, `_v1()`, `_v2()`, `_v3()`; `nfqueue_tg_check()` validates queue counts, range maximum, and flag masks; global `jhash_initval` seeds hash fanout.

Control flow: check initializes hash random once, rejects zero queues and ranges above 65535, and validates revision-specific flags. Runtime selects queue number directly, by packet hash, or by CPU modulo total queues, then returns `NF_QUEUE_NR(queue)` with optional bypass flag.

State and persistence: only global hash seed; queueing state is owned by nf_queue/userspace. Dependencies/integration include x_tables, nf_queue verdict encoding, jhash fanout, SMP CPU id, and ARP/IP aliases. Risks: queue range overflow, per-CPU fanout distribution changes with CPU count, bypass semantics can accept packets when no userspace listener exists, and revision structs share checkentry casting. Test signals: revisions 0-3, zero/overflow queue counts, hash distribution stability, CPU fanout, bypass flag, ARP/IPv4/IPv6 usage, and userspace queue absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_NFQUEUE.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_RATEEST.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_RATEEST.c

Purpose: `RATEEST` target maintains named packet/byte rate estimators that other matches can reference.

Important APIs/types/functions: per-net `xt_rateest_net` hash table, exported `xt_rateest_lookup()` and `xt_rateest_put()`, `xt_rateest_tg_checkentry()` to create/reuse estimators, `xt_rateest_tg()` to update counters, and pernet init.

Control flow: check validates estimator name, seeds hash randomness, looks up existing estimator and validates matching parameters, or allocates one, initializes stats/lock/refcount, starts a generic estimator, inserts it into the per-net hash, and stores a hidden pointer. Runtime increments byte and packet counters under spinlock. Destroy decrements refcount, removes final estimator, kills estimator, and frees after RCU.

State and persistence: named estimators persist per net namespace while referenced; stats and estimator timers persist beyond individual packets. Dependencies/integration include gen_stats estimators, pernet generic storage, mutex/hash, spinlocks, RCU, and x_tables usersize hiding. Risks: parameter mismatch on shared names, estimator timer RCU lifetime, refcount underflow, name termination, and per-net cleanup with live refs. Test signals: shared estimator reuse, mismatched interval/ewma rejection, packet counter increments, lookup/put exports, namespace isolation, destroy last ref cleanup, and IPv4/IPv6 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_RATEEST.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_REDIRECT.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_REDIRECT.c

Purpose: `REDIRECT` NAT target redirects connections to the local host for IPv4 and IPv6 PREROUTING/LOCAL_OUT.

Important APIs/types/functions: `redirect_tg4()` translates legacy IPv4 range to `nf_nat_range2`; `redirect_tg6()` calls IPv6 redirect helper; check functions reject MAP_IPS and pin conntrack; destroy releases conntrack.

Control flow: check validates target range and obtains conntrack support. Runtime calls `nf_nat_redirect_ipv4()` or `_ipv6()` with hook number and port range settings, then returns NAT verdict. Registration restricts hooks to PREROUTING and LOCAL_OUT in nat table.

State and persistence: NAT binding state lives in conntrack; rules hold conntrack netns refs. Dependencies/integration include nf_nat_redirect, conntrack, nat table hooks, IPv4/IPv6 range ABIs. Risks: explicit MAP_IPS is invalid, IPv4 legacy range size must be one, hook restrictions are essential to avoid invalid local address selection, and conntrack refs must unwind. Test signals: IPv4/IPv6 redirect, port range preservation, MAP_IPS rejection, rangesize rejection, prerouting vs local-out behavior, and destroy netns put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_REDIRECT.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_SECMARK.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_SECMARK.c

Purpose: `SECMARK` target writes LSM security identifiers to `skb->secmark`, enabling packet labeling for SELinux and related security policies.

Important APIs/types/functions: global `mode`; `checkentry_lsm()` maps security context strings to secids, checks relabel permission, and increments secmark refcount; `secmark_tg_check()` validates table/mode; revision wrappers handle v0/v1 ABI; `secmark_tg()` writes secid to skb.

Control flow: check restricts use to mangle/security tables, prevents mixing modes, maps and authorizes the security context, then stores secid in the rule. Runtime writes `skb->secmark` and continues. Destroy decrements the security secmark refcount for SEL mode.

State and persistence: global mode persists while module loaded; per-rule secid is kernel-private in v1; LSM secmark refcount persists per rule. Dependencies/integration include x_tables, Linux security hooks, skb secmark, and LSM policy. Risks: global mode mixing, security context mapping failures, permission failures, refcount symmetry, and secctx termination. Test signals: valid/invalid contexts, relabel denied, mangle/security table enforcement, v0/v1 usersize handling, mode mixing rejection, skb secmark assignment, and destroy refcount decrement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_SECMARK.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TCPMSS.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_TCPMSS.c

Purpose: `TCPMSS` target adjusts or inserts TCP MSS options, commonly clamping SYN packets to path MTU.

Important APIs/types/functions: `tcpmss_mangle_packet()` parses TCP options, lowers existing MSS, optionally inserts an MSS option, updates TCP checksum and lengths; `tcpmss_reverse_mtu()` routes back to source for reverse MTU; v4/v6 targets update IP total length or IPv6 payload length; check functions require TCP SYN matches for legacy iptables and validate clamp hooks.

Control flow: runtime skips fragments, ensures skb writable, validates TCP header length, computes desired MSS from configured value or min(dst MTU, reverse MTU) minus header length, never increases existing MSS, inserts option only for data-less headers with room or expanded tailroom, and updates checksums/length fields.

State and persistence: no persistent state; packet headers are modified. Dependencies/integration include TCP option parsing, nf_route, dst MTU, IPv4/IPv6 headers, checksum helpers, and x_tables match iteration. Risks: full-skb writability/expansion can fail and drop packets, PMTU unknown causes drop, option insertion must avoid TCP data and max header length, and nft compat bypasses SYN-match enforcement. Test signals: existing MSS lower/equal/higher, no MSS insertion, clamp PMTU, reverse route missing, fragments, IPv6 extension headers, SYN check enforcement, and checksum/length correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TCPMSS.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TCPOPTSTRIP.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_TCPOPTSTRIP.c

Purpose: `TCPOPTSTRIP` target removes selected TCP options by overwriting their bytes with NOPs and adjusting the TCP checksum.

Important APIs/types/functions: `tcpoptstrip_mangle_packet()` parses TCP option lengths safely, tests the configured bitmap, replaces selected option bytes, and updates checksums; v4/v6 wrappers compute TCP header offset.

Control flow: runtime skips fragments, reads and validates TCP header, ensures the TCP option area is writable, iterates options with finite progress for zero-length/malformed options, checks bitmap membership, replaces each byte with `TCPOPT_NOP`, and continues or drops on malformed/unwritable headers.

State and persistence: no persistent state; TCP header options are modified in the skb. Dependencies/integration include x_tables, mangle table, TCP parsing, IPv4/IPv6 extension header skipping, checksum replacement, and bitmap helpers from xt headers. Risks: malformed option lengths, checksum parity for odd/even option bytes, IPv6 extension parse failures, and fragments lacking TCP headers. Test signals: stripping single and multi-byte options, no-op for unselected options, malformed zero length, checksum validation, fragments, IPv6 extension headers, and writable failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TCPOPTSTRIP.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TEE.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_TEE.c

Purpose: `TEE` target duplicates matching packets to a configured gateway, optionally binding duplication to a named output interface.

Important APIs/types/functions: per-net `tee_net` holds private interface-tracking records; `tee_tg4()`/`tee_tg6()` call `nf_dup_ipv4/ipv6()`; `tee_tg_check()` validates gateway/interface and increments exported static key `xt_tee_enabled`; netdevice notifier maintains ifindex on register/unregister/rename.

Control flow: check rejects zero gateway, optionally allocates `xt_tee_priv`, resolves `oif` to ifindex, links it into the per-net list, and enables the static key. Runtime duplicates the skb and always continues original traversal. Destroy removes private state and decrements the static key. Module init registers pernet ops, targets, then netdevice notifier with ordered unwind.

State and persistence: per-rule private interface state, per-net lists, netdevice notifier, and global static key persist while rules exist. Dependencies/integration include x_tables, nf_dup IPv4/IPv6, net namespaces, netdevice events, route/gateway handling, and x_tables core static key. Risks: interface rename/unregister races, duplicated packet loops, static key balance, zero gateway validation, and pernet cleanup ordering. Test signals: IPv4/IPv6 duplication, interface present/missing/renamed/unregistered, zero gateway rejection, static key inc/dec, notifier registration failure unwind, and rule destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TEE.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TPROXY.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_TPROXY.c

Purpose: legacy xtables `TPROXY` target for transparent proxy redirection in mangle PREROUTING, assigning packets to local transparent sockets and optionally rewriting skb marks.

Important APIs/types/functions: `tproxy_tg4()` and `tproxy_tg6_v1()` perform socket lookup and assignment; revision wrappers translate v0/v1 config; check/destroy functions enable/disable IPv4/IPv6 defragmentation and enforce TCP/UDP protocol matches.

Control flow: runtime drops fragments or packets without transport headers, finds an established socket, computes local address/port defaults, handles TCP TIME_WAIT, looks up a listener when needed, checks `nf_tproxy_sk_is_transparent()`, updates mark with mask/value, assigns the socket, and accepts or drops.

State and persistence: no per-rule dynamic state beyond configured address/port/mark; defrag enablement persists per rule. Dependencies/integration include x_tables, nf_tproxy, inet socket tables, nf_defrag, mangle PREROUTING, and IPv4/IPv6 header parsing. Risks: defrag enable leak on protocol validation failure paths, socket reference ownership on assignment, IPv6 TIME_WAIT path uses configured laddr/lport rather than computed defaults, and mark rewrite is coupled with proxying. Test signals: v0/v1 IPv4, v1 IPv6, TCP/UDP only checks, fragments drop, established vs listener lookup, TIME_WAIT reopening, non-transparent socket drop, mark mask/value update, and defrag balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TPROXY.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TRACE.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_TRACE.c

Purpose: `TRACE` target marks packets for netfilter tracing and continues traversal.

Important APIs/types/functions: `trace_tg()` sets `skb->nf_trace = 1`; check/destroy pin and release an nf_log logger for the family.

Control flow: rule load obtains `NF_LOG_TYPE_LOG`; runtime sets the trace flag; unload unregisters targets and rule destroy puts logger refs. Registration is raw-table IPv4/IPv6.

State and persistence: trace state is a bit on the skb; logger references persist per rule. Dependencies/integration include x_tables, nf_log/syslog soft dependency, raw table, and netfilter trace consumers. Risks: missing logger rejects rules, tracing can produce high log volume, and trace bit affects downstream hooks globally for that packet. Test signals: logger availability, raw table hook enforcement, skb trace flag visibility, IPv4/IPv6 registration, destroy logger put, and continued traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_TRACE.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_addrtype.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_addrtype.c

Purpose: `addrtype` match tests source/destination address types such as local, unicast, multicast, anycast, or unreachable, optionally constrained to input/output interface.

Important APIs/types/functions: IPv4 `match_type()` uses `inet_dev_addr_type()`; IPv6 `match_type6()` combines address classification and route lookup; `addrtype_mt_v0()` and `_v1()` implement revisions; check functions validate hook/interface and unsupported IPv6 masks.

Control flow: runtime chooses device based on LIMIT_IFACE flags, classifies source and/or destination, applies inversion flags, and short-circuits destination check if source already failed. IPv6 route lookup detects local/anycast/unreachable where needed.

State and persistence: no persistent state. Dependencies/integration include x_tables, IPv4 address type, IPv6 route lookup, netdevice context, hook validation, and family-specific masks. Risks: route lookup cost and failure mapping to unreachable, unsupported IPv6 address type masks, invalid interface constraint on hook direction, and v0/v1 inversion differences. Test signals: IPv4 local/broadcast/unicast, IPv6 multicast/anycast/unreachable, source/dest inversion, iface-in/out constraints, hook validation failures, and route lookup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_addrtype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_bpf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_bpf.c

Purpose: `bpf` match runs classic or socket-filter BPF programs against packets.

Important APIs/types/functions: bytecode checker `__bpf_mt_check_bytecode()`, fd checker `__bpf_mt_check_fd()`, pinned-path checker `__bpf_mt_check_path()`, match functions using `bpf_prog_run()` or `bpf_prog_run_save_cb()`, and destroy functions releasing programs.

Control flow: checkentry validates mode and loads/creates a `BPF_PROG_TYPE_SOCKET_FILTER` program, storing the kernel pointer hidden from userspace. Runtime executes the program and returns its boolean result. Destroy calls `bpf_prog_destroy()` for loaded programs.

State and persistence: per-rule `bpf_prog` reference persists while the match exists. Dependencies/integration include x_tables, BPF verifier/program APIs, fd and pinned path lookup, and skb filter execution. Risks: bytecode length limits, path termination, fd type mismatch, callback state preservation in v1, and correct program ref release. Test signals: bytecode, fd, and pinned-path modes; invalid mode; oversized bytecode; missing pinned path; match true/false results; destroy after load failure; and IPv4/IPv6/unspecified family use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cgroup.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_cgroup.c

Purpose: `cgroup` match selects packets by socket cgroup classid or cgroup path ancestry, for per-application firewall policy.

Important APIs/types/functions: revision checks validate classid/path options and acquire cgroup refs; match functions inspect `skb->sk`, `sock_cgroup_classid()`, and `sock_cgroup_ptr()`; destroy releases cgroup refs for path modes.

Control flow: check rejects invalid inversion flags, missing or mixed path/classid selection, classid use without `CONFIG_CGROUP_NET_CLASSID`, and unterminated paths; path mode resolves a cgroup. Runtime requires a full socket in the same netns, then checks descendant relationship or classid equality with inversion.

State and persistence: path-based rules hold a `struct cgroup` reference; classid rules hold only user config. Dependencies/integration include x_tables, socket cgroup data, cgroup core, optional net_cls, and local in/out/postrouting hooks. Risks: packets without full sockets never match, netns mismatch protection, path ref lifetime, classid config dependence, and usersize hiding of `priv`. Test signals: classid enabled/disabled, path resolution success/failure, inversion flags, missing socket, different socket netns, descendant matching, destroy cgroup_put, and all three revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cluster.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_cluster.c

Purpose: `cluster` match distributes conntracked flows across cluster nodes by hashing original source address and comparing the selected bucket against a node mask.

Important APIs/types/functions: IPv4/IPv6 hash helpers, `xt_cluster_hash()`, multicast address detection, `xt_cluster_mt()` match body, and check/destroy functions managing conntrack support.

Control flow: runtime may rewrite `skb->pkt_type` from multicast to host for unicast L3 destinations, obtains conntrack or master conntrack, hashes original source address with configured seed, scales to `total_nodes`, and tests the resulting node bit with optional inversion. Check validates node count and mask bounds and pins conntrack.

State and persistence: no private dynamic state; conntrack netns ref persists per rule. Dependencies/integration include conntrack tuples, jhash, IPv4/IPv6 header classification, x_tables, and mirrored cluster network assumptions. Risks: match mutates `pkt_type`, requires conntrack, node mask arithmetic around total nodes, and multicast MAC deployment assumptions. Test signals: IPv4/IPv6 flow hashing, master conntrack use, no-ct false result, inversion, invalid node counts/masks, pkt_type correction, and conntrack ref cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cluster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_comment.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_comment.c

Purpose: no-op `comment` match that lets users attach comments to rules without affecting packet decisions.

Important APIs/types/functions: `comment_mt()` always returns true; `comment_mt_reg` registers revision 0 for `NFPROTO_UNSPEC` with `xt_comment_info` payload.

Control flow: module init registers one match; every packet matches; module exit unregisters it.

State and persistence: only user comment bytes stored in rule data; no runtime state. Dependencies/integration include x_tables userspace ABI and rule serialization. Risks: minimal, mostly ensuring match size ABI remains stable and comments do not influence logic. Test signals: any packet matches, comment survives list/save/restore through userspace, family-independent registration, and unload unregisters match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_comment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connbytes.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_connbytes.c

Purpose: `connbytes` match tests per-connection packet counts, byte counts, or average packet size from conntrack accounting.

Important APIs/types/functions: `connbytes_mt()` reads `nf_conn_acct` counters for original/reply/both directions and compares against a range; check validates mode/direction, pins conntrack, and forces accounting on if disabled; destroy releases conntrack.

Control flow: runtime requires conntrack and accounting extension, reads atomic64 counters by requested direction, computes average with `div64_u64()` if needed, and applies normal or inverted range semantics where `to < from` means outside range.

State and persistence: counter state lives in conntrack accounting; rule holds conntrack netns reference and may enable accounting globally in the namespace. Dependencies/integration include nf_conntrack_acct, x_tables, atomic counters, and conntrack. Risks: missing accounting extension yields false even after enabling for future flows, forced accounting is a namespace side effect, average packet division by zero returns zero, and inverted range semantics are non-obvious. Test signals: packets/bytes/avg modes, original/reply/both, inverted ranges, no conntrack, accounting disabled warning/enabling, and destroy ref release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connbytes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connlabel.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_connlabel.c

Purpose: `connlabel` match tests and optionally sets bits in conntrack labels.

Important APIs/types/functions: `connlabel_mt()` gets conntrack labels, tests `info->bit`, optionally sets it and emits `IPCT_LABEL`; `connlabel_mt_check()` validates options, pins conntrack, and reserves label bit support; destroy puts labels and conntrack.

Control flow: check accepts only INVERT and SET options, obtains conntrack, calls `nf_connlabels_get()` for the requested bit, and stores no private pointer. Runtime returns invert result on missing conntrack/labels, returns match on existing bit, or sets the bit and returns match when SET is enabled.

State and persistence: label bits persist in conntrack entries; namespace label support and conntrack refs persist while rule exists. Dependencies/integration include nf_conntrack labels, event cache, x_tables, and conntrack. Risks: missing labels returns inverted result, SET mutates connection state from a match, event emission only on first set, and label bit reservation must unwind on check failure. Test signals: bit absent/present, SET first and repeated packet, INVERT, no conntrack, no label extension, invalid option mask, and destroy puts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connlabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connlimit.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_connlimit.c

Purpose: `connlimit` match limits concurrent connections per masked source or destination address, with zone-aware keys.

Important APIs/types/functions: `connlimit_mt()` builds IPv4/IPv6 key plus conntrack zone, calls `nf_conncount_count_skb()`, and compares to limit; check initializes `nf_conncount` private data and pins conntrack; destroy frees data and releases conntrack.

Control flow: runtime gets conntrack zone if available, masks source or destination address depending on flags, appends zone id, counts matching live connections, hotdrops on count failure, and returns `(connections > limit)` with optional inversion.

State and persistence: per-rule `nf_conncount_data` persists as hidden private data; conntrack counting state tracks flows in the namespace. Dependencies/integration include nf_conntrack_count, zones, IPv4/IPv6 headers, x_tables usersize hiding, and conntrack. Risks: allocation/count failure causes hotdrop, key length differs by family, zone id affects buckets, address mask semantics must match userspace, and destroy must free private count data. Test signals: IPv4/IPv6 source and destination limits, masks, inversion, zone-specific counts, count failure hotdrop, rule destroy cleanup, and conntrack absence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_connlimit.c -->
