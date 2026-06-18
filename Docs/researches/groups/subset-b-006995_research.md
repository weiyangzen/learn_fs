<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_pubsub.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_pubsub.h

## Purpose

Defines RGW pubsub and S3 notification data models plus the `RGWPubSub` facade used to manage account topics, bucket notification bindings, and persistent notification event records. The header is the serialization contract for topic destinations, topic metadata, bucket-topic filters, S3-compatible notification XML, and queued event entries.

## Important APIs, Types, and Functions

`rgw_pubsub_s3_notification` models one S3 `TopicConfiguration`, with id, event list, topic ARN, and key/metadata/tag filters. The overloaded `match()` declarations cover key filters, metadata filters, tag filters, and event-type matching. `rgw_pubsub_s3_event` is the JSON/encoded event record with AWS-style fields plus RGW extensions for event id, bucket id, metadata, tags, and opaque data.

`rgw_pubsub_dest` describes delivery endpoint state: endpoint URL and args, ARN, secret-storage flag, persistence flag, queue object name, TTL/retry configuration, and shard count. `rgw_pubsub_topic`, `rgw_pubsub_topic_filter`, `rgw_pubsub_bucket_topics`, and `rgw_pubsub_topics` are the persisted topic and binding structures. `RGWPubSub` exposes topic create/read/list/delete and nested `RGWPubSub::Bucket` exposes bucket notification create/remove/list helpers. Free helpers include `topic_to_unique()`, `find_unique_topic()`, `remove_notification_v2()`, `get_bucket_notifications()`, and topic metadata key formatting/parsing.

## Control Flow and Data Flow

The data path starts with XML notification config decoding into `rgw_pubsub_s3_notification` objects. These become topic filters that are persisted as bucket-topic maps, keyed by topic name or a unique topic/notification composition. Event generation fills `rgw_pubsub_s3_event`, applies filter matching against event type, object key, metadata, and tags, then delivery code can encode queued `rgw::notify::event_entry_t` records for persistent delivery.

`RGWPubSub` chooses v1 or v2 topic management based on site configuration. V1 methods read/write aggregate topic maps, while v2 methods manipulate individual topic metadata and account topic listings. Bucket notification operations read a bucket's topic map with an object version tracker, update or remove entries, and write it back atomically.

## State and Persistence Behavior

All main structs use Ceph `ENCODE_START` versioning. Backward compatibility is explicit: `rgw_pubsub_dest` carries dummy legacy fields, pre-v7 persistent topics derive queue names from `arn_topic`, pre-v8 destinations default to one shard, `rgw_pubsub_topic` decodes legacy owner variants, `rgw_pubsub_topic_filter` stores events as strings, and `rgw_pubsub_topics` converts old `topic_subs` maps. Persistent event entries store delivery timing and retry configuration alongside the event.

Durable state lives in RGW metadata and bucket attributes through SAL driver calls implemented elsewhere. The header's key risk is that these encoded forms are on-disk and cross-version wire contracts, so field ordering and version gates are compatibility-sensitive.

## Dependencies and Integration Points

Depends on SAL forward declarations, zone/site configuration, `rgw_notify_event_type.h`, `rgw_s3_filter.h`, Ceph formatter/encoding utilities, `versioned_variant`, and C++ ranges for shard-name views. Integrates with S3 REST notification APIs, notification delivery queues, bucket metadata, topic metadata, and multisite/account topic listing.

## Risks and Edge Cases

Filter semantics must match S3 expectations for prefix/suffix/regex, metadata, and tags. `DEFAULT_GLOBAL_VALUE` uses `UINT32_MAX` as a sentinel, so dumping and application code must not confuse it with a real high value. Sharded persistent queues depend on stable naming. Notification id/topic uniqueness is split between `topic_to_unique()` and `find_unique_topic()`, which makes migration from older unqualified topic names a compatibility risk.

## Test Signals

Cover XML decode/dump round trips, event matching for key/metadata/tag/event filters, v1-to-v2 topic decode compatibility, persistent destination decode from versions before queue names and shards, topic metadata key parsing with tenants, removal by notification id versus topic name, bucket notification atomic update races, and event-entry encode/decode across all struct versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_pubsub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_putobj.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_putobj.cc

## Purpose

Implements data-processor pipeline components for object PUT paths. The processors reshape incoming byte streams into fixed-size chunks or stripe-relative writes before forwarding them to the next SAL `DataProcessor`.

## Important APIs, Types, and Functions

`ChunkProcessor::process()` buffers partial input until `chunk_size` bytes are available, forwards full chunks, and flushes leftover bytes on an empty-buffer call. `StripeProcessor::process()` forwards data within current stripe bounds, flushes the downstream processor at stripe boundaries, asks a `StripeGenerator` for the next stripe size, and rewrites offsets to be relative to each stripe.

## Control Flow and Data Flow

Chunk processing asserts that the caller's absolute offset has not moved behind buffered data, computes the first downstream position as `offset - chunk.length()`, appends input to the leftover buffer, then repeatedly splices and forwards full chunks. A zero-length input is a flush signal: any leftover chunk is forwarded at its computed position, then an empty flush is passed downstream at the caller's offset.

Stripe processing asserts the offset is inside or after the current stripe start. If input exceeds the current stripe's remaining bytes, it forwards the partial slice, sends an empty flush at the stripe-relative end, asks the generator for a new stripe, updates bounds, and continues. Remaining data that fits in the current stripe is forwarded without flushing.

## State and Persistence Behavior

The file owns only transient in-memory pipeline state: `ChunkProcessor::chunk` leftovers and `StripeProcessor::bounds`. It does not persist metadata or object data itself; persistence happens in the downstream processor.

## Dependencies and Integration Points

Depends on `bufferlist`, `rgw_putobj.h`, and SAL `DataProcessor`. It integrates with RGW PUT/copy/multipart upload code that builds processor chains for object layout, compression, encryption, or RADOS writes.

## Risks and Edge Cases

Zero-length buffers are control messages, so callers must not use them as ordinary data. `chunk_size` and generated stripe sizes must be nonzero; stripe code asserts the generated size but chunk code would loop forever if constructed with zero. Offset correctness is critical because downstream processors receive chunk- or stripe-relative positions.

## Test Signals

Test exact chunk boundaries, partial chunks followed by flush, multiple chunks in one call, stripe crossing with multiple generated stripes, empty flush propagation, downstream error propagation, and assertions/guard behavior for zero sizes or non-monotonic offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_putobj.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_putobj.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_putobj.h

## Purpose

Declares composable object PUT data processors used to transform upload streams before final storage. It provides a minimal pipe abstraction, a fixed-chunk processor, and a stripe-boundary processor.

## Important APIs, Types, and Functions

