# Group Research: group_1744_spdk_sources_virtualization_spdk_lib_jsonrpc_jsonrpc_server_c_sourc_4335ef54636f

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server.c -->
# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server.c

Implements JSON-RPC 2.0 protocol parsing, request object validation, response construction, error response construction, logging, send-buffer growth, and batch request aggregation for SPDK's JSON-RPC server.

Key entry points:
- `jsonrpc_parse_request()` detects a complete JSON value from a streaming receive buffer, copies it into request-owned storage, parses it in place, and dispatches top-level objects or arrays.
- `parse_single_request()` validates `jsonrpc`, `method`, `params`, and `id` fields and calls `jsonrpc_server_handle_request()` or `jsonrpc_server_handle_error()`.
- `spdk_jsonrpc_begin_result()`, `spdk_jsonrpc_end_result()`, `spdk_jsonrpc_send_bool_response()`, `spdk_jsonrpc_send_error_response()`, and `spdk_jsonrpc_send_error_response_fmt()` are the public response helpers.
- `jsonrpc_alloc_request()` and `jsonrpc_free_request()` manage per-request buffers, JSON writer contexts, connection outstanding counters, and queue membership.
- `jsonrpc_process_batch_array()`, `decode_batch_element()`, `jsonrpc_complete_batched_request()`, and `jsonrpc_batch_finalize_and_send()` implement JSON-RPC batch behavior.
- `spdk_jsonrpc_set_log_level()` and `spdk_jsonrpc_set_log_file()` configure request/response logging.

Core mechanics:
- Parsing is two-pass: first `spdk_json_parse()` finds whether a complete JSON value is available and where it ends; the second pass decodes into `request->values` with `SPDK_JSON_PARSE_FLAG_DECODE_IN_PLACE`.
- Request validation accepts JSON-RPC version `"2.0"` when present, requires a string method, accepts `id` only as string/number/null, and allows `params` only as object, array, or null.
- Notifications are represented by a missing or null `id`; `spdk_jsonrpc_end_result()` skips sending a response for those requests.
- Response data is accumulated through `spdk_json_write_begin()` using `jsonrpc_server_write_cb()`, which grows `send_buf` by doubling until `SPDK_JSONRPC_SEND_BUF_SIZE_MAX`.
- Parse errors are treated as unrecoverable on the stream because there is no guaranteed resynchronization point, so `jsonrpc_parse_request()` returns an error after emitting a parse error response.
- Batch requests take ownership of the original receive buffer and JSON value array, allocate individual request objects for each element, and collect non-empty per-item responses into a single JSON array.
- Batch finalization uses an extra completion count to avoid sending the aggregate response before all array elements have been decoded and any synchronous completions have run.

Important invariants:
- A request must explicitly send or skip its response before `jsonrpc_free_request()`; this is enforced by `assert(request->response == NULL)`.
- `begin_response()` asserts `send_len == 0` so callers cannot prepend a second response object onto an existing buffer.
- Batch responses omit notification results and emit no payload when every batch element was a notification.
- `conn->outstanding_requests` is incremented when a request is allocated and decremented only when the request is freed.
- Request and batch send buffers allocate one extra byte so the send path can append a temporary null terminator for logging or debugging.
- Batch aggregation is protected by `batch->lock` because individual requests may complete asynchronously.

Filesystem/block relevance:
- This file is not a filesystem algorithm, but it is SPDK's control-plane protocol core. Storage components such as bdevs, lvols, and keyring modules expose management operations through this request/response machinery.

Notable risks:
- Batch finalization queues a pseudo-request directly on the connection send queue; correctness depends on the connection's outstanding counter and queue cleanup paths treating it consistently with normal requests.
- `jsonrpc_parse_request()` copies `len` bytes but passes the original `size` into the second parse call; this relies on the copied buffer still containing enough bytes or the parser stopping at `end`.
- Logging mutates the request buffer by removing newlines when logging is enabled, which is intentional for backward compatibility but means logged/parsing storage is not strictly immutable text.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server_tcp.c -->
# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server_tcp.c

Implements the TCP/socket side of SPDK's JSON-RPC server: listening, accepting fixed-pool connections, polling receives and sends, queuing responses, handling close callbacks, and shutting the server down.

