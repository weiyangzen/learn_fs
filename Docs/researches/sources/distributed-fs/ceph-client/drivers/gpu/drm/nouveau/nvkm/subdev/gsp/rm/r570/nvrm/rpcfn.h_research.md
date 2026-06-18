<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/rpcfn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/rpcfn.h

## Purpose
Defines the global GSP/RM/UVM RPC function IDs for 570.144. The file uses an X macro so it can either define enum values directly or be included by another macro consumer.

## Important APIs, Types, And Functions
Important IDs include GET_GSP_STATIC_INFO=65, GSP_SET_SYSTEM_INFO=72, GSP_RM_CONTROL=76, GSP_RM_ALLOC=103, many CTRL_* operations for FIFO/GR/MMU/perf/NVLINK/fabric, SAVE_HIBERNATION_DATA/RESTORE_HIBERNATION_DATA, INVALIDATE_TLB, RM_API_CONTROL, and NUM_FUNCTIONS=227.

## Control Flow
There is no executable flow. RPC helpers pass these IDs in message headers so GSP-RM dispatches to the correct server-side handler. The X macro pattern allows alternate generation of tables or enums.

## State, Persistence, Dependencies, And Integration
State is symbolic RPC identity. Dependencies are nvrm/nvtypes.h and the message/RPC helpers. Integration points include every R570 RM API table entry, gsp.c static/system info RPCs, allocation/control paths, UVM paging channels, hibernation data handling, and TLB invalidation.

## Risks And Test Signals
Risks: one wrong numeric value can call the wrong firmware operation; deprecated/reserved values must not be reused by host code casually. Test signals include successful boot-time RPC sequence, object allocation/control operations, TLB invalidation, and no firmware status errors for known IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/rpcfn.h -->
