## sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.h

Purpose: documents and declares the multipart metadata object-name filter.

Important APIs/types: external `MP_META_SUFFIX` and `MultipartMetaFilter(name, key)`.

Control flow: caller passes a bucket-index object name; on true, `key` receives the user object key to use for bucket index sharding.

State and persistence: no state. The result influences placement/index behavior for multipart metadata objects.

Dependencies/integration: only includes `<string>`, making it lightweight for bucket-index users.

Risks and test signals: comments describe names adorned with upload id and suffix, but implementation is suffix/separator based. Tests should verify examples with object keys containing dots, no prefix, no suffix, and suffix-only names.
