<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/resource_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/resource_scale.sh

Purpose: Spectrum-1 aggregate resource-scale runner that tests multiple resource consumers across predefined KVD partition profiles.

Important functions/APIs: sources forwarding `lib.sh`, `tc_common.sh`, and `devlink_lib_spectrum.sh`; uses dynamic modules for router, tc flower, mirror GRE, tc police, port, RIF MAC profile, RIF counter, and port range. Relies on per-module hook names matching `${current_test}_*`.

Control flow: reads KVD defaults, installs cleanup restore, iterates tests, then for each KVD profile sets resource sizes and executes success and overflow target runs. It recomputes target after setup, logs normal and overflow tests, optionally runs a traffic test, and calls per-module cleanup.

State/dependencies: very stateful because KVD partitioning and hardware tables are changed across profiles. Cleanup restores KVD defaults. Risks include long runtime, cascading failures from sourced hooks, KVD profile sizes becoming stale, and failure to restore if interrupted outside trap. Test signals are per-profile scale logs, overflow logs, optional traffic logs, and final aggregate status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/resource_scale.sh -->
