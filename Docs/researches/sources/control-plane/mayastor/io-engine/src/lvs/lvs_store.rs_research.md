# sources/control-plane/mayastor/io-engine/src/lvs/lvs_store.rs

## Purpose
This file implements SPDK logical volume stores as io-engine pools. It creates/imports/destroys/exports/grows blobstores on backing bdevs, manages optional crypto wrapping, auto-restores shared lvols, tracks pool I/O stall state, and creates replicas.

## Important APIs, types, and functions
`Lvs` wraps `NonNull<spdk_lvol_store>` and exposes lookup, iteration, capacity/free/used/committed, base-bdev access, metadata page stats, uuid, encryption detection, stall detection, import/create/export/destroy/grow, snapshot/lvol iteration, and lvol creation. `LvsBackendBdevs` owns the bdev setup/rollback context for pool create/import, including base bdev ops, crypto bdev state, and top-level pool bdev name. Constants define 1 MiB cluster alignment, 4 MiB default cluster size, and 1 GiB maximum cluster size. `LvsPtpl` manages pool-level PTPL directories under `pool/<uuid>`.

## Control flow
Create/import starts by parsing a single disk URI, creating the underlying bdev if missing, optionally creating a crypto vbdev, and replacing pool args with the top-level bdev name. Import rejects claimed bdevs, calls `vbdev_lvs_import`, validates pool name and optional uuid, restores shared replicas, creates pool info cache, enables stall detection, and destroys pending discarded snapshots. Create validates cluster size and metadata expansion ratio, calls SPDK lvs create with or without explicit uuid, then looks up the created pool and enables tracking.

Export and destroy unshare all lvol bdevs without persisting unshare state, unload or destruct the SPDK store, remove pool info if gone, clean up crypto/base bdevs, and remove PTPL on destroy. Grow rescans AIO/uring base bdevs, waits for crypto bdev resize if encrypted, updates blobstore block count, calls live grow, and verifies capacity increased. `share_all` reads persisted `Shared`/`AllowedHosts` xattrs and retries briefly while old unshare operations complete.

## State and persistence behavior
Persistent pool state lives on the backing blobstore superblock and blob metadata. Persistent share state for replicas lives in lvol xattrs and PTPL files. In-memory pool status is stored in `pool_information` cache, including I/O stalled state and transition timestamps. Create/import rollback destroys bdevs created during the failed attempt.

## Dependencies and integration points
The file depends on SPDK lvs/blobstore APIs, bdev URI/create/destroy APIs, crypto vbdev helpers, core bdev/share/reactor/environment types, eventing, `Lvol`, snapshot cleanup, pool args, pool info cache, and mayastor sleep. It is the core implementation used by the LVS backend factories outside this subset.

## Risks and test signals
Pool creation assumes exactly one disk. Import can hang if a bdev is examined while already claimed, so it checks `is_claimed` first. `share_all` has a fixed two-second retry window and logs but does not fail import on share restoration failure. Grow support depends on AIO/uring rescan and async crypto resize events. Stall handling disables timeout callbacks during reset and relies on superblock read to mark recovery. Tests should cover import/create rollback, encrypted pool setup/cleanup, uuid/name mismatch errors, cluster-size and max-expansion validation, auto-share restoration, destroy/export cleanup, live grow, and I/O stall reset transitions.
