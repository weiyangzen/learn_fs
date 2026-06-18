<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_tier_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_tier_rados.h

Purpose: Declares small RADOS tier helpers for multipart object naming and raw-object-to-RGW-object conversion.

Important APIs, types, and functions: `RGWMPObj` builds multipart meta object names and part object names from object id and upload id, parses meta names with `from_meta()`, exposes `get_meta()`, `get_part()`, `get_upload_id()`, `get_key()`, `clear()`, and stream output. `RGWSI_Tier_RADOS` stores a zone pointer and exposes static `raw_obj_to_obj()` for converting raw object oids back to `rgw_obj`.

Control flow: Multipart code initializes name components with `<oid>.<upload_id>.meta` and part prefixes. `raw_obj_to_obj()` finds an underscore after the bucket marker and parses the suffix as a raw object key.

State and persistence: `RGWMPObj` stores only derived strings. The object names refer to persisted RADOS multipart metadata and part objects elsewhere.

Dependencies and integration points: Depends on multipart meta suffix definitions, RGW service base, `rgw_bucket`, `rgw_raw_obj`, and `rgw_obj_key` parsing. Used by RADOS tier/object listing code.

Risks and test signals: `from_meta()` uses `int` positions from `rfind()` results, so malformed names must be tested. `raw_obj_to_obj()` depends on marker placement and raw oid format. Tests should cover multipart naming round trips, optional upload id parsing, malformed meta names, and bucket marker conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_tier_rados.h -->
