<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_quota.h

Purpose: Declares the RGW quota service wrapper around zone period quota configuration.

Important APIs, types, and functions: `RGWSI_Quota` derives from `RGWServiceInstance`, stores an `RGWSI_Zone*`, and exposes `init()`, `get_bucket_quota()`, and `get_user_quota()`.

Control flow: The service is initialized with zone dependency and then read by quota enforcement paths.

State and persistence: No owned persistent state. It exposes references into zone current period config.

Dependencies and integration points: Depends on RGW service base and zone service.

Risks and test signals: Null `zone_svc` before `init()` is the main local risk. Compile and service-graph tests should catch dependency wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.h -->
