# Research: subset-b-007652

This grouped report covers the Lustre LNet configuration library files assigned to `subset-b-007652`. Each section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnd.h -->
# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnd.h

## Purpose
`liblnd.h` is the small public header for LNet Driver (LND) tunable conversion helpers used by the LNet configuration library. It exposes the bridge between kernel/user-space LND tunable structures and the `cYAML` representation emitted or consumed by `lnetctl` YAML workflows.

## Important APIs and Types
- `lustre_net_show_tunables(struct cYAML *tunables, struct lnet_ioctl_config_lnd_cmn_tunables *cmn)` serializes common network tunables such as peer timeout and credit counts.
- `lustre_ni_show_tunables(struct cYAML *lnd_tunables, __u32 net_type, struct lnet_lnd_tunables *lnd, bool backup)` serializes driver-specific tunables for O2IB, EFA, socket, and conditionally KFI/GNI networks.
- `lustre_yaml_extract_lnd_tunables(struct cYAML *tree, __u32 net_type, struct lnet_lnd_tunables *tun)` parses driver-specific `lnd tunables` YAML back into kernel ioctl tunable structures.
- The header depends on `struct lnet_lnd_tunables`, `struct lnet_ioctl_config_lnd_cmn_tunables`, `__u32`, and `struct cYAML`.

## Control Flow
The header itself has no executable control flow. Callers in `liblnetconfig.c` use these functions while showing network details and while extracting tunables from YAML network or interface blocks. The implementations in `liblnetconfig_lnd.c` dispatch by `net_type`, returning success for supported LNDs, no-match for unsupported show paths, or `false` for unsupported YAML extraction.

## State and Persistence
No state is stored by this header. The API mutates caller-owned `cYAML` trees on show and caller-owned tunable structs on YAML extraction. Persistent behavior occurs only after `liblnetconfig.c` later sends the populated structures to LNet kernel ioctls.

## Dependencies and Integration Points
This file includes Linux LNet UAPI headers, `socklnd` definitions, and `cyaml.h`. It integrates with `liblnetconfig.c` network show/configuration paths and with `liblnetconfig_lnd.c`, which provides the concrete serialization/extraction logic.

## Risks and Edge Cases
The API trusts callers to pass a valid `net_type` and correctly sized tunable union. Unsupported or conditionally compiled LNDs are intentionally absent at runtime, so callers must treat no-match/false as non-fatal when a network type has no user-space tunables. `backup` output can omit fields that are useful for inspection but not necessary or desirable for reconfiguration.

## Test Signals
Useful tests should verify show/extract round trips for each built LND, no-match handling for unsupported LNDs, backup-mode omission behavior, and null-allocation failure propagation through `cYAML_create_*` return checks in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig.c -->
# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig.c

## Purpose
`liblnetconfig.c` is the main user-space implementation of Lustre LNet configuration APIs. It exposes direct C APIs and YAML-driven APIs for bringing LNet up/down, configuring local NIs, routes, peers, routing buffers, health/global tunables, fault rules, statistics, ping/discovery, and YAML dispatch. It is the central translation layer from `lnetctl`-style input into LNet kernel ioctls, generic netlink YAML packets, sysfs module parameters, and process helpers.

## Important APIs and Types
- Library lifecycle: `lustre_lnet_config_lib_init()` and `lustre_lnet_config_lib_uninit()` register/unregister the LNet ioctl device.
- LNet setup: `lustre_lnet_config_ni_system()` uses legacy ioctls; `yaml_lnet_configure()` sends a generic netlink YAML `net:` request.
- Route APIs: `lustre_lnet_config_route()`, `lustre_lnet_del_route()`, and `lustre_lnet_show_route()` validate net/gateway/hop/priority inputs and call route ioctls.
- NI APIs: `lustre_lnet_parse_interfaces()`, `lustre_lnet_add_intf_descr()`, `lustre_lnet_add_ip_range()`, `lustre_lnet_resolve_ip2nets_rule()`, `lustre_lnet_config_ip2nets()`, `lustre_lnet_config_ni()`, `lustre_lnet_del_ni()`, and `lustre_lnet_show_net()`.
- Peer/manage APIs: `lustre_lnet_modify_peer()`, `lustre_lnet_show_peer()`, `lustre_lnet_list_peer()`, `lustre_lnet_ping_nid()`, `lustre_lnet_discover_nid()`, `lustre_lnet_show_peer_debug_info()`, and `lustre_lnet_set_peer_state()`.
- Global/settings APIs: routing enablement, buffers, health sensitivity, recovery interval/limit, response tracking, transaction timeout, retry count, max interfaces, discovery, drop-asym-route, NUMA range, LND timeout, recovery queues, stats show/reset, MR routing setup, sysctl setup, and service-id calculation.
- YAML entry points: `lustre_yaml_config()`, `lustre_yaml_del()`, `lustre_yaml_show()`, and `lustre_yaml_exec()` parse a `cYAML` tree and dispatch to lookup tables.
- Netlink/fault helpers: `yaml_netlink_setup_emitter()`, `yaml_netlink_complete_emitter()`, `yaml_lnet_fault_rule()`, and scalar mapping helpers `lnet_yaml_*_mapping()`.
- Local data structures include `lustre_lnet_ip_range_descr`, `lnet_dlc_network_descr`, `lnet_dlc_intf_descr`, `nid_node`, ioctl payload structs from LNet UAPI, and `cYAML` result/error trees.

