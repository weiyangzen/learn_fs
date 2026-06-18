# subset-b-007893 research

Grouped research for the Tahoe-LAFS source paths requested in subset `subset-b-007893`. Each section preserves the source path title and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/interfaces.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/interfaces.py

### Purpose
This module is the central Tahoe-LAFS contract file. It defines Foolscap `RemoteInterface` protocols, Zope interfaces, constants, and exception types used across storage, node capability handling, uploads/downloads, mutable files, directory operations, health checking, client/node construction, status reporting, helper services, storage plugins, and listener address families. It is mostly declarative: behavior is specified by method signatures, return shapes, and docstrings, while implementations live in storage, immutable, mutable, client, nodemaker, web, and plugin modules.

### Important APIs, Types, and Functions
Storage contracts include `RIBucketWriter`, `RIBucketReader`, `RIStorageServer`, and client-side `IStorageServer`, `IStorageBucketWriter`, `IStorageBucketReader`, `IStorageBroker`, `IDisplayableServer`, and `IServer`. The remote storage protocol covers immutable bucket allocation/leases, mutable `slot_readv`, atomic `slot_testv_and_readv_and_writev`, and corruption advisories. Constants such as `HASH_SIZE`, `SALT_SIZE`, `SDMF_VERSION`, `MDMF_VERSION`, `MAX_BUCKETS`, `DEFAULT_IMMUTABLE_MAX_SEGMENT_SIZE`, and Foolscap constraints such as `StorageIndex`, `Hash`, `ReadVector`, and `TestAndWriteVectorsForShares` shape wire compatibility.

Capability and filesystem contracts include `IURI`, `IVerifierURI`, file/directory URI marker interfaces, `IReadable`, `IWriteable`, `IMutableFileVersion`, `IFilesystemNode`, `IFileNode`, `IImmutableFileNode`, `IMutableFileNode`, and `IDirectoryNode`. These describe authority boundaries, read-only conversion, verify/repair caps, mutable servermap workflows, directory child/metadata operations, and deep traversal/manifest/stats operations.

Transfer and coding contracts include `ICodecEncoder`, `ICodecDecoder`, `IEncoder`, `IDecoder`, `IDownloadTarget`, `IDownloader`, `IEncryptedUploadable`, `IUploadable`, `IMutableUploadable`, `IUploadResults`, `IDownloadResults`, and `IUploader`. Health and repair contracts include `ICheckable`, `IDeepCheckable`, `ICheckResults`, `ICheckAndRepairResults`, `IDeepCheckResults`, `IDeepCheckAndRepairResults`, `IRepairable`, and `IRepairResults`. Node/client contracts include `IClient`, `INodeMaker`, operation status interfaces, remote helper/control interfaces, `IStatsProducer`, `IValidatedThingProxy`, `IConnectionStatus`, `IFoolscapStoragePlugin`, `IAnnounceableStorageServer`, and `IAddressFamily`.

### Control Flow
The module has little runtime control flow beyond exception constructors and `NoSuchChildError.__str__`. Its control-flow value is in the workflows it specifies. Immutable upload flows from an `IUploadable` through encryption, encoding, bucket writers, hash trees, URI extension data, and upload results. Download flows from an `IDownloader` to an `IDownloadTarget`, with producer/consumer cancellation semantics. Mutable update flows through servermap discovery modes, version selection, download, modifier/upload, storage test-and-set, and possible `UncoordinatedWriteError`. Health checks flow through a monitor, optional full verification, result object construction, and optional repair.

### State and Persistence Behavior
Interfaces define persistent state rather than own it. Important state includes storage shares and leases, mutable slots and write-enabler secrets, URI/capability authority, directory edge metadata, servermaps, upload/download timing/status, connection snapshots, and plugin announcements. Mutable interfaces explicitly depend on remembered servermap state and sequence/root-hash version identity. `IConnectionStatus` is intentionally a snapshot, not a live object.

### Dependencies and Integration Points
The module depends on `zope.interface`, Twisted `Deferred`/plugins, and Foolscap constraints/remote references. Implementations are spread throughout Tahoe-LAFS: `storage/server.py` and `storage_client.py` implement storage pieces; `mutable/filenode.py`, `mutable/servermap.py`, `mutable/publish.py`, and `mutable/retrieve.py` implement mutable contracts; `dirnode.py`, `nodemaker.py`, `client.py`, web resources, helper services, and tests consume the node, client, upload, download, and status interfaces.

