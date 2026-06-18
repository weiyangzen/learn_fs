# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_frontend.c

## Purpose

`dvb_frontend.c` implements the DVB frontend character device and tuning core. It registers frontend devices, manages open/release lifetime, runs the frontend tuning thread, translates DVBv3 and DVBv5 ioctl/property APIs into `struct dtv_frontend_properties`, handles event delivery, supports hardware/software/custom tuning algorithms, coordinates multi-frontend sharing, and integrates optional media-controller source pipelines.

The file is the user-visible control plane for demodulator/tuner drivers. Individual frontend drivers provide `struct dvb_frontend_ops`; this core supplies stable `/dev/dvb/adapterX/frontendY` behavior and compatibility semantics.

## Important APIs, Types, And Functions

`struct dvb_frontend_private` stores the registered `dvb_device`, output legacy parameters, event ring, tuning semaphore, wait queue, kthread pointer, release timeout, status, tune flags, remembered tone/voltage, software zigzag state, and media pipeline state.

Exported lifecycle APIs are `dvb_register_frontend`, `dvb_unregister_frontend`, `dvb_frontend_detach`, `dvb_frontend_suspend`, `dvb_frontend_resume`, `dvb_frontend_reinitialise`, and `dvb_frontend_sleep_until`. File operations are `dvb_frontend_open`, `dvb_frontend_release`, `dvb_frontend_ioctl`, compat ioctl support, and `dvb_frontend_poll`.

Tuning flow is organized around `dvb_frontend_start`, `dvb_frontend_thread`, `dvb_frontend_stop`, `dtv_set_frontend`, `prepare_tuning_algo_parameters`, `dvb_frontend_swzigzag`, and `dvb_frontend_swzigzag_autotune`. Property translation and validation use `dvb_frontend_check_parameters`, `dvb_frontend_get_frequency_limits`, `dvb_frontend_get_stepsize`, `dvb_frontend_clear_cache`, `dtv_property_cache_sync`, `dtv_property_legacy_params_sync`, `dvbv3_set_delivery_system`, `dvbv5_set_delivery_system`, and `emulate_delivery_system`.

## Control Flow

Registration allocates frontend-private state, initializes krefs and wait queues, registers a `DVB_DEVICE_FRONTEND`, sets the initial delivery system from `ops.delsys[0]`, and clears the property cache to delivery-system defaults. The open path handles adapter multi-frontend sharing, optional TS bus acquisition, generic DVB open accounting, optional media-controller source enablement, and starts the tuning thread for writable opens. Read-only opens can monitor most status ioctls without taking control of tuning.

The tuning thread initializes the frontend/tuner, then loops with a freezable wait. It exits on kthread stop, device removal, or a configurable shutdown timeout after last writer close. On wake, it handles requested reinitialization, restores tone/voltage, and dispatches to the frontend algorithm. Hardware algorithms call `ops.tune`; software algorithms run the core zigzag scan; custom algorithms call `ops.search` when `DVBFE_ALGO_SEARCH_AGAIN` is set and track lock status.

`dtv_set_frontend` validates frequency and symbol-rate ranges, syncs output DVBv3 parameters, derives bandwidth for systems that do not provide it directly, optionally forces auto inversion, normalizes low-priority FEC for non-hierarchical tuning, prepares algorithm parameters, sets `FESTATE_RETUNE`, clears old events, pushes an initial status-zero event, and wakes the thread. Software zigzag then cycles drift and inversion combinations until lock, switches from fast to slow search after wrapping, and records lock/lost-lock events.

The ioctl handler accepts batched DVBv5 `FE_SET_PROPERTY`/`FE_GET_PROPERTY`, legacy `FE_SET_FRONTEND`/`FE_GET_FRONTEND`, status/statistics reads, DiSEqC commands, tone/voltage controls, high-LNB voltage, tune mode, and event reads. `dvb_frontend_do_ioctl` serializes most operations with `fepriv->sem` and rejects write-affecting ioctls from read-only file descriptors.

