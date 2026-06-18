# sources/distributed-fs/ceph-client/drivers/infiniband/core/user_mad.c

## Purpose

`user_mad.c` implements userspace Management Datagram access for InfiniBand/RDMA devices. It creates per-port `umadN` character devices for MAD send/receive, optional `issmN` devices for subnet-manager operation, lets userspace register MAD agents, maps reads and writes to the kernel MAD layer, and tears down agents/files when RDMA ports disappear.

## Important APIs, Types, and Functions

- `struct ib_umad_port` represents a physical RDMA port's userspace MAD devices, cdevs, devices, subnet-manager semaphore, file list, RDMA device pointer, and port number.
- `struct ib_umad_file` is per-open-file state: receive queue, send queue, agent slots, locks, waitqueue, P_Key ABI mode, and death flag.
- `struct ib_umad_packet` wraps outbound send buffers, inbound receive WCs, queued list node, length, and ABI header/data.
- `ib_umad_open`, `ib_umad_close`, `ib_umad_read`, `ib_umad_write`, `ib_umad_poll`, and ioctl handlers implement the main `umad` file operations.
- `ib_umad_reg_agent`, `ib_umad_reg_agent2`, and `ib_umad_unreg_agent` manage up to `IB_UMAD_MAX_AGENTS` per file via `ib_register_mad_agent`.
- `send_handler` and `recv_handler` are callbacks from the MAD core.
- `ib_umad_sm_open` and `ib_umad_sm_close` manage exclusive subnet-manager capability on `issm` nodes.
- `ib_umad_add_one`, `ib_umad_remove_one`, `ib_umad_init_port`, and `ib_umad_kill_port` integrate with RDMA device add/remove and cdev creation.

## Control Flow

Module init reserves fixed and dynamic character-device ranges, registers class `infiniband_mad`, and registers two RDMA clients: `umad` and `issm`. When an RDMA device is added, `ib_umad_add_one` allocates a flexible per-device container and initializes a port device for each port with `rdma_cap_ib_mad`. Each port gets `umadN`; ports with SMI capability also get `issmN`.

Opening `umadN` verifies the RDMA device is present and accessible from the caller's network namespace, allocates a file object, initializes queues/locks, and links it to the port's file list. Agent registration ioctls copy registration data, validate QPN and flags, choose an empty agent slot, convert method masks/OUI as needed, register a MAD agent, return the slot ID, and set P_Key ABI mode. `IB_USER_MAD_ENABLE_PKEY` must happen before first use.

Writes copy a userspace MAD header and initial MAD bytes, resolve the agent slot, build an address handle from LID/SL/path/GRH fields, determine RMPP behavior, allocate an `ib_mad_send_buf`, copy payload including multi-segment RMPP data, uniquify request TIDs by embedding the agent's high TID, reject duplicates on active sends, and call `ib_post_send_mad`. Send completion removes the packet from `send_list`, frees AH and send buffer, and queues a timeout packet back to userspace on response timeout. Receive callbacks translate WC metadata into userspace headers, including OPA LID handling and GRH extraction, and queue packets to `recv_list` unless the receive queue exceeds `MAX_UMAD_RECV_LIST_SIZE`.

Reads block until `recv_list` has data unless nonblocking. The code dequeues the first packet, copies either received MAD segments or send-timeout data to userspace, requeues the packet if userspace copy fails or the buffer is too small, and frees receive MAD resources on success.

Device removal deletes cdevs, marks `port->ib_dev` NULL, marks every open file's agents dead, wakes readers, unregisters all agents, frees minor IDs, and drops device references.

## State and Persistence

State is runtime cdev/class/device state plus per-port and per-file memory. Per-file persistence across syscalls includes registered agent slots, queued receive packets, active send packets, P_Key ABI mode, and the death flag. The subnet-manager device uses a semaphore to permit only one opener and toggles `IB_PORT_SM` while open.

## Dependencies and Integration Points

The file depends on the RDMA MAD core, RDMA address-handle helpers, RDMA netlink client info, character devices, sysfs class attributes, tracepoints under `trace/events/ib_umad.h`, network namespace checks, and OPA capability helpers. Userspace consumers include subnet managers, diagnostic tools, and libraries needing raw MAD access.

## Risks

This is a privileged protocol boundary with complex queueing. Risks include queue growth, duplicate TID handling, stale agent references during unregister/remove, RMPP buffer sizing, copy-to-user requeue behavior, and correct teardown while callbacks may be in flight. `MAX_UMAD_RECV_LIST_SIZE` bounds receive backlog, but high-volume MAD traffic can still stress memory. The P_Key ABI compatibility mode is stateful and must be set before use. `issm` open modifies port capabilities and must reliably clear them on close/removal.

## Test Signals

Signals include cdev creation for fixed and dynamic minors, netns access denial, agent register/unregister for QP0/QP1 and both ABI versions, P_Key enable-before-use behavior, simple MAD send/receive, timeout events, RMPP multi-segment reads/writes with small and full buffers, duplicate request rejection, poll readability/error transitions, `issm` exclusivity and port-cap toggling, and hot-remove while files and agents are active.
