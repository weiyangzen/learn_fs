# File Research: sources/cow-pools/openzfs/module/zfs/dmu_zfetch.c

Implements adaptive predictive prefetch for DMU dnode data and indirect blocks.

Key points:
- Maintains per-dnode `zfetch_t` state containing a bounded list of active `zstream_t` streams.
- Tunables control global disable, maximum streams, stream reap times, minimum/maximum data prefetch distance, maximum indirect prefetch distance, reorder tolerance, and tolerated hole fraction.
- Kstats track hits, future accesses, stride detections, past accesses, misses, max-stream pressure, issued I/O, and active I/O.
- `dmu_zfetch_init()` / `dmu_zfetch_fini()` initialize and tear down per-dnode stream state.
- `dmu_zfetch_stream_create()` creates, reuses, or reaps streams based on age, reference count, file size, and `zfetch_max_streams`.
- Streams record current expected block, recent future ranges, data prefetch distance, indirect prefetch distance, prefetch windows, missed status, and whether more prefetched blocks were consumed.
- `dmu_zfetch_hit()` advances a stream on sequential hits and folds future ranges into the current progress.
- `dmu_zfetch_future()` records bounded out-of-order future reads and converts them into stream progress when the filled fraction is high enough.
- `dmu_zfetch_prime()` seeds a stream for callers that already know an upcoming sequential range.
- `dmu_zfetch_prepare()` classifies accesses as hits, near hits, future ranges, past accesses, or misses, then calculates data and indirect prefetch windows.
- `dmu_zfetch_run()` issues the actual data and indirect `dbuf_prefetch_impl()` calls, batching concurrent callers so the last caller performs the stream’s prefetch work.
- `dmu_zfetch()` is the simple wrapper that prepares and immediately runs a prefetch.

Behavioral details:
- Predictive prefetch is skipped when disabled, when the objset requests no prefetch, or when indirect vdev mappings are not loaded.
- Metadata-only objset mode disables data prefetch while still allowing indirect prefetch.
- Small files and first-block reads have fast paths to avoid unnecessary stream creation.
- Prefetch distance ramps quickly up to the minimum distance, grows more slowly after that, and is capped by configured maximums.
- Active prefetch pressure against ARC size limits aggressive doubling.
- Completion callback `dmu_zfetch_done()` updates stream state and active-I/O accounting.

Dependencies and interactions:
- Uses dnode structure locks, dbuf prefetch APIs, ARC flags, spa indirect-vdev readiness, refcounts, weighted sums, aggregate sums, and kstats.
- Complements prescient prefetch paths used by traversal/send; the global disable only disables predictive prefetch, not prescient prefetch.

Research relevance:
- This file is OpenZFS’s adaptive sequential/reordered read predictor. It reduces demand-read latency for regular file and volume access while bounding misprediction cost through stream limits, distance caps, stale-stream reap, and ARC pressure checks.
