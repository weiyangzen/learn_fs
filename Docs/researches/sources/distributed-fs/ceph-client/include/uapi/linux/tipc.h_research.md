# sources/distributed-fs/ceph-client/include/uapi/linux/tipc.h

## Purpose
Defines the Transparent Inter-Process Communication socket ABI: addressing, priorities, subscriptions, events, socket options, group membership, bearer/link names, crypto key payloads, and deprecated address helper macros.

## Important APIs, Types, and Constants
Core service/socket structs include `tipc_socket_addr`, `tipc_service_addr`, `tipc_service_range`, `tipc_subscr`, `tipc_event`, `sockaddr_tipc`, `tipc_group_req`, `tipc_sioc_ln_req`, `tipc_sioc_nodeid_req`, and variable-length `tipc_aead_key`. Constants define importance levels, scopes, address types, ancillary data objects, socket options (`TIPC_IMPORTANCE` through `TIPC_NODELAY`), group flags, max name sizes, SIOC protocol-private queries, AEAD key sizes, and rekeying. Deprecated macros and inline helpers encode/decode zone/cluster/node addresses.

## Control Flow, State, and Persistence
Userspace creates AF_TIPC sockets, binds to service names/ranges, subscribes for topology events, joins groups, queries bearer/link identity, and installs crypto keys. Kernel TIPC maintains name tables, subscriptions, socket queues, groups, node/bearer/link state, and key material.

## Dependencies and Integration Points
Depends on fixed-width types and socket constants; integrates with `sockios.h` protocol-private range, TIPC core, generic socket APIs, and cluster applications.

## Risks and Test Signals
Risks include deprecated 32-bit address helpers, variable-length key sizing, subscription timeout/filter misuse, queue-depth read-only options, and unknown future socket options. Test bind/connect/sendmsg/recvmsg, subscriptions/events, group join/leave, node/link SIOC queries, AEAD key min/max validation, and old address macro compatibility.
