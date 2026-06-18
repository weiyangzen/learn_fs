# Research: subset-b-000621

Grouped research for Linux kernel netlink specification YAML files under `sources/distributed-fs/ceph-client/Documentation/netlink/specs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/dpll.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/dpll.yaml

Purpose: defines the YAML netlink specification for the kernel DPLL subsystem. It describes how userspace discovers, reads, configures, and receives notifications for DPLL devices and their pins through generated Generic Netlink bindings.

Important APIs/types/functions: the top-level family is `dpll`. Definitions model the public enum/constant surface: device `mode`, `lock-status`, `lock-status-error`, `clock-quality-level`, device `type`, `pin-type`, `pin-direction`, `pin-state`, `pin-capabilities`, monitor `feature-state`, and divider/frequency constants. Attribute sets are `dpll`, `pin`, `pin-parent-device`, `pin-parent-pin`, `frequency-range`, and `reference-sync`. Device attributes include `id`, `module-name`, `clock-id`, `mode`, supported modes, lock status/error, temperature, quality levels, phase-offset monitor fields, and frequency monitor fields. Pin attributes cover identity labels, parent relations, frequency ranges, priority/state/capabilities, phase adjustment, fractional frequency offsets, embedded sync, reference sync, and measured frequency.

Control flow: operations form two flows. Device flow starts with `device-id-get` when userspace has identifying fields and needs a kernel id, then `device-get` for a single device or dump, and `device-set` to alter mutable device fields. Pin flow mirrors that with `pin-id-get`, `pin-get`, and `pin-set`. Create/delete/change notifications for devices and pins are tied to the corresponding `*-get` response schema. Several operations name generated C pre/post hooks such as `dpll-pre-doit`, `dpll-post-doit`, `dpll-pin-pre-doit`, and lock/unlock helpers, indicating that kernel implementation wraps lookup and mutation in subsystem locking.

State and persistence: the spec has no local runtime state, but it documents live kernel DPLL state: device ids, pin ids, parent-child topology, lock state, frequency, priority, phase, and monitor settings. Set operations mutate kernel-owned device/pin configuration rather than any YAML-local persistence.

Dependencies and integration points: consumed by the kernel netlink spec tooling to generate or validate UAPI descriptions and by userspace tooling that understands YAML netlink schemas. It integrates with DPLL subsystem code through named pre/post hooks and with notification subscribers through device and pin event messages.

Risks: many nested attributes reuse names without explicit type declarations in child sets, relying on inherited or generated resolution; schema generator regressions could mis-handle those references. Administrative permission is required on get/set/id paths, which may surprise read-only discovery tools. Frequency, phase, and fractional offsets mix signed, unsigned, and divider-scaled quantities, so userspace must preserve units and width. Parent device/pin nesting creates graph-like topology that can be misrepresented if a splitter only treats attributes as flat fields.

Test signals: useful validation includes YAML schema parsing, generated enum values, request/reply attribute coverage for all operations, round-trip dumps for device and pin objects, notification payload compatibility with get replies, and permission/error tests for id lookup and set operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/dpll.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/drm_ras.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/drm_ras.yaml

Purpose: specifies the DRM RAS Generic Netlink family, exposing reliability, availability, and serviceability counters from DRM drivers to userspace.

Important APIs/types/functions: the family is `drm-ras`, protocol `genetlink`, with generated UAPI header `drm/drm_ras.h`. The `node-type` enum identifies hardware/software component classes. Attribute set `node-attrs` describes registered RAS nodes with `node-id`, `device-name`, `node-name`, and `node-type`. Attribute set `error-counter-attrs` describes counters with `node-id`, `error-id`, `error-name`, and `error-value`.

Control flow: userspace first dumps `list-nodes` to discover dynamic node ids. It then calls or dumps `get-error-counter`: a do request can target `node-id` plus `error-id`, while a dump request uses `node-id` to enumerate counters for that node. Both operations require `admin-perm`, so the API is intended for privileged diagnostics rather than unprivileged telemetry.

State and persistence: the YAML stores no state. It describes kernel-maintained, dynamically registered DRM RAS nodes and live error counter values. Node ids are explicitly dynamic, so userspace should not persist them across driver reloads or reboot without rediscovery.

Dependencies and integration points: integrates DRM drivers with Generic Netlink and code generation for `drm/drm_ras.h`. Monitoring tools can build a discovery-then-counter query workflow from the two operations.

Risks: dynamic ids are easy to misuse if applications cache them. Error counter values are `u32`, which may be too small for long-running devices unless kernel drivers reset or expose counters consistently. The spec has no notification operation, so userspace must poll for changes.

Test signals: tests should verify that node dumps include all registered nodes, counter dumps require a valid node, invalid stale node ids fail predictably, generated headers match the YAML enum/attributes, and privilege checks are enforced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/drm_ras.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ethtool.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ethtool.yaml

Purpose: describes the large, partial `ethtool` netlink family in legacy Generic Netlink form. It is the schema used to generate/validate netlink access to link settings, device features, queue/channel/ring tuning, PHY/module data, timestamping, cable tests, statistics, PSE, PLCA, RSS, and newer diagnostics.

Important APIs/types/functions: protocol is `genetlink-legacy`, UAPI header is `linux/ethtool_netlink_generated.h`, with directional operation enum names under prefix `ethtool-msg-`. Definitions include UDP tunnel types, string sets, common header flags, module firmware flash status, C33 PSE extended state, PHY upstream type, TCP data split state, hardware timestamp source, PSE event flags, RSS input transforms, and RX flow-hash field flags. There are 62 attribute sets. Core reusable sets include `header`, `bitset`, string/string-set sets, and statistics nests. Domain sets include `linkinfo`, `linkmodes`, `linkstate`, `debug`, `wol`, `features`, `rings`, `channels`, `coalesce`, `pause`, `eee`, `tsinfo`, cable-test/tdr sets, tunnel UDP tables, `fec`, `module-eeprom`, `stats`, `phc-vclocks`, `module`, `pse`, `rss`, `plca`, `module-fw-flash`, `phy`, `tsconfig`, `pse-ntf`, and `mse`.

Control flow: most domains follow a consistent get/set/notification pattern: `*-get` accepts a nested `header` selecting the device, `*-set` carries mutable fields, and `*-ntf` reuses the get schema for multicast/event payloads. Action-like flows include `cable-test-act` and `cable-test-tdr-act`, whose progress arrives through notification schemas, `module-fw-flash-act` with status notifications, and RSS context create/delete actions with notifications. Dump variants exist for inventories such as string sets and some get operations. The `header` is the routing anchor for device index/name, flags, and optional PHY index; `compact-bitsets`, `omit-reply`, and `stats` flags influence reply shape and side data.

State and persistence: the file itself is static schema. The represented kernel state includes persistent or semi-persistent NIC settings, advertised link modes, Wake-on-LAN options, feature flags, ring/channel/coalesce configuration, pause/EEE/FEC/PLCA state, PSE power control, timestamp configuration, RSS contexts, module power mode, and firmware flash progress. Statistics and diagnostics are live counters/snapshots. Several operations mutate driver/device state and may survive only as long as the device/driver does.

Dependencies and integration points: integrates with the kernel ethtool netlink family, NIC drivers, PHY libraries, module EEPROM/firmware support, timestamping/PHC, cable diagnostics, and generated netlink user APIs. The many nested bitset/string-set forms are shared across ethtool domains and must align with legacy ethtool names and bit numbering.

Risks: this is a partial family, so tools must not assume every ethtool netlink command is modeled. The breadth of nested schemas makes generator correctness critical; a broken nested bitset implementation can affect features, link modes, WOL, FEC, stats group selection, RSS hash fields, and timestamp filters. Binary fields such as EEPROM data, PHC indices, FEC lane counters, and RSS tables require exact length handling. Action notifications can be asynchronous and multi-stage. Some newer operations may not be supported by all kernels or drivers even if the schema parses.

Test signals: validate YAML parse and generated constants, common header encoding, get/set request/reply generation across representative domains, compact and verbose bitset encoding, notification decoding, cable-test and firmware-flash progress handling, binary-length boundaries, and graceful handling of unsupported driver operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ethtool.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/fou.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/fou.yaml

Purpose: specifies the legacy Generic Netlink API for Foo-over-UDP tunnel port configuration.

Important APIs/types/functions: the family is `fou`, protocol `genetlink-legacy`. The `encap-type` enum distinguishes encapsulation modes. The single `fou` attribute set includes `port`, address family, IP protocol, encapsulation type, remote checksum mode, local/peer IPv4 and IPv6 addresses, peer port, and interface index. Network-order fields are explicitly marked for UDP ports and IPv4 addresses; IPv6 binary attributes require exact 16-byte lengths.

Control flow: `add` creates a configured UDP encapsulation port using port, protocol, type, local/peer addresses, peer port, and ifindex. `del` removes a matching port using address family, ifindex, port, peer-port, and address selectors. `get` can do a targeted lookup with the same selectors or dump all tunnel info. `unspec` is reserved value zero. The operations disable strict/dump validation, preserving legacy behavior.

State and persistence: mutations affect kernel FOU tunnel configuration. The YAML has no persistent state; configured ports live in kernel networking state and normally vanish when the namespace or system resets.

Dependencies and integration points: integrates with Linux FOU/GUE tunnel handling and userspace networking tools. The schema bridges tunnel port management to netlink code generation.

Risks: legacy non-strict validation increases ambiguity around missing or extra attributes. IPv4 and IPv6 selector combinations must match address family. Endianness is mixed: ports and IPv4 addresses are big-endian, while several small fields are host-order integers. `ipproto` enforces only a minimum of 1, leaving semantic protocol validation to kernel implementation.

Test signals: cover add/get/delete round trips for IPv4 and IPv6, peer-specific and wildcard lookups, exact IPv6 length validation, port byte order, invalid protocol zero, and legacy behavior with non-strict validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/fou.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/handshake.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/handshake.yaml

Purpose: defines the Generic Netlink protocol used by kernel transport code to request userspace-assisted security handshakes, such as TLS handshakes.

Important APIs/types/functions: definitions include `handler-class`, `msg-type`, and `auth` enums. The `x509` nested attribute set carries certificate and private-key file descriptors or ids as signed integers. The `accept` set carries `sockfd`, handler class, message type, timeout, auth mode, repeated peer identity values, repeated X.509 certificate nests, peer name, and keyring. The `done` set carries completion `status`, `sockfd`, and repeated `remote-auth` values.

Control flow: `ready` is a notification telling handlers that a handshake request is queued. A privileged handler calls `accept` with a `handler-class` and receives the socket fd plus parameters needed to complete the handshake. After userspace finishes, it calls `done` with status, socket, and remote authentication results. This forms a queue-consume-complete protocol with fd transfer semantics implied by the socket attribute.

State and persistence: live handshake requests are queued in kernel state, and sockets move through pending, accepted, and completed states. The YAML persists only schema. Handshake results may affect kernel socket security state but not this document.

Dependencies and integration points: integrates transport-layer security consumers, userspace handshake daemons, keyrings, X.509 material, and Generic Netlink notifications. The handler class enum allows multiple handler implementations to share the family.

Risks: fd-like signed attributes require precise ownership and lifecycle handling in userspace. Timeouts and queued request ordering are not described by the schema, so daemon behavior depends on kernel implementation. Repeated peer identities/certificates/remote-auth attributes require robust multi-attribute parsing. `done` lacks `admin-perm`, so authorization relies on kernel family implementation and socket/request matching.

Test signals: exercise notification delivery, handler-class filtering, accept of queued sockets, fd lifetime on success/failure, timeout handling, multiple certificate and identity attributes, and completion status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/handshake.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/lockd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/lockd.yaml

Purpose: specifies a small Generic Netlink API for configuring the kernel NFS lock manager daemon (`lockd`).

Important APIs/types/functions: family name is `lockd`, protocol `genetlink`, UAPI header `linux/lockd_netlink.h`. The single `server` attribute set has `gracetime`, `tcp-port`, and `udp-port`.

Control flow: `server-set` is an administrative do operation that updates lockd server parameters. `server-get` returns the current parameters. There are no dump or notification operations because the API addresses singleton server configuration.

State and persistence: the YAML is static; the represented state is kernel lockd server configuration. Set values affect the running server and may not persist beyond module unload, reboot, or higher-level service reconfiguration.

Dependencies and integration points: integrates NFS lockd server code with Generic Netlink and generated UAPI definitions. NFS administration tools can use it instead of procfs/sysfs-style configuration.

Risks: singleton configuration means concurrent administrators can race. Port numbers are `u16` and no min/max policy beyond type is expressed. Changing ports or grace time on a running server may have operational effects outside the schema.

Test signals: validate get defaults, set/get round trips, privilege enforcement for `server-set`, boundary ports, and behavior while lockd is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/lockd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/mptcp_pm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/mptcp_pm.yaml

Purpose: describes the legacy Generic Netlink path manager API for Multipath TCP endpoint, limit, flag, announce, remove, and subflow operations.

Important APIs/types/functions: the `event-type` enum documents MPTCP event categories. Attribute sets include `address`, `subflow-attribute`, `endpoint`, `attr`, and `event-attr`. Address attributes carry family, id, IPv4/IPv6 address, port, flags, and ifindex. `attr` wraps local/remote addresses plus receive-addrs/subflows limits, token, and local id. `event-attr` describes event payloads with token, ids, source/destination addresses and ports, backup/error flags, timeout, ifindex, reset metadata, and server-side indicator.

Control flow: administrative endpoint operations are `add-addr`, `del-addr`, and `flush-addrs`. `get-addr` supports targeted lookup and dump. `set-limits`/`get-limits` manage global or namespace path-manager limits. `set-flags` changes endpoint flags. Per-connection operations use tokens: `announce`, `remove`, `subflow-create`, and `subflow-destroy`. Most commands disable strict validation for legacy compatibility and use `uns-admin-perm` for writes.

State and persistence: the API mutates MPTCP path manager state: configured endpoints, address ids, flags, limits, and live connection subflow choices. This is kernel/network-namespace state, not YAML state, and typically persists only while the namespace and MPTCP sockets exist.

Dependencies and integration points: integrates with MPTCP kernel path manager logic, namespace-scoped networking, and userspace tools such as `ip mptcp`. The token fields connect management commands to established MPTCP connections.

Risks: non-strict validation plus nested address structures can allow ambiguous messages. Address byte order varies: IPv4 and event ports are big-endian in several places, while endpoint `port` lacks an explicit byte-order marker. Token-scoped operations can fail if the connection disappears between discovery and action. Event attributes exist in the schema but no multicast groups are declared here.

Test signals: endpoint add/get/delete/flush tests, limit set/get tests, per-token announce/remove/subflow actions against live sockets, IPv4/IPv6 exact length and endian checks, namespace isolation, and stale token/id failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/mptcp_pm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/net_shaper.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/net_shaper.yaml

Purpose: specifies a Generic Netlink API for hardware network rate limiting and scheduler tree manipulation on network devices.

Important APIs/types/functions: definitions include `max-handle-id`, shaper `scope`, and rate `metric`. The `net-shaper` attribute set models one shaper with `handle`, `metric`, `bw-min`, `bw-max`, `burst`, `priority`, `weight`, `ifindex`, optional `parent`, and repeated `leaves`. `handle` nests `scope` and bounded `id`. `leaf-info` carries child handle plus priority/weight. `caps` reports per-device/scope capability flags such as metric support, nesting, min/max bandwidth, burst, priority, and weight.

Control flow: `get` returns a selected shaper or dumps shapers for an ifindex. `set` creates or updates an attached shaper but cannot create node-scope shapers. `delete` clears a shaper and has special topology behavior for node removal and orphaned parents. `group` creates or updates a scheduling group, attaching queue leaves under a node or netdev-scope parent and returning the resulting handle. `cap-get` returns supported capabilities for an ifindex/scope. Write operations use `admin-perm` and named pre/post hooks that distinguish read, write, dump, and capability paths.

State and persistence: the represented state is hardware/driver shaper configuration and scheduler tree topology. Handles identify shapers within a device. Settings may persist only in driver/hardware runtime state and can be reset by device reload or link changes.

Dependencies and integration points: integrates with network device drivers that expose hardware shapers, kernel netlink spec generation, and traffic-control-like userspace tooling. The schema's pre/post hooks imply kernel-side locking and device lookup around each operation.

Risks: tree manipulation has high consistency risk: deleting a node reattaches leaves and may cascade parent deletion. The same operation accepts many optional shaping fields, so userspace must understand capability flags before setting unsupported metrics. Handle id bounds depend on a named constant rather than a literal, so generator support for symbolic checks matters. Hardware support is uneven across devices.

Test signals: validate capability query before set/group, queue/netdev/node scope rules, handle id bounds, bandwidth/packet metric behavior, deletion reparenting, dump consistency during concurrent changes, and privilege enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/net_shaper.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/netdev.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/netdev.yaml

Purpose: describes the Generic Netlink `netdev` configuration and introspection API for network devices, page pools, queues, NAPI instances, queue statistics, DMA buffer binding, and dynamic queue creation.

Important APIs/types/functions: definitions include XDP action/features, XDP RX metadata flags, XSK flags, queue type, queue-stat scope, and NAPI threaded state. Attribute sets include `dev`, `io-uring-provider-info`, `page-pool`, `page-pool-info`, `page-pool-stats`, `napi`, `xsk-info`, `queue`, `qstats`, `queue-id`, `lease`, and `dmabuf`. Device replies report ifindex and XDP/XSK capability bitmaps. Page-pool attributes expose ids, ifindex, NAPI id, inflight pages/bytes, detach time, dmabuf id, and io_uring provider info. Queue/NAPI/qstats sets describe queue ids/types, NAPI affinity and tunables, per-queue counters, leases, and dmabuf bindings.

Control flow: `dev-get`, `page-pool-get`, `queue-get`, `napi-get`, and `page-pool-stats-get` are query/dump paths. Device and page-pool add/delete/change notifications reuse get schemas. `qstats-get` is dump-only and filters by ifindex/scope. Mutating paths are `bind-rx` for RX dmabuf binding, `bind-tx` for TX binding, `napi-set` for NAPI tunables, and `queue-create` for driver-supported queue creation; most write paths require `admin-perm`, while `bind-tx` notably has no explicit flag in the schema.

State and persistence: the API exposes live netdevice capabilities, page-pool lifecycle, queue configuration, NAPI runtime settings, dmabuf leases, and counters. Some settings mutate driver/runtime state; counters and pool statistics are transient.

Dependencies and integration points: integrates with network core, XDP/XSK, page_pool, NAPI, io_uring provider plumbing, dmabuf-backed networking, and netdev queue management. User tools can discover capabilities, then bind memory or allocate queues based on driver support.

Risks: several attributes use symbolic min/max checks such as `u32-max` and `s32-max`, so generator support is required. Queue and page-pool ids are live objects that can disappear between dump and action. Dmabuf binding crosses fd, namespace, and hardware ownership boundaries. `bind-tx` lacking an explicit admin flag should be checked against kernel implementation expectations. Statistics coverage depends on driver support.

Test signals: parse/generation tests for nested queue/dmabuf/lease schemas, notification tests for device and page-pool lifecycle, qstats dumps on devices with and without per-queue counters, NAPI set/get round trips, dmabuf fd validation, and queue-create failure paths on unsupported drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/netdev.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nfsd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/nfsd.yaml

Purpose: specifies the Generic Netlink API for NFSD server configuration and status.

Important APIs/types/functions: protocol is `genetlink`, UAPI header `linux/nfsd_netlink.h`. Attribute sets cover `rpc-status`, `server`, `version`, `server-proto`, `sock`, `server-sock`, and `pool-mode`. `rpc-status` carries pending RPC metadata including xid, flags, program/version/procedure, service time, IPv4/IPv6 source/destination, ports, and compound NFSv4 operations. `server` carries thread counts, grace/leasetime, scope, min threads, and a 16-byte file-handle key. Version and socket sets model enabled protocol versions and listener addresses/transports.

Control flow: `rpc-status-get` dumps pending NFSD RPCs. Administrative setters configure threads/server parameters, enabled protocol versions, listeners, and pool mode. Getters return the corresponding server, version, listener, and pool-mode state. `threads-set`, `version-set`, `listener-set`, and `pool-mode-set` require `admin-perm`; read operations do not.

State and persistence: represented state is the running NFSD service: thread pools, grace and lease timers, server scope, file-handle key, enabled NFS protocol versions, listeners, pool mode, and pending RPCs. Persistence is controlled by NFSD/service configuration outside this YAML; netlink changes affect live kernel server state.

Dependencies and integration points: integrates NFSD kernel code with generated netlink UAPI and userspace NFS administration tools. The schema complements or replaces older procfs/sysfs configuration paths.

Risks: server socket addresses are binary/nested and may contain family-specific layouts not fully described in YAML. Changing listener, version, or pool state while service is active can have client-visible effects. `fh-key` has exact 16-byte validation and is accepted only on set, not returned by get, which is appropriate but requires tools to avoid assuming round-trip visibility. RPC status contains mixed endian network fields.

Test signals: check get/set round trips for threads, versions, listeners, and pool mode; validate exact `fh-key` length; dump pending RPCs under load; verify port/address byte order; and enforce privilege checks on setters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nfsd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nftables.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/nftables.yaml

Purpose: describes the raw netlink API schema for nftables configuration, including tables, chains, rules, expressions, sets, set elements, objects, generation ids, flowtables, and batch messages.

Important APIs/types/functions: protocol is `netlink-raw`. Definitions include `nfgenmsg` fixed header, operation enums for metadata/bitwise/compare/NAT/table/chain/set/lookup/payload/exthdr/ct/socket/tproxy/osf/xfrm/synproxy/flowtable concepts, and multiple flag sets. The 48 attribute sets cover expression payloads (`log`, `numgen`, `range`, `bitwise`, `byteorder`, `cmp`, `lookup`, `dynset`, `payload`, `exthdr`, `meta`, `ct`, `limit`, `counter`, `quota`, `reject`, `nat`, `tproxy`, `socket`, `osf`, `xfrm`, `synproxy`, `dup`, `fwd`, `objref`, `immediate`, and more) plus top-level table, chain, rule, set, setelem, object, flowtable, hook, counter, userdata, and batch attrs.

Control flow: batch operations bracket atomic netfilter updates. Table/chain/rule/set/setelem/object/flowtable resources have create/get/delete/destroy-style operations. Get operations often support both do and dump forms. Rule creation carries table, chain or chain-id, handle/position, expressions, userdata, and compatibility data. Set operations configure key/data types, lengths, flags, timeout, garbage collection, policy, descriptions, expressions, and elements. Generation-id retrieval exposes current ruleset generation and process metadata.

State and persistence: this schema mutates nftables ruleset state in kernel netfilter tables. Changes are live kernel state and can be made atomically through batch messages. Persistence across reboot is normally handled by userspace ruleset save/restore, not by netlink itself.

Dependencies and integration points: integrates with netfilter/nftables raw netlink, expression evaluators, hooks, counters, sets/maps, stateful objects, and userspace tools such as `nft`. The `nfgenmsg` header and raw protocol distinguish it from Generic Netlink specs.

Risks: this is a dense schema with deeply nested expression and set element attributes; incomplete generator support can silently break rule encoding. Raw netlink plus nfgenmsg family/version/res-id handling has stricter framing requirements than Generic Netlink. Destroy and delete variants have subtly different semantics in nftables. Batch atomicity depends on correctly paired begin/end messages. Many binary data fields carry expression-specific layouts not fully self-describing from generic type alone.

Test signals: validate raw netlink header generation, batch begin/end framing, table/chain/rule/set/object/flowtable CRUD, dump and reset-get behavior, expression nesting for representative rule types, set element timeout/userdata paths, generation id checks, and rejection of malformed nested attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nftables.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nl80211.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/nl80211.yaml

Purpose: specifies a legacy Generic Netlink description for selected `nl80211` wireless APIs, focused on wiphy/interface discovery and protocol feature reporting.

Important APIs/types/functions: protocol is `genetlink-legacy` with directional operation model. Definitions include the large `commands` enum, `feature-flags`, `channel-type`, `sta-flag-update` struct, and `protocol-features` flags. Attribute sets include the broad `nl80211-attrs` set with 333 attributes, plus nested sets for frame types, wiphy bands, band/rate/frequency data, interface combinations and limits, iftype data, SAR specs, supported iftypes, TXQ stats, WMM attrs, and WoWLAN triggers.

Control flow: only three operations are declared despite the large attribute vocabulary. `get-wiphy` can do or dump and returns capability-rich wiphy data such as bands, cipher suites, features, interface combinations, SAR, supported commands/iftypes, frame types, TXQ limits, antenna settings, and WoWLAN support. `get-interface` can do or dump and returns interface name/type/index, wiphy, wdev, MAC, generation, TXQ stats, and 4-address mode. `get-protocol-features` returns supported protocol features such as split wiphy dump.

State and persistence: the YAML is static schema. It represents live wireless device and interface state, regulatory/channel capabilities, advertised protocol features, and interface statistics. It does not model mutating nl80211 commands in this subset.

Dependencies and integration points: integrates with cfg80211/mac80211, wireless drivers, userspace tools such as `iw`, and generated netlink schema consumers. The broad attribute set is shared with many nl80211 commands even though only discovery operations are modeled here.

Risks: `nl80211-attrs` is huge and many attributes are binary or nested with command-specific semantics; consumers must not assume all attributes are valid for the three declared operations. The spec is partial, so command enum entries far exceed operation declarations. Wireless capability dumps are large and may require split dump handling. Regulatory and band/frequency flags need careful interpretation across kernel versions.

Test signals: parse the full attribute vocabulary, verify get-wiphy split dump handling, decode nested band/frequency/interface-combination structures, query interface dumps across multiple iftypes, and confirm unsupported/mutating commands are not generated from this partial spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nl80211.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nlctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/nlctrl.yaml

Purpose: describes the Generic Netlink controller meta-family, which lets userspace discover registered Generic Netlink families, operations, multicast groups, and policy information.

Important APIs/types/functions: family name is `nlctrl`, protocol `genetlink-legacy`, UAPI header `linux/genetlink.h`, operation prefix `ctrl-cmd-`. Definitions include `op-flags` and `attr-type`. Attribute sets include `ctrl-attrs`, `mcast-group-attrs`, `op-attrs`, `policy-attrs`, and `op-policy-attrs`. `ctrl-attrs` carries family id/name, version, header size, max attr, indexed arrays of ops and multicast groups, nested policy and op-policy data, and operation id.

Control flow: `getfamily` supports do lookup by family name and full dumps of registered families; replies include id, name, hdrsize, maxattr, groups, ops, and version. `getpolicy` dumps policy information for a family id/name and optional operation. Numeric values in request/reply entries align with legacy controller command ids.

State and persistence: the API exposes live kernel Generic Netlink registration state. Families, operations, groups, and policy data change as modules load/unload or register/unregister. No YAML-local state exists.

Dependencies and integration points: this is the discovery dependency for all Generic Netlink consumers, including many other specs in this group. It integrates with kernel genetlink registration and policy export code.

Risks: policy export can be incomplete or kernel-version-dependent. Indexed arrays and nest-type-value attributes require generator support beyond simple nested attributes. Family ids and multicast group ids are dynamic and should not be persisted by userspace without rediscovery.

Test signals: query known families by name and dump mode, validate operation and multicast group decoding, retrieve policies for operations, handle module load/unload races, and confirm generated command ids match `linux/genetlink.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/nlctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovpn.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovpn.yaml

