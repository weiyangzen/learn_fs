## sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.cc

Purpose: implements S3 Object Ownership parsing, serialization, XML output, and attr lookup.

Important APIs/functions: `to_string()` formats `ObjectOwnership`; `parse()` accepts `BucketOwnerEnforced`, `BucketOwnerPreferred`, and `ObjectWriter`; `OwnershipControls::decode_xml()` validates `Rule/ObjectOwnership`; `dump_xml()` emits the XML rule; `encode()`/`decode()` persist controls; `get_object_ownership()` reads `RGW_ATTR_OWNERSHIP_CONTROLS` from attrs and defaults to `ObjectWriter`.

Control flow: XML decode requires a `Rule` element and nested `ObjectOwnership`. Attr lookup decodes the binary ownership controls and falls back to backward-compatible `ObjectWriter` on absent or malformed attrs.

State and persistence: persisted as `OwnershipControls` in bucket attrs under `RGW_ATTR_OWNERSHIP_CONTROLS`.

Dependencies/integration: depends on RGW XML/common attr names and SAL attr map. Used by S3 bucket ownership controls APIs and request authorization/object ownership decisions.

Risks and test signals: fallback on decode error masks corrupted attrs but preserves availability. Tests should cover all valid values, invalid error message, missing XML elements, attr absence, malformed bufferlist fallback, and XML dump shape.
