# sources/distributed-fs/ceph/src/rgw/rgw_cache_driver.h

Purpose: declares an abstract external cache driver interface and cache object attribute names for RGW cache backends.

Important APIs/types/functions: constants like `RGW_CACHE_ATTR_MTIME`, `EPOCH`, `OBJECT_SIZE`, `ACCOUNTED_SIZE`, `MULTIPART`, `OBJECT_NS`, `BUCKET_NAME`, `VERSION_ID`, `SOURCE_ZONE`, `LOCAL_WEIGHT`, `DELETE_MARKER`, `INVALID`, `DIRTY`, delimiter `CACHE_DELIM`, callback aliases `ObjectDataCallback` and `BlockDataCallback`, `Partition`, and abstract `CacheDriver`.

Control flow: `CacheDriver` implementations must support initialization, sync and async put/get, append/delete/rename, attr get/set/update/delete, single-attr get/set, partition info/free space, and data recovery via callbacks.

State/persistence: concrete implementations persist cached object/block data and attrs outside this header. Attribute names define on-disk or backend metadata contracts.

Dependencies/integration: `rgw_common`, `rgw_aio`, SAL attrs, `DoutPrefixProvider`, `rgw_user`, `rgw_obj_key`, optional yield, and AIO result lists.

Risks: interface has many operations with no default semantics; backend implementations must align attr names and async cost/id behavior. `const::std::string` spelling appears in several pure virtual declarations but is accepted as `const std::string`; style may confuse maintainers.

Test signals: backend conformance for all virtual methods, attr naming compatibility, async get/put completion ordering, recovery callback coverage, partition free-space reporting, and rename/delete edge cases.
