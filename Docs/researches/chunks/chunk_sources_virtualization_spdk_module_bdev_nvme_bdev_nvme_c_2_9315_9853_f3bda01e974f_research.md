# Chunk Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.c lines 9315-9853

## Scope And Position

This chunk covers the end of `module/bdev/nvme/bdev_nvme.c`. It begins in the body of the optional CUSE config dump helper and ends at file end with SPDK trace registration. The code belongs to the SPDK NVMe bdev module in subset A, under virtualization/block-device integration.

The chunk is mostly control-plane code rather than data-path I/O submission. It serializes live NVMe bdev configuration to JSON/RPC replay records, exposes controller and discovery status helpers, updates DH-HMAC-CHAP keys with asynchronous authentication, and registers trace metadata for NVMe bdev I/O.

## APIs And Entry Points

- `bdev_nvme_config_json(struct spdk_json_write_ctx *w)` is the module `.config_json` callback wired earlier in the file through `nvme_if.config_json`.
- `bdev_nvme_get_ctrlr(struct spdk_bdev *bdev)` returns the underlying `struct spdk_nvme_ctrlr *` for an NVMe bdev.
- `bdev_nvme_set_keys(...)` is the exported asynchronous DHCHAP key-update/authentication path for a named NVMe bdev controller group.
- `nvme_io_path_info_json(...)` serializes one I/O path status object.
- `bdev_nvme_get_discovery_info(...)` emits active discovery contexts and referral transport IDs.
- `bdev_nvme_trace()`, registered by `SPDK_TRACE_REGISTER_FN`, publishes trace object/point metadata for bdev NVMe I/O.
- Under `SPDK_CONFIG_NVME_CUSE`, `nvme_ctrlr_cuse_config_json()` emits `bdev_nvme_cuse_register` replay RPCs only if CUSE controller-name lookup succeeds.

## Control Flow And State

`bdev_nvme_config_json()` dumps global NVMe bdev options, batches `bdev_nvme_attach_controller` records for all controller paths in `g_nvme_bdev_ctrlrs`, then emits dependent configuration individually: CUSE registration, bdev multipath policy overrides, discovery service RPCs, mDNS discovery config, and finally hotplug settings.

`nvme_ctrlr_config_json()` suppresses discovery-owned controllers, because those are restored via discovery RPCs. Explicit controllers include transport ID, PI check flags, timeout settings, optional PSK/DHCHAP key names, host options, digest settings, source address/service, queue count, fabrics timeout, and multipath options.

`bdev_nvme_set_keys()` allocates a context, gets keyring references, finds the named controller group, obtains live controller refs with `bdev_nvme_next_ctrlr()`, and authenticates controllers serially. For each controller it calls `spdk_nvme_ctrlr_set_keys()`, optionally authenticates the controller, then iterates connected qpairs with `spdk_for_each_channel()` and `spdk_nvme_qpair_authenticate()`. Completion releases refs, puts keys, and invokes the caller callback.

`nvme_io_path_is_current()` depends on path availability first. In active-active multipath, optimized ANA paths are current; non-optimized paths are current only when no optimized path exists. Other policies compare against `nbdev_ch->current_io_path`.

## Dependencies And Risks

Dependencies include SPDK JSON writers, NVMe controller/qpair APIs, keyring APIs, app-thread/channel iteration, CUSE APIs when enabled, trace registration, TAILQ/STAILQ lists, and local helpers from earlier chunks such as `nvme_bdev_dump_trid_json`, `bdev_nvme_write_multipath_config`, `nvme_io_path_is_available`, and controller refcount helpers.

Key risks:
- Config dump asserts `active_path_id` is the first transport path.
- Discovery-owned controllers are omitted from attach replay, so discovery config ordering matters.
- Hotplug is emitted last to avoid reconstruct-time races.
- `bdev_nvme_get_ctrlr()` asserts the bdev has at least one namespace.
- `bdev_nvme_set_keys()` assumes a valid callback.
- Disconnected qpairs are skipped during immediate authentication and must be handled by reconnect/reset paths elsewhere.
- `nvme_io_path_info_json()` assumes fully initialized `io_path`, qpair, namespace, and controller pointers.

## Cross-Chunk References

- This chunk starts mid-`nvme_ctrlr_cuse_config_json()`; its header/local declarations are immediately before line 9315.
- Module registration, global queue definitions, controller lookup, refcounting, path availability, and discovery setup are earlier in the file.
- Previous chunk code defines global options JSON and discovery/mDNS config helpers used here.
- Earlier data-path functions emit the tracepoints whose descriptions and NVMe lower-layer relations are registered at the end of this chunk.