Purpose: specifies the Generic Netlink API for controlling OpenVPN network devices in the kernel, including peers, session keys, key rotation, deletion, and peer endpoint floating notifications.

Important APIs/types/functions: definitions include `nonce-tail-size`, `cipher-alg`, `del-peer-reason`, and `key-slot`. Attribute sets model peer state (`peer`), peer input subsets for new/set/delete, key configuration (`keyconf`, `keydir`, `keyconf-get`, swap/delete inputs), top-level `ovpn`, and operation-specific wrappers that include `ifindex`. Peer fields cover ids, remote/local/VPN IPv4 and IPv6 addresses, scope id, ports, socket and netns id, keepalive settings, deletion reason, traffic counters, and transmit id. Key fields include peer id, slot, key id, cipher algorithm, encrypt/decrypt dirs, cipher key, and nonce tail.

Control flow: peer operations are `peer-new`, `peer-set`, `peer-get`, and `peer-del`, with peer delete and peer float notifications reusing `peer-get`. Key operations are `key-new`, `key-get`, `key-swap`, and `key-del`, plus a key-swap notification when IV space exhaustion requires renegotiation. Most operations name `ovpn-nl-pre-doit` and `ovpn-nl-post-doit`, implying device lookup/reference management around each request. Administrative permission is required throughout.

