# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set.h

## Purpose
Defines core ipset UAPI: protocol versions, command IDs, netlink attributes, error codes, command/create/CADT flags, dimensions, counter match structs, and legacy socket-option requests.

## Important APIs, Types, And Functions
Exports `IPSET_PROTOCOL`, `IPSET_MAXNAMELEN`, `ipset_cmd`, `IPSET_ATTR_*`, `ipset_errno`, `ipset_cmd_flags`, `ipset_cadt_flags`, `ipset_create_flags`, `ipset_adt`, `ip_set_id_t`, dimension/kopt enums, counter match structs, `SO_IP_SET`, and get/version request structs.

## Control Flow
Userspace manages sets through netlink commands: create/destroy/flush/rename/swap/list/save/add/del/test/header/type/get. Attributes nest command data and ADT entries; flags tune existence behavior, counters, comments, skb metadata, nomatch, and ordering.

## State, Persistence, And Dependencies
State persists in kernel ipset sets, elements, counters, comments, skbinfo, and references from firewall rules. Depends on `linux/types.h`.

## Integration Points
Used by ipset userspace, iptables/ip6tables match/target compatibility, and netfilter set lookups.

## Risks
Protocol version compatibility matters. Attribute spaces overlap by command context. Set IDs are 16-bit, and `IPSET_INVALID_ID` is a sentinel. Counter structs differ for backward compatibility.

## Test Signals
Validate protocol negotiation, all management commands, nested ADT parsing, restore line numbers, type revision min/max, counter/comment/skbinfo flags, legacy socket options, and type-specific error propagation.