## Control Flow
Direct APIs follow a consistent pattern: validate string/numeric inputs, translate them into LNet IDs or NIDs with libcfs helpers, populate ioctl/sysfs/netlink payloads, execute the kernel or system operation, then add a `cYAML_build_error()` status record. Show APIs allocate a root `cYAML` tree, iterate kernel objects by index or retrieved peer list, filter optional arguments, append entries, and either print immediately or merge the sequence/object into an existing caller-owned show root.

NI configuration has several paths. Legacy `ip2net` is copied straight into `lic_legacy_ip2nets`; explicit interfaces are converted to NIDs by inspecting socket interface addresses, GNI `/proc/cray_xt/nid`, KFI/CXI sysfs `nic_addr`, EFA wildcard address, or numeric PTL4 interface names. Structured `ip2nets` first matches interface addresses against IPv4 expression lists or IPv6 CIDR/netmask descriptors, then calls the same NI ioctl path. Each successful NI addition sends `IOC_LIBCFS_ADD_LOCAL_NI` with optional common/LND tunables and CPTs.

Route and peer operations expand NID strings, then perform one ioctl per gateway/peer NI. Route add tolerates `EEXIST`; peer add creates the primary peer first and then adds secondary NIDs, while peer delete can delete a full peer when only the primary NID is supplied.

YAML flows build a `cYAML` tree from input, iterate top-level keys, resolve a handler from the command-specific lookup table, and invoke the handler on either each sequence item or the singleton node. Handler functions mostly extract `cYAML` fields and call direct APIs. YAML config and show support route/net/ip2nets/peer/routing/buffers/global/numa/udsp/statistics, while YAML exec only performs ping/discover. UDSP add/delete/show implementation is in `liblnetconfig_udsp.c`; this file contributes handler dispatch and high-detail show helpers that embed constructed UDSP priority/preference data into net and peer show output.

## State and Persistence
Persistent state is mainly kernel LNet state, modified through `l_ioctl()` calls on `LNET_DEV_ID`: local NI membership, route table, peer table, routing buffers, health values, peer properties, NUMA range, stats reset, and recovery queues. Some global tunables are persisted only as live module parameters under `/sys/module/lnet/parameters/` and LND module parameter directories. KFI and GNI helpers read hardware/kernel state from `/sys/class/net`, `/sys/class/cxi`, and `/proc/cray_xt`. `lustre_lnet_setup_mrrouting()` and `lustre_lnet_setup_sysctl()` execute external helper programs, so their state effects are outside this process. In-process state is transient: allocated descriptors, NID arrays, YAML trees, and netlink parser/emitter state are freed before return.

## Dependencies and Integration Points
The file depends heavily on libcfs parsing/ioctl utilities (`libcfs_str2nid`, `cfs_parse_nidlist`, `cfs_expand_nidlist`, `cfs_expr_list_parse`, `l_ioctl`), Linux networking (`ifaddrs`, sockets, `SIOCGIFADDR`, `SIOCGIFFLAGS`), libyaml/generic netlink adapters provided elsewhere in the same library, `cYAML`, Lustre LNet UAPI structs and ioctl constants, RDMA service-id definitions, sysfs/procfs paths, and optional external helpers `ksocklnd-config` and `lnet-sysctl-config`. `Makefile.am` builds this file together with `liblnetconfig_lnd.c`, `liblnetconfig_udsp.c`, `liblnetconfig_netlink.c`, and `cyaml.c` into `liblnetconfig.la`.