### Risks and Edge Cases
This is a high-blast-radius compatibility file. Remote interface names and constraints are wire protocol, so type/encoding changes can break old peers. Mutable `slot_testv_and_readv_and_writev` semantics are subtle around zero-filling, new lengths, deletion, and test vector operators. Interface docs mix historical behavior with current behavior; comments note removed v1/v2 differences and TODOs. Capability methods encode authority, so mistaken read/write/repair cap behavior can be a security issue. Several methods document large memory/bandwidth effects and cancellation expectations that implementations must honor.

### Test Signals
Tests exercise these contracts indirectly and directly. `test_istorageserver.py` covers shared, immutable, and mutable `IStorageServer` APIs for Foolscap and HTTP clients. Mutable test suites cover `IMutableFileNode`, `IMutableFileVersion`, update, repair, checker, multiple versions, and interoperability. Client, dirnode, web, upload, download, helper, storage plugin, and introducer tests depend on interface shapes. `test/storage_plugin.py` provides plugin-style implementations of `IFoolscapStoragePlugin` and `IStorageServer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/interfaces.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/__init__.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/__init__.py

### Purpose
This package initializer exposes the public introducer construction entry point and preserves a legacy class name. It imports `create_introducer` from `allmydata.introducer.server` and aliases `_IntroducerNode` as `IntroducerNode` for old `.tac` files that may have the historical import path burned in.

### Important APIs, Types, and Functions
The exported API is `create_introducer`, used to create a configured introducer node, and `IntroducerNode`, a compatibility alias. `__all__` limits intended exports to those names and quiets unused-import tooling.

### Control Flow
Importing the package imports `server.py`, which has heavier Twisted/Foolscap/node dependencies. No additional runtime logic happens in this file.

### State and Persistence Behavior
No state is owned here. Persistence behavior belongs to `_IntroducerNode` in `server.py`, especially node configuration and the private `introducer.furl` file.

### Dependencies and Integration Points
This module is an integration shim for callers that import `allmydata.introducer.create_introducer` or legacy `allmydata.introducer.IntroducerNode`. It points all real behavior to `introducer/server.py`.

### Risks and Edge Cases
The main risk is import coupling: package import now eagerly imports server-side dependencies. Removing the alias could break old deployment descriptors. The file is intentionally minimal; adding logic here would make package import side effects harder to reason about.

### Test Signals
Introducer tests import server classes directly and also instantiate `IntroducerClient`/`IntroducerService`; legacy alias behavior is likely covered indirectly by node creation/import tests rather than a focused test in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/client.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/client.py

### Purpose
`IntroducerClient` is the client-side Foolscap service used by Tahoe nodes to publish local services and subscribe to peer service announcements. It signs outbound announcements, verifies inbound signed announcements, filters them by service, persists a YAML cache for startup/offline use, and reports connection status to the introducer.

### Important APIs, Types, and Functions
`InvalidCacheError` marks malformed cache input. `V2` is the required introducer protocol key. `IntroducerClient` implements `RIIntroducerSubscriberClient_v2` and `IIntroducerClient`. Its public methods are `startService`, `subscribe_to`, `publish`, `remote_announce_v2`, `got_announcements`, `connection_status`, `connected_to_introducer`, and `get_since`. Internal helpers include `_load_announcements`, `_save_announcements`, `_got_introducer`, `_got_versioned_introducer`, `_maybe_subscribe`, `_maybe_publish`, `create_announcement_dict`, `_process_announcement`, and `_deliver_announcements`.

### Control Flow
On `startService`, the client starts a Foolscap reconnection to the introducer and separately attempts `getReference`; initial connection failure loads cached announcements so local subscribers can still see remembered peers. Once connected, `_got_introducer` obtains remote version information and `_got_versioned_introducer` requires v2, records the publisher reference, registers disconnect handling, then publishes/subscribes any queued state.

`subscribe_to` registers a local callback in an `ObserverList`, sends a remote `subscribe_v2` if connected, and immediately replays cached inbound announcements for the requested service. `publish` obtains a monotonic sequence/nonce from the caller-provided sequencer, builds service announcement dictionaries, signs every outbound announcement with `sign_to_foolscap`, and republishes all signed announcements. Inbound `announce_v2` calls are passed through `got_announcements`; each announcement is unsigned and signature-verified, then `_process_announcement` rejects wrong services, exact duplicates, and stale/replayed sequence numbers before saving and delivering the new state.

### State and Persistence Behavior
Important in-memory state includes `_outbound_announcements` before signing, `_published_announcements` after signing, `_publisher`, `_subscriptions`, `_local_subscribers`, `_inbound_announcements`, `_since`, and debug counters. `_inbound_announcements` is keyed by `(service_name, key_s)` and stores `(announcement, verifying_key, timestamp)`. `_save_announcements` persists inbound state to `cache_filepath` as YAML entries containing `ann` and ASCII `key_s`; `_load_announcements` tolerates a missing cache but logs malformed shapes.

### Dependencies and Integration Points
The client integrates Twisted `service.Service`, Foolscap `Referenceable`, Tahoe `log`, YAML helpers, connection status conversion, remote-reference version negotiation, Ed25519 signature helpers from `introducer.common`, and crypto `BadSignature`. `allmydata.client` constructs introducer clients; `storage_client.py` subscribes to storage announcements; tests use `MemoryIntroducerClient` for model-only behavior.

### Risks and Edge Cases
Replay protection depends on valid integer `seqnum`; announcements without valid newer sequence numbers cannot replace an existing sequenced announcement. Cache loading assumes keys like `key_s` and `ann` are present in dict entries; malformed entries are logged but individual missing keys could still surface if not shaped as expected. Python bytes/text normalization is explicit but fragile around `service-name`, `nickname`, and YAML encodings. Signature failures are ignored per-announcement, so mixed batches continue processing. `_subscriptions` is cleared on disconnect so resubscribe happens on reconnect.

### Test Signals
`test_introducer.py` covers client instantiation, v2 version requirements, cache behavior, bad signatures, duplicate/replay/update behavior, publish/subscribe flows, and connection failure handling. Web and storage-client tests exercise `connected_to_introducer` and service announcement consumption. The signature tests verify invalid signatures are not delivered to subscribers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/common.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/common.py

### Purpose
This module contains shared introducer announcement utilities and status descriptor types. It extracts Foolscap tub IDs, serializes/signs announcement dictionaries, verifies/splits signed Foolscap announcement tuples, and provides descriptor objects for introducer status pages.

### Important APIs, Types, and Functions
`get_tubid_string_from_ann` picks `anonymous-storage-FURL` or `FURL` from an announcement and delegates to `get_tubid_string`, which extracts the lower-cased tub ID from a `pb://...@...` Foolscap FURL. `sign_to_foolscap` JSON-serializes an announcement as UTF-8 bytes, signs it with Ed25519, base32-encodes the signature with a `v0-` prefix, strips the `pub-` prefix from the verifying key string, and returns `(msg, sig, key)`. `unsign_from_foolscap` validates the `v0-` prefixes, rebuilds the public verifying key, verifies the signature, JSON-decodes the message, and returns `(announcement, key_vs)`. `UnknownKeyError` distinguishes unsupported unsigned/unknown-key formats. `SubscriberDescriptor` and `AnnouncementDescriptor` are plain status containers.

