<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower.sh

Purpose: comprehensive Spectrum-2 ACL TC flower test for A-TCAM, C-TCAM, eRP state machine, delta masks, Bloom filter behavior, rehash/migration, and resource limits.

Important functions/APIs: topology helpers `h1_create`, `h2_create`, `setup_prepare`, `cleanup`; perf helpers `tp_record`, `tp_record_all`, `tp_check_hits`, `tp_check_hits_any`; tests `single_mask_test`, `identical_filters_test`, `two_masks_test`, `multiple_masks_test`, `ctcam_edge_cases_test`, `delta_simple_test`, `delta_two_masks_one_key_test`, `delta_simple_rehash_test`, `bloom_simple_test`, `bloom_complex_test`, `bloom_delta_test`, `max_erp_entries_test`, `max_group_size_test`, and `collision_test`. It uses `tc filter flower`, `tc chain`, `devlink dev param acl_region_rehash_interval`, perf tracepoints (`mlxsw:*`, `objagg:*`), and `tc_check_packets`.

Control flow: first runs with `tcflags=skip_hw` to validate software-visible semantics, then if `tc_offload_check` passes, reruns with `skip_sw` for hardware offload. Tests add/delete filters in controlled orders, send crafted packets with mausezahn, inspect packet counters, and use tracepoint hit counts for internal TCAM/eRP transitions.

State/dependencies: modifies tc filters, chains, devlink runtime params, and perf data. Cleanup removes qdisc and VRF, but interrupted tests may leave ACL state. Risks include perf tracepoint availability, timing of rehash traces, high scale loops, and source code containing additional helper tests not listed in `ALL_TESTS` (`delta_simple_ipv6_rehash_test`, `delta_massive_ipv6_rehash_test`). Test signals are packet counter correctness, expected tracepoint hits/non-hits, insertion failure at limits, and final offload-check rerun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower.sh -->
