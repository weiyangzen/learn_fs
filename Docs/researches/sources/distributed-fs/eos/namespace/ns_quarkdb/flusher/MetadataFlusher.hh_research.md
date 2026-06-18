## sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.hh

Purpose: Declares the metadata flusher facade used by QuarkDB namespace components to enqueue Redis-style mutations without blocking hot paths on network round trips.

Important APIs and types: `ItemIndex` identifies background queue entries. `MetadataFlusher` constructors configure queue path, QuarkDB contact details, and optional flusher type/RocksDB options. `exec()` is a variadic request builder; explicit helpers cover common commands; `synchronize()` blocks until an acknowledged queue index; `getPersistencyType()` reports the selected persistent queue. `FlusherNotifier` implements qclient notification callbacks for network and unexpected-response events.

State and integration: the class owns the notifier, background flusher, queue-size monitoring thread, ID string, and cached persistency config. It is injected into accounting services and other metadata writers as a non-owning dependency from their perspective.

Dependencies: namespace metadata interfaces for context, QuarkDB constants, qclient background flusher/persistency abstractions, and standard containers.

Risks and test signals: `exec(const Args... args)` requires arguments convertible to `std::string` and copies them into a vector. Consumers should not assume immediate visibility after helper calls. Tests should validate notifier dispatch, request construction, lifecycle synchronization, and behavior when a custom flusher type is configured.
