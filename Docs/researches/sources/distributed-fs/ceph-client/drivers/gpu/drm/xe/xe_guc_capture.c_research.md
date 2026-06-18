# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.c

## Purpose

`xe_guc_capture.c` defines GuC error-capture register lists, registers those lists for ADS consumption, processes GuC state-capture log output after engine resets, supports manual engine capture, matches captured nodes to timed-out exec queues, and prints captured engine register state for devcoredump/debug output.

## Important APIs, Types, and Functions

- Public list APIs: `xe_guc_capture_getlistsize()`, `xe_guc_capture_getlist()`, `xe_guc_capture_getnullheader()`, `xe_guc_capture_ads_input_worst_size()`, and `xe_guc_capture_get_reg_desc_list()`.
- Runtime processing: `xe_guc_capture_process()` reads GuC log capture output and turns it into parsed nodes on `outlist`.
- Snapshot integration: `xe_guc_capture_get_matching_and_lock()`, `xe_engine_manual_capture()`, `xe_engine_snapshot_capture_for_queue()`, `xe_engine_snapshot_print()`, and `xe_guc_capture_put_matched_nodes()`.
- Init: `xe_guc_capture_init()` selects platform static register lists and initializes lists; `xe_guc_capture_steered_list_init()` creates dynamic steered register descriptors and preallocated output nodes.
- Internal state includes `struct xe_guc_state_capture`, `__guc_capture_parsed_output`, ADS list caches, dynamic extension lists, and cache/out linked lists.

## Control Flow

At init, the file selects register descriptor tables by graphics version. ADS population asks for sizes and cached list blobs; after hwconfig, steered render/compute registers are expanded per DSS steering target. Runtime GuC capture notifications cause the driver to copy log-buffer state, detect overflow, parse group headers and capture headers from the circular state-capture region, allocate or recycle preallocated parsed nodes, attach global/class/instance register lists, and add nodes to `outlist`. Later devcoredump code matches nodes by GuC class, instance, GuC id, and LRCA or falls back to manual MMIO capture.

## State and Persistence Behavior

`guc->capture` persists for the GuC lifetime and owns descriptor caches, dynamic extension lists, node cache, and output list. Parsed nodes are recycled between cache and output lists; matched nodes are marked `locked` to prevent stale removal until devcoredump releases them. The GuC log read pointer and flush flags are updated in the log BO after processing.

## Dependencies and Integration Points

It integrates GuC capture/log ABI, ADS registration, GT topology steering, hardware engine definitions, LRC and exec-queue state, GuC submission reset handlers, devcoredump snapshots, MMIO/MCR reads, DRM managed allocations, and GuC CT acknowledgements for log flush completion.

## Risks and Edge Cases

The parser must handle circular buffer wrap, overflow, malformed lengths, partial captures, unknown capture types, and too many registers per node. Linked-list access is not guarded by an obvious lock in this file, so callers rely on higher-level sequencing around capture processing and devcoredump. The print path still dereferences live GT/engine pointers, called out by an in-code FIXME. Dynamic steered-list sizing depends on fuse topology being initialized.

## Test Signals

Tests should exercise platform list selection, size caching, steered list generation from DSS masks, circular log parsing with wrap/overflow/malformed entries, node recycling and stale-match removal, manual capture on render/compute and non-render classes, 64-bit register print ordering warnings, and matching by GuC id/LRCA. Integration signals include devcoredump output containing GuC or manual capture data after resets.
