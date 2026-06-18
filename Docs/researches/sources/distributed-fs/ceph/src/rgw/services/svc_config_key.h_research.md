<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_config_key.h

Purpose: Defines the abstract RGW service interface for reading monitor config-key values.

Important APIs, types, and functions: `RGWSI_ConfigKey` derives from `RGWServiceInstance` and declares pure virtual `get(const std::string& key, bool secure, bufferlist *result)`.

Control flow: Concrete backends implement `get()`; callers pass `secure=true` when the fetched value is sensitive and should trigger transport security checks or warnings.

State and persistence: This interface has no state beyond RGW service lifetime. Config-key values are persisted by the Ceph monitor config-key store.

Dependencies and integration points: Depends on RGW service base and Ceph `bufferlist`. The RADOS implementation uses monitor commands.

Risks and test signals: The key contract is intentionally minimal, so backend behavior around secure reads is important. Tests should mock or run a monitor command path and confirm errors and sensitive-key warnings are surfaced by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key.h -->