`Pipe` derives from `rgw::sal::DataProcessor` and forwards `process(bufferlist&&, uint64_t)` to a next processor. `ChunkProcessor` adds a fixed `chunk_size` and leftover `bufferlist`. `StripeGenerator` is the callback interface that returns the next stripe size for a given absolute offset. `StripeProcessor` holds a generator and current `[first, second)` stripe bounds.

## Control Flow and Data Flow

The header establishes that processors are chained by raw `DataProcessor*` pointers and that `process()` owns the moved bufferlist. `ChunkProcessor` normalizes variable input into chunks. `StripeProcessor` normalizes absolute upload offsets into stripe-local offsets and resets downstream state between stripes using empty-buffer flush calls.

## State and Persistence Behavior

No durable state is declared. Runtime state is limited to retained chunk bytes and current stripe bounds. The raw pointer ownership model implies the chain owner is responsible for processor lifetimes.

## Dependencies and Integration Points

Depends on `include/buffer.h` and `rgw_sal.h`. The API plugs into SAL object write paths and layout-specific processors.

## Risks and Edge Cases

The classes do not validate `chunk_size`, `first_stripe_size`, `next`, or `gen`; invalid construction can cause null dereferences, asserts, or infinite loops. Because empty buffers mean flush, callers must preserve that convention throughout the chain. Raw pointers make lifetime tests important.

## Test Signals

Compile-time coverage should ensure derived processors override SAL correctly. Unit tests should use fake downstream processors/generators to verify forwarded offsets, flush counts, ownership of moved bufferlists, and behavior at boundary sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_putobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_quota.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_quota.cc

## Purpose

Implements RGW bucket, user, and account quota enforcement using cached storage stats, asynchronous refresh, background owner-stat synchronization, and configurable quota limit application. It is the runtime enforcement layer behind `RGWQuotaHandler`.

## Important APIs, Types, and Functions

`RGWQuotaCache<T>` is the template base for TTL-cached stats with async refresh hooks. `RGWBucketStatsCache` fetches bucket stats by loading the bucket and reading current index shard stats. `RGWOwnerStatsCache` fetches owner stats via SAL, starts optional sync threads, tracks modified buckets, and synchronizes owner stats from bucket stats and metadata listings. `RGWQuotaInfoApplier`, `RGWQuotaInfoDefApplier`, and `RGWQuotaInfoRawApplier` decide whether limits compare against rounded or raw size. `RGWQuotaHandlerImpl` implements `check_quota()` and `update_stats()`. The file also implements default quota application and JSON/dump helpers for `RGWQuotaInfo`.

## Control Flow and Data Flow

Quota checks first return early when both user and bucket quota are disabled. Bucket quota checks fetch bucket stats through `bucket_stats_cache.get_stats()`, which serves fresh cached entries, starts async refresh after half TTL, or synchronously fetches from storage on miss/expiry. User/account quota checks use `owner_stats_cache.get_stats()` similarly. The applier then compares `stats.num_objects + requested_objects` and either raw or rounded size against configured max values and returns `-ERR_QUOTA_EXCEEDED` on violations.

Write paths call `update_stats()` after object changes. Both bucket and owner caches adjust cached stats in place and `RGWOwnerStatsCache::data_modified()` records the bucket for the bucket-sync thread. Background sync threads periodically process modified buckets and all owners/accounts, loading metadata keys and calling `sync_owner()` when owners are not idle or need a full sync.

## State and Persistence Behavior

The caches are in-memory LRU maps with expiration and async refresh timestamps. They do not make quota decisions from strong, freshly persisted state on every request unless cache entries are absent or expired. Persistent state is read and updated through SAL bucket stats, owner stats, metadata listing, `bucket->sync_owner_stats()`, `bucket->check_bucket_shards()`, and `rgw_sync_all_stats()`. The destructor waits for async refresh references and stops sync threads.

## Dependencies and Integration Points

Depends on SAL driver/bucket APIs, `lru_map`, Ceph clocks, threads, mutexes, `RefCountedWaitObject`, bucket layout helpers, RADOS-specific user helpers when available, and config values including quota cache size, TTL, sync intervals, default limits, and raw-size mode. Integrates with object mutation paths via `RGWQuotaHandler::update_stats()` and with account/user metadata via `meta_list_keys_*`.

## Risks and Edge Cases

Quota enforcement is eventually consistent because cached stats can be stale and async refresh failures are logged but not fatal. `fetch_stats_from_storage()` treats `-ENOENT` as zero stats after `get_stats()`, which may be correct for missing buckets/owners but should be tested. Owner sync thread stop takes locks while joining bucket sync. Default applier uses rounded object size while raw applier uses raw bytes; mismatched configuration can surprise operators. Full owner sync relies on metadata key parsing into `rgw_owner` and tenant lookup for account ids.

## Test Signals

Cover bucket and user quota enabled/disabled combinations, raw versus rounded size checks, max object boundaries, cache fresh/expired/async-refresh paths, async success/failure callbacks, indexless buckets, negative deltas clamped to zero, owner sync idle-user skipping, account tenant lookup, metadata listing errors, default quota config application, JSON backward compatibility for `max_size_kb`, and thread start/stop with pending async operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_quota.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_quota.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_quota.h

## Purpose

Declares the public quota handler interface used by RGW write paths to check quota and adjust cached stats, plus helpers that apply configured default quotas.

## Important APIs, Types, and Functions

`RGWQuotaHandler::check_quota()` validates a prospective object/count delta for a bucket owner, bucket, and `RGWQuota`. `update_stats()` applies object and byte deltas after data changes. `generate_handler()` and `free_handler()` allocate the concrete implementation. `rgw_apply_default_bucket_quota()`, `rgw_apply_default_user_quota()`, and `rgw_apply_default_account_quota()` populate `RGWQuotaInfo` from config defaults.

## Control Flow and Data Flow

Callers construct a handler for a SAL driver, call `check_quota()` before accepting writes, and call `update_stats()` after mutations so the in-memory quota caches track recent changes. Default quota helpers are used when creating or loading quota policy state that should inherit cluster configuration.

## State and Persistence Behavior

The interface itself owns no state, but the implementation created by `generate_handler()` owns caches and optional sync threads. Default helper changes apply to the passed `RGWQuotaInfo` object only; persistence depends on callers saving that info.

## Dependencies and Integration Points

Depends on quota types, user types, `optional_yield`, config forwarding, and SAL driver forward declarations. It is used by object operations, account/user admin paths, and storage driver initialization.

## Risks and Edge Cases

The API expects negative errno returns but exposes raw pointers and manual `free_handler()`. Callers must pair check/update correctly; missing updates make cached quota less accurate, while updates before failed writes overcount. Default helpers enable quotas only when configured max values are non-negative.

