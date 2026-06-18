# sources/distributed-fs/ceph-client/net/mptcp/pm_netlink.c

## Purpose

`pm_netlink.c` is the generic-netlink front door for the MPTCP path-manager API. It registers the `MPTCP_PM_NAME` family, parses and formats endpoint address attributes, dispatches address operations either to the in-kernel PM or userspace PM depending on whether a token is present, and emits MPTCP path-management events to listeners.

## Important APIs, types, and functions

- `mptcp_genl_family`: exported generic-netlink family using generated `mptcp_pm_nl_ops` from `mptcp_pm_gen.h`.
- `mptcp_pm_parse_addr()` and `mptcp_pm_parse_entry()`: shared parsers for nested address attributes into `mptcp_addr_info` and `mptcp_pm_addr_entry`.
- `mptcp_pm_nl_get_addr_doit()` and `mptcp_pm_nl_get_addr_dumpit()`: netlink GET endpoint handlers.
- `mptcp_pm_nl_set_flags_doit()`: dispatches backup/fullmesh-like endpoint flag changes to userspace or kernel PM backends.
- `mptcp_event()`, `mptcp_event_addr_announced()`, `mptcp_event_addr_removed()`, `mptcp_event_pm_listener()`: multicast event producers for connection, subflow, address, and listener lifecycle events.
- `mptcp_userspace_pm_active()`: tests whether userspace PM event listeners exist in the socket netns.

## Control flow

Address parsing starts in `mptcp_pm_parse_pm_addr_attr()`: it validates nested policy, optional ID, required family when requested, IPv4/IPv6 address payload, and optional port. GET and SET handlers parse a user-provided endpoint and dispatch by the presence of `MPTCP_PM_ATTR_TOKEN`: no token means the global/kernel PM namespace, token means a specific MPTCP socket managed by userspace PM.

Event emission first checks for listeners on `MPTCP_PM_EV_GRP_OFFSET`, allocates an skb, writes event-specific attributes, and multicasts in the socket network namespace. `mptcp_event()` handles common connection/subflow events, while address announced/removed and listener events use dedicated helpers because they carry different attribute sets.

## State and persistence

This file does not own durable PM state. It serializes PM state owned by other modules into netlink messages and reads socket state through `mptcp_sock`, `mptcp_subflow_context`, and inet socket fields. The only persistent object here is the registered `mptcp_genl_family` and its multicast groups. Runtime events are transient skb messages.

## Dependencies and integration points

It depends on `protocol.h` for MPTCP socket/subflow structures and PM backend declarations, `mptcp_pm_gen.h` for generated netlink policies/ops, generic-netlink helpers, inet address helpers, and optional IPv6 support. It integrates with `pm_userspace.c` through token-dispatched functions and with the kernel PM via `mptcp_pm_nl_*` backend functions declared in `protocol.h`.

## Risks and edge cases

Important risks are netlink ABI compatibility, missing or mismatched address-family attributes, `-EMSGSIZE` paths while filling nested attributes, and correct GFP choice for event contexts. Event helpers intentionally return silently when no listeners exist; tests must not expect side effects without a subscribed multicast listener. IPv6 code is conditional, so AF_INET6 parsing/event coverage depends on `CONFIG_MPTCP_IPV6`.

## Test signals

Useful tests include generic-netlink endpoint add/get/dump/set-flag paths for kernel PM and token-scoped userspace PM, negative tests for missing family/address/port attributes, IPv4 and IPv6 event decoding, and listener-created/listener-closed multicast notifications. Runtime signals include `MPTCP_EVENT_*` messages, extack strings, and MPTCP PM selftests that exercise the `mptcp_pm` netlink family.
