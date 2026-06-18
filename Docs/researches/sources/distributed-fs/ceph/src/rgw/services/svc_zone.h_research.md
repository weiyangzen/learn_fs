<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_zone.h

Purpose: Declares RGW's central zone/period configuration service.

Important APIs, types, and functions: `RGWSI_Zone` derives from `RGWServiceInstance`, stores sysobj/RADOS/sync/bucket-sync dependencies, realm/zonegroup/zone/zone_params/current_period objects, zone ids, capability flags, sync policy handlers, REST connection maps, zone indexes, sync policy, config store, and site config. Public API exposes configuration accessors, sync policy handler lookup, zone id/name helpers, sync/write/logging capability queries, connection maps, placement selection, and metadata listing.

Control flow: The service is initialized by the service graph, started early, and then queried by nearly every other RGW service for pool locations, sync relationships, placement decisions, and remote REST connections.

State and persistence: In-memory loaded site/period configuration and connection maps are declared here. Persistent state lives in RGW zone/period system objects and config store.

Dependencies and integration points: Depends on RGW service base, sysobj, sync modules, bucket sync, realm/zone/period types, sync policy info, REST connections, and SAL config store.

Risks and test signals: Raw pointer ownership makes startup/shutdown paths important. Tests should verify getters are valid after start, connection maps are stable, and absent optional realm/period cases behave correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone.h -->