Key entry points:
- `spdk_jsonrpc_server_listen()` allocates a server, initializes the free connection pool, creates a nonblocking close-on-exec stream socket, binds, and listens.
- `spdk_jsonrpc_server_poll()` is the main progress loop for accepting new connections, sending queued responses, receiving new request bytes, and removing fully closed connections.
- `jsonrpc_server_conn_recv()` receives bytes into the connection buffer and repeatedly calls `jsonrpc_parse_request()` until no full request remains.
- `jsonrpc_server_send_response()` moves a completed request from the outstanding queue to the send queue.
- `jsonrpc_server_conn_send()` drains queued response buffers through `send()` and frees requests after their full payload is written.
- `spdk_jsonrpc_conn_add_close_cb()` and `spdk_jsonrpc_conn_del_close_cb()` install or remove a single connection-close callback.
- `spdk_jsonrpc_server_shutdown()` closes the listen socket and all active connections.

Core mechanics:
- The server keeps a fixed array of `SPDK_JSONRPC_MAX_CONNS` connection objects, split between `free_conns` and active `conns`.
- Accepted sockets are made nonblocking, receive/send queues are initialized, and a per-connection spin lock protects request queues and callback state.
- Receive parsing supports multiple JSON values in one socket read by advancing `offset` by the byte count returned from `jsonrpc_parse_request()` and compacting leftover bytes with `memmove()`.
- Send progress uses `conn->send_request` as the currently partially written response and a `send_offset` plus shrinking `send_len` to handle short writes.
- Connection close marks all outstanding requests' `conn` pointers as `NULL`; batched requests also have their batch connection nulled so later completions skip sending.
- Closed sockets are removed only after `outstanding_requests` reaches zero, allowing asynchronous request handlers to complete and free their requests safely.

Important invariants:
- `send_queue` and `outstanding_queue` are protected by `conn->queue_lock`.
- A response is queued only if the connection is not already marked closed.
- `jsonrpc_server_conn_remove()` asserts `send_queue` is empty after cleanup and before returning the object to the free pool.
- `spdk_jsonrpc_server_poll()` sends before receiving on each connection, which lets already completed responses make progress even if the peer stops sending new input.
- Parse failure closes the connection because stream resynchronization is not guaranteed.

Filesystem/block relevance:
- This file is the network transport for SPDK's JSON-RPC management plane. It carries configuration and runtime control commands for storage subsystems but does not implement block or filesystem state itself.

Notable risks:
- `jsonrpc_server_accept()` uses `accept()` rather than `accept4()`, so close-on-exec is applied to the listen socket but not explicitly to accepted sockets in this file.
- `spdk_jsonrpc_server_shutdown()` frees the server immediately after closing connections; callers must ensure no asynchronous users retain the server object.
- Close callbacks are single-slot only; attempts to register a second distinct callback return `-ENOSPC`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server_tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/keyring/Makefile -->
# File Research: sources/virtualization/spdk/lib/keyring/Makefile

Builds SPDK's `keyring` library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares shared-library ABI version `SO_VER := 4` and `SO_MINOR := 0`.
- Builds `keyring.c` and `keyring_rpc.c` into `LIBNAME = keyring`.
- Uses `spdk_keyring.map` as the library export map.
- Includes the standard `mk/spdk.lib.mk` library rules.

Filesystem/block relevance:
- The keyring library provides secret/key management used by storage modules such as crypto-capable bdevs, so this Makefile controls whether the keyring implementation and RPC surface are linked as an SPDK library.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/keyring/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/keyring/keyring.c -->
# File Research: sources/virtualization/spdk/lib/keyring/keyring.c

Implements SPDK's global keyring registry with module-backed key storage, lazy probing, reference counting, removed-key lifetime handling, module initialization/cleanup, and config/introspection helpers.

