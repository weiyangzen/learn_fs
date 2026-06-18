<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rpc.h

## Purpose
Declares shared helper interfaces for GSP-RM RPC/message handling and payload container recovery.

## Important APIs, Types, And Functions
Important APIs are to_payload_hdr(p, header), r535_gsp_rpc_poll, r535_gsp_msg_recv, r535_gsp_msg_ntfy_add, and r535_rpc_status_to_errno.

## Control Flow
No implementation is present. Callers use to_payload_hdr to recover an enclosing RPC header from a params pointer, poll/wait for RPC completion, receive asynchronous messages, register notification callbacks, and translate RM status values to Linux errno.

## State, Persistence, Dependencies, And Integration
State is held by the caller's nvkm_gsp queues and message buffers. Dependencies are rm.h and container_of semantics. Integration points are r570_gsp static/system RPCs, event registration for nocat/lockdown notices, FIFO RC events, and all RM control/allocation helpers.

## Risks And Test Signals
Risks: wrong payload/header association corrupts message parsing; status translation must preserve actionable errno. Test signals include RPC completion under load, asynchronous event callback delivery, and correct errno propagation from firmware failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/rpc.h -->
