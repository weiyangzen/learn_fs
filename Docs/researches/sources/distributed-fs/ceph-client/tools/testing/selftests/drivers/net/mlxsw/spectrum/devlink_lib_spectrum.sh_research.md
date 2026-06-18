<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_lib_spectrum.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_lib_spectrum.sh

Purpose: Spectrum-1 devlink KVD resource helper library used by resource profile and scale tests.

Important functions/APIs: sources forwarding `devlink_lib.sh` and `../mlxsw_lib.sh`; gates with `mlxsw_only_on_spectrum 1`; defines `KVD_DEFAULTS`, `KVD_CHILDREN`, `KVDL_CHILDREN`, `KVD_PROFILES`; functions `devlink_sp_resource_minimize`, `devlink_sp_size_kvd_to_default`, `devlink_sp_read_kvd_defaults`, and `devlink_sp_resource_kvd_profile_set`.

Control flow: defaults are read into an associative array, resource partitions can be minimized, restored to defaults, or set to predefined `default`, `scale`, and `ipv4_max` profiles followed by `devlink_reload` when needed.

State/dependencies: persistently changes devlink resource sizes and reloads the device. Requires jq and Spectrum-1 resource tree names. Risks include leaving non-default resource partitions if callers skip restore, hard-coded sizes becoming stale, and reload disruption to active tests. Test signals are normally produced by callers through successful resource set/reload and cleanup restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_lib_spectrum.sh -->