Key entry points:
- `spdk_keyring_add_key()` registers a key owned by a `spdk_keyring_module` and delegates module-specific storage to `module->add_key()`.
- `spdk_keyring_remove_key()` removes an existing key if it is owned by the requesting module.
- `spdk_keyring_get_key()`, `spdk_keyring_put_key()`, and `spdk_key_dup()` manage references to keys.
- `spdk_key_get_name()`, `spdk_key_get_key()`, `spdk_key_get_ctx()`, and `spdk_key_get_module()` expose key metadata, secret material, module-private context, and ownership.
- `spdk_keyring_for_each_key()` iterates active keys and optionally removed keys.
- `spdk_keyring_register_module()`, `spdk_keyring_init()`, and `spdk_keyring_cleanup()` manage module lifecycle.
- `spdk_keyring_write_config()` and `keyring_dump_key_info()` export module/key metadata to JSON.

Core mechanics:
- The implementation currently supports only a global keyring. Names like `"key0"` and `":key0"` compare as the same global key, while `"ring:key0"` is rejected because named keyrings do not exist.
- Keys live on `g_keyring.keys` while active and move to `g_keyring.removed_keys` after removal if references remain.
- Each `spdk_key` includes inline module-private context immediately after the struct; `spdk_key_get_ctx()` returns `key + 1`.
- `spdk_keyring_get_key()` first searches active keys, then calls each registered module's `probe_key()` callback to lazily instantiate keys not already present.
- Probed keys are automatically removed when the last external reference is dropped and only the keyring's own reference remains.
- Keyring initialization creates a recursive mutex, then initializes registered modules. Modules returning `-ENODEV` are skipped and removed from the module list.
- Cleanup removes all active keys, forcibly frees removed keys that still have references after warning, then calls module cleanup callbacks.

Important invariants:
- All key list and reference count operations are protected by `g_keyring.mutex`.
- `keyring_free_key()` requires `refcnt == 0`.
- Removed keys stay valid until their outstanding references are put.
- A module may only remove keys it owns.
- Active key names must be unique after stripping any leading global-keyring prefix.
- `spdk_key_get_key()` returns `-ENOKEY` for removed keys and otherwise delegates secret retrieval to the owning module.

Filesystem/block relevance:
- This is SPDK's in-process secret registry. Storage stacks that need encryption keys can reference named keys without embedding the key material directly in block-device configuration.

Notable risks:
- `spdk_key_dup()` assumes a non-null key and does not validate removed state.
- `spdk_keyring_register_module()` inserts modules without locking; the intended use is static/early registration before concurrent keyring operations.
- Cleanup forcibly sets leaked removed-key references to zero, which prevents memory leaks at shutdown but can hide caller lifetime bugs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/keyring/keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/keyring/keyring_internal.h -->
# File Research: sources/virtualization/spdk/lib/keyring/keyring_internal.h

Provides the private keyring header shared by the keyring implementation and keyring RPC code.

Key contents:
- Includes `spdk/json.h` and `spdk/keyring.h`.
- Declares `keyring_dump_key_info(struct spdk_key *key, struct spdk_json_write_ctx *w)`.
- Uses a normal include guard, `SPDK_KEYRING_INTERNAL_H`.

Filesystem/block relevance:
- This header keeps the RPC layer from duplicating key metadata serialization logic while leaving the helper out of the public keyring API.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/keyring/keyring_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/keyring/keyring_rpc.c -->
# File Research: sources/virtualization/spdk/lib/keyring/keyring_rpc.c

Adds the JSON-RPC method for listing keyring keys.

Key entry points:
- `rpc_keyring_get_keys()` emits a JSON result array and iterates all active and removed keys with `spdk_keyring_for_each_key(..., SPDK_KEYRING_FOR_EACH_ALL)`.
- `rpc_keyring_for_each_key_cb()` writes one JSON object per key using `keyring_dump_key_info()`.
- `SPDK_RPC_REGISTER("keyring_get_keys", rpc_keyring_get_keys, SPDK_RPC_RUNTIME)` registers the method at runtime.

Core mechanics:
- The RPC takes no decoded parameters in this file.
- Each returned object includes the key info emitted by `keyring_dump_key_info()`: name, module, removed flag, probed flag, refcount, and any module-specific dump fields for active keys.

Filesystem/block relevance:
- This is the management-plane view of SPDK's key registry, useful for inspecting keys that storage components may use for encryption or authentication.