### Control Flow
Signing is deterministic for the JSON bytes produced by `jsonbytes.dumps`, aside from the signing key. Verification rejects missing signature/key data, unknown version prefixes, bad base32/key material, or signature mismatch before JSON decoding is returned to callers. `AnnouncementDescriptor` decodes connection hints from `anonymous-storage-FURL` using Foolscap `decode_furl` when present.

### State and Persistence Behavior
No persistent state is stored here. The signed tuple returned by `sign_to_foolscap` is the durable/wire representation stored by client caches and server announcement maps. Descriptor instances hold snapshot attributes for status displays.

### Dependencies and Integration Points
The module depends on Foolscap FURL decoding, Tahoe Ed25519 utilities, Tahoe `base32`, JSON byte utilities, and `remove_prefix`. It is used by both `introducer/client.py` and `introducer/server.py`, and the descriptor classes are returned from `IntroducerService.get_announcements()` and `get_subscribers()` for web/status code.

### Risks and Edge Cases
`get_tubid_string` asserts the FURL regex matches, so malformed FURLs fail hard. The signature version is fixed to `v0-`; future versioning needs explicit compatibility logic. The claimed key is trusted only after signature verification, but callers must handle `BadSignature` and `UnknownKeyError`. JSON byte/text normalization is part of cross-version compatibility and can be sensitive to non-ASCII or non-JSON-serializable announcement fields.

