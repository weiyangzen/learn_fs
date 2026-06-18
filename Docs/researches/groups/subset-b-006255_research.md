<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.c

## Purpose
CALIPSO/IPv6 NetLabel glue. It exposes the Generic Netlink family for CALIPSO DOI administration and provides wrapper entry points used by the rest of NetLabel to call the actual CALIPSO packet engine registered through `netlbl_calipso_ops_register()`.

## APIs, Types, and Functions
Important local types are `netlbl_calipso_doiwalk_arg` for multipart DOI dumps and `netlbl_domhsh_walk_arg` for removing domain mappings tied to a DOI. The exported registration API is `netlbl_calipso_ops_register()`. Netlink handlers implement `ADD`, `REMOVE`, `LIST`, and `LISTALL` through `netlbl_calipso_add()`, `netlbl_calipso_remove()`, `netlbl_calipso_list()`, and `netlbl_calipso_listall()`. Public wrappers include `calipso_doi_add/remove/getdef/putdef/walk`, socket/request/sk_buff label operations, option parsing, and cache operations.

## Control Flow
`ADD` requires DOI and mapping type, currently accepts `CALIPSO_MAP_PASS`, allocates `struct calipso_doi`, then delegates to `calipso_doi_add()`. `LIST` gets a referenced DOI definition, emits type data into a reply skb, and releases the reference. `LISTALL` streams DOI/type pairs using the packet engine walk cursor stored in `cb->args[0]`. `REMOVE` first walks the domain hash and removes all CALIPSO mappings for the DOI, then removes the DOI itself and decrements `netlabel_mgmt_protocount` on success. The wrapper functions read the registered ops pointer and return `-ENOMSG` or NULL when no CALIPSO engine is registered.

## State and Persistence
The only local persistent state is the global `calipso_ops` pointer and the `__ro_after_init` Generic Netlink family. DOI state, label caches, and references live in the IPv6 CALIPSO engine. Mapping persistence is coordinated through `netlabel_domainhash.c`; protocol enablement is reflected in `netlabel_mgmt_protocount`.

## Dependencies and Integration
Depends on Generic Netlink, audit helpers, `net/calipso.h`, domain hash walking/removal, and the management protocol count. The file is compiled only when IPv6 CALIPSO support is relevant, while `netlabel_calipso.h` provides a no-op init when IPv6 is disabled.

## Risks and Test Signals
Risks include a missing or late CALIPSO ops registration, limited netlink support for only pass-through mappings, stale mappings if domain-hash removal partially fails, and refcount misuse around DOI get/put wrappers. Test signals should cover netlink add/list/listall/remove, remove with attached domain mappings, no-ops when IPv6/CALIPSO ops are absent, and cache/socket/sk_buff wrapper delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.h

## Purpose
Private NetLabel CALIPSO interface declaration. It documents the userspace Generic Netlink payload contract and declares the internal CALIPSO wrappers consumed by management, KAPI, and domain-hash code.

## APIs, Types, and Functions
Defines `NLBL_CALIPSO_C_*` commands for `ADD`, `REMOVE`, `LIST`, and `LISTALL`, plus `NLBL_CALIPSO_A_DOI` and `NLBL_CALIPSO_A_MTYPE` attributes. Declares `netlbl_calipso_genl_init()` conditionally on IPv6, DOI lifecycle functions, socket/request/sk_buff label functions, `calipso_optptr()`, `calipso_getattr()`, and CALIPSO cache helpers.

## Control Flow
This header is declarative, but it encodes the netlink contract: DOI and mapping type are required for add, DOI is required for remove/list, and dump replies expose DOI/type tuples. When `CONFIG_IPV6` is disabled, `netlbl_calipso_genl_init()` becomes an inline success path so global NetLabel init can proceed without a CALIPSO family.

## State and Persistence
No state is stored here. The declarations imply externally managed DOI reference ownership: callers that receive a DOI from `calipso_doi_getdef()` must release it with `calipso_doi_putdef()`.

## Dependencies and Integration
Includes `net/netlabel.h` and `net/calipso.h`. It is the bridge between NetLabel code and the IPv6 CALIPSO implementation, letting NetLabel build even when CALIPSO packet support is provided elsewhere or compiled out.

