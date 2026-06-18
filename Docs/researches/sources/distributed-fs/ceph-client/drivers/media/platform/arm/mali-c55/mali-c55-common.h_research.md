# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-common.h

Purpose: Central shared definitions for the Mali-C55 ISP driver, including constants, entity structures, buffer structures, context state, register-helper declarations, and cross-file registration/control APIs.

Important APIs/types: Defines ISP pad ids, TPG, ISP, resizer, capture, params, stats, buffer, format-info, context, and top-level `struct mali_c55`. Declares register accessors, context config writes, entity registration/unregistration functions, active-context access, capture buffer programming/completion, frame-sync events, format lookup helpers, pipeline readiness, stats filling, and parameter config writes.

Control flow and state: The top-level `struct mali_c55` is the persistent in-memory driver state containing MMIO base, clocks, resets, IRQ, capabilities, media/V4L2 devices, notifier, media pipeline, all entities, a config context shadow, and next config-space selector. Substructures define locks and queues used by vb2 and interrupt paths.

Dependencies and integration: Pulls in Linux clock/reset/io/list/mutex/spinlock/V4L2/media/vb2 headers. Every Mali-C55 implementation file includes it to share object ownership and function contracts.

Risks: This header is the ABI between all driver units; structure layout changes affect many files. Locking expectations are encoded in comments but enforced in implementation, so misuse can race ISR, stream control, and userspace queueing.

Test signals: Full driver build, sparse/lockdep runs, entity registration/unregistration paths, and compile coverage for every declaration.
