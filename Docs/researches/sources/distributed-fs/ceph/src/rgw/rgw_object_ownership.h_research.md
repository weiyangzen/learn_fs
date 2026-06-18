## sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.h

Purpose: declares S3 Object Ownership configuration types and helpers.

Important APIs/types: `enum class ObjectOwnership` contains `BucketOwnerEnforced`, `BucketOwnerPreferred`, and `ObjectWriter`. `OwnershipControls` stores `object_ownership` and supports XML decode/dump. Free functions handle string conversion, parsing, binary encode/decode, and attr lookup.

Control flow: API handlers parse XML into `OwnershipControls`, persist encoded attrs, and later retrieve ownership mode through `get_object_ownership()`.

State and persistence: default ownership is `ObjectWriter`; encoded controls are stored in RGW bucket attrs.

Dependencies/integration: forward declares XML/Formatter and SAL attrs, and includes Ceph encoding.

Risks and test signals: enum class is encoded directly; compatibility depends on stable enum ordering. Tests should include binary round trips and default behavior when attrs are missing.
