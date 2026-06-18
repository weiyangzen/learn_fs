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
