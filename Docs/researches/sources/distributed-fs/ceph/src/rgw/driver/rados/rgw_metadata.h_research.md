# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.h

## Purpose
Defines RGW's metadata abstraction layer. Metadata handlers expose typed get/put/remove/mutate/list behavior for sections such as users, buckets, and OTP, while `RGWMetadataManager` dispatches string metadata keys to the right handler and provides common JSON/log/list operations.

## Important APIs And Types
`RGWMetadataObject` stores an object version, mtime, optional attr map pointer, and a virtual formatter hook. `RGWMetadataHandler` is the plugin interface: type name, JSON object construction, `get`, `put`, `remove`, transactional `mutate`, listing lifecycle, marker retrieval, shard selection, and manager attachment. `RGWMetadataManager` owns registered handlers plus a top handler and provides high-level `get()`, `put()`, `remove()`, `mutate()`, `list_keys_*()`, `dump_log_entry()`, `get_sections()`, `parse_metadata_key()`, and `get_shard_id()`.

The free `rgw_shard_name()` functions are declared here for shared shard naming. `RGWMDLogSyncType` and `RGWMDLogStatus` appear in handler methods to connect metadata writes with mdlog replication status.

## Control Flow And State
Callers pass keys shaped as metadata section plus entry. The manager parses the key, finds a handler, and delegates the operation. Handlers are responsible for persisting their own typed data, maintaining object version trackers, and completing mdlog entries when appropriate. Listing uses opaque handler-owned handles so each metadata section can list from its backing store.

## Dependencies And Integration Points
The header pulls in common RGW types, period history, mdlog types, cls version/log types, and SAL forward declarations. Concrete handlers in other files, including OTP in this subset, implement this interface and attach to the manager. Admin metadata APIs and multisite sync logic rely on the common manager dispatch semantics.

## Risks And Test Signals
The manager stores raw handler pointers, so ownership/lifetime is external except for its top handler. `RGWMetadataObject::pattrs` is a borrowed pointer. Handler `mutate()` callbacks must preserve version and mdlog semantics. Tests should exercise key parsing, unknown section errors, handler registration, list marker propagation, version conflict handling, and handler-specific mdlog completion behavior.