Notable risks:
- The RPC includes removed keys and reference counts, which is helpful for diagnostics but exposes internal lifetime state to callers with RPC access.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/keyring/keyring_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/log/Makefile -->
# File Research: sources/virtualization/spdk/lib/log/Makefile

Builds SPDK's `log` library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares ABI version `SO_VER := 9`, `SO_MINOR := 1`, and `SO_SUFFIX := $(SO_VER).$(SO_MINOR)`.
- Builds `log.c`, `log_flags.c`, and `log_deprecated.c` into `LIBNAME = log`.
- Adds `-Wpointer-arith` to `CFLAGS`.
- Uses `spdk_log.map` as the export map and includes `mk/spdk.lib.mk`.

Filesystem/block relevance:
- Logging is cross-cutting infrastructure used by SPDK storage subsystems for diagnostics, runtime control-plane visibility, and deprecation reporting.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/log/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/log/log.c -->
# File Research: sources/virtualization/spdk/lib/log/log.c

Implements SPDK's base logging backend: log levels, stderr/syslog routing, optional custom callbacks, timestamp generation, file logging, and hex dumping.

Key entry points:
- `spdk_log_set_level()` / `spdk_log_get_level()` configure syslog emission level.
- `spdk_log_set_print_level()` / `spdk_log_get_print_level()` configure stderr emission level.
- `spdk_log_open()`, `spdk_log_open_ext()`, and `spdk_log_close()` configure syslog or caller-provided log callbacks/open/close hooks.
- `spdk_log_enable_timestamps()` toggles timestamp prefixes.
- `spdk_log()` and `spdk_vlog()` are the primary variadic logging paths.
- `spdk_flog()` and `spdk_vflog()` write formatted log records to an arbitrary `FILE`.
- `spdk_log_dump()` prints a hex/ascii dump of a memory buffer.

Core mechanics:
- If a custom `g_log_opts.log` callback is installed, `spdk_vlog()` delegates immediately and bypasses built-in filtering and output formatting.
- Built-in logging filters independently against `g_spdk_log_print_level` for stderr and `g_spdk_log_level` for syslog.
- `spdk_log_to_syslog_level()` maps SPDK levels to syslog severities and drops `SPDK_LOG_DISABLED`.
- Messages are formatted into a 1024-byte stack buffer first; longer output attempts `vasprintf()` and falls back to truncated stack output on allocation failure.
- Timestamp prefixes use `CLOCK_REALTIME`, local time, and microsecond precision unless disabled.
- File/line/function metadata is included when `file` is non-null; otherwise the message is written without source metadata.
- `fdump()` emits 16-byte rows with offsets, hex bytes, and printable ASCII.

Important invariants:
- Log level setters assert the level is between `SPDK_LOG_DISABLED` and `SPDK_LOG_DEBUG`.
- `spdk_log_close()` clears the global options after running any close hook.
- `spdk_vflog()` always flushes its target file.
- The static `spdk_level_names[]` array relies on enum values matching its indexed entries.

Filesystem/block relevance:
- This file supplies diagnostics for all SPDK modules, including block-device and logical-volume code. It is not storage logic itself, but it is essential for operational debugging.

Notable risks:
- `localtime()` is not thread-safe on all platforms; concurrent logging can race on the returned static state.
- A custom log callback receives the original `va_list`; callback implementations must consume it correctly because built-in formatting will not run.
- `spdk_vlog()` uses `rc > MAX_TMPBUF` rather than `rc >= MAX_TMPBUF` when deciding to allocate an expanded buffer, so exactly boundary-sized formatted output may remain truncated by `vsnprintf()` semantics.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/log/log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/log/log_deprecated.c -->
# File Research: sources/virtualization/spdk/lib/log/log_deprecated.c

Implements SPDK's deprecation registry and rate-limited warning emission for deprecated features.

Key entry points:
- `spdk_log_deprecation_register()` creates a deprecation record with tag, description, target removal release, and warning rate limit.
- `spdk_log_deprecated()` records a hit and emits a warning when not suppressed by rate limiting.
- `spdk_log_deprecation_find_by_tag()` looks up a registered deprecation.
- `spdk_log_for_each_deprecation()` iterates all registered deprecations.
- `spdk_deprecation_get_tag()`, `spdk_deprecation_get_description()`, `spdk_deprecation_get_remove_release()`, and `spdk_deprecation_get_hits()` expose deprecation metadata.

