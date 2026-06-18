<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.h

Purpose: Declares zone utility service for generating identifiers.

Important APIs, types, and functions: `RGWSI_ZoneUtils` derives from `RGWServiceInstance`, stores RADOS and zone pointers plus `trans_id_suffix`, and declares `gen_host_id()`, `unique_id()`, and `unique_trans_id()`.

Control flow: Service graph initializes RADOS/zone dependencies, startup computes suffix, and request paths use the generated ids.

State and persistence: In-memory suffix only; no persistence.

Dependencies and integration points: Depends on RGW service base, RADOS pointer, and zone service.

Risks and test signals: Null dependencies before startup are the main local risk. Unit tests can validate formatting against fixed fake instance/zone data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.h -->