## Risks and Test Signals
Risks are contract drift between documented netlink attributes and `netlabel_calipso.c`, missing IPv6 guard coverage, and misuse of DOI references by callers. Test signals include compile coverage with IPv6 enabled and disabled, netlink policy conformance, and sparse/lockdep checks at call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.c

## Purpose
CIPSO/IPv4 NetLabel administration layer. It registers the CIPSOv4 Generic Netlink family and translates userspace DOI mapping requests into `cipso_v4_doi` definitions for the IPv4 CIPSO engine.

## APIs, Types, and Functions
Local walk-argument structs support DOI dumps and domain-hash cleanup. `netlbl_cipsov4_genl_policy` defines DOI, mapping type, tag list, MLS level, and category attributes. Key handlers are `netlbl_cipsov4_add_common()`, `netlbl_cipsov4_add_std()`, `netlbl_cipsov4_add_pass()`, `netlbl_cipsov4_add_local()`, `netlbl_cipsov4_add()`, `netlbl_cipsov4_list()`, `netlbl_cipsov4_listall()`, and `netlbl_cipsov4_remove()`. `netlbl_cipsov4_genl_init()` registers the family.

## Control Flow
`ADD` validates DOI/type, then dispatches by mapping type. Standard translated mappings parse nested tag, level, and optional category lists twice: first to size local/remote arrays and then to fill bidirectional mappings initialized to invalid sentinels. Pass and local mappings only need common DOI/tag parsing. `LIST` builds a reply from the current DOI definition under RCU; for large translated maps it retries with larger skbs up to a small fixed multiplier. `LISTALL` streams DOI/type pairs via `cipso_v4_doi_walk()`. `REMOVE` removes matching domain mappings before removing the DOI.

## State and Persistence
Persistent DOI definitions are owned by the CIPSO engine. This file mutates global protocol state only through `netlabel_mgmt_protocount` after DOI add/remove. Netlink dump cursors are stored in callback args. Domain mapping cleanup persists in the domain hash and drops DOI references there.

## Dependencies and Integration
Depends on Generic Netlink, RCU, audit helpers, `net/cipso_ipv4.h`, `netlabel_domainhash`, and management counters. It integrates with KAPI and management code indirectly through the shared CIPSO DOI registry and domain hash.

## Risks and Test Signals
Risks include malformed nested netlink attributes, memory sizing mistakes for translated MLS arrays, retry exhaustion in `LIST`, mismatched DOI reference lifetime during removal, and policy looseness from deprecated non-strict validation. Test signals should include add/list/remove for all mapping types, invalid tag/level/category bounds, multipart dumps, domain-map cleanup on DOI removal, and leak/refcount checks on failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.h

## Purpose
Private declaration and userspace ABI description for the NetLabel CIPSOv4 Generic Netlink family.

## APIs, Types, and Functions
Defines command IDs for add, remove, list, and dump operations, and attribute IDs for DOI, mapping type, tag entries/lists, MLS level local/remote mappings, category local/remote mappings, and nested selector lists. Declares `netlbl_cipsov4_genl_init()`.

## Control Flow
The header documents the required payload shapes consumed by `netlabel_cipso_v4.c`: translated mappings require tag, level, and category lists; pass/local mappings require DOI, type, and tags only; list replies mirror the DOI mapping type.

## State and Persistence
No runtime state. It fixes the command and attribute numbers that userspace tools and the kernel handlers must agree on, making it an ABI-sensitive file.

## Dependencies and Integration
Includes `net/netlabel.h` and references constants from `cipso_ipv4.h` in comments. It is consumed by the CIPSO netlink implementation and by global NetLabel netlink initialization.

## Risks and Test Signals
Risks include ABI drift, typo-prone nested attribute contracts, and mismatches with the netlink policy array. Test signals are userspace netlabelctl compatibility, attribute fuzzing, and build checks that `NLBL_CIPSOV4_A_MAX` matches the policy table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_cipso_v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.c

## Purpose
Central NetLabel domain-to-protocol mapping table. It maps LSM domains and optional address selectors to unlabeled, CIPSOv4, or CALIPSO label definitions, with RCU lookup for packet/socket fast paths and audited update operations.