Core mechanics:
- A constructor records a monotonic epoch at library load time.
- Timestamps are tracked as nanoseconds since that epoch using `CLOCK_MONOTONIC`.
- Each deprecation record stores hit count, last logged time, rate-limit interval, and deferred warning count.
- Rate-limited calls increment `deferred` and return without logging until the interval expires.
- When a warning is emitted after suppression, an additional warning reports how many messages were suppressed.

Important invariants:
- Tags, descriptions, and removal-release strings must fit in fixed-size arrays; this is enforced with assertions before allocation.
- A null deprecation pointer is treated as a programmer error: it logs, asserts false, and returns.
- The implementation intentionally accepts approximate counters under multithreaded races to avoid locking hot paths.

Filesystem/block relevance:
- Storage APIs evolve over time; this file provides a uniform way for block and filesystem-adjacent SPDK modules to flag deprecated behavior while limiting log volume.

Notable risks:
- The global `g_deprecations` list is not protected by a lock.
- Hit, deferred, and last-log updates are racy by design, so statistics are advisory rather than exact.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/log/log_deprecated.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/log/log_flags.c -->
# File Research: sources/virtualization/spdk/lib/log/log_flags.c

Implements SPDK's dynamic debug-log flag registry and command-line usage formatting.

Key entry points:
- `spdk_log_register_flag()` registers a named `spdk_log_flag` in case-insensitive sorted order.
- `spdk_log_get_flag()` returns whether a named flag is enabled.
- `spdk_log_set_flag()` and `spdk_log_clear_flag()` enable or disable flags by exact/wildcard pattern, with special support for `"all"`.
- `spdk_log_get_first_flag()` and `spdk_log_get_next_flag()` iterate registered flags.
- `spdk_log_usage()` prints the `--logflag` help text with line wrapping.

Core mechanics:
- Flag lookup is case-insensitive through `strcasecmp()`.
- Pattern setting/clearing uses `fnmatch(..., FNM_CASEFOLD)` so callers can enable groups of flags by wildcard.
- Duplicate registration or missing registration parameters logs an error and asserts.
- Usage output wraps around a 100-character line limit using a fixed continuation prefix.

Important invariants:
- Registered flags must remain valid for the lifetime of the registry; this file stores caller-owned `struct spdk_log_flag` pointers.
- The list is kept sorted by flag name to produce stable usage output.
- `"all"` is handled before wildcard matching and applies to every registered flag.

Filesystem/block relevance:
- Component-specific debug flags are heavily used by SPDK storage modules. This registry controls targeted debug output without globally raising log verbosity.

Notable risks:
- The global flag list is not locked, so registration and flag updates are expected during controlled initialization or from serialized control paths.
- `spdk_log_usage()` assumes the flag list is stable while it formats help output.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/log/log_flags.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/lvol/Makefile -->
# File Research: sources/virtualization/spdk/lib/lvol/Makefile

Builds SPDK's logical volume library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares ABI version `SO_VER := 13` and `SO_MINOR := 0`.
- Builds `lvol.c` into `LIBNAME = lvol`.
- Uses `spdk_lvol.map` as the export map.
- Includes the standard `mk/spdk.lib.mk` library rules.

Filesystem/block relevance:
- This Makefile produces the logical-volume layer that maps blobstore-backed allocation and snapshot features into SPDK lvol APIs used by virtual block devices.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/lvol/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/lvol/lvol.c -->
# File Research: sources/virtualization/spdk/lib/lvol/lvol.c

Implements SPDK logical volume stores and logical volumes on top of blobstore, including lvolstore create/load/unload/destroy/grow/rename, lvol create/open/close/destroy/resize/rename, snapshots, clones, external snapshots, degraded external-snapshot tracking, shallow copy, and parent management.

