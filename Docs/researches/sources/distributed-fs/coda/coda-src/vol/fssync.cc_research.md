# sources/distributed-fs/coda/coda-src/vol/fssync.cc

Purpose: coordinates volume utilities with the running file server. In this version it is an in-process LWP/timer and shared table mechanism, not an external socket listener.

Important APIs: `FSYNC_fsInit` starts the `FSYNC_sync` LWP, which waits for volume initialization and periodically expires relocation entries. `FSYNC_clientInit` and `FSYNC_clientFinis` register/unregister utility LWPs. `FSYNC_askfs(volume, command, reason)` handles `FSYNC_ON`, `FSYNC_OFF`, `FSYNC_NEEDVOLUME`, and `FSYNC_MOVEVOLUME`. `FSYNC_CheckRelocationSite` returns a temporary moved-to server address.

Control flow/state: registered utilities get a row in `OfflineVolumes[MAXUTILITIES][MAXOFFLINEVOLUMES]`. `FSYNC_NEEDVOLUME` may offline a volume, leave read-only/dump/clone cases online, or set `VBUSY`; `FSYNC_ON` removes it from the offline list and reattaches it for update. Move commands add relocation entries and mark attached volumes `VMOVED`. Relocations age out after `REDIRECT_TIME`.

Dependencies/integration: uses LWP, IOMGR timers, volume attach/update/offline operations, and volume status fields. It is called from `VAttachVolumeById`, `VOffline`, `VDetachVolume`, and lookup/location paths. Risks include fixed utility/offline/relocation table sizes, assertion on unknown utility id, limited locking around global arrays, and semantic overload of the `reason` field for move target. Test signals: utility attach/detach while file server serves a volume, clone/dump leave-online cases, relocation expiry, MAXUTILITIES exhaustion, and failed attach cleanup path returning a volume online.
