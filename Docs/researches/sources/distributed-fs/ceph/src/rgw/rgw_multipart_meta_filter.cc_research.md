## sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.cc

Purpose: implements recognition of multipart metadata object names and extracts the base key used for bucket index shard calculation.

Important APIs/functions: `MP_META_SUFFIX` is `.meta`; `MultipartMetaFilter(const std::string& name, std::string& key)` returns true if the name ends with `.meta` and has a preceding dot separator, then sets `key` to the prefix before that separator.

Control flow: checks minimum length, searches for the suffix exactly at the end, finds the previous dot before the suffix, and extracts `name.substr(0, pos)`.

State and persistence: stateless string utility. It affects how multipart metadata entries are interpreted in bucket indexes.

Dependencies/integration: used by bucket index/listing code that needs to treat multipart metadata objects specially.

Risks and test signals: names with dots near the suffix and malformed upload-id forms need coverage. Function only checks suffix/separator, not upload id prefix, so callers must understand its permissive behavior.