### Test Signals
`test_introducer.py::Signatures` checks signing round trips, byte types, prefix validation, missing signature/key rejection, bad signature rejection, and unknown version rejection. Additional introducer tests exercise descriptor/status paths through server announcement and subscription state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/interfaces.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/interfaces.py

### Purpose
This module defines the v2 Foolscap introducer protocol and the local `IIntroducerClient` interface. It documents the signed announcement tuple format and the expected announcement/subscriber metadata used for Tahoe service discovery.

### Important APIs, Types, and Functions
`Announcement_v2` is currently `Any()` because signed announcement tuples are heterogeneous `(msg, sig_vs, claimed_key_vs)` values. `RIIntroducerSubscriberClient_v2` exposes remote `announce_v2(announcements)`. `RIIntroducerPublisherAndSubscriberService_v2` exposes remote `get_version`, `publish_v2`, and `subscribe_v2`. `SubscriberInfo` is a bytes-keyed Foolscap dictionary for diagnostic metadata. `IIntroducerClient` specifies `publish`, `subscribe_to`, and `connected_to_introducer`.

### Control Flow
The declared flow is publish/subscribe. Publishers call `publish_v2` with a signed announcement and canary. Subscribers call `subscribe_v2` with a remote subscriber reference and service name. The introducer calls subscriber `announce_v2` with matching announcements. Local consumers call `IIntroducerClient.subscribe_to`, which must invoke callbacks for new and changed announcements and tolerate duplicates.

### State and Persistence Behavior
No state is stored by this module, but it defines the state keys carried on the wire: announcement metadata such as `version`, `nickname`, `app-versions`, `my-version`, `oldest-supported`, `service-name`, storage FURLs, and plugin-specific fields. It also defines subscriber diagnostic metadata used by the server.

### Dependencies and Integration Points
It depends on Zope interfaces and Foolscap `RemoteInterface`, `Referenceable`, and constraints. `IntroducerClient` implements the subscriber remote interface and local interface; `IntroducerService` implements the publisher/subscriber service remote interface. `client.py`, `server.py`, storage discovery, and tests rely on the remote names being stable.

### Risks and Edge Cases
Remote interface names are wire-compatibility identifiers. The broad `Any()` for `Announcement_v2` provides flexibility but moves validation into `common.py`, `client.py`, and `server.py`. Comments still describe removed v1 behavior for historical compatibility context; new code should assume signed v2 announcements.

### Test Signals
`test_introducer.py` and `test_multi_introducers.py` exercise the protocol through real `IntroducerClient` and `IntroducerService` instances. Version-negotiation tests ensure clients reject servers without v2 support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/interfaces.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/server.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/server.py

### Purpose
This module builds and runs the Tahoe introducer node and implements the server-side v2 publish/subscribe service. The introducer remembers the latest signed announcement for each `(service_name, signing_key)` pair and forwards matching announcements to subscribers.

### Important APIs, Types, and Functions
`create_introducer` reads/creates node configuration, builds I2P/Tor providers and the main Foolscap tub, and returns a `_IntroducerNode` in a Deferred-like success or a Twisted `Failure` on exception. `_IntroducerNode` subclasses `node.Node`, initializes the introducer service, registers it with the tub, migrates old public `introducer.furl` files to `private/introducer.furl`, and optionally starts web status. `FurlFileConflictError` protects conflicting old/new FURL files. `stringify_remote_address` normalizes subscriber peer addresses. `IntroducerService` implements `RIIntroducerPublisherAndSubscriberService_v2` and exposes `remote_get_version`, `remote_publish_v2`, `remote_subscribe_v2`, `get_announcements`, and `get_subscribers`.

### Control Flow
Node creation builds transport providers and tub options from config, then `_IntroducerNode.init_introducer` validates that the tub is listening before registering `IntroducerService`. Publication calls enter `remote_publish_v2`, then `publish`, then `_publish`. `_publish` verifies the signed tuple with `unsign_from_foolscap`, extracts `service-name`, and compares it with the old announcement for the same index. Exact duplicates are ignored. Sequenced updates must provide a newer integer `seqnum`; stale or unsequenced replacements are rejected. Accepted announcements are stored and pushed via subscriber `announce_v2` calls to all subscribers for that service.

Subscription calls enter `remote_subscribe_v2`, normalize bytes/text keys into `UnicodeKeyDict`, and call `add_subscriber`. `add_subscriber` records the remote subscriber, registers a disconnect cleanup callback, and immediately sends any already-known announcements for that service.

