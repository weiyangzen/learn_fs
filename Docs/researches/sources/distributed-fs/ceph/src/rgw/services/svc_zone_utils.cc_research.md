<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.cc

Purpose: Implements utility functions for RGW host ids, unique ids, and Swift-compatible transaction ids.

Important APIs, types, and functions: `do_start()` initializes transaction id suffix dependencies. `gen_host_id()` returns `<rados instance>-<zone name>-<zonegroup name>`. `unique_id()` returns `<zone id>.<rados instance>.<unique_num>`. `init_unique_trans_id_deps()` URL-encodes a suffix of instance id and zone name. `unique_trans_id()` formats `tx%021llx-%010llx` from a unique number and current timestamp and appends the suffix.

Control flow: Startup precomputes suffix. Runtime calls format identifiers using RADOS instance id and zone service config.

State and persistence: Only `trans_id_suffix` is stored in memory. No persistent state is modified.

Dependencies and integration points: Depends on RADOS instance id, `RGWSI_Zone`, `url_encode()`, fmt formatting, and Swift API transaction id compatibility requirements.

Risks and test signals: Uses `time(NULL)` and caller-supplied uniqueness, so uniqueness depends on the caller's counter. Tests should verify transaction id format, URL-encoded suffix, and stability across zone names with special characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.cc -->
