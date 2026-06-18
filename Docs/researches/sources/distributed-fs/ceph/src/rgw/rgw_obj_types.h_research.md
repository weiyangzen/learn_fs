## sources/distributed-fs/ceph/src/rgw/rgw_obj_types.h

Purpose: defines fundamental serialized RGW object key and object-location types shared by RGW and lower layers.

Important APIs/types: `rgw_obj_index_key` stores bucket-index key name/instance and comparison/encoding helpers. `rgw_obj_key` stores user-facing name, version instance, and namespace; it parses/serializes raw object ids and index keys, handles namespace escaping, null-instance behavior, and object locator compatibility. `rgw_raw_obj` stores pool, oid, locator, and legacy decode from old `rgw_obj` encodings. `rgw_obj` combines bucket and key plus in-memory flags/index hash source and explicit data-pool selection.

Control flow: object names are mangled into RADOS oids with leading underscore namespace syntax and optional `:<instance>` in namespace. Index keys use similar escaping but keep instance separately. Decode paths include legacy compatibility branches for old object encodings.

State and persistence: these types are persisted widely in bucket indexes, manifests, metadata, and logs. `in_extra_data` and `index_hash_source` are in-memory behavior controls; encoded `rgw_obj` version is 6.

Dependencies/integration: intentionally avoids heavy RGW/SAL dependencies; includes pool, bucket, user types, Formatter, and encoding.

Risks and test signals: empty strings are often indexed at `name[0]`, so callers must ensure non-empty names before certain helpers. Namespace parsing, underscore escaping, and legacy decode are high-risk compatibility areas. `generate_test_instances()` and JSON decode/dump declarations support encoding tests; add cases for underscores, namespaces, instances, null instance, malformed raw oid, and legacy versions.