### State and Persistence Behavior
Server memory state includes `_announcements`, keyed by `(service_name, key_s)` and containing `(ann_t, canary, ann, timestamp)`, plus `_subscribers`, keyed by service name and then subscriber remote reference. Debug counters track inbound messages, duplicates, replay failures, updates, outbound messages, and subscriptions. Persistent state is the registered private `introducer.furl`; old public FURL migration is intentionally guarded.

### Dependencies and Integration Points
The module integrates Twisted services/deferreds/failures, Foolscap `Referenceable`, Tahoe node configuration and tub helpers, I2P/Tor provider creation, Tahoe logging, `dictutil.UnicodeKeyDict`, and `introducer.common`. Web status integrates through `IntroducerWebishServer`.

### Risks and Edge Cases
`create_introducer` returns `Failure()` instead of raising, so callers must handle both success and failure Deferred values. `FurlFileConflictError` intentionally stops ambiguous FURL migration. Replay protection only applies when the old announcement had `seqnum`; first announcements without sequence numbers can be accepted. Subscriber remote failures are logged asynchronously. The canary is stored for status but disconnect pruning of announcements is not active.

### Test Signals
`test_introducer.py` covers service construction, publish/subscribe behavior, duplicate and stale announcement rejection, v2 version advertisement, FURL conflict handling, subscriber status, and signature paths. Web introducer tests exercise status display data produced from descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/listeners.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/listeners.py

### Purpose
This module defines a typed abstraction for listener providers used during Tahoe node creation. It lets transports such as TCP, Tor, and I2P report availability, privacy properties, generated tub configuration, and runtime address-family objects through a common protocol.

### Important APIs, Types, and Functions
`ListenerConfig` is an `attrs.frozen` value with `tub_ports`, `tub_locations`, and `node_config`. `Listener` is a `typing.Protocol` requiring `is_available`, `can_hide_ip`, async `create_config`, and `create`. `TCPProvider` implements plain TCP listener configuration, allocating a port with `allocate_tcp_port` when explicit `--port/--location` options are absent. `StaticProvider` is a frozen test/config helper that returns precomputed availability, privacy, config, and address-family behavior; its config may be an awaitable.

### Control Flow
Node creation selects one or more listener providers, asks whether each is available and whether it can hide IP addresses, awaits `create_config`, merges resulting `ListenerConfig` values into `tahoe.cfg`, then later calls `create` to obtain an `IAddressFamily`. `TCPProvider.create_config` either uses paired CLI port/location values or allocates a TCP port for the provided hostname.

### State and Persistence Behavior
`ListenerConfig` is the persistence boundary: its values are merged into the node configuration file. `TCPProvider` itself has no state. `StaticProvider` stores fixed constructor values and can defer config production until an awaitable resolves.

### Dependencies and Integration Points
The module depends on `attrs`, Twisted CLI `Options`, Tahoe `_Config`, `IAddressFamily`, and `allocate_tcp_port`. `scripts/create_node.py` imports these providers, while `util/tor_provider.py` and `util/i2p_provider.py` return compatible configs and address families.

### Risks and Edge Cases
TCP `create` is intentionally unimplemented, so using `TCPProvider` beyond config generation requires another path to instantiate address handling. Automatic port allocation can race with later bind attempts. CLI options must provide `--port` and `--location` together; the broader create-node code validates this. Merging multiple `node_config` values can conflict, as tested in create-node tests.

### Test Signals
`test/cli/test_create.py` covers `ListenerConfig` merge behavior and asynchronous `StaticProvider.create_config`. Tor/I2P provider tests and create-node integration tests exercise compatibility with this protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/listeners.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/monitor.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/monitor.py

### Purpose
This module provides a small monitor object for long-running Tahoe operations. It lets operation code publish arbitrary status, observe cancellation, finish exactly through a one-shot observer, and let initiators wait for completion.

### Important APIs, Types, and Functions
`IMonitor` defines operation-side methods `is_cancelled`, `raise_if_cancelled`, `set_status`, `get_status`, and `finish`, plus initiator-side methods `is_finished`, `when_done`, and `cancel`. `OperationCancelledError` is raised when cancelled operations check in. `Monitor` implements `IMonitor` with `cancelled`, `finished`, `status`, and `observer.OneShotObserverList`.

