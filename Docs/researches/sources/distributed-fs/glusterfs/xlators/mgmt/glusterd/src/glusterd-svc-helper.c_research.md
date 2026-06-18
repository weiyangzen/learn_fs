# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-helper.c

## Purpose
`glusterd-svc-helper.c` contains policy helpers for glusterd-managed auxiliary services. It coordinates reconfiguration, start/stop management, volfile comparison, and multiplexed self-heal daemon attach/detach behavior.

## Important APIs, Types, and Functions
Top-level service orchestration APIs are `glusterd_svcs_reconfigure()`, `glusterd_svcs_stop()`, and `glusterd_svcs_manager()`. Volfile comparison helpers include `glusterd_svc_check_volfile_identical()`, `glusterd_svc_check_topology_identical()`, `glusterd_volume_svc_check_volfile_identical()`, and `glusterd_volume_svc_check_topology_identical()`.

Multiplexing helpers include `glusterd_svcprocess_new()`, `glusterd_is_svcproc_attachable()`, `__gf_find_compatible_svc()`, `__gf_find_compatible_svc_from_pid()`, and `glusterd_shd_svc_mux_init()`. Runtime attach/detach is handled by `glusterd_attach_svc()`, `glusterd_detach_svc()`, and `__glusterd_send_svc_configure_req()`.

## Control Flow
`glusterd_svcs_reconfigure()` recreates service volfiles and notifies fetchspec consumers. It handles NFS when built, volume-level SHD when a volume is supplied, and skips quotad/bitd/scrub when the cluster op-version is still at minimum. `glusterd_svcs_manager()` starts or reconciles services in a similar order and ignores `-EINVAL` from optional service managers as a disabled-service signal. Snapshot volumes are skipped.

Volfile comparison helpers generate a temporary volfile with `mkstemp`, call the appropriate graph builder, then compare either full file content or topology with the existing service volfile. For SHD multiplexing, `glusterd_shd_svc_mux_init()` decides whether a volume-level SHD service can attach to an existing process. It handles abnormal death cleanup, stale pidfiles, compatible process lookup, creation of a new `glusterd_svc_proc_t`, list linking, and SHD-specific initialization.

`__glusterd_send_svc_configure_req()` sends a brick-program RPC request to attach or detach a service. Attach requests read the volfile content, optionally serialize a dictionary from `build_volfile_path()`, install callback state in a frame, and submit the XDR request. `glusterd_attach_svc()` and `glusterd_detach_svc()` retry up to 15 times, temporarily releasing `big_lock` while sleeping so the connection can progress.

## State and Persistence Behavior
This file does not write durable metadata directly. It mutates runtime service state: `svc->online`, `svc->inited`, `svc->svc_proc`, `volinfo->shd.attached`, multiplex process lists, and atomic blocker counters. It reads generated volfiles from disk for comparison and attach payloads, so it depends on persistence and volgen layers having already produced those files.

## Dependencies and Integration Points
It integrates global services (`nfs`, `quotad`, `bitd`, `scrub`) and volume-level `glustershd`. It depends on service-specific modules, `glusterd-svc-mgmt.c` for process/RPC primitives, volfile generation and comparison functions, RPC/XDR infrastructure, snapshot utilities, and glusterd locks/condition variables. Callers are volume, brick, replace/reset-brick, geo-replication, op-sm, and startup paths that need service reconciliation after metadata changes.

## Risks and Edge Cases
The attach/detach retry loop deliberately unlocks `big_lock`, which is called out in comments as risky but necessary for connection progress. Any change here needs careful deadlock and stale-volume analysis. Attach callback code currently logs success with a message ID named like failure, which can confuse log analysis. The attach path reads the whole volfile into memory based on `st_size`; large or concurrently replaced volfiles need bounds and consistency consideration. Temporary volfile paths are under `/tmp/g<svc>-XXXXXX` and are cleaned up, but tests should verify all error paths close descriptors and unlink. Multiplexed SHD assumptions are narrow; comments state the generic mux notifier currently assumes glustershd.

## Test Signals
Test service manager behavior across enabled and disabled optional services, minimum op-version, snapshot volumes, and volume-level SHD. For volfile comparisons, verify both content changes and topology-only changes. For multiplexing, test clean attach to existing SHD, stale pidfile cleanup, abnormal SHD death followed by re-init, stale volume deletion during attach retries, and detach RPC failures.