## APIs, Types, and Functions
`netlbl_domhsh_tbl` holds buckets. Global state includes `netlbl_domhsh`, default IPv4/IPv6 mappings, and `netlbl_domhsh_lock`. Helpers handle RCU freeing, hashing, family matching, exact/default search, auditing, and validation. Public APIs initialize, add, remove whole entries/defaults/address selectors, get domain/address matches, and walk the hash table.

## Control Flow
Initialization allocates power-of-two buckets. Add validates entry family/protocol consistency, rejects duplicates, then inserts either a named bucket entry or default family entry. Address-selector additions can merge new selectors into an existing address-select mapping after duplicate checks. Removal marks entries invalid under the spinlock, unlinks or clears default pointers, audits, drops DOI references, and frees after RCU. Address-selector removal deletes one selector, synchronizes RCU before freeing selector memory, and removes the parent mapping if empty. Lookups run under caller-held RCU read lock and fall back to defaults.

## State and Persistence
Mappings persist in RCU-protected global hash/default pointers until explicitly removed. Entries carry `valid` bits to make removal visible before memory reclamation. Named domains own copied strings; DOI-backed mappings hold references that are released on removal.

## Dependencies and Integration
Depends on address-list helpers, audit helpers, CIPSO/CALIPSO DOI refcount APIs, RCU lists, and spinlocks. It is used by management netlink, KAPI socket/packet paths, and DOI removal code that cleans dependent mappings.

## Risks and Test Signals
Risks include default AF_UNSPEC splitting semantics, duplicate selector merge handling, RCU lifetime mistakes, `synchronize_rcu()` latency for selector deletes, and validation gaps for mixed family/protocol entries. Test signals should include concurrent lookup while add/remove, default fallback, selector specificity, DOI put on removal, duplicate rejection, and hash walk cursor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.h

## Purpose
Internal data model and API for NetLabel domain hash mappings.

## APIs, Types, and Functions
Defines `NETLBL_DOMHSH_BITSIZE`, address selector containers `netlbl_domaddr_map`, `netlbl_domaddr4_map`, `netlbl_domaddr6_map`, generic mapping union `netlbl_dommap_def`, and top-level `netlbl_dom_map`. Declares initialization, add/remove, default remove, IPv4/IPv6 selector removal, direct and address-specific lookups, and `netlbl_domhsh_walk()`.

## Control Flow
Callers allocate and populate `netlbl_dom_map` and optional selector lists, then transfer ownership to `netlbl_domhsh_add()`. Lookup callers are expected to hold RCU read protection. Remove APIs select whole-domain or family/address-specific paths.

## State and Persistence
The structs define ownership-sensitive persistent state: `domain` strings, DOI pointers, selector lists, `valid` flags, RCU heads, and list links. The header exposes that entries are RCU-managed and that selector definitions embed address-list nodes.

## Dependencies and Integration
Includes RCU/list primitives and `netlabel_addrlist.h`. It is shared by NetLabel KAPI, management netlink, CIPSO/CALIPSO DOI cleanup, and unlabeled default setup.

## Risks and Test Signals
Risks include callers misunderstanding ownership transfer, missing RCU read locks, and conditional IPv6 declaration drift. Test signals are sparse/RCU annotations, compile coverage with IPv6 toggled, and KAPI/management add-remove round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_kapi.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_kapi.c

## Purpose
Kernel-facing NetLabel API. It provides configuration helpers for LSMs/protocol engines, category bitmap utilities, socket/request/sk_buff labeling operations, cache management, audit entry points, and subsystem initialization.

## APIs, Types, and Functions
Configuration APIs include `netlbl_cfg_map_del()`, unlabeled map/static add/remove, CIPSO/CALIPSO DOI add/remove/map add. Category helpers include `netlbl_catmap_walk()`, `walkrng()`, `getlong()`, `setbit()`, `setrng()`, `setlong()`. Bitmap helpers are `netlbl_bitmap_walk()` and `netlbl_bitmap_setbit()`. Runtime APIs include `netlbl_enabled()`, socket/request/connection/sk_buff set/get/delete operations, `netlbl_skbuff_err()`, cache invalidate/add, and `netlbl_audit_start()`. `netlbl_init()` wires the subsystem at `subsys_initcall`.

