# sources/distributed-fs/openafs/src/vol/volume.c

## Purpose

`volume.c` is the central OpenAFS volume package implementation. It owns process-wide volume package initialization, vice partition attachment, volume attach/get/put/offline/detach lifecycles, on-disk volume header I/O, vnode allocation bitmaps, volume usage persistence, volume hash indexing, demand-attach filesystem (DAFS) state management, online salvage scheduling, and cache/statistics reporting.

The file is compiled in several modes. Non-DAFS builds eagerly attach all volume headers during fileserver startup and use simpler reference and shutdown behavior. DAFS builds preattach volume IDs, lazily perform full attachment on first access, track a detailed `VolState` state machine, use lightweight reservations to protect `Volume` objects while dropping the global volume lock, coordinate online salvage through SALVSYNC/FSSYNC, and use a volume LRU scanner to soft-detach idle volumes.

## Important APIs, Types, And Globals

- `VOptDefaults`, `VInitVolumePackage2`, `VInitAttachVolumes`, `VShutdown`, and `VSetTranquil` initialize, bring up, shut down, and quiet the package. `VInit` progresses through initialization levels: uninitialized, partitions/structures initialized, volumes attached/preattached, and FSSYNC connected.
- `VAttachVolume`, `VAttachVolume_r`, `VAttachVolumeByName`, `VAttachVolumeByName_r`, and DAFS-only `VPreAttachVolume*`/`VAttachVolumeByVp_r` construct usable `Volume` objects from partition `.vol` headers and inode handles.
- `VGetVolume`, `VGetVolumeWithCall`, `VGetVolume_r`, `VGetVolumeByVp_r`, and `VPutVolume*` implement heavyweight access references. `GetVolume` is the private core that performs lookup, demand attach, status checks, timeout handling, and header loading.
- `VOffline`, `VForceOffline`, `VTakeOffline`, `VDetachVolume`, and DAFS `VOfflineForVolOp_r` move volumes out of service and release cached vnode/inode resources.
- `VUpdateVolume`, `VUpdateVolume_r`, `VSyncVolume`, and `WriteVolumeHeader_r` persist `VolumeDiskData` back to `diskDataHandle`, including `inUse`, `needsSalvaged`, `dontSalvage`, usage counters, and uniquifier state.
- `ReadHeader`, `VolumeHeaderToDisk`, and `DiskToVolumeHeader` provide the volume header/file format boundary, including split low/high inode handling for 64-bit inode environments.
- `VAllocBitmapEntry`, `VFreeBitMapEntry`, `VGrowBitmap`, and `VGetBitmap_r` manage in-memory vnode allocation bitmaps derived from vnode index files.
- DAFS-only `VRequestSalvage_r`, `VCheckSalvage`, `VScheduleSalvage_r`, `VUpdateSalvagePriority_r`, `VRegisterVolOp_r`, and `VDeregisterVolOp_r` coordinate with online salvage and fileserver volume operations.
- DAFS-only `VLRU_SetOptions` and the static VLRU scanner functions maintain a generational LRU used to soft-detach idle attached volumes.
- `VSetVolHashSize`, `VLookupVolume_r`, and the static hash helpers manage the global `VolumeHashTable`; DAFS can reorder hash chains based on lookup counts.

Key process-wide state includes `programType`, `vol_opts`, `VStats`, `VolumeCacheCheck`, `VolumeHashTable`, global locks/condition variables, and DAFS flags such as `vol_disallow_salvsync` and `vol_shutting_down`. The main in-memory object is `struct Volume` from `volume.h`; its durable payload is accessed through the `struct volHeader` cache and `VolumeDiskData` macros.

## Control Flow

Startup begins in `VInitVolumePackage2`. It stores caller options, initializes partitions, the volume hash, optional VLRU/SALVSYNC/FSSYNC services, header cache entries, vnode caches, and vice partitions. For non-fileserver programs it immediately calls `VInitAttachVolumes`. For fileservers, callers can attach volumes separately; non-DAFS scans each partition and fully attaches every `*.vol`, while DAFS scans partitions in worker threads and posts batches of preinitialized `Volume` structs to the main thread for insertion into the hash table, VByP list, and `VOL_STATE_PREATTACHED`.

The attach path is layered. `VAttachVolume_r` resolves a volume ID to partition/name and delegates to `VAttachVolumeByName_r`. That function handles partition locks for non-DAFS utilities, DAFS races with existing preattached or attached objects, FSSYNC checkout bookkeeping, and then calls `attach2` without `VOL_LOCK`. `attach2` calls `attach_volume_header`, reads/verifies the volume disk header, initializes inode handles for small/large vnode indexes, volume info, and namei link table, validates index headers, builds writeable-volume bitmaps for fileservers, handles `needsSalvaged`, `inUse`, `destroyMe`, `blessed`, and `inService`, breaks callbacks if the salvager marked `needsCallback`, and finally inserts the volume into hash/VLRU state as attached or unattached.