## State And Persistence Behavior

Frontend state is volatile and held in `fe->dtv_property_cache`, `fepriv->state`, `fepriv->status`, event ring indices, the tuning thread pointer, and remembered tone/voltage. The property cache persists across ioctls and is reset by `DTV_CLEAR`, registration, or delivery-system changes. Tuning status is exposed asynchronously through the event ring and synchronously through status/statistics ioctls.

Lifetime is kref-based. Registration establishes references for unregister and detach; open obtains another reference; release drops it. `dvb_frontend_put` invokes detach before kref drop when relevant. Thread state is protected by `fepriv->sem`, wait queues, memory barriers around `fe->exit`, and the global `frontend_mutex` for registration/unregistration.

Multi-frontend sharing uses `adapter->mfe_lock`, `adapter->mfe_dvbdev`, `mfe_shared`, and a wait/retry loop controlled by `dvb_mfe_wait_time`. Media-controller integration stores a `media_pipeline` in private state and enables/disables sources around writable open/release.

## Dependencies And Integration Points

The core depends on frontend driver callbacks in `struct dvb_frontend_ops` and nested tuner/analog ops. Important callbacks include init/sleep/suspend/resume/release, set/get frontend, read status/statistics, tune/search/get_frontend_algo, DiSEqC/tone/voltage operations, LNA, TS bus control, and I2C gate control. It uses `dvbdev.c` for device registration and generic open/ioctl plumbing, media-controller APIs when enabled, Linux kthreads/freezer/wait queues, and compat user-copy structures for 32-bit userspace.

Userspace integration is via DVBv3 and DVBv5 frontend ioctls. Adapter integration is via `dvb_register_frontend` and `dvb_unregister_frontend`, typically called by PCI/USB/I2C bridge drivers when a demod/tuner stack is attached.

## Risks And Edge Cases

Compatibility behavior is complex. DVBv3 calls may emulate non-DVBv3 delivery systems, default to the first compatible delivery system, or fail if no compatible type exists. Early DVBv5 apps passing `SYS_UNDEFINED` are mapped to the first supported delivery system. These compatibility branches are necessary but can surprise multi-standard devices.

Thread state is sensitive to open mode and release timing. With `dvb_shutdown_timeout`, the thread may remain alive briefly after writer close; statistics ioctls return `-EAGAIN` when no thread exists. Read-only mode intentionally blocks event and DiSEqC reply ioctls because they interfere with tuning state.

Parameter derivation has several assumptions: satellite frequency units are converted to kHz for range checks, DVB-C/ATSC bandwidths are inferred, and software zigzag defaults rely on symbol rate or step size. Incorrect frontend ops metadata can cause false `-EINVAL`, warnings about undefined frequency limits, or ineffective scans.

Concurrency risks include MFE handoff races, source-enable failure cleanup, and thread stop/resume interactions. A build should also validate this snapshot against generated-tree anomalies elsewhere in the same folder.

## Test Signals

High-value tests include DVBv5 property batches with `DTV_CLEAR`, delivery-system switches, `DTV_TUNE`, and invalid message counts; DVBv3 `FE_SET_FRONTEND` compatibility across QPSK/QAM/OFDM/ATSC and unsupported systems; frequency and symbol-rate boundary checks; read-only ioctl permission checks; event overflow and blocking/nonblocking `FE_GET_EVENT`; software zigzag lock/lost-lock transitions; hardware/custom algorithm status event emission; suspend/resume restoring tone and voltage; MFE shared open contention; media-controller source busy cleanup; and unregister while users and the frontend thread are active.

Runtime signals include frontend registration logs, creation of `/dev/dvb/adapterX/frontendY`, event poll readiness after tuning state changes, clean kthread exit on close/unregister, and no leaked media source pipeline after failed writable open.