## Risks and Edge Cases
Many functions mutate input strings in place through `strtok`, `strsep`, or `replace_sep`, so callers should not pass immutable/shared buffers. Some error reporting mixes library return codes with `errno` and negative errno values, making tests important around failure paths. The file contains several partial-success behaviors: route add continues on existing routes, peer add/delete may have already changed some NIDs before a later NID fails, and `ip2nets` no-match is treated as non-fatal in YAML handling. Show-path merge logic manually splices `cYAML` children and frees partial roots, so ownership bugs would surface as leaks or double frees. External command paths are restricted by basename checks but still invoke `system()`. Sysfs writes are live-system side effects and often require privileges. IPv6 range support is CIDR/netmask based, while IPv4 uses libcfs expression lists; mixed-family interfaces and down interfaces have explicit filtering behavior. Some paths assume LNet kernel ABI structure layouts, especially peer show bulk parsing and NI show bulk offsets.

## Test Signals
High-value tests include unit coverage for interface parsing with CPT expressions, NID range expansion, IPv4/IPv6 `ip2nets` matching, KFI `cxi` translation, route validation, peer add/delete primary-NID semantics, YAML handler dispatch for singleton and sequence nodes, tunable inheritance from net-level to local-NI-level YAML, global setting inversion for discovery, backup-mode output suppression, and error YAML contents for missing/bad inputs. Integration tests need privileged or mocked ioctl/sysfs/netlink layers to verify local NI add/delete, route iteration ending on `ENOENT`, peer list `E2BIG` resizing, stats reset/show, and recovery queue output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig.h -->
# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig.h

## Purpose
`liblnetconfig.h` is the public API contract for the Lustre LNet configuration library. It defines status codes, command names, data structures used by the user-space parser, and the exported direct/YAML/netlink helper functions consumed by `lnetctl` and other programs that configure or inspect LNet.

## Important APIs and Types
- Return code macros normalize common library outcomes onto negative errno values, including bad/missing/out-of-range parameters, no-match, match, skip, out-of-memory, and marshal failure.
- Command macros and `enum lnetctl_cmd` define the vocabulary used in YAML error/status records.
- Network/interface descriptors: `lnet_dlc_network_descr`, `lnet_dlc_intf_descr`, `lustre_lnet_ip2nets`, and `lustre_lnet_ip_range_descr` represent explicit interfaces, CPT expressions, and IPv4/IPv6 ip2nets ranges.
- UDSP descriptors: `lnet_ud_net_descr`, `lnet_ud_nid_descr`, `lnet_udsp`, and `union lnet_udsp_action` mirror kernel structures for user-defined selection policies.
- Direct LNet APIs cover system configure/unconfigure, route add/delete/show, NI add/delete/show, routing/global tunables, peer modification/show/list, ping/discover, stats, UDSP, peer debug, and peer state.
- YAML APIs `lustre_yaml_config()`, `lustre_yaml_del()`, `lustre_yaml_show()`, and `lustre_yaml_exec()` expose file/string driven configuration.
- Parser and helper APIs include NID/NID-range parsing, interface parsing, ip2nets resolution, LND KFI interface conversion, libyaml netlink setup/cleanup, and scalar mapping helpers.

## Control Flow
The header documents the intended API layering. Callers can either pass expanded arguments to direct functions or pass YAML to the four YAML entry points, which parse and dispatch internally. Netlink helper declarations support generic-netlink YAML exchange with the kernel, while lower-level parse helpers are exposed so CLI code can pre-validate and construct descriptor lists before direct calls.

## State and Persistence
The header has no runtime state, but most declared functions mutate live LNet state in the kernel, live module parameters under `/sys/module`, or caller-owned YAML/descriptor structures. The descriptor types own linked-list membership and sometimes parsed expression lists; callers and implementations must free them using exposed/freeing helpers such as `free_intf_descr()` and `lustre_lnet_free_list()`.

## Dependencies and Integration Points
It includes standard networking headers, libyaml, libnl generic netlink headers, libcfs utility headers, and Linux LNet UAPI headers. It is the shared contract between `lnetctl`, `liblnetconfig.c`, LND-specific helpers, UDSP helpers, netlink helpers, and kernel ABI structures in `linux/lnet`.