State and persistence: represented state is live OpenVPN device peer tables, socket associations, endpoint addresses, counters, keepalive parameters, and primary/secondary key material. Keys are sensitive runtime state; `key-get` intentionally returns non-sensitive key/cipher metadata rather than raw key material.

Dependencies and integration points: integrates kernel OpenVPN data path, net_device ifindex lookup, socket ownership, network namespaces, cipher/key management, and userspace OpenVPN control daemons.

Risks: key and nonce fields are security-sensitive, so length validation and zeroization are important outside the YAML. Peer ids and tx ids are bounded to 24 bits, and key ids to 3 bits; tools must enforce these limits. IPv6 scope, socket-netnsid, endpoint floating, and socket fd/id semantics cross namespace boundaries. Notifications are important for renegotiation; missing them can break key rollover.

Test signals: peer create/set/get/delete round trips, key create/get/swap/delete flows without leaking key bytes, nonce-tail exact length, id bound enforcement, endpoint float notifications, key exhaustion notification handling, and namespace/socket validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovpn.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_datapath.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_datapath.yaml

Purpose: describes the legacy Generic Netlink API for Open vSwitch datapath configuration and state.

Important APIs/types/functions: protocol is `genetlink-legacy`, UAPI header `linux/openvswitch.h`, operation prefix `ovs-dp-cmd-`, and fixed header `ovs-header`. Definitions include `ovs-header` with datapath ifindex, `user-features` flags, `ovs-dp-stats`, and `ovs-dp-megaflow-stats`. The `datapath` attribute set includes datapath `name`, upcall pid(s), stats, megaflow stats, user features, mask cache size, per-CPU pids, and ifindex.

