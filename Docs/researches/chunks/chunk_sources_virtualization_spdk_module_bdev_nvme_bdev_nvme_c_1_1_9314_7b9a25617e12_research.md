# Chunk Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.c lines 1-9314

## Scope

This chunk covers the NVMe bdev module from file start through the end of the concrete NVMe command wrappers and the beginning of config JSON helpers. It includes module registration, global options, controller/bdev/channel models, multipath I/O path selection, retry/error handling, reset/failover/reconnect, namespace population/depopulation, discovery, hotplug, public create/delete/options APIs, and command submission wrappers for NVM/ZNS/admin/passthrough/abort/copy.

The file continues after line 9314 with controller/config JSON emission, CUSE config, key reauthentication, I/O path JSON, discovery info JSON, logging, and tracing. Those are cross-chunk continuation points, not owned by this chunk except where helper entry points are declared or first entered.

## Main APIs And Entry Points

- `SPDK_BDEV_MODULE_REGISTER(nvme, &nvme_if)` registers the `nvme` bdev module with async fini, init/fini callbacks, config JSON callback, and per-I/O context size.
- Public lifecycle/configuration APIs include `spdk_bdev_nvme_create()`, `spdk_bdev_nvme_delete()`, `spdk_bdev_nvme_get_opts()`, `spdk_bdev_nvme_set_opts()`, `spdk_bdev_nvme_get_default_ctrlr_opts()`, `bdev_nvme_set_hotplug()`, `bdev_nvme_start_discovery()`, `bdev_nvme_stop_discovery()`, `bdev_nvme_set_preferred_path()`, and deprecated `spdk_bdev_nvme_set_multipath_policy()`.
- The bdev function table `nvmelib_fn_table` routes bdev operations to `bdev_nvme_submit_request_initial()`, `bdev_nvme_io_type_supported()`, channel acquisition, JSON info/config, module context, memory-domain reporting, accel sequence support, and device statistics.
- Internal control APIs wrap SPDK channel iteration: `nvme_ctrlr_for_each_channel()` and `nvme_bdev_for_each_channel()` allocate iterator contexts and call `spdk_for_each_channel()`.

## Core State

- `g_opts` is the module-wide `spdk_bdev_nvme_opts` default/runtime configuration: timeouts, retry counts, reconnect policy, transport knobs, statistics toggles, flush enablement, multipath defaults, DH-HMAC-CHAP masks, and acceleration support.
- `g_nvme_bdev_ctrlrs` is the top-level list of logical NVMe bdev controllers. Each owns controller instances and namespace bdevs.
- `nvme_ctrlr` owns the SPDK controller, path list, namespace RB tree, pollers, ANA buffers/state, key references, OPAL device, memory-domain type cache, refcount, and state flags for destruct/reset/disable/reconnect/failover.
- `nvme_bdev` wraps `spdk_bdev` and tracks namespace paths for multipath, bdev refcount, error stats, multipath policy/selector/min-I/O, OPAL support, and update state.
- `nvme_bdev_io` stores NVMe extended opts, selected I/O path, submit timestamp, retry count/timer, primary/fused iovec cursors, saved completion, fused command state, zone-report buffer/progress, and retry linkage.

## Control Flow

- Init registers `g_nvme_bdev_ctrlrs` as an SPDK I/O device whose per-thread channels are NVMe poll groups. Fini stops hotplug/discovery and destructs controllers asynchronously.
- Controller deletion unregisters pollers/interrupts, starts async NVMe detach, then frees ANA buffers, OPAL, namespace tree, path IDs, key refs, and controller grouping.
- Bdev channel creation snapshots multipath policy and adds one `nvme_io_path` for each namespace path. Path deletion releases the controller channel but defers freeing the path until qpair deletion to protect in-flight completions.
- I/O path selection supports active-passive caching, active-active round-robin with `rr_min_io`, and active-active queue-depth selection. ANA optimized paths are preferred over non-optimized.
- `bdev_nvme_submit_request_initial()` initializes retry state, selects a path, and dispatches to wrappers for read/write/compare/fused compare-write/unmap/write-zeroes/reset/flush/ZNS/admin/passthrough/abort/copy/write-uncorrectable.
- Completion handles stats, NVMe error counters, retry limits, DNR/abort cases, ANA update requests, delayed retries, and bdev status conversion.
- Controller reset destroys/disconnects qpairs, reconnects the controller, checks namespaces, recreates qpairs, clears pending resets, and decides whether to destruct, delayed-reconnect, or fail over.
- Failover rotates alternate TRIDs, preserves failed-path timing for reconnect backoff, and resets to establish the new active path.
- Discovery connects to discovery controllers, reads discovery log pages, creates NVMe bdev controllers for discovered NVM entries, removes missing controllers, and reacts to discovery AERs.

