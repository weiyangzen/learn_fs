# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.c

## Purpose

`ib_srp.c` implements the Linux InfiniBand/RDMA SCSI RDMA Protocol initiator. It registers an RDMA client and SCSI transport, exposes `infiniband_srp` class devices for each local RDMA port, accepts target definitions through the `add_target` sysfs attribute, connects to SRP targets with either IB CM/path-record lookup or RDMA CM/IP routing, then translates SCSI midlayer commands into SRP information units and RDMA buffer descriptors.

## Important APIs, Types, and Functions

The main external integrations are `srp_attach_transport()`, `ib_register_client()`, `ib_sa_path_rec_get()`, `ib_create_cm_id()`, `rdma_create_id()`, `scsi_host_alloc()`, `srp_rport_add()`, and the `scsi_host_template` callbacks. Module parameters control SG limits, memory registration policy, timeout behavior, immediate data, and channel count. Important internal flows include `srp_add_one()`/`srp_remove_one()` for HCA lifetime, `add_target_store()` for target creation, `srp_new_cm_id()`, `srp_create_ch_ib()`, `srp_connect_ch()`, `srp_send_req()`, `srp_cm_rep_handler()`, `srp_queuecommand()`, `srp_map_data()`, `srp_recv_done()`, `srp_process_rsp()`, `srp_rport_reconnect()`, and SCSI EH callbacks `srp_abort()`, `srp_reset_device()`, and `srp_reset_host()`.

## Control Flow

Module initialization validates SRP IU layout sizes, clamps module parameters, creates the remove workqueue, attaches the SRP transport, registers the `infiniband_srp` class, registers an SA client, and registers as an RDMA client. When an RDMA device appears, `srp_add_one()` allocates a protection domain, chooses fast-registration capabilities and global-rkey policy, then creates one `srp_host` class device per RDMA port. Writing target options to `add_target` allocates a SCSI host, parses IB CM or RDMA CM parameters, creates one or more channels, resolves paths/routes, creates CQs/QPs, sends SRP login, posts receive IUs, registers an rport, scans LUNs, and marks the target live.

For normal I/O, `srp_queuecommand()` selects a channel from the block-mq hardware queue tag, reserves a TX IU and request credit, fills `SRP_CMD`, maps the SCSI SG list, emits direct, indirect, fast-registered, or immediate-data descriptors, DMA-syncs the IU, and posts an IB send. Receive completions dispatch by opcode: `SRP_RSP` completes SCSI commands and returns credits, `SRP_CRED_REQ` and `SRP_AER_REQ` send SRP responses, and transport/QP errors start SRP transport failure timers. Reconnect tears down CM state, recreates QPs, resets outstanding requests, and logs in each channel again.

## State and Persistence Behavior

Long-lived state is split across `srp_device` per HCA, `srp_host` per port, `srp_target_port` per target, and `srp_rdma_ch` per RDMA channel. Each target persists SCSI host/rport state, namespace reference, target identity, queue sizing, retry timeout, work items, and connection state. Each channel persists CQs, QP, CM ID, IU rings, free TX list, request credits, task-management completion state, and optional fast-registration pool. Per-SCSI-command private state persists indirect descriptors, DMA mappings, and fast-registration descriptor pointers until command completion or cleanup.

## Dependencies and Integration Points

The file depends on RDMA core verbs, IB CM, RDMA CM, SA path records, net namespaces, SCSI core, and `scsi_transport_srp`. It consumes SRP wire definitions from `<scsi/srp.h>` and local object layouts from `ib_srp.h`. Sysfs class attributes expose target identity and runtime counters. SCSI transport timers call back into reconnect/delete/terminate hooks. The SCSI EH path depends on SRP task management IUs and on rport state for fast-fail decisions.

## Risks and Edge Cases

The highest-risk areas are concurrent teardown versus completions, request-credit accounting, and memory registration lifetime. `srp_free_ch_ib()` deliberately nulls `ch->target` after CQ/QP destruction to block late SCSI EH use, and `srp_destroy_qp()` drains before destroying to avoid receive callbacks on freed QPs. The fast-registration path must invalidate rkeys and return descriptors exactly once. Immediate data has strict offset and IU-size constraints. Reconnect relies on serialization by the SRP rport mutex. Option parsing must reject incomplete IB/RDMA CM tuples, duplicate targets, oversized SG tables, and bad timeout combinations. Topspin/Cisco workaround behavior intentionally changes login port-ID layout for known legacy targets.

## Test Signals

Useful signals include module load/unload with RDMA devices present, `add_target` success and validation failures for both IB CM and RDMA CM formats, multi-channel login and partial-channel fallback, LUN scan success/removal, direct, indirect, external SG, fast-registration, global-rkey, and immediate-data I/O, request-credit exhaustion and recovery, SCSI abort/LUN reset/host reset, target logout/disconnect, QP error injection, reconnect after link loss, sysfs attribute reads, namespace cleanup, and builds with fast registration unavailable or disabled by module parameters.
