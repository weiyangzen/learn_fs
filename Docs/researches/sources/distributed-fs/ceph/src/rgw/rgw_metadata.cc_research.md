## sources/distributed-fs/ceph/src/rgw/rgw_metadata.cc

Purpose: implements generic RGW metadata object/log serialization helpers and the `RGWMetadataManager` dispatch layer over typed metadata handlers.

Important APIs/functions: `LogStatusDump::dump()` maps mdlog statuses to strings. `RGWMetadataLogData` encodes read/write versions and status. `RGWMetadataTopHandler` lists registered metadata sections. `RGWMetadataManager` registers handlers, parses metadata keys, finds handlers, and exposes `get()`, `put()`, `remove()`, `mutate()`, shard lookup, list-keys iteration, log-entry dumping, and section listing.

Control flow: metadata keys split on the first `:` into type and entry. Empty type dispatches to the top handler for listing sections. `get()` calls handler `get()` then emits a JSON `metadata_info` envelope with key/version/mtime/data. `put()` parses an incoming JSON envelope, builds the typed `RGWMetadataObject` through the handler, then calls handler `put()` with version tracking and sync options. `remove()` reads current version then calls handler removal.

State and persistence: manager state is a map of type string to handler pointer. Persistent metadata lives behind handlers, usually in RADOS/config stores. Log data persists as encoded `RGWMetadataLogData`.

Dependencies/integration: depends on RADOS metadata/mdlog headers, `RGWMetadataHandler`, `RGWObjVersionTracker`, JSON parser/decoder, and cls log entries.

Risks and test signals: manager does not own registered handlers, so lifetime is external. JSON envelope parsing is strict and returns `-EINVAL` on missing data/version. Tests should cover duplicate handler registration, unknown type, section listing, get/put/remove/mutate dispatch, version propagation, malformed JSON, and mdlog dump decode failure tolerance.