## Namespace And Bdev Population

- `nvme_ctrlr_create()` constructs controller state, copies key references, creates the initial path, caches memory-domain types, rejects OCSSD, initializes pollers/interrupts/timeouts/remove callbacks, creates OPAL if supported, groups the controller, initializes ANA, and registers it as an I/O device.
- `nvme_ctrlr_populate_namespaces()` full-scans or processes changed namespace lists. Existing namespaces are resized/depopulated; new active namespaces are inserted into the RB tree and exposed as bdevs.
- `nvme_bdev_create()` initializes multipath policy, fills bdev geometry/capabilities, registers the bdev I/O device, links namespace/bdev/controller structures, and registers the public bdev.
- Multipath namespace attach requires shared namespace support and identity match by NGUID/EUI64/UUID/CSI, then dynamically adds I/O paths to open bdev channels.
- Depopulation decrements bdev refcount, unregisters the bdev on last namespace, or removes only that namespace and deletes dynamic I/O paths.

## Concrete NVMe Command Wrappers

- Read/write use `spdk_nvme_ns_cmd_read_iov()` and `spdk_nvme_ns_cmd_write_iov()` with metadata, DIF flags, memory domains, directive fields, and accel sequence support.
- PI/DIF error diagnostics can perform a second no-PI read before completing with the original error.
- Zone append uses single-buffer or vectored ZNS append APIs and stores appended LBA into `offset_blocks`.
- Compare and fused compare-and-write maintain separate primary/fused iovec cursors and preserve compare failure status over write completion.
- Unmap builds DSM deallocate ranges; write zeroes enforces the 16-bit NVMe NLB limit.
- ZNS get-zone-info allocates a report buffer, validates zone alignment/count, may issue multiple reports, converts descriptors to bdev zone info, and frees the buffer on completion.
- Admin passthrough scans for an available controller and checks MDTS. I/O passthrough fills `cmd->nsid` and validates data/metadata sizes.
- Abort first removes queued retry I/O, then uses `spdk_nvme_ctrlr_cmd_abort_ext()` on the known path or scans paths.

## Dependencies

- SPDK bdev core: module registration, bdev registration/unregistration, completion/status, channel iteration, stats, block-count notification, descriptors, and buffer acquisition.
- SPDK NVMe library: connect/detach/reconnect/disconnect, qpair allocation/connect/disconnect/free, poll groups, namespace commands, raw passthrough, AER/ns callbacks, timeout callbacks, discovery log page, ANA log page, ZNS, copy, write-uncorrectable, transport IDs/options, and identify data.
- SPDK thread/poller/interrupt APIs, accel and memory-domain APIs, DIF/DIX, keyring, OPAL, JSON, trace/DTrace/logging, endian/net/string/uuid utilities.

## Risks And Invariants

- Most topology mutation asserts app-thread context. Violating this risks races in RB/TAILQ/STAILQ structures and refcounts.
- Final controller ref release asserts no reset/ANA/cache-clear operation is active and `destruct` is true.
- `_bdev_nvme_delete_io_path()` intentionally defers path freeing until qpair deletion; changing that risks completion-time use-after-free.
- Reset I/O has an explicit TODO risk: cached `bio->io_path` can be removed during namespace depopulation, causing undefined behavior.
- Retry of accel sequences is disabled because sequence execution state cannot be known safely after errors.
- `spdk_bdev_nvme_set_opts()` is rejected after init once controllers exist, so runtime option changes are intentionally constrained.

## Cross-Chunk References

- `bdev_nvme_write_multipath_config()` and `bdev_nvme_opts_config_json()` begin near the end of this chunk and continue into config JSON helpers after line 9314.
- Post-9314 code continues with controller config JSON, hotplug/multipath JSON, key reauthentication, I/O path JSON, discovery info JSON, log registration, and trace registration.
- The final merged per-file report is intentionally not created by this chunk.