## Control Flow
Config map helpers allocate domain entries or selector maps, take DOI references, and transfer ownership to the domain hash. Socket and packet label setters look up the domain and destination address under RCU, then dispatch to CIPSOv4, CALIPSO, or unlabeled deletion/no-op behavior. Receive-side `netlbl_skbuff_getattr()` tries packet-provided labels first and falls back to static unlabeled mappings. Init builds the domain hash, unlabeled hash, netlink families, and default unlabeled allow policy, panicking on failure.

## State and Persistence
Persistent state lives mostly outside this file: domain hash mappings, DOI registries, protocol caches, and unlabeled static maps. Locally, category maps are caller-owned linked bitmap chunks. `netlbl_enabled()` reflects global `netlabel_mgmt_protocount`.

## Dependencies and Integration
Integrates LSM callers with `net/cipso_ipv4.h`, CALIPSO wrappers, Generic Netlink setup, unlabeled fallback, address-list helpers, audit, RCU, and socket/sk_buff internals. Several exported symbols are used by security modules and protocol engines.

## Risks and Test Signals
Risks include GFP_ATOMIC allocation failures, incorrect address-family dispatch, missing socket locks, catmap range overflow, protocol count drift, and init-time panic on netlink or default-config failure. Test signals should cover config API round trips, IPv4/IPv6 address selectors, catmap sparse/range operations, lockdep for socket paths, receive fallback to unlabeled, cache add only when `NETLBL_SECATTR_CACHE` is set, and boot init logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_kapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.c

## Purpose
Generic Netlink management interface for NetLabel domain mappings and protocol metadata. It lets privileged users add/remove/list domain mappings and defaults, query supported protocols, and retrieve the NetLabel protocol version.

## APIs, Types, and Functions
Defines global `atomic_t netlabel_mgmt_protocount`. Uses `netlbl_domhsh_walk_arg` for dumps. `netlbl_mgmt_add_common()` parses add/add-default payloads, while `netlbl_mgmt_listentry()` serializes mappings. Command handlers include add, remove, listall, adddef, removedef, listdef, protocols, and version. `netlbl_mgmt_genl_init()` registers the family.

## Control Flow
Add paths validate mutually exclusive IPv4/IPv6 selector attributes, copy optional domain strings, resolve CIPSO/CALIPSO DOI references, optionally build address-selector maps, and call `netlbl_domhsh_add()`. Remove deletes a named domain for all families; removedef deletes defaults. Listall walks the domain hash with bucket/chain cursors. Listdef looks up a family-specific default and serializes it. Protocol dumps emit unlabeled, CIPSOv4, and optionally CALIPSO.

## State and Persistence
The management counter tracks configured protocols and is incremented/decremented by DOI/static mapping layers as well as management-adjacent operations. Persistent mappings are transferred into the domain hash; on parse failures this file releases domain strings, selector allocations, and DOI references.

## Dependencies and Integration
Depends on Generic Netlink, CIPSO/CALIPSO DOI lookup, domain hash APIs, audit info from `netlabel_user.h`, and IPv4/IPv6 address helpers. It is registered by `netlbl_netlink_init()`.

## Risks and Test Signals
Risks include attribute validation gaps for binary address attrs in this policy, DOI reference leaks on complex add failure paths, counter drift, and dump truncation behavior when an skb fills. Test signals should include netlink add/list/remove for direct and selector mappings, default family behavior, protocol/version queries, DOI missing cases, and IPv6-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.h

## Purpose
Private ABI declaration for the NetLabel management Generic Netlink family and shared configured-protocol counter.

## APIs, Types, and Functions
Defines management commands for add/remove/listall/default operations, protocol enumeration, and version query. Defines attributes for domain, protocol, version, CIPSO DOI, CALIPSO DOI, IPv4/IPv6 addresses and masks, address selector nesting, selector list nesting, and family. Declares `netlbl_mgmt_genl_init()` and `netlabel_mgmt_protocount`.

## Control Flow
No executable control flow. The comments specify required request and reply payloads, including how selector-list mappings differ from direct protocol mappings and how default operations can optionally target a family.

