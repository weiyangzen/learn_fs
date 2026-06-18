# sources/distributed-fs/lustre-release/lustre/mdt/mdt_mds.c

## Purpose

`mdt_mds.c` is the Lustre Metadata Service LU/OBD type wrapper that owns PTLRPC service registration for MDT-related portals. It allocates `struct mds_device`, starts regular MDT, readpage, object update, sequence controller/server, FLD, and MDT I/O services, exposes health checks and nodemap ioctl handling, and registers/unregisters the `LUSTRE_MDS_NAME` device type.

## Important APIs, Types, and Functions

- `struct mds_device` embeds `struct md_device` and stores service pointers plus `mds_health_mutex`.
- Module parameters `mds_num_threads`, `mds_cpu_bind`, `mds_max_io_threads`, `mds_io_cpu_bind`, `mds_io_num_cpts`, `mds_num_cpts`, `mds_rdpg_num_threads`, `mds_rdpg_cpu_bind`, `mds_rdpg_num_cpts`, and `mdt_enable_flr_ec` control service thread placement and feature advertisement.
- `mds_start_ptlrpc_service()` registers all PTLRPC services with tailored `ptlrpc_service_conf` instances.
- `mds_stop_ptlrpc_service()` unregisters all services and frees the MDT I/O CPT table.
- `ldlm_enqueue_hpreq_check()` and `mds_hpreq_handler()` special-case resent LDLM enqueue requests so already-granted locks can be handled as high-priority requests.
- `mds_device_alloc()`, `mds_device_fini()`, and `mds_device_free()` implement LU device lifecycle.
- `mds_health_check()` aggregates service health.
- `mds_iocontrol()` currently accepts only `OBD_IOC_NODEMAP`.
- `mds_mod_init()` and `mds_mod_exit()` register and unregister the OBD/LU type.

## Control Flow

Device allocation creates `struct mds_device`, initializes the embedded MD device, resolves the named OBD from the Lustre config, links `ld_obd` and `obd_lu_dev`, registers lprocfs entries, initializes the health mutex, and calls `mds_start_ptlrpc_service()`. Any failure unwinds lprocfs setup, services, and allocated memory.

`mds_start_ptlrpc_service()` repeatedly populates a static `ptlrpc_service_conf` and calls `ptlrpc_register_service()`. The regular MDT service uses `MDS_REQUEST_PORTAL` and `MDC_REPLY_PORTAL`, dispatches to `tgt_request_handle()`, prints through `target_print_req()`, and uses `mds_hpreq_handler()`. Readpage uses `MDS_READPAGE_PORTAL`. OUT uses `OUT_PORTAL` and `OSC_REPLY_PORTAL`. Sequence controller/server and FLD use their own portals and smaller other-thread pools. The MDT I/O service uses OST-style I/O buffer sizing on `MDS_IO_PORTAL`, initializes/destroys I/O threads with `tgt_io_thread_init()`/`tgt_io_thread_done()`, and uses `tgt_hpreq_handler()`.

Before the I/O service registration, the code may build `mdt_io_cptable`: when the global CPT table has one CPT but the node mask has multiple NUMA nodes, it allocates a new table with one CPT per node for I/O service node affinity. If allocation or node insertion fails, it logs and falls back to the default CPT pattern.

Stopping services is serialized under `mds_health_mutex`: each non-NULL service pointer is unregistered and nulled. After unlocking, `mdt_io_cptable` is freed if present.

## State and Persistence Behavior

This file persists no on-disk metadata. Its state is live kernel service state: PTLRPC service registrations, thread pools, portal bindings, CPT affinity tables, OBD/LU type registration, and module parameters. The `mdt_enable_flr_ec` parameter is writable at module scope and influences advertised FLR EC behavior elsewhere.

Health state is derived from active service objects. Device finalization unregisters services before lproc cleanup; device free finalizes the embedded MD device and frees memory.

## Dependencies and Integration Points

The file depends on PTLRPC service infrastructure, target request dispatch (`tgt_request_handle`, `target_print_req`, high-priority handlers), LDLM lock lookup for resend prioritization, LU device type registration, OBD class lookup and type registration, lprocfs OBD setup/cleanup, libcfs CPT/NUMA helpers, nodemap server ioctl handling, and MDT thread-local key initialization through `LU_TYPE_INIT_FINI(mds, &mdt_thread_key)`.

It is the integration point that makes higher-level MDT request handlers reachable over LNet portals; request opcode routing after service receive is handled in target/MDT layers outside this file.

## Risks and Edge Cases

- `mds_start_ptlrpc_service()` uses a static local `ptlrpc_service_conf` but reassigns it before each registration. This is safe only because registration copies or consumes the data synchronously as expected.
- Partial service startup failure relies on `mds_stop_ptlrpc_service()` to unregister every service that succeeded earlier. Any new service added to startup must be added to stop and health checks.
- `ldlm_enqueue_hpreq_check()` initializes the request capsule and looks up the first client lock handle only for `MSG_RESENT` without `MSG_REPLAY`; mistakes here can change resend priority and recovery latency.
- The MDT I/O CPT-table fallback logs warnings but continues. Performance/NUMA locality can silently degrade.
- `mds_health_check()` assumes all service pointers are valid enough for `ptlrpc_service_health_check()` after allocation; stop/start races are guarded by `mds_health_mutex`.

## Test Signals

Tests should cover successful registration of all services, injected registration failures at each service and full unwind, health check aggregation, module parameter propagation into thread configs, I/O CPT table creation/fallback on multi-node single-CPT systems, LDLM resend high-priority detection for granted and non-granted locks, nodemap ioctl acceptance/rejection, and lifecycle ordering of alloc/fini/free/mod init/exit.