## Test Signals

Test handler allocation/destruction with quota threads enabled and disabled, pre-write quota rejection, post-write stats deltas, default helper behavior for only size, only object count, both, and neither configured, and error propagation from the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_quota_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_quota_types.h

## Purpose

Defines the serialized quota data structures shared outside RGW implementation-heavy contexts. The header is intentionally dependency-light because these types are persisted and compiled in multiple Ceph components.

## Important APIs, Types, and Functions

`rgw_rounded_kb()` converts byte values to rounded-up KiB. `RGWQuotaInfo` carries `max_size`, `max_objects`, `enabled`, and `check_on_raw`. It implements versioned encode/decode, formatter dump, JSON decode, and test instance generation. `RGWQuota` groups user and bucket quota info.

## Control Flow and Data Flow

Quota config enters `RGWQuotaInfo` through JSON decode, binary decode, or default application elsewhere. Runtime enforcement reads `enabled`, negative max values as unlimited dimensions, and `check_on_raw` to choose raw-byte versus rounded-size comparison. Encoded form stores both legacy KiB size and byte-accurate `max_size` for compatibility.

## State and Persistence Behavior

`RGWQuotaInfo` is a durable encoding contract. Version 1 stores max size in KiB; version 2 adds byte-accurate `max_size`; version 3 adds `check_on_raw`. Decode preserves old data by multiplying KiB by 1024 and defaults `check_on_raw` to false for old records.

## Dependencies and Integration Points

Uses Ceph `bufferlist` encoding macros and formatter/JSON declarations without including RGW SAL or common implementation-heavy headers. Integrated with user, account, bucket metadata and quota admin APIs.

## Risks and Edge Cases

Negative `max_size` values are specially encoded by rounding the absolute value and negating, so compatibility depends on preserving sign behavior. `abs(max_size)` on the most negative `int64_t` is a theoretical overflow edge. JSON fallback from `max_size_kb` can lose byte precision. `check_on_raw` changes quota semantics for existing deployments.

## Test Signals

Round-trip encode/decode for versions 1, 2, and 3, negative unlimited values, non-KiB byte values, JSON with `max_size` and legacy `max_size_kb`, `check_on_raw` defaulting, and `RGWQuota` embedding in higher-level metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_quota_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_range_projection.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_range_projection.h

## Purpose

Provides stateless helpers that project requested plaintext object byte ranges onto compressed or encrypted on-disk byte ranges. It lets GET paths fetch the minimum required stored bytes while preserving enough skip/block metadata for decompression or decryption filters.

## Important APIs, Types, and Functions

`DiskRange` stores disk offset/end, first-block plaintext skip, original request length, and encryption block start skip. `DecompressRange` extends it with compression block indices and plaintext query offset/length. `project_compress_range()` maps plaintext ranges to compression blocks. `find_part_for_offset()` locates which encrypted multipart part contains a plaintext offset. `project_encrypt_range()` maps plaintext ranges to encrypted byte ranges for single-part and multipart objects.

## Control Flow and Data Flow

Compression projection uses binary search over `RGWCompressionInfo::blocks` for partial content and full first/last block selection for whole-object reads. It returns the compressed disk span from first block `new_ofs` through last block end, and records how many decompressed bytes to skip.

Encryption projection aligns plaintext start and end to encryption block boundaries, converts them with `crypt_logical_to_enc_offset()` and `crypt_align_enc_block_end()`, and clamps to encrypted object or part sizes. Multipart projection first finds start and end parts by converting encrypted part lengths back to plaintext sizes, then computes cumulative encrypted offsets.

## State and Persistence Behavior

No state is stored. The functions rely on persisted compression block maps, encrypted object total size, and multipart encrypted part lengths passed by the caller.

## Dependencies and Integration Points

Depends on `rgw_compression_types.h` for compression block metadata and `rgw_crypt.h` for encryption offset conversion helpers. Integrated into RGW GET range handling for compressed and encrypted objects.

## Risks and Edge Cases

`project_compress_range()` assumes `cs_info.blocks` is non-empty and sorted by plaintext offset. `r.length = end + 1 - ofs` assumes valid inclusive ranges. Multipart encryption projection assumes `parts_len` is non-empty when using multipart and that `end_part_idx` remains valid; clamping behavior around last part is subtle. `block_size` should be a power of two because bit masks are used for alignment.

## Test Signals

Cover full-object and partial compressed ranges, single-block and multi-block compressed reads, empty block vectors as invalid input, encrypted single-part first/middle/last block ranges, encrypted object-size clamping, multipart ranges within one part and crossing parts, range ending at a part boundary, and invalid or zero block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_range_projection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ratelimit.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_ratelimit.h

## Purpose

Implements an in-memory token-bucket style rate limiter for RGW users and buckets, with separate operation and bandwidth counters for read, write, list, and delete traffic. It also manages active/passive limiter maps to bound memory growth.

## Important APIs, Types, and Functions

`OpType` distinguishes `Read`, `Write`, `List`, and `Delete`. `RateLimiterEntry` holds fixed-point token counters and exposes `should_rate_limit()`, `decrease_bytes()`, `giveback_tokens()`, and `compute_delay()`. `RateLimiter` maps string keys to entries, classifies operations from HTTP method/resource, and exposes per-key rate-limit methods. `ActiveRateLimiter` owns two `RateLimiter` instances, a background replacement thread, and `get_active()`/`start()`.

## Control Flow and Data Flow

Each request calls `RateLimiter::should_rate_limit()` with method, key, timestamp, config info, and resource. The limiter skips empty/one-character keys and disabled configs, classifies list operations by query patterns, finds or creates an entry, replenishes tokens based on elapsed time, and returns either zero or a retry delay. Body input/output calls later call `decrease_bytes()` to charge bandwidth debt; failed requests can call `giveback_tokens()` to restore operation tokens.

When the map exceeds 90 percent of the fixed `map_size`, `find_or_create()` flips `replacing` and wakes `ActiveRateLimiter::replace_active()`. The replacement thread switches active maps, waits until the old shared pointer is no longer used by requests, clears it, and resets replacement state.

## State and Persistence Behavior

All state is transient process memory. Token counters are fixed-point scaled by 1000 to preserve fractional refill. No rate-limit state survives RGW restart, and active/passive map replacement intentionally drops old entries.

## Dependencies and Integration Points

Depends on `rgw_common.h`, `RGWRateLimitInfo`, global Ceph config for interval, Ceph time types, logging, `shared_mutex`, condition variables, and threads. It integrates with REST body send/receive paths and request pre-checks that populate user and bucket rate-limit info.

## Risks and Edge Cases

