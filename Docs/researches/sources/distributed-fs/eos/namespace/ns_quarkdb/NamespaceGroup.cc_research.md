# sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.cc

Purpose: implements `QuarkNamespaceGroup`, the lifecycle and dependency owner for the QuarkDB namespace plugin.

Important APIs/types/functions: constructor creates a 48-thread `folly::IOThreadPoolExecutor`. `initialize` parses config keys, creates performance monitor, validates QuarkDB version, and records flusher options. Getter methods lazily create file/container services, hierarchical view, filesystem view, accounting views, quota stats, flushers, qclient, executor, cache refresh listener, and performance monitor.

Control flow: initialization requires `queue_path`, `qdb_cluster`, `qdb_flusher_md`, and `qdb_flusher_quota`, optionally reads `qdb_password`, `qclient_flusher_type`, and `qclient_rocksdb_options`, then calls `enforceQuarkDBVersion(getQClient())`. Lazy getters lock a recursive mutex and construct dependencies in dependency order. Destructor tears down listener, accounting, views, services, flushers, qclient, executor, and monitor in explicit order.

State and persistence: stores configuration strings, contact details, recursive mutex, executor, flushers, qclient, services, views, accounting listeners, cache listener, and performance monitor. Persistent namespace state is accessed through qclient and flushers, not stored here.

Dependencies and integration: integrates the plugin with `QuarkFileMDSvc`, `QuarkContainerMDSvc`, `QuarkHierarchicalView`, `QuarkFileSystemView`, `QuarkContainerAccounting`, `QuarkSyncTimeAccounting`, `MetadataFlusher`, `CacheRefreshListener`, `QClPerfMonitor`, and version enforcement.

Risks: initialization creates qclient before optional flusher type parsing, so version checks use default contact options. Lazy construction means call ordering matters for listener registration. Executor must outlive qclient, documented by the destructor order. `startCacheRefreshListener` assumes file service and metadata provider are initialized.

Test signals: plugin/namespace integration tests under `ns_quarkdb/tests` exercise service/view creation and end-to-end namespace behavior; configuration errors are visible through `initialize` return values.
