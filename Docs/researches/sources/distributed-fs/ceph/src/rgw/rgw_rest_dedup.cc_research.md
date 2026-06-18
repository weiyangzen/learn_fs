# sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.cc

## Purpose

`rgw_rest_dedup.cc` implements authenticated admin REST operations for RGW deduplication control. It exposes stats, throttle inspection/update, scan start, and abort/pause/resume controls by dispatching `GET` and `POST` requests under the dedup resource.

## Important APIs and Functions

The file defines internal operations: `RGWOp_Dedup_Stats`, `RGWOp_Dedup_Throttle_Get`, `RGWOp_Dedup_Scan`, `RGWOp_Dedup_Control`, and `RGWOp_Dedup_Throttle_Set`. `RGWHandler_Dedup::op_get()` maps `op=stats` and `op=throttle`; `op_post()` maps `estimate`, `exec`, `abort`, `pause`, `resume`, and `throttle`.

All operations require the RADOS SAL driver through `get_rados_store()`. Read operations check `dedup` read caps, while mutation/control operations check `dedup` write caps.

## Control Flow

Stats and throttle GET start the response flusher, then call `rgw::dedup::cluster::collect_all_shard_stats()` or `dedup_control_bl()`. Estimate and exec scans call `dedup_restart_scan()` with the selected request type. Exec additionally requires `yes-i-really-mean-it=true` and is compiled behind `FULL_DEDUP_SUPPORT`. Control operations send urgent messages to the dedup cluster code. Throttle SET parses optional `max-bucket-index-ops` and `max-metadata-ops`, encodes a throttle message, and echoes the applied control response.

## State and Persistence Behavior

This file does not maintain state itself. It triggers persistent or cluster-wide dedup state through `rgw::dedup::cluster` and encoded urgent messages. Throttle settings, scan restarts, pause/resume/abort, and stats collection are delegated to the dedup subsystem and RADOS-backed store.

## Dependencies and Integration Points

It depends on `rgw_dedup_cluster.h`, `rgw_dedup_utils.h`, `rgw_sal_rados.h`, and RGW REST auth/operation classes. It is tightly coupled to the RADOS store and returns `-EPERM` when invoked with a non-RADOS driver.

## Risks and Test Signals

The `URGENT_MSG_PASUE` spelling is used as a constant and must match the dedup subsystem. Throttle parsing casts signed `int64_t` values to `uint32_t` without explicit negative-range validation. `op=exec` is deliberately guarded by both confirmation and compile-time support. Tests should verify cap checks, non-RADOS rejection, invalid throttle values, missing throttle params, exec confirmation behavior, and each `op` dispatch path.
