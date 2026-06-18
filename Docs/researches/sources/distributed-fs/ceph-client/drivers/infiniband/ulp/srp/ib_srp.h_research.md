# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.h

## Purpose

`ib_srp.h` defines the in-kernel state model for the SRP initiator implemented by `ib_srp.c`. It is the contract between connection setup, SCSI command dispatch, RDMA completions, fast memory registration, and target removal logic.

## Important APIs, Types, and Functions

The header defines SRP constants for path and abort timeouts, redirect status codes, default queue and SG sizes, immediate-data layout, and special tags. Core enums are `srp_target_state` and `srp_iu_type`. Core structures are `srp_device`, `srp_host`, `srp_request`, `srp_rdma_ch`, `srp_target_port`, `srp_iu`, `srp_fr_desc`, `srp_fr_pool`, and `srp_map_state`.

## Control Flow

There are no functions in the header, but the structure layout describes runtime flow. `srp_device` is created from RDMA client add callbacks and owns HCA-level registration capability and PD state. `srp_host` represents a local port and owns target lists and the `add_target` entry. `srp_target_port` is created per target definition, then owns channels, SCSI host/rport state, target identifiers, queue sizing, and work items. `srp_rdma_ch` is the hot-path object used by SCSI queuecommand, send/receive completions, CM callbacks, and reconnect.

## State and Persistence Behavior

The header separates hot-path fields from less frequently used fields in `srp_rdma_ch` and `srp_target_port`. Persistent state includes CM IDs, path records, QPs/CQs, IU rings, request credits, task-management state, target identity, network namespace, and queued work. `srp_fr_pool` persists a free-list of MRs for fast registration. `srp_request` persists per-command DMA and descriptor state until command-private cleanup.

## Dependencies and Integration Points

It includes Linux list, mutex, scatterlist, SCSI host/command, RDMA verbs, SA, IB CM, and RDMA CM headers. It depends on `<scsi/srp.h>` indirectly through the C file for SRP wire structures. The structures are embedded in SCSI host private data, SCSI command private data, RDMA CM contexts, CQ contexts, and work items.

## Risks and Edge Cases

Cacheline-sensitive fields are explicitly grouped; careless layout churn can hurt I/O path performance. Several fields are shared across interrupt/completion context and process context, so their lock ownership matters. `union` CM state is selected by `using_rdma_cm`; mixing the wrong branch can corrupt connection teardown. The counted flexible array in `srp_fr_pool` must match allocation size. `srp_map_state` has union members reused by FR and generic mapping flows, so each mapping path must initialize the right branch.

## Test Signals

Compile coverage catches most type drift. Runtime coverage should exercise all structures through target add/remove, reconnect, task management, fast-registration allocation/exhaustion, immediate data, multi-channel I/O, and SCSI command-private init/exit.
