# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.c

## Purpose
This file provides the utility and state-management layer for the iWARP Port Mapper. It manages in-flight netlink requests, local mapping-info and remote-info hash tables, registration state, sockaddr comparison/hashing, netlink message allocation/parsing, mapinfo replay, and hello responses.

## Important APIs, Types, And Functions
Lifecycle APIs are `iwpm_init()` and `iwpm_exit()`. Mapping APIs are `iwpm_create_mapinfo()`, `iwpm_remove_mapinfo()`, `iwpm_add_remote_info()`, `iwpm_get_remote_info()`, `iwpm_send_mapinfo()`, and `iwpm_mapinfo_available()`. Request APIs are `iwpm_get_nlmsg_request()`, `iwpm_free_nlmsg_request()`, `iwpm_find_nlmsg_request()`, `iwpm_wait_complete_req()`, and `iwpm_get_nlmsg_seq()`. Registration and helper APIs include `iwpm_get_registration()`, `iwpm_set_registration()`, `iwpm_check_registration()`, `iwpm_compare_sockaddr()`, `iwpm_create_nlmsg()`, `iwpm_parse_nlmsg()`, `iwpm_print_sockaddr()`, and `iwpm_send_hello()`.

## Control Flow
Initialization allocates mapinfo and remote-info hash tables and marks registration undefined. Mapinfo creation hashes original and mapped local sockaddr pairs under `iwpm_mapinfo_lock`; removal deletes the matching mapped address. Remote info is keyed by mapped local and mapped remote sockaddrs, then consumed once by passive CM request processing. Netlink requests are linked into an in-process list, protected by `iwpm_nlmsg_req_lock`, and completed by callbacks via a semaphore. `iwpm_send_mapinfo()` batches persisted mapinfo records into multipart netlink messages and sends a final count message to the daemon.

## State And Persistence
All state is runtime-only. Request list, mapinfo table, and remote-info table are protected by separate spinlocks. `iwpm_admin.nlmsg_seq` is the atomic sequence generator, and `reg_list[]` stores per-client registration bits. Mapinfo persists while connections/listeners are mapped so it can be replayed to a restarted daemon.

## Dependencies And Integration Points
The file depends on RDMA netlink helpers, IWPM UAPI definitions, Linux jhash, socket address structures, skbuff allocation, semaphores, krefs, and spinlocks. `iwpm_msg.c` uses these utilities to implement synchronous request/response behavior, and `iwcm.c` relies on mapinfo/reminfo for address translation.

## Risks And Test Signals
Risks include freeing hash buckets while callbacks add records, request kref/list races, timeout paths racing with late callbacks, mapinfo replay while dropping the lock between skbs, duplicate mapinfo records, and hash collisions requiring exact sockaddr comparison. Tests should cover init/exit, duplicate add/remove, IPv4/IPv6 comparison, invalid families, request timeout and late callback, concurrent lookup/free, mapinfo replay spanning multiple skbs, skb allocation failure, ack count mismatch, one-shot remote-info retrieval, and registration bit transitions.