`ActiveRateLimiter` destructor unconditionally joins `runner`; destruction before `start()` would be unsafe. `RateLimiter::clear()` is not protected by `insert_lock` in this header, relying on active/passive pointer isolation. List detection is heuristic based on query substrings. Byte counters are charged after body transfer, so op admission can pass before bandwidth debt is known. Zero limits return no delay in `compute_delay()`, so disabled dimensions must be represented consistently.

## Test Signals

Test fractional refill for low rates, delay computation boundaries, read/write/list/delete classification, bandwidth debt capped at two minutes, token giveback, disabled and empty-key bypass, concurrent insert/find, map replacement while requests hold old shared pointers, and destructor behavior when `start()` was or was not called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ratelimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_realm.cc

## Purpose

Implements core `RGWRealm` helpers for realm pool selection, control object naming, zone lookup in the current period, and formatter/JSON support.

## Important APIs, Types, and Functions

Defines defaults under `rgw_zone_defaults`: realm info/name object prefixes, default realm info object, and default root pool. Implements `RGWRealm::get_pool()`, `get_info_oid_prefix()`, `get_control_oid()`, `find_zone()`, `generate_test_instances()`, `dump()`, and `decode_json()`.

## Control Flow and Data Flow

`get_pool()` returns configured `rgw_realm_root_pool` or `rgw.root`. `get_control_oid()` appends the realm id to the realm info prefix and `.control`. `find_zone()` reads the current period from the config store, asks the period to find the requested zone, and returns the period and zonegroup only when found.

## State and Persistence Behavior

The file does not mutate realm state. It reads period metadata through `rgw::sal::ConfigStore::read_period()` using `current_period`. Realm fields `id`, `name`, `current_period`, and `epoch` are serialized through JSON formatter/decode helpers elsewhere in the type.

## Dependencies and Integration Points

Depends on zone/period types, realm watcher declarations, config store, system object service, Ceph JSON and formatter helpers, and logging. Integrated with multisite period/zone discovery and realm notification object naming.

## Risks and Edge Cases

`get_info_oid_prefix(bool old_format)` ignores `old_format`, so callers expecting legacy naming behavior should be checked. `find_zone()` requires `pfound`, `pperiod`, and `cfgstore` to be valid pointers. If period read fails, zone lookup is skipped and the error propagates.

## Test Signals

Cover default versus configured root pool, control object naming, period read failure, zone found/not found, JSON decode/dump fields, and compatibility expectations for old-format prefix callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.cc

## Purpose

Implements dynamic RGW realm reconfiguration. `RGWRealmReloader` reacts to realm notifications by pausing frontends, shutting down the current storage driver, reloading site configuration, creating a new driver, reinitializing dependent subsystems, and resuming frontends.

## Important APIs, Types, and Functions

`RGWRealmReloader` constructor initializes a `SafeTimer`; destructor shuts it down. `C_Reload` is a timer context that calls `reload()`. `handle_notify()` schedules one reload and wakes any retry loop. `reload()` performs the full driver replacement and subsystem reinitialization.

## Control Flow and Data Flow

Notifications are ignored while `env.driver` is null, which means reload is already in progress. Otherwise `handle_notify()` locks, avoids duplicate scheduled reloads, creates a `C_Reload`, wakes waiters, and schedules it immediately. `reload()` pauses frontends, finalizes usage logging, shuts down and closes the old driver, clears `env.driver`, then releases the scheduled marker early so later notifications are not missed.

The reload loop repeatedly loads `env.site` from the config store and attempts `DriverManager::get_storage()`. If creation fails, it waits on a condition variable until a new notification arrives. If a new notification arrives after a driver is created but before completion, it cancels that scheduled event, closes the just-created driver outside the lock, and loops again. Once stable, it registers the service map, reinitializes REST, usage logging, auth registry, Lua manager/background hooks, and resumes frontends with the new driver.

## State and Persistence Behavior

The class mutates process-local runtime state in `RGWProcessEnv`: driver pointer, site config, auth registry, Lua manager bindings, and service map registration. It does not directly write realm metadata, but it consumes persisted config-store periods/realms. It intentionally tolerates bad persisted realm config by waiting and retrying instead of aborting the process.

## Dependencies and Integration Points

Depends on `RGWProcessEnv`, auth registry, bucket/log/REST initialization, RADOS SAL driver manager, zone service, Lua manager, service map registration, `SafeTimer`, and frontend pause/resume abstraction. It is registered as an `RGWRealmWatcher::Watcher`.

## Risks and Edge Cases

`reload()` captures `cct` from the old driver before closing it and continues using it. Duplicate notifications are coalesced, but timing between clearing `reload_scheduled` and site load is subtle. Frontends must honor `pause()` or old driver use-after-close is possible. Constructor initializes `timer` with `env.driver->ctx()` before `mutex` member initialization order in the class definition, so member declaration order matters. Failure loops can leave frontends paused until a valid config arrives.

## Test Signals

Cover single notification reload, duplicate notification coalescing, notification during reload causing restart, driver creation failure followed by retry, service map registration failure ignored, Lua manager replacement for RADOS and non-RADOS drivers, frontend pause/resume ordering, destructor cancelling scheduled timer events, and behavior when notification arrives while `env.driver` is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.h

## Purpose

Declares `RGWRealmReloader`, a realm notification watcher that coordinates frontend pause/resume and storage driver replacement after multisite period changes.

## Important APIs, Types, and Functions

`RGWRealmReloader::Pauser` abstracts frontend `pause()` and `resume(rgw::sal::Driver*)`. The constructor receives `RGWProcessEnv`, implicit-tenant config, service-map metadata, pauser, and an Asio context. `handle_notify()` overrides the watcher interface. Private `reload()` performs replacement, and `C_Reload` is the timer callback type.

## Control Flow and Data Flow

The header documents the design: notifications should schedule a timer callback rather than doing slow reload work in the notify thread, and the timer can cancel/requeue reload events while a reload is already running. The pauser boundary prevents direct dependency on frontend classes.

## State and Persistence Behavior

Persistent state is not declared here. Runtime state includes references to process environment and auth/metadata inputs, the frontend pauser, io context, a `SafeTimer`, mutex/condition variable, and a raw pointer to the scheduled reload context.

## Dependencies and Integration Points

Depends on `RGWRealmWatcher`, `SafeTimer`, Ceph condition/mutex primitives, SAL forward declarations, and Boost.Asio. Integrated with RGW process setup and realm watch registration.

## Risks and Edge Cases

The class stores many references, so their lifetimes must outlive the reloader. `reload_scheduled` is a raw pointer managed by `SafeTimer`; cancellation/destruction paths need coverage. Frontend pause/resume correctness is outside the class but critical.

