# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSIoSupport.cpp

## Purpose

`AFSIoSupport.cpp` supports paging and non-cached I/O over OpenAFS cache-file extents. It maps a file offset/length onto cached extents, collapses cache-contiguous extents into I/O runs, allocates and submits child IRPs, aggregates completions, and provides a direct memory-copy path against `AFSLibCacheBaseAddress`.

## Important APIs, types, and functions

`AFSGetExtents` counts covering extents and discontiguous cache runs. `AFSSetupIoRun` builds `AFSIoRun` entries and child IRPs. `AFSStartIos` fills child IRP stack locations and calls the cache device. `CompletionFunction` forwards child status, releases MDLs, frees the IRP, and returns `STATUS_MORE_PROCESSING_REQUIRED`. `AFSCompleteIo` aggregates child completion into the master IRP, event, or gather allocation lifetime. `AFSProcessExtentRun` copies data between a caller buffer and mapped cache memory. Key structures are `AFSExtent`, `AFSIoRun`, and `AFSGatherIo`.

## Control flow

The extent walkers assume `From` contains the starting offset, then advance with `NextExtent(..., AFS_EXTENTS_LIST)` until the requested span is covered. `AFSGetExtents` increments extent count for every extent and run count whenever the next cache offset is not contiguous.

`AFSSetupIoRun` computes the cache offset for each run, merges adjacent cache-contiguous extents, trims the final run, computes the buffer offset, allocates child IRPs with `CacheDevice->StackSize + 1`, and initializes kernel-mode child request fields. On allocation failure it frees created child IRPs and returns `STATUS_INSUFFICIENT_RESOURCES`.

`AFSStartIos` gets the related cache device, writes read/write style stack parameters, increments `Gather->Count` before submission, installs the completion routine, and calls `IoCallDriver`. `AFSCompleteIo` records failure status, decrements the outstanding count, completes/signals/frees when it reaches zero, and updates the master IRP on failure. `AFSProcessExtentRun` uses the same run coalescing to perform `RtlCopyMemory` for read or write direction.

## State and persistence behavior

The file mutates transient IRPs, run arrays, gather counters/status, and caller/cache buffers. Extent metadata is assumed stable while these helpers run. `CompletionFunction` owns child IRP and MDL cleanup; `AFSCompleteIo` owns gather lifetime after the last child completion.

## Dependencies and integration points

Dependencies include FCB extent metadata, extent-list helpers, Windows IRP APIs, `IoGetRelatedDeviceObject`, `IoCallDriver`, interlocked counters, kernel events, OpenAFS completion/allocation helpers, and the global cache mapping `AFSLibCacheBaseAddress`. Higher-level read/write paths are expected to locate the starting extent and hold necessary synchronization.

## Risks and test signals

The walkers have asserts but no explicit end-of-list guard, so corrupt or incomplete extents are dangerous. `ULONG` lengths require callers to split very large I/O. `AFSStartIos` increments the gather count before `IoCallDriver`; synchronous lower-layer failure semantics must still balance completion. Allocation-failure cleanup assumes the run array is zero-initialized. Tests should cover single and multi-extent spans, contiguous coalescing, discontiguous runs, final trimming, allocation failure cleanup, child failure aggregation, synchronous and asynchronous gather lifetimes, and driver-verifier checks for IRP/MDL leaks.
