<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_quota.cc

Purpose: Implements accessors for current period bucket and user quota configuration.

Important APIs, types, and functions: `get_bucket_quota()` returns `zone_svc->get_current_period().get_config().quota.bucket_quota`. `get_user_quota()` returns the corresponding user quota.

Control flow: Callers initialize the service with a zone service and then read immutable references to quota config from the current period.

State and persistence: No persistence is owned here; quota data comes from the current period configuration maintained by the zone service.

Dependencies and integration points: Depends on `RGWSI_Zone` and `RGWQuotaInfo`. Bucket/user operation code can use this service to apply period-wide defaults.

Risks and test signals: References become invalid if the underlying period object lifetime changes unexpectedly. Tests should verify quota values reflect period config and service order initializes zone before quota use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.cc -->
