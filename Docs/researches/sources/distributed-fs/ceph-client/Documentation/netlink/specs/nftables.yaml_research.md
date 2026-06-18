# sources/distributed-fs/ceph-client/Documentation/netlink/specs/nftables.yaml

Purpose: describes the raw netlink API schema for nftables configuration, including tables, chains, rules, expressions, sets, set elements, objects, generation ids, flowtables, and batch messages.

Important APIs/types/functions: protocol is `netlink-raw`. Definitions include `nfgenmsg` fixed header, operation enums for metadata/bitwise/compare/NAT/table/chain/set/lookup/payload/exthdr/ct/socket/tproxy/osf/xfrm/synproxy/flowtable concepts, and multiple flag sets. The 48 attribute sets cover expression payloads (`log`, `numgen`, `range`, `bitwise`, `byteorder`, `cmp`, `lookup`, `dynset`, `payload`, `exthdr`, `meta`, `ct`, `limit`, `counter`, `quota`, `reject`, `nat`, `tproxy`, `socket`, `osf`, `xfrm`, `synproxy`, `dup`, `fwd`, `objref`, `immediate`, and more) plus top-level table, chain, rule, set, setelem, object, flowtable, hook, counter, userdata, and batch attrs.

Control flow: batch operations bracket atomic netfilter updates. Table/chain/rule/set/setelem/object/flowtable resources have create/get/delete/destroy-style operations. Get operations often support both do and dump forms. Rule creation carries table, chain or chain-id, handle/position, expressions, userdata, and compatibility data. Set operations configure key/data types, lengths, flags, timeout, garbage collection, policy, descriptions, expressions, and elements. Generation-id retrieval exposes current ruleset generation and process metadata.

State and persistence: this schema mutates nftables ruleset state in kernel netfilter tables. Changes are live kernel state and can be made atomically through batch messages. Persistence across reboot is normally handled by userspace ruleset save/restore, not by netlink itself.

Dependencies and integration points: integrates with netfilter/nftables raw netlink, expression evaluators, hooks, counters, sets/maps, stateful objects, and userspace tools such as `nft`. The `nfgenmsg` header and raw protocol distinguish it from Generic Netlink specs.

Risks: this is a dense schema with deeply nested expression and set element attributes; incomplete generator support can silently break rule encoding. Raw netlink plus nfgenmsg family/version/res-id handling has stricter framing requirements than Generic Netlink. Destroy and delete variants have subtly different semantics in nftables. Batch atomicity depends on correctly paired begin/end messages. Many binary data fields carry expression-specific layouts not fully self-describing from generic type alone.

Test signals: validate raw netlink header generation, batch begin/end framing, table/chain/rule/set/object/flowtable CRUD, dump and reset-get behavior, expression nesting for representative rule types, set element timeout/userdata paths, generation id checks, and rejection of malformed nested attributes.