Key entry points:
- `spdk_lvs_opts_init()`, `spdk_lvs_init()`, `spdk_lvs_load()`, and `spdk_lvs_load_ext()` initialize or load lvolstores.
- `spdk_lvs_rename()`, `spdk_lvs_unload()`, `spdk_lvs_destroy()`, `spdk_lvs_grow()`, and `spdk_lvs_grow_live()` manage lvolstore lifecycle and capacity changes.
- `spdk_lvol_create()`, `spdk_lvol_create_esnap_clone()`, `spdk_lvol_open()`, `spdk_lvol_close()`, `spdk_lvol_destroy()`, `spdk_lvol_resize()`, `spdk_lvol_rename()`, and `spdk_lvol_set_read_only()` manage individual lvol lifecycle and metadata.
- `spdk_lvol_create_snapshot()` and `spdk_lvol_create_clone()` expose blobstore snapshot/clone operations as lvol operations.
- `spdk_lvol_inflate()` and `spdk_lvol_decouple_parent()` materialize shared data or sever clone parentage.
- `spdk_lvs_esnap_missing_add()`, `spdk_lvs_esnap_missing_remove()`, and `spdk_lvs_notify_hotplug()` track and retry missing external snapshots.
- `spdk_lvol_iter_immediate_clones()`, `spdk_lvol_get_by_uuid()`, `spdk_lvol_get_by_names()`, and `spdk_lvol_is_degraded()` provide lookup/introspection helpers.
- `spdk_lvol_shallow_copy()`, `spdk_lvol_set_parent()`, and `spdk_lvol_set_external_parent()` handle data export and parent reassignment.

Core mechanics:
- A process-global `g_lvol_stores` list tracks loaded lvolstores by name under `g_lvol_stores_mutex`; each store also records the SPDK thread that created/loaded it.
- Each lvolstore has a blobstore plus a super blob whose xattrs store the lvolstore UUID and name. Loading opens the super blob, validates those xattrs, inserts the store globally, then iterates blobs to rebuild the lvol list.
- Individual lvol blobs store `name` and `uuid` xattrs. If an older/corrupt blob lacks a valid UUID, `unique_id` falls back to `<lvs_uuid>_<blob_id>`.
- New lvols are first placed on `pending_lvols` to reserve names while asynchronous blob creation is in progress, then moved to `lvols` once the blob opens successfully.
- Blobstore options are wrapped by lvolstore options, including cluster size, clear method, metadata page sizing, and optional external-snapshot bs_dev creation callbacks.
- The options-copy helper uses `opts_size` and a static size assertion to preserve ABI compatibility as fields are added.
- Snapshot and clone creation allocate a new lvol object, attach xattr callbacks for name/UUID, and delegate to blobstore snapshot/clone APIs.
- Destroy checks open references and clone relationships. If a degraded external-snapshot clone is deleted, degraded-set membership may transfer to its remaining clone.
- Open/close reference counting avoids reopening an already open blob and closes the blob only when the last reference is dropped.

External snapshot and degraded-mode mechanics:
- `lvs_esnap_bs_dev_create()` bridges blobstore external-snapshot callbacks to the lvolstore's registered `esnap_bs_dev_create` callback.
- During initial lvolstore load, `load_esnaps` is false so external snapshot devices are not opened while enumerating blobs; it is set true once loading completes.
- Missing external snapshots are stored in a red-black tree keyed by external snapshot ID bytes. Each tree node owns a tailq of lvols degraded by that same missing snapshot.
- `spdk_lvs_notify_hotplug()` searches lvolstores on the current thread for a matching degraded set and tries to attach the newly available external snapshot device to each lvol blob.
- Hotplug retry temporarily removes an lvol from the degraded tailq before invoking the callback, preventing tailq corruption if the callback re-adds the lvol on failure.

Important invariants:
- Lvolstore names must be unique globally, including pending `new_name` values during rename.
- Lvol names must be non-empty, null-terminated within `SPDK_LVOL_NAME_MAX`, and unique across both active and pending lvols in the store.
- Lvolstore unload and destroy reject stores with pending lvol actions or open lvol references.
- Most external-snapshot degraded-set operations assert they run on the lvolstore's owning SPDK thread.
- Removed degraded-set nodes are freed only after their lvol tailq becomes empty.
- `spdk_lvol_set_external_parent()` rejects an external snapshot ID that is identical to the lvol's own UUID string.

