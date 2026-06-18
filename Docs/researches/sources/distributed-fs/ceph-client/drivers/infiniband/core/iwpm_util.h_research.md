# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.h

## Purpose
This private header defines the internal IWPM utility contract shared between the IWPM message layer and the iWARP CM. It centralizes constants, request/mapping/remote-info data structures, registration state representation, and function prototypes for netlink and address mapping helpers.

## Important APIs, Types, And Functions
Constants include netlink retry/timeout limits, mapinfo batching count, daemon PID sentinel values, and registration flags `IWPM_REG_UNDEF`, `IWPM_REG_VALID`, and `IWPM_REG_INCOMPL`. `struct iwpm_nlmsg_request` represents an in-flight synchronous netlink request. `struct iwpm_mapping_info` stores original and mapped local addresses with client ID and flags. `struct iwpm_remote_info` stores mapped local/remote addresses and the original remote address. `struct iwpm_admin_data` stores the global sequence and per-client registration bits. The inline `iwpm_validate_nlmsg_attr()` rejects missing required attributes.

## Control Flow
No executable flow beyond the inline validator is defined here. The types describe request allocation and lookup by sequence, mapinfo persistence for replay, remote-info one-shot storage for passive accepts, and registration state checks before netlink requests.

## State And Persistence
The structures are runtime-only kernel state. Request objects are transient and kref-managed; mapping and remote-info objects persist in hash tables until removed or consumed; registration state persists until IWPM exit or daemon state changes.

## Dependencies And Integration Points
The header depends on Linux networking, netlink, spinlock, workqueue, mutex, delay, jhash, kref, and RDMA IWPM/netlink UAPI headers. It is included by `iwpm_msg.c` and `iwpm_util.c`, and its declarations support `iwcm.c` mapping paths.

## Risks And Test Signals
Risks are ABI and contract drift: timeout constants, registration bits, request fields, sockaddr record layouts, and mandatory-attribute assumptions must remain aligned with the message parser and userspace daemon. Tests should compile all IWPM users and exercise callback policies, missing attributes, request lifetime, and mapinfo/reminfo storage.