### Control Flow
Callers construct `Monitor` and pass it into work such as checks, deep checks, or repairs. Operation code periodically calls `raise_if_cancelled` or `is_cancelled`, updates status with `set_status`, and calls `finish` when done. `finish` sets status, marks the monitor finished, fires all `when_done` waiters, and returns the original status/failure so it can be attached with `Deferred.addBoth`.

### State and Persistence Behavior
All state is in memory and process-local. `status` can be any object, including a Twisted `Failure`. `when_done` returns Deferreds backed by a one-shot observer and does not persist across process restarts.

### Dependencies and Integration Points
The monitor depends on Zope interface machinery and Tahoe `observer.OneShotObserverList`. It is used by `interfaces.ICheckable` contracts, mutable checkers/filenodes, dirnode deep operations, upload tests, system/deepcheck/checker tests, and repair paths.

### Risks and Edge Cases
`finish` does not guard against multiple calls; repeated calls depend on `OneShotObserverList` behavior and could overwrite status. Cancellation is cooperative only; operation code must check the monitor before starting more work. The status type is unconstrained, so consumers must know operation-specific shapes.

### Test Signals
`test_monitor.py` directly verifies cancellation, status setting, and finish/when_done behavior. `test_deepcheck.py` verifies cancelled deep operations surface `OperationCancelledError`. Checker and repair tests pass monitors through health workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/monitor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/__init__.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/__init__.py

### Purpose
This package initializer is empty. It marks `allmydata.mutable` as a package containing mutable-file implementation modules such as `filenode`, `checker`, `common`, `servermap`, `publish`, `retrieve`, `layout`, and `repairer`.

### Important APIs, Types, and Functions
There are no exports, imports, functions, classes, or constants in this file.

### Control Flow
No runtime control flow occurs on package import from this file.

### State and Persistence Behavior
No state or persistence behavior is defined here.

### Dependencies and Integration Points
Integration is only the Python package boundary. Consumers import concrete modules directly, for example `allmydata.mutable.filenode.MutableFileNode` or `allmydata.mutable.common.MODE_READ`.

### Risks and Edge Cases
The file is intentionally empty. Adding imports here could introduce import cycles because mutable modules already depend on each other and on global Tahoe interfaces.

### Test Signals
No direct tests are expected for this file; the mutable package is heavily exercised by tests under `src/allmydata/test/mutable/`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/checker.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/checker.py

### Purpose
This module implements mutable-file health checking and check-and-repair orchestration. It builds a `ServerMap`, determines whether a mutable file is healthy/recoverable, optionally verifies all share bytes, reports corrupt shares, and invokes repair when appropriate.

### Important APIs, Types, and Functions
`MutableChecker` owns normal checks with `SERVERMAP_MODE = MODE_CHECK`. Its public `check(verify=False, add_lease=False)` returns a Deferred firing with `CheckResults`. Key helpers are `_got_mapupdate_results`, `_verify_all_shares`, `_process_bad_shares`, `_count_shares`, and `_make_checker_results`. `MutableCheckAndRepairer` subclasses it with `SERVERMAP_MODE = MODE_WRITE`, stores a `CheckAndRepairResults`, and overrides `check` to stash pre-repair results and call `_maybe_repair`.

### Control Flow
`MutableChecker.check` creates a fresh `ServerMap`, starts `ServermapUpdater` in check mode, optionally notifies history, and waits for the update. `_got_mapupdate_results` marks repair needed when there are unrecoverable versions, not exactly one recoverable version, or the best recoverable version has fewer than `N` distinct shares. If `verify=True`, `_verify_all_shares` runs `Retrieve(..., verify=True)` against the best version so data-level corruption is caught, then `_process_bad_shares` records failures and marks repair needed. `_make_checker_results` synthesizes human-readable report/summary strings, counters, share maps, corrupt share locators, server response lists, and a servermap copy into `CheckResults`.

`MutableCheckAndRepairer.check` runs the base check, stores pre-repair results, and `_maybe_repair` skips repair if not needed or if the node is read-only. Otherwise it calls `node.repair`, records success/failure, and builds post-repair results from the repairer servermap.

### State and Persistence Behavior
Checker state is per-operation: `bad_shares`, `need_repair`, `responded`, `_storage_index`, and `best_version`. It does not persist data itself. It may add leases through `ServermapUpdater(add_lease=True)` and repair can publish replacement shares through the node repair path.

