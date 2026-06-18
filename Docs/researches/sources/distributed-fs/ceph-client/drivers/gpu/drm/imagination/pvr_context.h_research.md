# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.h

Purpose: defines PowerVR context data structures, queue lookup helpers, reference helpers, and public context lifecycle APIs.

Important APIs/types: `enum pvr_context_priority` maps low/medium/high internal priorities. `struct pvr_context` includes kref, device, VM context, type/flags/priority, firmware object/data, firmware context ID, faulty flag, type-specific queues, and file-list linkage. Inline helpers map job type to queue, take/drop references, look up contexts by file handle or firmware ID, and fetch firmware address.

Control flow and state: contexts are reference-counted and registered in both per-file and per-device xarrays. Queue lookup is constrained by context type. `atomic_t faulty` marks contexts made unusable after reset with unfinished jobs.

Dependencies and integration: includes DRM scheduler, dma-fence, kref, xarray, UAPI types, CCCB, device, and queue headers.

Risks: inline lookup by firmware ID must handle concurrent destruction; the code attempts this with xarray locking and `kref_get_unless_zero()`. Queue union fields must be used consistently with `ctx->type`.

Test signals: compile coverage from job submission, context reset, close cleanup, and ioctl handling; runtime tests for invalid handles and stale references.