## State and Persistence
The header exposes `netlabel_mgmt_protocount`, a global atomic used to decide whether NetLabel is enabled. Command/attribute enum values are persistent userspace ABI.

## Dependencies and Integration
Includes `net/netlabel.h` and atomic primitives. Used by management implementation, KAPI enable checks, DOI handlers, and unlabeled static-label code.

## Risks and Test Signals
Risks include ABI drift, misspelled/documented selector requirements diverging from code, and protocol count misuse by non-management components. Test signals are userspace compatibility, netlink policy coverage, and compile checks across IPv6 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.c

## Purpose
Unlabeled-packet support for NetLabel. It manages static fallback labels by interface and source address, exposes a Generic Netlink interface for those labels and the accept flag, and supplies receive-side security attributes when packets lack protocol labels.

## APIs, Types, and Functions
Local persistent types include `netlbl_unlhsh_tbl`, IPv4/IPv6 address entries with secids, and per-interface `netlbl_unlhsh_iface`. Public functions are `netlbl_unlabel_genl_init()`, `netlbl_unlabel_init()`, `netlbl_unlhsh_add()`, `netlbl_unlhsh_remove()`, `netlbl_unlabel_getattr()`, and `netlbl_unlabel_defconf()`. Netlink handlers cover accept/list, static add/remove/list, and default static add/remove/list.

## Control Flow
Static add resolves an interface in `init_net` or default interface, creates an interface bucket entry if needed, inserts an ordered address-list entry, audits, and increments the protocol count. Remove deletes the matching address entry, audits, conditionally removes now-empty interface entries, and decrements the count. Device-down notifications invalidate and RCU-free matching interface entries. Netlink parsing converts LSM security contexts to secids and enforces one address family per entry. Listing walks hash buckets, interface chains, and address-list cursors through `cb->args`.

## State and Persistence
State is global: RCU hash table `netlbl_unlhsh`, default interface pointer, `netlabel_unlabel_acceptflg`, netdevice notifier, address entries with secids, and Generic Netlink family metadata. The default boot configuration allows unlabeled packets and installs a default unlabeled domain mapping through the domain hash.

## Dependencies and Integration
Depends on address-list helpers, audit, LSM secctx/secid conversion, netdevice lookup/notifiers, Generic Netlink, domain-hash default configuration, and management protocol count. It is the final fallback used by `netlbl_skbuff_getattr()`.

## Risks and Test Signals
Risks include namespace limitations despite namespace-looking parameters, device-down cleanup races, IPv6 add helper returning 0 after nonzero add failures, accept-flag policy surprises, static-list cursor bugs, and protocol count imbalance on notifier cleanup. Test signals should cover static add/remove/list for interface/default and IPv4/IPv6, receive lookup by `skb_iif` and source address, accept flag off/on, device-down cleanup, and LSM context conversion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.h

## Purpose
Private command definitions and internal APIs for NetLabel unlabeled traffic handling.

## APIs, Types, and Functions
Defines commands for accept/list and static label add/remove/list operations, including default-interface variants. Defines attributes for accept flag, IPv4/IPv6 addresses and masks, interface name, and LSM security context. Declares hash size `NETLBL_UNLHSH_BITSIZE`, initialization, static add/remove, receive getattr, and default configuration functions.

## Control Flow
The comments specify netlink payload requirements: static mutations need address/mask pairs and usually an interface, default variants omit the interface, and accept toggles require a boolean flag. The receive API is designed to return secattrs for unlabeled packets or permit unlabeled traffic according to policy.

## State and Persistence
No state is stored in the header, but declarations correspond to persistent hash entries keyed by interface/address and to a global accept flag maintained in the C file.

## Dependencies and Integration
Includes `net/netlabel.h`. Used by KAPI configuration wrappers, global NetLabel initialization, netlink setup, and receive fallback.

## Risks and Test Signals
Risks include ABI drift, attribute naming mismatch (`NLA_NULL_STRING` in comments vs implementation policy), and callers passing incorrect address lengths. Test signals include netlink policy/enum alignment, IPv6-disabled builds, and add/remove/getattr integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_unlabeled.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.c -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.c

## Purpose
Shared NetLabel Generic Netlink and audit helper implementation.