`GetVolume` is the runtime access path. It looks up the volume, waits for DAFS exclusive states, demand-attaches `VOL_STATE_PREATTACHED` volumes, maps salvage and offline states to package and client errors, loads a valid header if needed, waits or times out when the volume is going offline, then increments `nUsers` and updates VLRU access. `VPutVolume_r` decrements `nUsers`; when it reaches zero it runs event-style cleanup checks for offline, detach, salvage, and free.

Offline and detach are deliberately asynchronous. `VOffline_r` marks a referenced fileserver volume as going offline, drops the heavy reference, and waits until other users leave. `VCheckOffline` does the actual transition when `nUsers` reaches zero: clears `inUse`, persists the header, closes handles, logs status, invalidates header cache, and moves DAFS state to `UNATTACHED` unless an error/salvage state supersedes it. `VDetachVolume_r` removes hash/list/VLRU membership, marks shutdown, puts the reference, and notifies FSSYNC when required.

Shutdown is simple in non-DAFS: scan hash chains, hold each volume, and offline it. DAFS shutdown is partition-oriented and multi-pass: pass 0 handles unattached, preattached, error, and deleted volumes; later passes handle attached volumes with headers, attached volumes without headers, and finally exclusive-state volumes. A controller thread periodically allocates worker capacity across partitions by remaining list length.

## State And Persistence Behavior

The critical persisted files are the partition `.vol` header (`VolumeDiskHeader_t`) and per-volume data object (`VolumeDiskData`). `attach_volume_header` reads the `.vol` header and converts it to in-memory inode handles; `ReadHeader` validates magic/version for volume info, vnode index, and link table files. `WriteVolumeHeader_r` writes `V_disk(vp)` to the volume info inode. `VUpdateVolume_r` updates the disk uniquifier policy: active fileserver volumes write `nextVnodeUnique + 200`, and inactive volumes write the exact next uniquifier.

`inUse` is the crash/salvage signal. Fileserver attach sets it to `fileServer` only when a volume is blessed, in service, and not marked for salvage. Clean offline/detach clears it and writes the header. If a writeable volume is found with `inUse` already set during attach, the code marks `needsSalvaged` and schedules or returns salvage. `needsSalvaged`, `dontSalvage`, `destroyMe`, `needsCallback`, and `offlineMessage` are persisted in `VolumeDiskData`.

The header cache maintains an invariant that `nUsers > 0` implies `vp->header` is valid, and `nUsers == 0` fileserver headers are either on the LRU or absent. `GetVolumeHeader` may evict an LRU header from another volume and write it back if `diskstuff.inUse` is set. `FreeVolumeHeader` invalidates the association, while `ReleaseVolumeHeader` preserves cached disk data on the LRU.

DAFS adds an in-memory state machine, not persisted directly: `PREATTACHED`, `ATTACHING`, `ATTACHED`, `UPDATING`, `GOING_OFFLINE`, `OFFLINING`, `DETACHING`, `SALVAGING`, `SALVAGE_REQ`, `ERROR`, and vnode/header helper states. `VChangeState_r` updates counters and broadcasts waiters. Lightweight `nWaiters` reservations protect objects across operations that drop `VOL_LOCK`.

The non-DAFS update list eventually sets `DONT_SALVAGE` after `SALVAGE_INTERVAL`; DAFS moved this behavior into VLRU demotion. Usage stats roll daily in `VAdjustVolumeStatistics_r`, and `VBumpVolumeUsage_r` rate-limits header writes by `usage_threshold` and `usage_rate_limit`.

## Dependencies And Integration Points

This file depends heavily on local volume-layer modules: `volume.h`, `volume_inline.h`, `vnode.h`, `partition.h`, `ihandle.h`, `fssync.h`, `salvsync.h`, `daemon_com.h`, `vutils.h`, and directory/vnode cache helpers. The inode-handle API (`IH_OPEN`, `FDH_PREAD`, `FDH_PWRITE`, `IH_RELEASE`, `IH_REALLYCLOSE`, `IH_CONDSYNC`) is the main storage abstraction. `DFlushVolume`, `VCloseVnodeFiles_r`, and `VReleaseVnodeFiles_r` connect to vnode and directory caches.