## Test Signals

Use fake pausers and fake environment/driver managers to exercise notify scheduling, timer cancellation, destruction with pending reload, reference lifetime expectations, and no direct frontend dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.cc

## Purpose

Implements the small base watcher registry for realm notifications. The concrete watch mechanism is elsewhere; this file stores observer registrations by notification type.

## Important APIs, Types, and Functions

`RGWRealmWatcher::~RGWRealmWatcher()` is an empty virtual destructor. `add_watcher(RGWRealmNotify type, Watcher& watcher)` inserts the watcher reference into the `watchers` map.

## Control Flow and Data Flow

Callers register an observer for a given `RGWRealmNotify` enum value. Later concrete watcher implementations can look up that type and invoke `Watcher::handle_notify()`.

## State and Persistence Behavior

Only in-memory references are stored. No watch handle or persisted realm state is managed in this file.

## Dependencies and Integration Points

Depends on `rgw_realm_watcher.h`. Integrated with realm reloader and other components interested in `Reload` or `ZonesNeedPeriod` notifications.

## Risks and Edge Cases

`std::map<RGWRealmNotify, Watcher&>::emplace()` ignores later registrations for the same type, so duplicate registration silently keeps the first watcher. Stored references must remain valid until watcher destruction. No locking is provided.

## Test Signals

Cover registering each enum type, duplicate registration semantics, callback dispatch in concrete subclasses, and lifetime ordering between registered watchers and the watcher container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.h

## Purpose

Declares the realm notification enum and observer interface used by RGW components that react to realm control-object notifications.

## Important APIs, Types, and Functions

`RGWRealmNotify` has `Reload` and `ZonesNeedPeriod`, with raw encoder support. `RGWRealmWatcher::Watcher` declares `handle_notify(RGWRealmNotify, bufferlist::const_iterator&)`. `RGWRealmWatcher` stores a map from notification type to watcher reference and exposes `add_watcher()`.

## Control Flow and Data Flow

Notification payloads are expected to be decoded from a `bufferlist::const_iterator` by the registered watcher. The base class only holds registrations; subclasses establish actual RADOS watches and dispatch.

## State and Persistence Behavior

No durable state is present. The enum's raw encoder is a wire/persistence concern for notification payload compatibility.

## Dependencies and Integration Points

Depends on Ceph buffer and encoding support. Integrated with realm reloader, period update flows, and realm control object watch implementations.

## Risks and Edge Cases

Raw enum encoding depends on enum value stability. The map stores references, not owned pointers. Only one watcher per notification type is naturally supported by the current map shape.

## Test Signals

Test enum encode/decode compatibility, registering reload and zone-period watchers, duplicate registration behavior, and payload iterator consumption by concrete watcher implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.cc

## Purpose

Implements an RGW D4N/L1 cache backend backed by Redis or Valkey using Boost.Redis. It stores cached object data and attributes as Redis hashes under a partition-location prefix and supports synchronous and AIO-style operations.

## Important APIs, Types, and Functions

`build_attrs()` converts SAL attrs to alternating field/value strings. `async_exec()` and `redis_exec()` adapt Boost.Redis async execution to Ceph optional-yield or blocked completion. `RedisDriver::initialize()` starts the Redis connection. Data methods include `put()`, `get()`, `append_data()`, `delete_data()`, `rename()`, `get_attrs()`, `set_attrs()`, `update_attrs()`, `delete_attrs()`, `get_attr()`, `set_attr()`, `get_async()`, `put_async()`, and `shutdown()`. `resolve_valkey_data_dir()` and `get_free_space()` inspect Redis `CONFIG GET dir` and filesystem free space.

## Control Flow and Data Flow

Writes build `entry = partition_info.location + key`, convert attrs, optionally add the `data` field, and issue `HSET`. Reads issue `HGETALL`, return `-ENOENT` on empty hashes, append the `data` field to the output bufferlist, and convert all other fields back to attrs. Appends read the existing `data` field and rewrite the concatenated value. Deletes wrap `HSTRLEN` and `DEL` in `MULTI/EXEC` and add the removed data length back to local `free_space`. AIO methods enqueue Redis HGET/HSET operations through RGW `Aio` using callbacks that place results back into the throttle.

## State and Persistence Behavior

Persistent cache state is stored in Redis hashes. `free_space` and `outstanding_write_size` are process-local counters; `free_space` is decremented/incremented by operations but initialized only to zero in the constructor in this file. Redis data dir is discovered dynamically by `CONFIG GET dir`, then host filesystem space is checked against partition reserve size.

## Dependencies and Integration Points

Depends on Boost.Redis/Asio, Ceph async blocked completion, RGW cache driver interfaces, SAL attrs, bufferlists, and `rgw_d4n_l1_datacache_address`. Integrates as a `CacheDriver` implementation for D4N data cache.

## Risks and Edge Cases

Offset and length parameters in `get()`/`get_async()` are ignored; the full `data` field is returned. Several optional Redis response accesses call `.value().value()` and can throw on missing optional values. `delete_attrs()` passes alternating attr field/value output to `HDEL`, but Redis `HDEL` expects field names only. `get_async()`/`put_async()` use `aio->get()` for both reads and writes. The file contains `std::clog` debug prints in `resolve_valkey_data_dir()`. `append_data()` rewrites whole values and is race-prone. Local `free_space` arithmetic can underflow because it starts at zero and is not synchronized.

## Test Signals

Cover connection address parsing, Redis command errors, missing keys/attrs/data fields, binary attribute round trips, offset reads, append races, delete free-space accounting, `HDEL` field behavior, AIO read/write callback result and data propagation, shutdown cancellation, `CONFIG GET dir` disabled or malformed, and filesystem reserve calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.h

## Purpose

Declares the Redis/Valkey cache driver implementation for RGW's cache-driver abstraction.

## Important APIs, Types, and Functions

`RedisDriver` derives from `CacheDriver` and overrides partition/free-space, initialization, put/get, async put/get, append, delete, rename, attribute CRUD, restore stub, and shutdown behavior. It owns a Boost.Redis connection, partition info, free-space counters, a private `redis_response` bundle, `redis_aio_handler`, and helpers for Redis-backed AIO operations.

## Control Flow and Data Flow

Callers interact through the `CacheDriver` interface. The driver prefixes keys with the partition location, stores object bytes in a `data` hash field, stores attrs as additional hash fields, and uses Asio/Boost.Redis for both coroutine/blocking style and AIO callbacks.

## State and Persistence Behavior

The class holds connection and local accounting state. Redis holds the cache contents; the header does not expose any durability or eviction policy. `restore_blocks_objects()` is a no-op returning success.

## Dependencies and Integration Points

