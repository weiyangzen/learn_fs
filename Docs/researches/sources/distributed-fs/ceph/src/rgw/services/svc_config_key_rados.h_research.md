<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.h

Purpose: Declares the RADOS-backed implementation of the config-key service.

Important APIs, types, and functions: `RGWSI_ConfigKey_RADOS` derives from `RGWSI_ConfigKey`, owns `maybe_insecure_mon_conn`, `warned_insecure`, and a public `librados::Rados*`. It declares `init()`, `do_start()`, `warn_if_insecure()`, destructor, and override `get()`.

Control flow: `init()` binds RADOS, startup probes connection security, and `get()` performs monitor command reads.

State and persistence: Only in-memory warning and RADOS dependency state is declared here. Config-key values remain in monitor storage.

Dependencies and integration points: Depends on `<atomic>`, RGW service base, the abstract config-key service, and librados.

Risks and test signals: Callers must initialize `rados` before use. Tests should confirm the service can be started in the RGW service graph and that `secure` reads interact with the warning state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.h -->