Fileserver RPC integration happens through `VGetVolumeWithCall` and `VScanCalls_r`. Callers can register an `rx_call` so the volume package can interrupt clients when a volume is forced offline after `offline_timeout` or `offline_shutdown_timeout`.

Volume utilities and volserver integrate through FSSYNC checkout/return semantics. `VMustCheckoutVolume`, `VVolOpLeaveOnline_r`, `VVolOpSetVBusy_r`, `needsPutBack`, and `checkoutMode` encode when a utility owns a volume and whether it must be returned online, left offline, or marked deleted. DAFS fileservers also use FSSYNC to track pending volume operations and SALVSYNC to schedule online salvage.

The fileserver command-line/configuration surface integrates through `VSetVolHashSize` and `VLRU_SetOptions`, which are referenced from `viced.c`. Volserver procedures call `VAttachVolume*`, `VUpdateVolume`, and `VDetachVolume` for clone, dump, move, purge, and split operations. Vnode code calls volume update/salvage and DAFS state helpers around vnode allocation and I/O.

## Risks And Edge Cases

- Locking is subtle. Many helpers require `VOL_LOCK`, some deliberately drop it, and DAFS callers often must hold either a heavyweight user reference or lightweight reservation. Violating those preconditions can free a `Volume` while a caller still uses it.
- DAFS preattach/attach races are explicitly handled, but pointer identity can change across `VPreAttachVolumeByVp_r` and `VAttachVolumeByVp_r`; callers must not assume the returned `Volume *` is the same as the input.
- `attach_volume_header` may first take a read lock before discovering the volume is writeable and retrying with a write lock. Changes here risk stale lock type, leaked checkout, or leaked inode handles.
- Header cache eviction writes back old `diskstuff` when `inUse` is set and ignores write errors until later. This preserves startup progress but can hide early persistence failures.
- `VGetVolumePath` returns static buffers and scans partition order, so it is not reentrant and can choose the wrong volume if stale `.vol` headers exist on multiple partitions.
- Salvage scheduling can be deferred while `nUsers` or `nWaiters` are nonzero. Incorrect refcount handling can delay salvage indefinitely or schedule it while a caller still depends on header data.
- Online salvage is capped by `SALVAGE_COUNT_MAX`; repeated attach/salvage failures eventually force an error state requiring manual intervention.
- `VolumeNumber` performs loose parsing via `strtoul(name + 1, NULL, 10)` and relies on callers already matching `VFORMAT`/`VHDREXT`.
- VLRU and hash reordering perform queue manipulation while dropping `VOL_LOCK` under custom busy flags. Bugs in queue membership flags (`VOL_ON_VLRU`, `VOL_IN_HASH`, `VOL_ON_VBYP_LIST`) can create leaks, double removes, or lookup misses.
- Bitmap scanning trusts vnode index sizing and magic checks; if a vnode index is corrupt, it returns `VSALVAGE`. Bitmap allocation also performs unaligned `bit32 *` reads from byte arrays, which is an old-code portability concern.

## Test Signals

Useful tests should exercise both non-DAFS and DAFS builds when possible. Startup tests should verify that valid `.vol` files are attached or preattached, duplicate volume IDs are logged and ignored, missing partition directories fail cleanly, and `VInit` transitions wake waiters.

Attach/get tests should cover read-only, clone, dump, update, secret, and peek modes; FSSYNC checkout denial; lock retry from read to write; stale `inUse` on writeable volumes; `needsSalvaged`; `destroyMe`; unblessed/not-in-service volumes; and callback-breaking after `needsCallback`.

Lifecycle tests should assert that `VGetVolume` increments users and loads headers, `VPutVolume` releases headers to the LRU, `VOffline` waits for users and then clears `inUse`, `VForceOffline` marks `needsSalvaged`, and `VDetachVolume` sends the correct FSSYNC return operation. Timed offline tests should verify registered RX calls are interrupted only after the configured timeout.

Persistence tests should verify exact `VolumeDiskData` writes, uniquifier bump/rollover behavior, daily usage rollover, `dontSalvage` update-list/VLRU behavior, and header cache eviction writeback. Corrupt magic/version or short-read cases should return salvage errors and not leave active handles behind.

DAFS-specific tests should stress concurrent `VGetVolume` on a preattached volume, pending volume operation states, reservation cleanup, SALVSYNC/FSSYNC salvage scheduling failures, salvage priority updates, VLRU soft-detach eligibility, hash-chain reordering, and parallel shutdown passes. The most valuable observable signals are volume state transitions, `VStats` counters, correct queue/list membership, absence of leaked headers/handles, and stable behavior under repeated attach/offline/salvage cycles.