Filesystem/block relevance:
- This is SPDK's logical volume manager. It provides thin provisioning, snapshots, clones, parent/child relationships, and degraded external snapshot recovery for blobstore-backed virtual block devices.

Notable risks:
- The file is callback-heavy; failures in late async stages often rely on carefully paired cleanup callbacks to avoid leaked lvol objects, blobstore handles, or global list entries.
- Some global lookups return lvol pointers after releasing `g_lvol_stores_mutex`, so callers rely on higher-level SPDK threading/lifetime rules for safety.
- `spdk_lvs_destroy()` frees lvol structs without removing each from the list first because the whole store is being destroyed; this is correct only if no later code walks that list before `lvs_free()`.
- Degraded external-snapshot handling is explicitly thread-affine. Notifications from the wrong thread are discarded with a notice, which can leave lvols degraded until a correct-thread notification occurs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/lvol/lvol.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/mlx5/Makefile -->
# File Research: sources/virtualization/spdk/lib/mlx5/Makefile

Builds SPDK's mlx5 support library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares ABI version `SO_VER := 5` and `SO_MINOR := 0`.
- Builds `mlx5_crypto.c`, `mlx5_qp.c`, `mlx5_dma.c`, and `mlx5_umr.c` into `LIBNAME = mlx5`.
- Links system libraries `-lmlx5` and `-libverbs`.
- Uses `spdk_mlx5.map` as the export map and includes `mk/spdk.lib.mk`.

Filesystem/block relevance:
- The mlx5 library provides low-level RDMA, DMA, memory-key, and crypto offload support that SPDK storage transports and bdev modules can use for high-performance data movement.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/mlx5/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/mlx5/mlx5_crypto.c -->
# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_crypto.c

Implements mlx5 hardware crypto device discovery and AES-XTS data encryption key object management for SPDK's mlx5 integration.

Key entry points:
- `spdk_mlx5_crypto_devs_allow()` configures an optional allowlist of mlx5 device names eligible for crypto use.
- `spdk_mlx5_crypto_devs_get()` returns RDMA contexts for Mellanox/mlx5 devices that support the required crypto capabilities.
- `spdk_mlx5_crypto_devs_release()` frees the returned device context array.
- `spdk_mlx5_device_query_caps()` queries general and crypto HCA capabilities through DEVX.
- `spdk_mlx5_crypto_keytag_create()` creates hardware DEK objects for all eligible devices from a plaintext AES-XTS key.
- `spdk_mlx5_crypto_keytag_destroy()` destroys DEK objects, releases protection domains, and scrubs stored keytag bytes.
- `spdk_mlx5_crypto_get_dek_data()` finds the DEK associated with a protection domain and returns its object ID and tweak mode.

Core mechanics:
- Device discovery starts from `spdk_rdma_cm_get_devices()`, filters by Mellanox vendor ID, optional allowlist, RoCE availability for Ethernet ports, and mlx5 crypto capability bits.
- Unsupported devices are rejected when AES-XTS tweak modes are unavailable or wrapped AES-XTS import is required, because this library only handles plaintext key import.
- Device capabilities are read using `MLX5_CMD_OP_QUERY_HCA_CAP` for general HCA caps and then crypto caps.
- Supported key lengths are AES-XTS 128 and 256 pairs, with or without an 8-byte keytag appended.
- `mlx5_crypto_dek_init()` creates a DEVX `MLX5_OBJ_TYPE_DEK` object bound to a protection domain and securely zeroes the copied key material in the command buffer after object creation.
- Each keytag object owns an array of per-device DEKs so later queue/mkey setup can select the DEK matching its protection domain.
- DEK creation is followed by a query that verifies state is `MLX5_ENCRYPTION_KEY_OBJ_STATE_READY` and opaque metadata remains zero.
- Tweak mode is selected per device, preferring big-endian multi-block tweak support when available, otherwise little-endian.

Important invariants:
- `spdk_mlx5_crypto_keytag_create()` either creates DEKs for every eligible device or destroys all partial state before returning an error.
- `keytag->deks_num` is incremented before each per-device attempt so the destroy path can clean partial allocations.
- A returned DEK data lookup is keyed by exact `ibv_pd *`.
- Keytag bytes are stored only when the input key length includes the 8-byte keytag suffix and are scrubbed on destroy.