## APIs, Types, and Functions
`netlbl_netlink_init()` registers management, CIPSOv4, CALIPSO, and unlabeled Generic Netlink families in order. `netlbl_audit_start_common()` starts an audit record, writes common NetLabel audit fields, and appends the current subject context.

## Control Flow
Netlink initialization stops at the first failed family registration and returns that error. Audit start exits early when auditing is off or allocation fails; otherwise it uses `audit_context()`, `GFP_ATOMIC`, loginuid/session values, and LSM subject properties from the supplied `netlbl_audit`.

## State and Persistence
No owned persistent state. Successful family registration persists in Generic Netlink core. Audit buffers are returned to callers, which must append event-specific fields and call `audit_log_end()`.

## Dependencies and Integration
Depends on management, CIPSOv4, CALIPSO, and unlabeled init functions, audit subsystem, security LSM property formatting, Generic Netlink, and init user namespace UID conversion.

## Risks and Test Signals
Risks include partial Generic Netlink registration without rollback if a later family fails, NULL audit buffers being normal when auditing is disabled, and callers forgetting to end audit records. Test signals include init failure injection, audit-off behavior, and representative add/remove audit log formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.h

## Purpose
Shared declarations for NetLabel netlink initialization and common audit helpers.

## APIs, Types, and Functions
Defines inline `netlbl_netlink_auditinfo()` to populate `struct netlbl_audit` from current LSM subject properties, loginuid, and audit session. Declares `netlbl_netlink_init()` and `netlbl_audit_start_common()`.

## Control Flow
The inline helper is called by netlink command handlers before audited mutations. It snapshots current credentials/audit identity for later use in event-specific audit records.

## State and Persistence
No persistent state. It fills caller-provided stack or heap audit metadata.

## Dependencies and Integration
Depends on security, audit, netlink, Generic Netlink, and `net/netlabel.h`. Used by all NetLabel Generic Netlink families and by domain/unlabeled audit paths.

## Risks and Test Signals
Risks include missing audit identity initialization before audited operations and assumptions about current task context. Test signals include audit field checks for management, DOI, and unlabeled commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/Kconfig -->
# sources/distributed-fs/ceph-client/net/netlink/Kconfig

## Purpose
Kconfig entry for optional Netlink socket diagnostics.

## APIs, Types, and Functions
Defines `CONFIG_NETLINK_DIAG` as a tristate named `NETLINK: socket monitoring interface`, defaulting to `n`, with help text identifying `ss` as a consumer.

## Control Flow
No runtime control flow. At configuration time this symbol determines whether the netlink diagnostic module/object is built.

## State and Persistence
The selected config value persists in kernel build configuration and drives Makefile object inclusion.

## Dependencies and Integration
Integrated by the networking Kconfig tree. The paired Makefile uses `obj-$(CONFIG_NETLINK_DIAG)` to include `netlink_diag.o`.

## Risks and Test Signals
Risks are minimal; the main concern is disabled diagnostic visibility unless selected. Test signals are Kconfig menu visibility, module/built-in builds, and `ss` netlink-monitoring functionality when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/Makefile -->
# sources/distributed-fs/ceph-client/net/netlink/Makefile

## Purpose
Build rules for the core netlink subsystem directory.

## APIs, Types, and Functions
Always builds `af_netlink.o`, `genetlink.o`, and `policy.o` into the networking core. Conditionally builds `netlink_diag.o` when `CONFIG_NETLINK_DIAG` is set, with `netlink_diag-y := diag.o`.

## Control Flow
No runtime control flow. Kbuild expands `obj-y` and `obj-$(CONFIG_NETLINK_DIAG)` based on the configuration.

## State and Persistence
Build output composition persists into the resulting kernel image or modules. Core netlink and Generic Netlink are always present for this tree.

## Dependencies and Integration
Integrates the netlink socket implementation, Generic Netlink support used by NetLabel, netlink policy validation, and optional diagnostic support.

## Risks and Test Signals
Risks include accidental omission of core objects breaking broad networking users, or diagnostic object mismatches with Kconfig. Test signals are allmodconfig/allyesconfig builds, boot smoke tests for Generic Netlink families, and `CONFIG_NETLINK_DIAG=m/y` module or built-in checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/Makefile -->