Depends on Boost.Redis, Boost.Asio, filesystem, RGW cache driver definitions, RGW common types, and Ceph async completion. It is selected by cache-driver setup code for Redis/Valkey-backed D4N cache.

## Risks and Edge Cases

The constructor creates the connection but does not connect until `initialize()`. `redis_aio_handler` detects GET operations by searching the request payload for `"HGET"`, which is brittle. Captured references in AIO lambdas require caller-provided buffers/attrs/keys to outlive operation execution. `outstanding_write_size` is declared but unused in the implementation.

## Test Signals

Compile and interface-conformance tests, lifecycle tests around initialize/shutdown, AIO lifetime tests, partition prefixing, no-op restore behavior, and driver selection with invalid Redis endpoint configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_redis_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_req_context.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_req_context.h

## Purpose

Defines a compact request context struct intended to carry frontend-created request metadata down to backend calls.

## Important APIs, Types, and Functions

`req_context` contains `const DoutPrefixProvider* dpp`, `optional_yield y`, and `const jspan* span`.

## Control Flow and Data Flow

Backend helpers can accept this struct instead of separate logging prefix, coroutine yield context, and tracing span parameters. The struct is a passive carrier with default null prefix and default yield state.

## State and Persistence Behavior

No owned or durable state is present. The pointers are borrowed and require external lifetime management.

## Dependencies and Integration Points

Depends on `common/async/yield_context.h` and forward declares `DoutPrefixProvider`. Integrates with tracing/logging-aware SAL/backend function calls.

## Risks and Edge Cases

`span` is not default-initialized in the declaration, unlike `dpp`; users must initialize it before reading. Borrowed pointers can dangle if contexts outlive the request.

## Test Signals

Build coverage for aggregate initialization, static analysis for uninitialized `span`, and API tests where backend helpers receive null and non-null logging/yield/span values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_req_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_request.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_request.h

## Purpose

Declares lightweight request holder types used by RGW request handling and load generation.

## Important APIs, Types, and Functions

`RGWRequest` stores an id, `req_state*`, and `RGWOp*`, with `init_state()` to attach request state. `RGWLoadGenRequest` extends it with method, resource, content length, and an atomic failure flag pointer.

## Control Flow and Data Flow

Request processing can allocate an `RGWRequest` with an id, later attach the frontend `req_state`, and associate an operation. Load-generation code can use the derived type to represent synthetic HTTP requests and signal failures through shared atomic state.

## State and Persistence Behavior

Only transient pointers and request metadata are held. The class does not own `req_state`, `RGWOp`, or the failure flag.

## Dependencies and Integration Points

Depends on RGW common state, ACL, RADOS user types, operation declarations, QueueRing, and atomics. Integrated with request scheduling/dispatch and load generator paths.

## Risks and Edge Cases

Raw pointers and null defaults require careful ownership and initialization. `RGWLoadGenRequest` stores content length as `int`, so very large synthetic requests may not be representable. The destructor is virtual but performs no cleanup of associated operation/state pointers.

## Test Signals

Cover request initialization, loadgen construction, queueing through request rings, cleanup ownership expectations, and failure flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_resolve.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_resolve.cc

## Purpose

Implements the RGW DNS CNAME resolver wrapper used by REST virtual-host request preprocessing.

## Important APIs, Types, and Functions

`RGWResolver::RGWResolver()` obtains the singleton `DNSResolver`. `resolve_cname()` delegates to `DNSResolver::resolve_cname()`. `rgw_init_resolver()` allocates the global `rgw_resolver`, and `rgw_shutdown_resolver()` deletes it.

## Control Flow and Data Flow

During RGW startup, `rgw_init_resolver()` creates the wrapper. REST preprocessing can call `rgw_resolver->resolve_cname(host, cname, found)` when configured to resolve CNAMEs. Shutdown deletes the global wrapper.

## State and Persistence Behavior

Only process-global resolver pointer state is managed. No DNS results are persisted here; caching, if any, belongs to `DNSResolver`.

## Dependencies and Integration Points

Depends on resolver system headers, Ceph DNS resolver, `rgw_common.h`, and global `g_ceph_context`. Integrated with `rgw_rest_transform_s3_vhost_style()`.

## Risks and Edge Cases

`rgw_shutdown_resolver()` does not null the global pointer after deletion. Callers must ensure initialization before use and no concurrent use during shutdown. Resolver errors are propagated from the DNS layer.

## Test Signals

Cover init/shutdown lifecycle, successful CNAME, not found, resolver error, REST fallback when resolver returns failure, and repeated init/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_resolve.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_resolve.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_resolve.h

## Purpose

Declares the RGW DNS resolver wrapper and global lifecycle functions.

## Important APIs, Types, and Functions

`RGWResolver` owns a `DNSResolver*` and exposes `resolve_cname(hostname, cname, found)`. Global functions `rgw_init_resolver()` and `rgw_shutdown_resolver()` manage `extern RGWResolver* rgw_resolver`.

## Control Flow and Data Flow

RGW startup initializes the global resolver; REST host preprocessing asks it for CNAME resolution; RGW shutdown releases it.

## State and Persistence Behavior

No durable state. The global pointer is mutable process state and should be treated as a singleton service.

## Dependencies and Integration Points

Depends on `rgw_common.h` and forward declares `ceph::DNSResolver`. Integrated with virtual-host bucket routing and CNAME support.

## Risks and Edge Cases

Global mutable pointer has lifecycle and thread-safety risks. The wrapper does not expose copy/move restrictions, though it only contains a raw pointer.

## Test Signals

Compile/link lifecycle tests, null-global protection in callers, CNAME routing integration, and shutdown ordering under concurrent request handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_resolve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest.cc

## Purpose

Implements common RGW REST infrastructure: HTTP status/header/body output, formatter allocation, request argument parsing, input body reading, generic object-store operation parameter handling, REST manager routing, S3 virtual-host transformation, and request preprocessing.

## Important APIs, Types, and Functions

Initialization and mappings: `rgw_rest_init()`, `rgw_to_http_attrs`, `generic_attrs_map`, status name tables, hostname sets. Response helpers: `dump_errno()`, `dump_header()`, `dump_content_length()`, `dump_etag()`, time/owner/CORS helpers, `end_header()`, `abort_early()`, `dump_continue()`, `dump_range()`, `dump_body()`. Input helpers: `recv_body()`, `rgw_rest_read_all_input()`, `read_all_chunked_input()`. Parameter helpers: `RESTArgs::*`. Operation methods cover `RGWGetObj_ObjStore`, `RGWPutObj_ObjStore`, `RGWPostObj_ObjStore`, ACL/lifecycle/object-lock/legal-hold/multipart/list/delete parameter reads. Routing classes implement `RGWRESTFlusher`, `RGWRESTOp`, `RGWHandler_REST`, `RGWRESTMgr`, and `RGWREST`.