## Risks and Edge Cases
Because the API exposes raw linked-list descriptors and C strings, ownership and mutability expectations are important. Several direct APIs accept nullable optional filters, but others require mandatory strings or initialized descriptors; callers must follow the per-function contract. The UDSP structs are explicitly required to match kernel-space structures, so ABI drift is risky. Return code macros are negative errno values rather than a separate enum, which means callers must avoid assuming only one error domain. `LNET_MAX_NIDS_PER_PEER` bounds peer operations and rejects expanded NID strings beyond 128 entries.

## Test Signals
Header contract tests should compile representative callers against direct, YAML, and netlink helper APIs. Behavioral tests should verify documented optional/mandatory arguments, max-NID enforcement, descriptor initialization, linked-list cleanup, UDSP ABI expectations, and consistent interpretation of library return codes by CLI code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig_lnd.c -->
# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig_lnd.c

## Purpose
`liblnetconfig_lnd.c` implements the LND-specific tunable serialization and YAML extraction functions declared in `liblnd.h`. It keeps driver-specific fields out of the main LNet configuration implementation while allowing network show output and YAML config input to carry common and LND-specific tunables.

## Important APIs and Types
- `lustre_net_show_tunables()` emits common network tunables: `peer_timeout`, `peer_credits`, `peer_buffer_credits`, and `credits`.
- `lustre_ni_show_tunables()` dispatches by LND type and emits driver-specific fields for O2IB (`peercredits_hiw`, FMR/cache/send/timeout/TOS fields), EFA (`nqps`), SOCK (`conns_per_peer`, `timeout`, `tos`), optional KFI (`prov_*`, `auth_key`, `traffic_class`, `traffic_class_num`, `timeout`), and optional GNI (`timeout`).
- `lustre_yaml_extract_lnd_tunables()` dispatches by LND type and fills the corresponding union member of `struct lnet_lnd_tunables`.
- Static extraction helpers parse the `lnd tunables` YAML object and apply per-driver defaults for absent fields.

## Control Flow
Show helpers are linear serializers: each field calls `cYAML_create_number()` or `cYAML_create_string()` and returns `LUSTRE_CFG_RC_OUT_OF_MEM` on the first allocation failure. `lustre_ni_show_tunables()` chooses the helper based on `net_type`, with KFI and GNI branches included only when compile-time macros enable them.

YAML extraction helpers first locate the `lnd tunables` child object. If absent, they return `false` so the caller can distinguish "no LND tunables supplied" from supplied values. Present fields are copied from `cy_valueint` or `cy_valuestring`; absent fields get defaults such as O2IB `map_on_demand = UINT_MAX`, O2IB/SOCK `conns_per_peer = 1`, TOS `-1`, and most other numeric fields `0`. KFI string extraction copies `traffic_class` only if it is present and shorter than `LNET_MAX_STR_LEN`.

## State and Persistence
The file stores no global state. It only mutates caller-provided YAML trees or tunable structs. Persistence occurs later when `liblnetconfig.c` copies the populated `struct lnet_ioctl_config_lnd_tunables` into NI configuration ioctl payloads, or when show output is saved as backup YAML.

## Dependencies and Integration Points
It depends on `liblnd.h`, `liblnetconfig.h`, `cyaml`, libc/limits utilities, and LNet UAPI tunable structs. It is called from `liblnetconfig.c` during `lustre_lnet_show_net()` and YAML NI/ip2nets configuration. Compile-time integration depends on `HAVE_KFILND` and `HAVE_GNILND`.

## Risks and Edge Cases
Extraction does not perform numeric range validation; invalid or out-of-range values are left for later kernel/ioctl validation. Missing `lnd tunables` returns false even if common tunables are present, which is intentional but requires the caller to combine masks correctly. Backup mode suppresses KFI `traffic_class_num`, so backup YAML preserves the string-oriented configuration rather than runtime numeric detail. String copying for KFI traffic class avoids overflow by length check but silently leaves the field unchanged/default when the string is too long. Unsupported LND types produce no-match/false rather than hard errors.

## Test Signals
Tests should cover successful show output for each compiled LND, allocation failure on each emitted field, YAML extraction defaults for absent fields, KFI traffic-class length behavior, backup vs non-backup KFI output, unsupported LND return behavior, and integration with `liblnetconfig.c` tunable inheritance from network-level YAML to local NI entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig_lnd.c -->
