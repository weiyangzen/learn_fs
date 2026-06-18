# sources/distributed-fs/ceph/src/rgw/rgw_basic_types.h

Purpose: declares foundational RGW types shared across RGW, cls, and other Ceph components. The header warns against RGW-only dependencies because these serialized types cross subsystem boundaries.

Important APIs/types/functions: `RGWIntentEvent`, `rgw_err`, `rgw_zone_id`, `rgw::auth::Principal`, JSON/XML declarations for `rgw_user`, `rgw_zone_id`, pools, placement, and access keys, plus `RGWUploadPartInfo`. `Principal` has factory methods for wildcard, user, role, account, OIDC provider, assumed role, and service principals. `RGWUploadPartInfo` records multipart part number, size, accounted size, etag, modification time, manifest, compression info, optional checksum, and old prefixes for cleanup.

Control flow: most functions are inline serialization, comparison, and accessors. `RGWUploadPartInfo::decode()` handles legacy structure versions: manifest appears at v3, compression/accounted size at v4, old prefixes at v5, checksum at v6.

State/persistence: `rgw_zone_id` and `RGWUploadPartInfo` are buffer-encoded persisted data. `Principal` is in-memory identity matching data. Multipart uploads persist manifests, compression info, and checksums through this type.

Dependencies/integration: pulls in pool/user/bucket/object/checksum/compression types and the RADOS object manifest. Used by IAM/auth, bucket/object metadata, multipart upload completion, and JSON/admin surfaces.

Risks: adding dependencies here can break non-RGW build contexts. Changing encode versions or defaults can corrupt old multipart upload decode. `Principal::operator==` compares only type and `rgw_user`, so OIDC provider/service-specific fields are not part of equality.

Test signals: serialization compatibility for `rgw_zone_id` and all `RGWUploadPartInfo` versions, multipart checksum persistence, `Principal` comparisons/rendering, and `rgw_err` clear/error behavior.
