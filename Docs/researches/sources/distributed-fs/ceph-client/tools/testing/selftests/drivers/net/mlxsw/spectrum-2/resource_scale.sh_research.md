<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/resource_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/resource_scale.sh

Purpose: Spectrum-2 aggregate scale runner that executes multiple resource exhaustion tests under current Spectrum-2 resource layout.

Important functions/APIs: sources forwarding `lib.sh`, `tc_common.sh`, `devlink_lib.sh`, and `../mlxsw_lib.sh`; gates with `mlxsw_only_on_spectrum 2+`; uses dynamic test modules `router_scale.sh`, `tc_flower_scale.sh`, `mirror_gre_scale.sh`, `tc_police_scale.sh`, `port_scale.sh`, `rif_mac_profile_scale.sh`, `rif_counter_scale.sh`, and `port_range_scale.sh`. Per-test hooks are `${name}_get_target`, `${name}_setup_prepare`, `${name}_test`, optional `${name}_traffic_test`, and `${name}_cleanup`.

Control flow: iterates selected `TESTS` or `ALL_TESTS`, sources each module, computes required netif count, runs normal-capacity and overflow-capacity passes, waits for setup, recomputes target after setup, logs scale/overflow, cleans up, and reloads devlink after each pass to avoid router aborts.

State/dependencies: highly stateful across devlink resources, tc filters, routing tables, and hardware tables. Cleanup dispatch is based on `current_test`; devlink reload is a persistence boundary. Risks include source-time namespace collisions, incomplete cleanup on sourced-module failures, long runtimes, and capacity changes from occupancy. Test signals are per-resource scale logs, overflow rejection logs, optional traffic checks, and final `RET_FIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/resource_scale.sh -->
