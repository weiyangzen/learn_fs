# sources/distributed-fs/eos/mgm/geobalancer/GeoBalancer.hh

## Purpose
`GeoBalancer.hh` declares the EOS MGM per-space geo-balancing worker. It exists to reduce large fill-ratio differences between geotags by selecting files from overfilled locations and scheduling converter jobs that will create a replica in another geotag. The header also defines `GeotagSize`, a small capacity/used-bytes accumulator used while deciding whether a geotag is above the configured average.

## Important APIs, Types, And Functions
`GeotagSize` stores `mSize` and `mCapacity` and exposes `usedBytes()`, `setUsedBytes()`, `capacity()`, `setCapacity()`, and `filled()`. `filled()` is the key API: it returns used divided by capacity, and the implementation asserts that capacity is nonzero at construction.

`GeoBalancer` owns an `AssistedThread`, the target space name, a fill threshold, cached maps from geotag to filesystems and filesystem to geotag, cached `GeotagSize*` values, the current average fill ratio, a last-cache-refresh timestamp, and `mTransfers`, which tracks scheduled file ids and conversion proc paths. Public APIs are the constructor, destructor, `Stop()`, and `GeoBalance(ThreadAssistant&) noexcept`. Private helpers declared here cover cache management (`populateGeotagsInfo`, `clearCachedSizes`, `fillGeotagsByAvg`, `cacheExpired`), candidate selection (`chooseFidFromGeotag`, `fileIsInDifferentLocations`, `getFileProcTransferNameAndSize`), transfer scheduling (`prepareTransfer`, `prepareTransfers`, `scheduleTransfer`), and ongoing job cleanup (`updateTransferList`).

## Control Flow
Construction starts the background `GeoBalance` thread for one MGM space. The loop waits for namespace boot, runs only on the master MGM, requires the converter engine to be running, reads the space's `geobalancer`, `geobalancer.ntx`, and `geobalancer.threshold` configuration, refreshes geotag fill caches every `CACHE_LIFE_TIME`, cleans completed transfer records, and schedules up to the configured number of converter jobs. Scheduling chooses an over-average geotag, chooses a random filesystem in that geotag, asks the namespace for an approximately random file, rejects files already spread across locations or already in transfer, then calls the converter engine.

## State And Persistence
The header exposes only in-memory state. Runtime persistence is indirect: scheduled work is handed to `ConverterEngine`, tracked by the global file-id tracker, and represented through conversion proc names. The geotag and capacity caches are intentionally temporary and are cleared/rebuilt from `FsView` snapshots. `mTransfers` is a local guard against duplicate in-flight selections and is refreshed from the converter tracker.

## Dependencies And Integration Points
The class depends on MGM namespace types, `common::FileId`, `common::FileSystem`, `common::AssistedThread`, `XrdSysPthread`, and implementation-side MGM globals such as `gOFS`, `FsView`, namespace metadata services, and `ConverterEngine`. It is created from `FsSpace` handling in `fsview/FsView.cc`, and operational config is stored as MGM space config members. It assumes the converter is enabled and that scattered placement is the default conversion policy.

## Risks And Edge Cases
`mGeotagSizes` stores owning raw pointers, so every cache rebuild must call `clearCachedSizes()` or it leaks. `GeotagSize::filled()` divides by capacity, so zero-capacity snapshots must not be admitted. The worker mutates caches and transfer state from its own thread; integration must ensure no outside thread touches those private maps. Selection is randomized and bounded by attempts, so a heavily filtered geotag can remain over average until a later cycle. File-location comparison relies on the `mFsGeotag` cache; missing fs ids can map to empty strings through `operator[]` if the metadata contains locations absent from the current cache.

## Test Signals
Useful tests should cover construction/destruction and `Stop()`, master/slave gating, disabled converter behavior, empty or missing space views, cache refresh thresholds, per-geotag capacity aggregation, threshold filtering, scheduled transfer cleanup, rejection of files in multiple geotags, rejection of proc files and zero-size/no-location files, and behavior when `ScheduleJob()` fails. Integration tests should configure `geobalancer=on`, `geobalancer.ntx`, and threshold values on an MGM space and verify only over-threshold geotags produce converter jobs.