### Dependencies and Integration Points
The module depends on `ServerMap`, `ServermapUpdater`, `Retrieve`, `CheckResults`, `CheckAndRepairResults`, `servers_of_happiness`, URI parsing, logging, and mutable common modes/errors. `MutableFileNode.check` and `check_and_repair` instantiate these classes. Repair integrates with `mutable/repairer.py`.

### Risks and Edge Cases
Lightweight `check` can miss corrupted block/share data because it trusts share metadata; full `verify=True` is required to download and validate bytes. Defaults for totally missing shares use arbitrary `k=3`, `N=10`, which can affect summary counters when no version exists. Sorting bad shares by `id` is deterministic only within a process. Read-only mutable files cannot be repaired here. The monitor is checked before expensive result creation and repair decisions, so cancellation depends on callers passing a live monitor.

### Test Signals
`test/mutable/test_checker.py` covers good files, no shares, insufficient shares, bad signatures, verify-vs-check differences for corrupted share data, corrupt share hash chains, encrypted private key failures, SDMF and MDMF behavior, and corrupt-share reporting. `test_deepcheck.py`, `test_checker.py`, and `test_repairer.py` exercise this through node-level check and check-and-repair APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/checker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/common.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/common.py

### Purpose
This module contains shared mutable-file constants, exception types, and cryptographic key derivation helpers. It is imported by servermap, publish, retrieve, checker, repairer, and filenode code.

### Important APIs, Types, and Functions
Mode constants are `MODE_CHECK`, `MODE_ANYTHING`, `MODE_WRITE`, `MODE_READ`, and `MODE_REPAIR`, defining how thoroughly servermaps query peers and whether private-key/write information is needed. Exception types include `NotWriteableError`, `BadShareError`, `NeedMoreDataError`, `UncoordinatedWriteError`, `UnrecoverableFileError`, `NotEnoughServersError`, `CorruptShareError`, and `UnknownVersionError`. Crypto helpers are `encrypt_privkey(writekey, privkey)`, `decrypt_privkey(writekey, enc_privkey)`, and `derive_mutable_keys(keypair)`.

### Control Flow
`derive_mutable_keys` DER-serializes RSA public/private keys, hashes the private key to produce the SSK writekey, AES-encrypts the private key under that writekey, hashes the public key into the fingerprint, and returns `(writekey, encprivkey, fingerprint)`. `encrypt_privkey` and `decrypt_privkey` wrap Tahoe AES helper creation and data transform calls.

### State and Persistence Behavior
The module owns no mutable state. Its outputs become persistent mutable-file identity/authority data: write keys, encrypted private keys stored in shares, and public-key fingerprints embedded in capabilities and share validation.

### Dependencies and Integration Points
It depends on Tahoe AES/RSA crypto helpers and `hashutil`. `MutableFileNode.create_with_keys` calls `derive_mutable_keys` in a CPU thread. `servermap.py` and `retrieve.py` call `decrypt_privkey` to recover signing keys when write authority is available. `checker.py` uses common modes and corrupt-share errors.

### Risks and Edge Cases
These helpers sit on a security boundary. Changes to DER serialization, hash functions, AES mode, or prefix handling would break capability identity or make old mutable shares unreadable. `UncoordinatedWriteError.__repr__` carries user-facing guidance but no structured metadata. `NeedMoreDataError` includes offsets/lengths used by layout/retrieve logic and must remain consistent with share parsing.

### Test Signals
Mutable creation tests compare derived key/fingerprint behavior through caps, web tests derive expected mutable keys from generated RSA keys, and retrieve/servermap tests exercise private-key decryption paths. Integration web tests call `derive_mutable_keys` to construct expected mutable URIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/filenode.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/filenode.py

### Purpose
This module implements the main mutable-file node and version facades. `MutableFileNode` represents a mutable file capability and coordinates servermap discovery, reading, overwriting, modifying, checking, and repair. `MutableFileVersion` represents a specific recoverable version and performs version-scoped reads, writes, modify retries, and MDMF partial updates. `BackoffAgent` provides retry delay behavior for write collisions.

### Important APIs, Types, and Functions
`BackoffAgent.delay` implements exponential jittered retry and gives up after four attempts. `MutableFileNode` implements `IMutableFileNode` and `ICheckable`. Important construction methods are `init_from_cap`, async `create_with_keys`, and `_get_initial_contents`. Capability/state methods include `get_cap`, `get_readcap`, `get_verify_cap`, `get_repair_cap`, `get_uri`, `get_write_uri`, `get_readonly_uri`, `get_readonly`, `get_writekey`, `get_readkey`, `get_storage_index`, `get_fingerprint`, `get_privkey`, `get_pubkey`, and encoding-share getters. Operational methods include `check`, `check_and_repair`, `repair`, `get_best_readable_version`, `download_best_version`, `get_size_of_best_version`, `get_best_mutable_version`, `overwrite`, `upload`, `modify`, `download_version`, `get_servermap`, `_update_servermap`, and `_upload`.

