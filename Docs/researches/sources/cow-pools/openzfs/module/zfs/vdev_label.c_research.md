# File Research: sources/cow-pools/openzfs/module/zfs/vdev_label.c

## Purpose
Implements OpenZFS vdev label management: physical label offsets, label config nvlist generation and reads, vdev label initialization, boot environment label storage, uberblock discovery/sync, and transactional config sync. The file defines the on-disk update choreography that keeps vdev labels and uberblocks consistent across crashes.

## Main Responsibilities
- Translate logical label numbers and offsets into physical disk offsets with `vdev_label_offset()` and reverse-map offsets with `vdev_label_number()`.
- Read and write label regions through physical ZIOs using label checksums.
- Generate vdev configuration nvlists, including topology, stats, allocation class, DTL/indirect-removal metadata, ZAP object ids, and action progress stats.
- Read the best usable label config at or below a target txg.
- Detect whether a candidate device is already in use by a pool, spare, or L2ARC device.
- Initialize labels for regular, spare, L2ARC, remove, replace, and split workflows.
- Read and write the label boot environment area in raw, nvlist, and FreeBSD bootonce-compatible forms.
- Scan all label uberblock rings to choose the best uberblock and associated config.
- Sync labels and uberblocks in a crash-consistent sequence.

## Key Entry Points
- `vdev_label_offset()`, `vdev_label_number()`: low-level label geometry helpers.
- `vdev_label_write()`: exported physical label writer; paired with local `vdev_label_read()`.
- `vdev_config_generate_stats()`: serializes vdev stats and extended queue/latency histograms.
- `vdev_config_generate()`: recursively emits a vdev subtree config nvlist.
- `vdev_top_config_generate()`: emits root top-level child count and hole array.
- `vdev_label_read_config()`: reads and selects a valid label config.
- `vdev_label_init()`: recursively initializes leaf labels and uberblock rings.
- `vdev_label_read_bootenv()`, `vdev_label_write_bootenv()`: manage label bootenv storage.
- `vdev_uberblock_compare()`, `vdev_uberblock_load()`: select import/load uberblock state.
- `vdev_uberblock_sync_list()`: writes uberblocks and flushes affected vdevs.
- `vdev_config_sync()`: top-level transactional sync for labels and uberblocks.

## Important Algorithms and Semantics
- Label placement keeps two labels at the start and two at the end of the device. `vdev_label_offset()` handles end-label relocation by subtracting total label size from physical size for labels in the second half.
- Label config selection favors the highest label txg not exceeding the requested txg. Auxiliary labels and partially initialized labels without usable txg are accepted as first-valid configs.
- Config sync is intentionally ordered:
  1. Flush data writes for the txg.
  2. Write and flush even labels.
  3. Write and flush uberblocks.
  4. Update MMP uberblock state if multihost is enabled.
  5. Write and flush odd labels.
  This preserves recovery paths if power fails before, during, or after the uberblock update.
- Uberblock comparison orders by txg, then timestamp, then valid MMP sequence. This handles duplicate txg writes from interrupted imports or multihost-aware writers.
- Uberblock load tracks both the best allowed uberblock and the latest observed uberblock. It rejects a rewind candidate if RAIDZ expansion reflow info differs from the latest uberblock.
- Expanded leaf vdevs may need end-label uberblock rings copied from label 0 because labels 2 and 3 moved.
- dRAID distributed spares are special-cased: label configs may be generated instead of read, and uberblocks/top-level configs are not written to them.

## Data and State
- Uses `vdev_phys_t` for packed config storage in `vp_nvlist`.
- Uses `vdev_label_t` regions: vdev phys area, bootenv padding area, and uberblock ring.
- Uses ABD buffers for all label I/O.
- Uses `spa_config_dirty_list` to decide which vdevs need label rewrites.
- Tracks successful writes with per-top-vdev `good_writes` counters so config sync can fail when no visible leaf accepted a label write.
- Auxiliary vdev state is handled through `spa_spares`, `spa_l2cache`, and `spa_aux_sync_uber`.

## Dependencies
Heavy integration with `spa`, `vdev`, `zio`, `nvlist`, `uberblock`, `metaslab`, scan/removal/checkpoint/rebuild stats, dRAID, ABD, and bootenv definitions. Correctness depends on spa config locks and ZIO flags such as `ZIO_FLAG_CONFIG_WRITER`, `ZIO_FLAG_CANFAIL`, `ZIO_FLAG_TRYHARD`, `ZIO_FLAG_SPECULATIVE`, and `ZIO_FLAG_IO_RETRY`.

## Edge Cases and Failure Handling
- Retries label reads/writes with `ZIO_FLAG_IO_RETRY` before declaring failure.
- Avoids consuming labels with txg greater than the selected uberblock txg.
- Records create-info metadata when refusing an already-in-use device.
- Preserves shared spare/L2ARC GUIDs when adding or replacing known auxiliary devices.
- Treats log and auxiliary label sync errors as ignorable in the per-vdev label-sync callback path.
- `nvlist_pack()` overflow is converted to `ENAMETOOLONG` during initial label writes.