Control flow: `get` value 3 performs targeted or dump retrieval by datapath name and replies with datapath status and statistics. `new` value 1 creates a datapath with name, upcall pid, and user features. `del` value 2 deletes an existing datapath by name.

State and persistence: operations mutate or read kernel OVS datapath instances, upcall delivery configuration, stats, and flow mask cache state. This state is live kernel state and normally managed by OVS userspace daemons rather than persisted by netlink itself.

Dependencies and integration points: integrates with the kernel OVS datapath module and userspace `ovs-vswitchd`/datapath tooling. The fixed OVS header is shared with OVS flow and other OVS netlink families.

Risks: datapath name and ifindex must stay synchronized with kernel state. Upcall pids and per-CPU pids affect packet miss delivery; misconfiguration can break control-plane flow installation. Binary struct stats require exact layout compatibility with `linux/openvswitch.h`.

Test signals: create/get/delete datapath round trips, dump multiple datapaths, validate stats struct decoding, upcall pid behavior, and generated command values against `openvswitch.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_datapath.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_flow.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_flow.yaml

Purpose: specifies the legacy Generic Netlink schema for Open vSwitch flow lookup and creation within an OVS datapath.

Important APIs/types/functions: protocol is `genetlink-legacy`, UAPI header `linux/openvswitch.h`, operation prefix `ovs-flow-cmd-`, fixed header `ovs-header`. Definitions model OVS flow stats, packet key structs for Ethernet/MPLS/IPv4/IPv6/TCP/UDP/SCTP/ICMP/ARP/ND/conntrack tuples, fragment enum, UFID flags, VLAN/MPLS/hash action structs, hash algorithm enum, and conntrack state flags. Attribute sets include `flow-attrs`, `key-attrs`, `action-attrs`, tunnel key attrs, packet-length check attrs, sample/userspace attrs, NSH attrs, conntrack/NAT attrs, TTL decrement attrs, VXLAN extensions, and psample attrs.

Control flow: `get` supports do and dump. Requests can identify flows by parsed key, UFID, and UFID flags; replies include key, UFID, mask, stats, and actions. `new` installs a flow using key, UFID, mask, and actions. The schema models recursive/nested action and key structures: encapsulation nests keys, actions can set keys, sample nested actions, perform conntrack/NAT, output/userspace, VLAN/MPLS/ETH push/pop, tunnel operations, packet length branching, TTL decrement, and psample.

State and persistence: flow entries, masks, actions, stats, and last-used timestamps live in the OVS kernel datapath. They are runtime forwarding state and are usually controlled by OVS userspace; they do not persist across datapath deletion, module unload, or reboot unless recreated.

Dependencies and integration points: integrates with OVS datapath netlink, flow miss/upcall handling, tunnel metadata, conntrack, NAT, NSH, VXLAN, psample, and userspace daemons that program datapath flows. It shares `ovs-header` with the datapath family.

Risks: recursive keys and actions are complex and easy to encode incorrectly. Binary structs must match `linux/openvswitch.h` layout and endian expectations. Flow masks must align with keys; bad masks can cause incorrect matching or kernel rejection. Action lists can contain nested actions and side effects such as conntrack commit and NAT. Only `get` and `new` are modeled here, so modify/delete behavior is outside this partial spec.

Test signals: generate and parse representative L2/L3/L4 keys, UFID lookup, masked flow creation, action-list nesting, tunnel and conntrack/NAT attrs, stats decoding after traffic, dump behavior, and rejection of malformed recursive nests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_flow.yaml -->