## Control Flow and Data Flow

`RGWREST::get_handler()` preprocesses the request, resolves a manager from the decoded URI, asks it for a handler, initializes the handler, and initializes metadata info. Preprocessing stores the original URI for AWSv4 auth, attaches client IO, decodes and validates URI, resolves content length from CGI/FastCGI env variants, extracts generic metadata headers, handles `Expect: 100-continue`, and maps HTTP method to `s->op`.

Handlers use `RGWHandler_REST::get_op()` to allocate the operation for the HTTP method and initialize it. Operations use `RESTArgs` and input helpers to parse query/body state. Response flow sets request errors, sends status/headers, optionally writes formatter output, and body send/receive paths charge rate-limit byte counters.

`rgw_rest_transform_s3_vhost_style()` normalizes Host headers, matches configured S3/S3Website hostnames or CNAMEs, optionally treats the host as a bucket name, prepends the bucket to the request URI, sets website flags, and re-decodes the final URI.

## State and Persistence Behavior

This file owns process-global maps and hostname sets initialized from config and zonegroup hostnames. Per-request state is mutated heavily: `req_state` formatter, content length, generic attrs, op type, URI/domain, redirect/error headers, and rate-limit accounting. It does not persist object metadata itself, but it reads request headers into `s->generic_attrs` for later persistence by operations.

## Dependencies and Integration Points

Depends on RGW auth, op, S3/Swift REST handlers, CORS, perf counters, client IO, DNS resolver, rate limiter, formatters, UTF-8 validation, Ceph config, and SAL bucket state. It is the central integration layer between frontends, protocol handlers, RGW operations, and IO filters.

## Risks and Edge Cases

Global initialization appends to maps/sets and should be idempotent only if duplicate overwrites are harmless. Hostname suffix matching can be ambiguous; comments note missing sanity checks. Content-length compatibility chooses the larger valid length when both CGI headers exist. Chunked input reader grows chunks until max and can return partial data on `-ERANGE`. POST multipart parsing is custom and sensitive to CRLF/boundary handling. `dump_body()` and `recv_body()` charge bandwidth after transfer, not before. `abort_early()` may rewrite 404 to redirect and must avoid double formatter/header output.

## Test Signals

Cover REST init with configured extended attrs and hostnames, content-length conflict cases, zero-byte and negative lengths, zero byte in URL rejection, formatter selection from query and Accept header, all `RESTArgs` parsers, PUT max-size boundaries, POST multipart boundaries and malformed headers, chunked read limits, multipart/list parameter bounds, handler routing/default managers, S3 virtual-host/CNAME/IP/S3Website priority cases, CORS/error/redirect headers, rate-limit byte charging, and IO exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest.h

## Purpose

Declares the common REST interface, object-store operation subclasses, REST routing managers, request/response helpers, and input parsing utilities used across RGW REST protocols.

## Important APIs, Types, and Functions

Exports initialization/flush functions, `rgw_sanitized_hdrval()`, JSON input helper, `RESTArgs`, `RGWRESTFlusher`, many `RGW*ObjStore` operation subclasses, `RGWRESTOp`, `RGWHandler_REST`, `RGWRESTMgr`, `RGWREST`, content-length constants, header/body dump helpers, `parse_content_length()`, `compute_domain_uri()`, and `rgw_rest_transform_s3_vhost_style()`.

## Control Flow and Data Flow

The header defines the reusable shape of REST operations: handlers allocate per-method ops, ops parse params and send responses through `RGWRESTFlusher`, managers route URI prefixes, and `RGWREST` ties manager resolution to frontend IO. Inline helpers sanitize metadata header values, parse content length, and derive request domain URI from request state/env.

## State and Persistence Behavior

Most declarations operate on per-request `req_state`. `rgw_to_http_attrs` is global mapping state initialized at runtime. Operation subclasses hold parsed request payloads or flags but persistence is handled in base operation implementations and storage drivers.

## Dependencies and Integration Points

Depends on RGW operation hierarchy, formatters, client IO, Lua background declarations, Ceph JSON/string helpers, and Boost flat sets. It is included by S3, Swift, admin, account, bucket logging, and other REST dialect handlers.

## Risks and Edge Cases

The many thin `ObjStore` subclasses rely on base-class behavior; changing base op contracts can affect many REST paths. `RGWGetObjAttrs_ObjStore::get_params()` remains pure virtual despite default response methods. `dump_header_quoted()` declares an unused template parameter pack, which is harmless but unusual. `parse_content_length()` treats empty content length as zero and invalid strings as -1.

## Test Signals

Build coverage for all subclasses, formatter allocation/reallocation, header sanitization with trailing NULs and embedded NULs, JSON input parse failures, manager registration/routing, REST handler ownership, and protocol-specific operation factories using these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_account.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_account.cc

## Purpose

Implements REST admin account operations for creating, modifying, retrieving, deleting, and setting quotas on RGW accounts.

## Important APIs, Types, and Functions

Defines `RGWOp_Account_Create`, `RGWOp_Account_Modify`, `RGWOp_Account_Get`, `RGWOp_Account_Delete`, and `RGWOp_Account_Quota_Set`, all derived from `RGWRESTOp`. Handler factory methods `RGWHandler_Account::op_post()`, `op_put()`, `op_get()`, and `op_delete()` choose the correct operation.

## Control Flow and Data Flow

Each operation checks `accounts` caps for read or write. Create parses id, tenant, name, email, and max limits. If the local zone is not metadata master, it forwards to the master and uses the master-generated account id from the JSON response before calling `rgw::account::create()`. Modify and delete forward to master first, then parse state and call account modify/remove locally. Get parses selectors and calls `rgw::account::info()`. Quota set requires `id` and `quota-type` of `account` or `bucket`, parses optional max-size, max-objects, and enabled, then calls `rgw::account::modify()`.

## State and Persistence Behavior

Persistent account metadata and quota state are changed by `rgw::account::*` helpers and master-zone forwarding. This file builds `rgw::account::AdminOpState`, handles error mapping such as `-EEXIST` to `-ERR_ACCOUNT_EXISTS`, and streams output through the REST flusher.

## Dependencies and Integration Points

Depends on account admin helpers, process env/site for forwarding, `RESTArgs`, user caps, and SAL driver metadata-master detection. Integrated under the account REST manager and admin API authentication stack.

## Risks and Edge Cases

