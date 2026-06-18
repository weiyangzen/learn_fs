<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh

Purpose: Spectrum-1 devlink KVD resource partition selftest for profiles, minimum sizing, and maximum/overflow rejection.

Important functions/APIs: sources forwarding `lib.sh` and `devlink_lib_spectrum.sh`; defines `setup_prepare`, `cleanup`, `profiles_test`, `resources_min_test`, and `resources_max_test`.

Control flow: reads KVD defaults, installs cleanup restore, tests each named profile, then minimizes each child resource and reloads, then computes per-child maximum by subtracting other children minima, tests almost-max, overflow rejection, and max sizing where supported.

State/dependencies: persistently changes hardware resource partitions and reloads the device repeatedly. Cleanup restores defaults. Risks include skipped exact max for hash resources due known issue, arithmetic tied to resource tree schema, and disruptive reloads. Test signals are `log_test` entries for each profile, min, almost-max, overflow rejection, and max case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh -->
