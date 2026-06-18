# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_msg.c

## Purpose
This file implements the iWARP Port Mapper netlink protocol message layer. It sends kernel requests to the userspace `iwpmd` port mapper, processes responses and notifications, negotiates ABI version, tracks the userspace daemon PID, and bridges synchronous CM mapping calls to asynchronous RDMA netlink callbacks.

## Important APIs, Types, And Functions
Request APIs include `iwpm_valid_pid()`, `iwpm_register_pid()`, `iwpm_add_mapping()`, `iwpm_add_and_query_mapping()`, and `iwpm_remove_mapping()`. Registered callbacks include `iwpm_register_pid_cb()`, `iwpm_add_mapping_cb()`, `iwpm_add_and_query_mapping_cb()`, `iwpm_remote_info_cb()`, `iwpm_mapping_info_cb()`, `iwpm_ack_mapping_info_cb()`, `iwpm_mapping_error_cb()`, and `iwpm_hello_cb()`. Global state includes `iwpm_user_pid`, `iwpm_ulib_version`, `iwpm_ulib_name`, and `echo_nlmsg_seq`.

## Control Flow
Registration multicasts a PID request containing interface/device/library identity and waits on an `iwpm_nlmsg_request`. The response verifies identity and ABI, records daemon PID and ABI version, marks the client valid, and wakes the waiter. Add and query mapping requests build netlink messages with local/remote socket addresses and optional flags, unicast to the daemon, and block until callbacks validate the response and copy mapped addresses into the caller's buffer. Remove mapping sends a best-effort unicast delete. Remote-info notifications store passive peer address translations. Mapping-info and hello callbacks handle daemon startup/restart, mapinfo replay, and ABI negotiation.

## State And Persistence
State is runtime-only and global to the IWPM client. `iwpm_user_pid` is undefined, unavailable, or a daemon PID. `iwpm_ulib_version` controls optional flag attributes. `echo_nlmsg_seq` follows daemon sequence echoing and is included in outgoing requests. In-flight request state and mapping tables live in `iwpm_util.c`.

## Dependencies And Integration Points
The file depends on `iwpm_util.h`, RDMA netlink send helpers, netlink attribute parsing, IWPM UAPI constants, and CM callers in `iwcm.c`. It integrates synchronous kernel calls with userspace daemon responses through request semaphores and callback completion.

## Risks And Test Signals
Risks include daemon restart races, stale `iwpm_user_pid`, downlevel ABI behavior when flags are required, request timeouts, mismatched sequences, malformed sockaddr families, leaked requests on send failures, and global ABI/PID state shared across clients. Tests should cover no daemon, valid/invalid registration, ABI flag behavior, add/query/remove success and timeout, remote query reject, malformed families, remote-info storage/retrieval, daemon restart mapinfo replay, mapping errors, hello negotiation, and concurrent sequence matching.