`MutableFileVersion` implements `IMutableFileVersion` and `IWriteable`. It exposes version identity and accessors (`get_sequence_number`, `get_writekey`, `get_size`, `get_storage_index`), read paths (`download_to_data`, `read`, `_read`), write paths (`overwrite`, `modify`, `_modify_and_retry`, `_modify_once`, `_upload`), and `update` for MDMF in-place-ish updates.

### Control Flow
Existing nodes are initialized from caps, learning protocol version, read/write keys, storage index, and fingerprint. New nodes are created with an RSA keypair; mutable keys are derived in a CPU thread, an SDMF or MDMF write URI is built, initial contents are wrapped as an `IMutableUploadable`, and `_upload` publishes initial shares.

Most public `MutableFileNode` operations use `_do_serialized`, chaining a persistent Deferred serializer and firing caller Deferreds via `eventually` to avoid reentrancy. Reads obtain a servermap in `MODE_READ`, build a read-only `MutableFileVersion`, and download through `Retrieve`; `download_best_version` retries with `MODE_WRITE` if a read-mode download lacks enough shares. Write-intent operations obtain a servermap in `MODE_WRITE` and build a writeable `MutableFileVersion`. `overwrite`, `upload`, and `modify` are serialized because they must not race on the same node.

`MutableFileVersion.modify` updates the servermap, downloads old bytes with private-key fetch, calls a synchronous modifier, validates bytes-or-None output, publishes changed data, and retries on `UncoordinatedWriteError` through `BackoffAgent`. `update` handles MDMF partial updates: SDMF falls back to full modify/re-encode; MDMF calculates affected segments, updates the servermap over that range, decodes needed old edge segments via `Retrieve.decode`, builds a `TransformingUploadable`, and calls `Publish.update`.

### State and Persistence Behavior
`MutableFileNode` stores authority and learned state: `_uri`, `_writekey`, `_readkey`, `_storage_index`, `_fingerprint`, `_pubkey`, `_privkey`, `_encprivkey`, encoding parameters, `_most_recent_size`, `_protocol_version`, `_downloader_hints`, and a serializer Deferred. Persistent data is created or changed only through `Publish`, storage server mutable slots, and repair paths. Lease/write secrets are derived per server from the node secret holder and storage index. `MutableFileVersion` stores the servermap and immutable version tuple it was built for, plus optional write authority.

### Dependencies and Integration Points
This module is the integration point between URI/capability classes, mutable key derivation, `ServerMap`/`ServermapUpdater`, `Retrieve`, `Publish`, checker/repairer classes, Twisted Deferreds/reactor, Foolscap `eventually`, consumer utilities, and history/status notifications. `nodemaker.py` constructs mutable file nodes, `dirnode.py` uses mutable files as backing stores for directories, and web/client APIs expose these operations.

### Risks and Edge Cases
Serialization is central: callbacks passed to `_do_serialized` must not invoke serialized methods on the same node/version or they can deadlock. `MutableFileVersion._did_upload` sets `_most_recent_size` on the version object, not the node, which is local status only. `is_allowed_in_immutable_directory` returns false for mutable URIs, enforcing deep-immutable constraints. `modify` requires a synchronous, idempotent modifier because it may run repeatedly. Retry behavior gives up after four attempts. MDMF partial update logic has segment-boundary and power-of-two cases and falls back to full re-encode for SDMF. Read-only nodes cannot produce writeable versions or repair caps.

### Test Signals
`test/mutable/test_filenode.py` covers SDMF/MDMF creation, caps, single-share and max-share cases, downloads, readonly/writecap behavior, and keypair creation. `test/mutable/test_update.py` covers append, replacement, zero-length writes, segment-boundary fenceposts, extension, and re-encode cases. Additional mutable tests cover multiple versions, encoding variations, repair, round trip, interoperability, data/file handles, and write-collision behavior. `test_dirnode.py` uses mutable files for directory mutation and uncoordinated write retry scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/filenode.py -->