Modify/delete/quota unconditionally forward to master; behavior on the master depends on `rgw_forward_request_to_master()` semantics. Quota `max-size` is parsed as `int32_t`, which is too narrow for large byte limits despite documentation implying byte sizes. Create uses the forwarded JSON id and fails if it is empty. Optional numeric parsers can leave invalid values as operation errors only if callers inspect returns; these execute methods do not consistently check every `RESTArgs` return.

## Test Signals

Cover caps enforcement, create on master and non-master, generated id propagation, duplicate account mapping, modify/delete forwarding failures, get by id/tenant/name, quota set missing id/type, invalid quota type, large max-size overflow, enabled parsing, and handler method-to-operation selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_account.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_account.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_account.h

## Purpose

Declares the REST handler and manager for account administration endpoints.

## Important APIs, Types, and Functions

`RGWHandler_Account` derives from `RGWHandler_Auth_S3`, overrides method factories for GET/PUT/POST/DELETE, and allows `read_permissions()` to return success after auth. `RGWRESTMgr_Account` returns a new account handler for matching routes.

## Control Flow and Data Flow

The manager creates an authenticated S3-style account handler. The handler chooses account operation classes based on HTTP method, with PUT further distinguishing quota subresource in the implementation.

## State and Persistence Behavior

No persistent state is declared. Handlers are allocated per request and deleted by REST manager ownership.

## Dependencies and Integration Points

Depends on `rgw_rest.h` and `rgw_rest_s3.h`. Integrated into admin/account REST resource registration.

## Risks and Edge Cases

`read_permissions()` returning 0 means fine-grained authorization relies on each operation's `check_caps()`. Manager ignores the `driver`, `req_state`, and frontend prefix arguments when constructing the handler.

## Test Signals

Route `/account` requests through the manager, verify auth strategy use, method factory outputs, operation-level cap checks, and handler cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_account.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_admin.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_admin.h

## Purpose

Declares the base REST manager class for admin resources.

## Important APIs, Types, and Functions

`RGWRESTMgr_Admin` derives from `RGWRESTMgr` and provides default constructor/destructor only.

## Control Flow and Data Flow

The class serves as a type marker/extension point for admin resource manager registration. Actual routing behavior is inherited from `RGWRESTMgr`.

## State and Persistence Behavior

No additional state or persistence behavior beyond `RGWRESTMgr`.

## Dependencies and Integration Points

Depends on `rgw/rgw_rest.h`. Integrated with admin API setup that registers sub-managers for users, buckets, accounts, metadata, and related admin resources.

## Risks and Edge Cases

Because it adds no overrides, all behavior depends on resources registered on the inherited manager. Missing subresource registration will fall back to default manager behavior.

## Test Signals

Compile coverage, admin manager construction/destruction, resource registration through inherited APIs, and default routing behavior with unknown admin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.cc

## Purpose

Implements S3-compatible bucket logging REST operations for reading, configuring, disabling, and manually flushing bucket access logging.

## Important APIs, Types, and Functions

Utility helpers verify the `?logging` subresource and update the logging mtime attribute. `RGWGetBucketLoggingOp` reads and returns logging configuration. `RGWPutBucketLoggingOp` parses XML configuration, validates target bucket and policy, writes source bucket logging attributes, updates target logging source lists, and rolls over old pending log objects when configuration changes. `RGWPostBucketLoggingOp` flushes pending logging objects. Factory methods on `RGWHandler_REST_BucketLogging_S3` create GET/PUT/POST operations.

## Control Flow and Data Flow

GET validates the request, loads the source bucket, decodes `RGW_ATTR_BUCKET_LOGGING` and optional mtime attr, and returns XML `BucketLoggingStatus`. PUT validates query/body, parses XML into `rgw::bucketlogging::configuration`, loads the target bucket when enabled, checks requester ownership and IAM permission, verifies target bucket policy and attributes, then uses `retry_raced_bucket_write()` to atomically add/update/remove logging attributes on the source bucket. If a previous config changed, it may roll over the old pending logging object and update logging source attributes on old/new target buckets. POST loads source/target config, verifies permission/policy, ensures target source metadata is current, gets the pending logging object name, and calls `rollover_logging_object()`.

## State and Persistence Behavior

Source bucket attrs store `RGW_ATTR_BUCKET_LOGGING` and `RGW_ATTR_BUCKET_LOGGING_MTIME`. Target bucket attrs track logging source buckets via bucketlogging helpers. Pending logging objects are committed/rolled over into the target bucket. Updates are protected with bucket-attribute merge/retry logic to handle racing writers.

## Dependencies and Integration Points

Depends on RGW op/rest/S3 auth, ARN parsing, URL helpers, `rgw_bucket_logging` configuration and rollover helpers, IAM condition checks, SAL bucket loading/attrs, and XML formatter/decoder. Integrated with S3 `GET/PUT/POST Bucket logging`.

## Risks and Edge Cases

The helper requires `logging` to exist with no value and bucket name to be present. PUT permission uses `configuration` and `target_bucket` prepared during init processing, so operation ordering matters. Target bucket must differ from source and share the zonegroup. Failures updating logging source lists are warnings after source config may already be changed. Decode failures of existing config can still overwrite unknown old state. POST response always writes `FlushedLoggingObject`, which may be empty if no pending object existed or rollover behavior changes.

## Test Signals

Cover missing/valued `logging` param, non-bucket requests, GET with no config, corrupt config, mtime absent/corrupt, PUT malformed XML, disabling logging cleanup, target bucket parse/load failures, same-bucket and cross-zonegroup rejection, IAM owner/policy failures, raced attribute writes, old target source removal, rollover failures, POST no pending object, POST successful flush, and factory method selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.h

## Purpose

Declares the S3 bucket logging REST handler factory.

## Important APIs, Types, and Functions

`RGWHandler_REST_BucketLogging_S3` derives from `RGWHandler_REST_S3`, overrides permission initialization/reading to return success, disables quota support, and exposes static `create_get_op()`, `create_put_op()`, and `create_post_op()` factories.

## Control Flow and Data Flow

The surrounding S3 handler can route `?logging` requests to this handler and call the static factories to create operation instances implemented in the `.cc` file. Operation-level permission checks perform the real IAM and ownership checks.

## State and Persistence Behavior

No state is stored in the handler declaration. Persistence is handled by the operation implementations against bucket attrs and log objects.

## Dependencies and Integration Points

Depends on `rgw_rest_s3.h`. Integrated with S3 bucket subresource routing and bucket logging operation classes.

## Risks and Edge Cases

Returning success from handler-level permission hooks means tests must ensure operation-level `verify_permission()` always runs and enforces access. `supports_quota()` returns false because logging configuration operations should not be quota-charged.

## Test Signals

Route GET/PUT/POST `?logging` requests through the S3 dispatcher, verify quota bypass, operation-level permission enforcement, and factory ownership/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.h -->
