# sources/distributed-fs/openafs/src/afs/discon.h

Purpose: public interface and inline queue helpers for disconnected and disconnected-readwrite cache-manager operation.

Important APIs/types: declares global mode flags `afs_is_disconnected`, `afs_is_discon_rw`, `afs_in_sync`, locks `afs_discon_lock` and `afs_disconDirtyLock`, queues `afs_disconDirty` and `afs_disconShadow`, conflict policy, and `afs_DisconVnode`. Prototypes cover resync, connection removal, fake/shadow FID generation, shadow directories, dcache lookup by FID, status update, discard-all, and `afs_WriteVCacheDiscon`. Macros `AFS_IS_DISCONNECTED`, `AFS_IS_DISCON_RW`, and `AFS_IN_SYNC` are used by vcache/volume code.

Control flow: `afs_DisconAddDirty` appends a vcache to `afs_disconDirty` only on the first dirty operation, optionally taking `afs_xvcache`, then takes a vcache reference so queue membership pins it. `afs_DisconRemoveDirty` removes the queue entry, clears dirty flags, and releases that reference.

State and persistence: tracks in-memory dirty and shadow queues; persistence is indirect through later resync and dcache/shadow directory machinery. `avc->f.ddirty_flags` accumulates operations such as metadata update or truncation.

Dependencies and integration points: consumed by `afs_vcache.c` for disconnected status writes and callback behavior; relies on `struct vcache`, `struct dcache`, `struct vrequest`, AFS queue primitives, and vcache refcount helpers.

Risks: dirty queue membership and vcache references must stay paired, or disconnected vcaches can leak or be freed while queued. `afs_DisconVnode` is explicitly not protected. The inline helpers assume the vcache lock is already held; misuse can race dirty flags.

Test signals: dirty add/remove idempotence, refcount balance, resync after metadata-only changes, truncation dirty flags, concurrent disconnected writes, discard-all, and reconnect while `AFS_IN_SYNC` suppresses normal status updates.
