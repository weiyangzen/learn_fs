<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/liveupdate.h -->
# sources/distributed-fs/ceph-client/include/linux/liveupdate.h

## Purpose
This header declares a live update orchestrator interface for preserving and restoring file-related kernel state across a kexec-style kernel transition. It defines file handlers and file-lifecycle-bound shared objects.

## Important APIs, Types, and Functions
`struct liveupdate_file_op_args` carries handler, file, serialized data, retrieve status, and private runtime data. `struct liveupdate_file_ops` defines `can_preserve`, `preserve`, `unpreserve`, `freeze`, `unfreeze`, `retrieve`, `can_finish`, `finish`, and `get_id`. `struct liveupdate_file_handler` registers compatible file types. FLB support uses `struct liveupdate_flb_op_args`, `struct liveupdate_flb_ops`, `struct luo_flb_private_state`, `struct luo_flb_private`, and `struct liveupdate_flb`. Public APIs include `liveupdate_enabled`, `liveupdate_reboot`, registration calls, and `liveupdate_flb_get_incoming/outgoing`; disabled builds return false, zero, or `-EOPNOTSUPP`.

## Control Flow
Outgoing kernels preserve file state, optionally freeze it before transition, and serialize opaque handles. Incoming kernels retrieve file objects, wait until `can_finish` permits completion, then call `finish`. FLBs run preserve/retrieve/finish once for shared data when first/last dependent files cross lifecycle boundaries.

## State and Persistence Behavior
State includes handler lists, FLB lists, per-FLB incoming/outgoing counts, serialized `u64` handles, live object pointers, locks, and finished/retrieved flags. Persisted cross-kernel state is represented by serialized handles in LUO/KHO data, not by the C structures themselves.

## Dependencies and Integration Points
It depends on KHO LUO ABI headers, UAPI liveupdate definitions, files, modules, lists, mutexes, and rwsems. It integrates with kexec/live-update orchestration and drivers that can preserve file-backed resources such as memfd, VFIO, or shared subsystem objects.

## Risks and Test Signals
Risks include handler compatibility drift, leaked private data on abort, FLB refcount bugs, retrieve/finish ordering errors, module lifetime issues, and invalid serialized handles. Test signals are enabled/disabled config behavior, preserve-abort-unpreserve tests, preserve-reboot-retrieve-finish tests, FLB first/last user tests, and fault injection in each callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/liveupdate.h -->