Filesystem/block relevance:
- This file enables hardware crypto offload for SPDK data paths on mlx5 devices. It is especially relevant to encrypted block devices and storage transports that need per-device crypto key object IDs.

Notable risks:
- The device allowlist is global mutable state without locking.
- Plaintext key import is intentionally unsupported on devices requiring wrapped import, limiting hardware compatibility.
- The error log string for the 256-bit-with-keytag case contains a typo (`"lye"`), harmless but visible in diagnostics.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/mlx5/mlx5_crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/mlx5/mlx5_dma.c -->
# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_dma.c

Implements low-level mlx5 queue-pair RDMA read/write WQE construction, send completion doorbell handling, CQ polling, CQE error decoding, and debug WQE dumping.

Key entry points:
- `spdk_mlx5_qp_rdma_write()` and `spdk_mlx5_qp_rdma_read()` post RDMA write/read work requests through a shared `mlx5_qp_rdma_op()` helper.
- `spdk_mlx5_cq_poll_completions()` polls send completions and returns work request IDs plus completion status.
- `spdk_mlx5_qp_complete_send()` rings the send doorbell and handles last-signaled mode completion accounting.
- `mlx5_qp_dump_wqe()` dumps raw WQE building blocks under `DEBUG` when the `mlx5_sq` log flag is enabled.

Core mechanics:
- WQEs are built directly in the mlx5 send queue as control segment, remote address segment, and one data segment per SGE.
- `mlx5_qp_rdma_op()` computes the number of 64-byte WQE building blocks needed: one block covers control, remote address, and up to two SGEs; additional SGEs consume more blocks.
- The code checks both available SQ building blocks and `qp->max_send_sge` before writing the WQE.
- `mlx5_dma_xfer_full()` handles WQEs that fit contiguously before the end of the circular SQ.
- `mlx5_dma_xfer_wrap_around()` writes segment-by-segment and wraps data segments to the beginning of the SQ when needed.
- After WQE construction, `mlx5_qp_wqe_submit()` advances producer state and `mlx5_qp_set_comp()` records completion metadata indexed by producer index.
- `mlx5_qp_tx_complete()` updates completion aggregation for `SPDK_MLX5_QP_SIG_LAST` and rings the queue doorbell.
- CQ polling checks ownership and opcode validity, finds the originating QP by QPN, converts CQEs to SPDK completion records, and restores `tx_available` from recorded completion counts.

Error handling:
- `_mlx5_err_cqe` and `mlx5_sigerr_cqe` model mlx5 error CQE layouts.
- `mlx5_cqe_err_opcode()` decodes the failed WQE opcode into readable operation names.
- `mlx5_cqe_err()` maps mlx5 CQE syndromes to diagnostic text, treats flushed work requests as debug-level, and logs other CQE failures as warnings with QP number, WQE index, syndrome, vendor syndrome, hardware syndrome, and opcode.

Important invariants:
- Send queue size is treated as a power-of-two ring and producer indices are masked with `sq_wqe_cnt - 1`.
- `qp->tx_available` must be at least the WQE building block count before posting and is decremented after posting.
- Completion records are indexed by WQE counter masked to the SQ size.
- Unsignaled work requests are accumulated into the next signaled completion.
- CQ consumer index is advanced only after owner/opcode checks pass.

Filesystem/block relevance:
- This file is data-plane infrastructure for SPDK's RDMA/mlx5 paths. It does not implement filesystem logic, but it directly affects block-storage transport throughput and correctness for RDMA reads/writes.

Notable risks:
- Direct WQE construction is layout-sensitive and depends on mlx5 hardware ABI structures and endian conversions being correct.
- Wrap-around WQE construction must update `to_end` exactly or it can corrupt the SQ ring.
- `spdk_mlx5_cq_poll_completions()` returns `-ENODEV` if a CQE's QPN cannot be mapped to a known QP, which can abort polling even if later CQEs are valid.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/mlx5/mlx5_dma.c -->