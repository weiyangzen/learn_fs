# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.c

## Purpose

`ib_srpt.c` implements the Linux SRP target fabric driver for target core. It advertises SRP target ports through InfiniBand Device Management MADs, accepts SRP login over IB CM or RDMA CM, creates target-core sessions, receives SRP commands, performs RDMA reads/writes through `rdma_rw`, and sends SRP responses.

## Important APIs, Types, and Functions

Module parameters are `srp_max_req_size`, `srpt_srq_size`, and `srpt_service_guid`. HCA lifetime is handled by `srpt_add_one()` and `srpt_remove_one()`. Discovery is handled by `srpt_refresh_port()`, MAD registration, and `srpt_mad_recv_handler()`. Login and connection management are centered on `srpt_cm_req_recv()`, `srpt_cm_handler()`, `srpt_rdma_cm_handler()`, `srpt_cm_rtu_recv()`, `srpt_disconnect_ch()`, and `srpt_release_channel_work()`. I/O is handled by `srpt_recv_done()`, `srpt_handle_new_iu()`, `srpt_handle_cmd()`, `srpt_get_desc_tbl()`, `srpt_write_pending()`, `srpt_queue_response()`, and `srpt_send_done()`. Configfs target-fabric operations are collected in `srpt_template`.

## Control Flow

Initialization validates request and SRQ sizes, registers the target-core fabric template, then registers an RDMA client. Device add allocates a `srpt_device`, PD, optional SRQ, IB CM listener, event handler, and per-port `srpt_port` objects, then refreshes each port to cache LID/GID names and register a MAD agent. Configfs `fabric_make_wwn` and `fabric_make_tpg` map target-core portal groups to discovered RDMA port names, and enabling a TPG allows login.

For login, IB CM or RDMA CM request handlers normalize private data into `srp_login_req`, validate IU length, target enablement, and target port ID, create or find a nexus, allocate a channel, CQs/QP, send/receive context rings, target-core session, and response/reject payloads. The channel is added to the nexus, moved through RTR/RTS or RDMA-CM-established state, and a zero-length write triggers wait-list processing after the channel becomes live. Received SRP commands are parsed into target-core commands with scatterlists from direct, indirect, or immediate descriptors. Target core calls back for write-pending RDMA reads, data-in/status responses, task-management responses, aborts, and command release.

## State and Persistence Behavior

Global state includes the SRPT device list, shared memory-cache xarray, service GUID, RDMA CM listen port/ID, and locks. Per-HCA `srpt_device` state persists PD/lkey, optional SRQ, receive ring, event handler, and per-port array. Per-port state persists enablement, cached LID/GID/name data, target-core port IDs, configfs attributes, nexus list, and channel refcount. Per-channel state persists CM ID, QP/CQ, session pointer, request/response rings, send-queue credits, SRP request credits, command wait list, channel state, and release work. Per-command `srpt_send_ioctx` tracks target-core command state, RDMA contexts, immediate data receive ownership, and sense data.

## Dependencies and Integration Points

The file integrates RDMA verbs, IB MAD, IB CM, RDMA CM, `rdma_rw`, target-core fabric APIs, SCSI protocol definitions, and local SRPT/SRP wire structures. It registers `target_core_fabric_ops` named `srpt`, creates configfs attributes for RDMA CM port and TPG tuning, and depends on target-core session/tag management for command lifetimes. Port discovery and service advertisement depend on `ib_dm_mad.h`.

## Risks and Edge Cases

Concurrency and lifetime management are the dominant risks. Channel state is monotonic and protected by `spinlock`, but close paths can be entered from CM callbacks, configfs disable, session close, and QP completions. The zero-length write drain mechanism must run before freeing QP/CQ and rings. SRQ toggling disables the port and logs out sessions, but global SRQ state is per-HCA while the config attribute is per-port. Login rejection paths must not leak CM IDs after ownership transfer. Immediate-data buffers require 512-byte alignment and careful receive-buffer reposting after target command release. Request-limit and send-queue accounting must remain balanced across normal responses, aborts, failed sends, and delayed wait-list processing.

## Test Signals

Useful tests include module load/unload, RDMA device add/remove, configfs WWN/TPG create/drop/enable/disable, MAD GETs for all supported attributes, IB CM and RDMA CM login, invalid login length/target ID/disabled TPG rejection, multichannel relogin behavior, SRQ on/off transitions, direct/indirect/immediate SRP command descriptors, write-pending RDMA read, read data-in RDMA write, sense/residual response formatting, task management, initiator disconnect, target disable with live sessions, QP error/drain behavior, and KASAN/KCSAN/leak checks across rejection and teardown paths.
