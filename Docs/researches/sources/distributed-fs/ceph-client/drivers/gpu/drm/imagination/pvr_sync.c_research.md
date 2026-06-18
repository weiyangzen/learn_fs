<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_sync.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_sync.c

Purpose: Implements PowerVR job synchronization around DRM syncobjs, timeline syncobjs, dma-fences, and DRM scheduler dependencies.

Important APIs/types/functions: Public helpers are `pvr_sync_signal_array_cleanup()`, `pvr_sync_signal_array_collect_ops()`, `pvr_sync_signal_array_update_fences()`, `pvr_sync_signal_array_push_fences()`, and `pvr_sync_add_deps_to_job()`. Internal helpers validate UAPI ops, cache signal syncobjs in an xarray, and split native UFO-backed dependencies.

Control flow: Signal collection validates signal ops and records unique `<handle, point>` entries. After job fences are produced, update replaces cached fences with the job's done fence, and push attaches fences to regular or timeline syncobjs. Wait ops are translated into scheduler dependencies, using the local signal cache when a submission batch waits on a syncobj point signaled by an earlier job.

State and persistence behavior: State is held in an `xarray` of `struct pvr_sync_signal`, with references to syncobjs, optional timeline chains, and fence references. Persistent userspace-visible syncobj state is updated only in `pvr_sync_signal_array_push_fences()`.

Dependencies: Uses UAPI `drm_pvr_sync_op`, DRM syncobj APIs, dma-fence chains and unwrap helpers, DRM scheduler jobs/fences, PowerVR queue native-fence detection, and xarrays.

Integration points: Job submission uses this file to validate sync arrays, build scheduler dependencies, and publish completion fences back to syncobjs.

Risks: Incorrect handle-type validation can allow illegal UAPI combinations. Fence reference lifetime and timeline-chain handling are subtle. Native PowerVR fences must wait on scheduled fences to avoid redundant firmware waits while still preserving ordering.

Test signals: Submit jobs with regular and timeline syncobjs, duplicate signal ops, wait-after-signal within one submit batch, native and non-native fence arrays, invalid flags/value combinations, and cleanup under error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_sync.c -->
