# Research: subset-b-006830

Grouped research for Linux networking selftests under `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net`. Each section is source-tree aligned and bounded by reconciliation markers for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rtnetlink.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rtnetlink.sh

Purpose: broad mlxsw rtnetlink regression suite for interface, bridge, VLAN, LAG, neighbor, nexthop, nexthop-object, locked-port, and devlink reload scenarios. It validates that valid kernel networking configurations succeed, unsupported configurations fail with no driver warnings, and mlxsw RIF/FDB/offload reference state is not leaked.

Important functions/APIs: `setup_prepare`, `cleanup`, and `ALL_TESTS` integrate with forwarding `lib.sh`; `devlink_reload` comes from `devlink_lib.sh`. Test bodies exercise `ip link`, `ip address`, `bridge vlan`, `bridge fdb`, `ip neigh`, `ip nexthop`, route installation, LAG creation, VLAN upper stacking, locked bridge ports, and offload checks through `wait_for_offload`, `busywait`, `check_err`, `check_fail`, and `log_test`.

Control flow: the harness reserves two netifs, brings both ports up, runs each named scenario, and tears the ports down. Tests create temporary bridges, VLAN devices, VRFs, LAGs, nexthops, and routes, then delete or mutate them to trigger previous bug paths such as RIF deletion, duplicate VLAN rejection, nexthop object updates, and devlink reload cleanup.

State/dependencies: persistent state is only kernel networking state; cleanup is local to each test plus global `pre_cleanup`. Requires real mlxsw-capable ports, iproute2 with nexthop support, bridge/vlan/vrf modules, and devlink. Risks are high around incomplete cleanup after failed mid-test mutations, timing of offload indication, and extack/message matching. Test signals are ksft-style `log_test` outcomes and absence of kernel traces or reload failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rtnetlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_ets.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_ets.sh

Purpose: mlxsw driver adapter for the generic ETS qdisc selftest, forcing the tests through offloaded datapath behavior and buffer settings that make DWRR/strict scheduling observable.

Important functions/APIs: sources `sch_ets_core.sh` and `devlink_lib.sh`; overrides `switch_create` and `collect_stats`; calls `bail_on_lldpad` and `ets_run`. It uses `tc qdisc replace ... tbf`, ETS qdisc setup from the common core, and devlink shared-buffer helpers such as `devlink_port_pool_th_set` and `devlink_tc_bind_pool_th_set`.

Control flow: `switch_create` installs a TBF bottleneck on `$swp2`, delegates common ETS topology setup, raises ingress/egress shared-buffer thresholds, and defers restoration. `collect_stats` waits for qdisc counters to update and returns per-stream byte counters for the common ETS runner.

State/dependencies: state is qdisc configuration and devlink shared-buffer thresholds, restored through `defer`. It depends on DCB not being managed by lldpad and on mlxsw's hard-coded 1:1 802.1p priority mapping. Risks include scheduler timing, stale qdisc counters, and environmental DCB daemons. Test signals are ping success, priomap tests, and strict/mixed/DWRR byte distributions from the shared ETS core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_ets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_offload.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_offload.sh

Purpose: validates qdisc offload indication for root and nested qdisc combinations on mlxsw, especially legal and illegal trees involving ETS/PRIO containers, RED/TBF leaves, FIFO leaves, and unsupported DRR.

Important functions/APIs: `check_not_offloaded`, `check_all_offloaded`, `with_ets`, `with_prio`, `with_red`, `with_tbf`, `with_pfifo`, `with_bfifo`, `with_drr`, recursive `with_qdiscs`, `do_test_combinations`, `test_root`, `test_port_tbf`, `test_etsprio`, and `test_etsprio_port_tbf`. It uses `tc qdisc`, `tc q sh ... invisible`, and `qdisc_stats_get`.

Control flow: recursive helpers build temporary qdisc trees, execute either an offload or no-offload checker at the leaf, then unwind by deleting qdiscs. The combinator covers allowed single RED/TBF chains and rejects duplicated RED/TBF or DRR combinations. `test_port_tbf` tests parent offload under a port-level TBF and ETS/PRIO parent.

State/dependencies: only qdisc state on one interface is persistent during each subtest; `cleanup` calls `pre_cleanup`. Requires qdisc JSON/offload visibility from iproute2 and mlxsw qdisc offload support. Risks include fragile parsing of `tc q sh dev ... invisible`, recursive cleanup if a nested creation fails, and evolving offload semantics. Test signals are per-combination `log_test` results and `.offloaded` booleans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_offload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_core.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_core.sh

Purpose: shared RED/WRED/ECN qdisc test core for mlxsw. It builds a multi-port, multi-VLAN topology that can intentionally create controlled backlog on `$swp3`, then supplies helpers for root RED and RED-under-ETS/PRIO tests.

Important functions/APIs: topology helpers `host_create`, `h1_create`, `h2_create`, `h3_create`, `switch_create`, `setup_prepare`, `ping_ipv4`; queue helpers `get_qdisc_handle`, `get_qdisc_backlog`, `get_nmarked`, `build_backlog`, `check_marking`; test helpers `do_ecn_test`, `do_ecn_test_perband`, `do_ecn_nodrop_test`, `do_red_test`, `do_mc_backlog_test`, `do_drop_mirror_test`, `do_drop_trap_test`, and `do_mark_mirror_test`. It depends on forwarding `lib.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, mausezahn, ethtool stats, devlink traps, and tc qevents.

Control flow: setup creates hosts, VLANs 10/11, four bridges, ingress/egress VLAN priority maps, TBF bottlenecks, and adjusted shared-buffer thresholds. Test helpers start baseline TCP/UDP traffic, incrementally inject packets until backlog crosses a target, then verify marking, early drop, qevent mirror/trap counts, or multicast backlog visibility.

State/dependencies: state is extensive but scoped through `defer` plus common cleanup. It requires real hardware timing, working traffic generation, accurate qdisc/ethtool counters, devlink trap counters, and Spectrum-version feature gates. Risks are timing sensitivity, leftover traffic after `kill`, buffer threshold calibration, and false failures from congestion variance. Test signals are backlog thresholds, packet-mark percentages, qdisc packet/mark counters, tc block stats, and devlink trap packet increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_core.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_ets.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_ets.sh

Purpose: RED/WRED test front-end that installs RED leaf qdiscs under an ETS root qdisc, using `sch_red_core.sh` for topology and behavioral checks.

Important functions/APIs: defines `ALL_TESTS`, `QDISC=ets` by default, `install_root_qdisc`, `install_qdisc_tc0`, `install_qdisc_tc1`, `install_qdisc`, uninstall variants, and test wrappers `ecn_test`, `ecn_test_perband`, `ecn_nodrop_test`, `red_test`, `mc_backlog_test`, `red_mirror_test`, `red_trap_test`, `ecn_mirror_test`.

Control flow: installs an ETS root at parent `1:` on `$swp3`, then attaches RED instances to TC0 and TC1 bands with distinct backlog thresholds. Each wrapper defers uninstall and calls common core routines for ECN, RED drop, multicast backlog, and qevent behavior. It blocks execution if lldpad may be managing DCB.

State/dependencies: persistent state is temporary qdisc hierarchy and tc block qevents. It relies on precise per-band mapping from VLAN priority to mlxsw traffic classes. Risks include mis-mapped bands, qdisc counter latency, and qevent support variation. Test signals are per-TC backlog, ECN mark, early drop, mirror, trap, and multicast backlog outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_ets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_prio.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_prio.sh

Purpose: thin wrapper that reruns the ETS RED/WRED suite with a PRIO root qdisc instead of ETS, covering the alternative mlxsw offloaded classful parent.

Important functions/APIs: sets `QDISC=prio` and sources `sch_red_ets.sh`, inheriting all install/uninstall/test routines from that file and all topology helpers from `sch_red_core.sh`.

Control flow: shell variable override occurs before sourcing, so `install_root_qdisc` in the sourced file uses `prio bands 8 priomap ...` while keeping the same RED children and tests.

State/dependencies: no additional state beyond the sourced suite. The main risk is that this wrapper's behavior is implicit and depends on source order. Test signals are identical to `sch_red_ets.sh` but indicate PRIO parent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_prio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_root.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_root.sh

Purpose: RED/ECN/qevent test front-end for a single RED qdisc directly under the shaped root, rather than under ETS/PRIO bands.

Important functions/APIs: sources `sch_red_core.sh`; defines root-level `install_qdisc`, `uninstall_qdisc`, and wrappers for ECN, per-band ECN, ECN nodrop, RED drop, multicast backlog, and early-drop mirror tests.

Control flow: setup is inherited from the core. Each test attaches one RED qdisc to `$swp3 parent 1:` with a fixed backlog threshold, runs the common behavioral helper on VLAN 10, and deletes the qdisc through `defer`.

State/dependencies: qdisc state is narrower than the ETS/PRIO variants. It still depends on core traffic shaping, counters, and shared-buffer setup. Risks include RED threshold rounding and backlog build failures under hardware load. Test signals are ECN marking/non-marking, RED early drop, MC backlog visibility, and qevent mirror packet counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_ets.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_ets.sh

Purpose: mlxsw-specific wrapper for the generic TBF-under-ETS forwarding selftest, forcing offloaded TC setup.

Important functions/APIs: defines `sch_tbf_pre_hook` to reject lldpad-managed DCB, sets `TCFLAGS=skip_sw`, and sources forwarding `sch_tbf_ets.sh`.

Control flow: all topology and tests are delegated to the generic forwarding script after mlxsw-specific pre-hook and tc flag setup. The hook runs before qdisc configuration.

State/dependencies: state and cleanup are owned by the sourced generic test. Depends on mlxsw offload support and a system not controlled by lldpad. Risks are implicit behavior through sourcing and mismatch with generic script changes. Test signals come from the generic TBF ETS suite with `skip_sw` enforcing hardware offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_ets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_prio.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_prio.sh

Purpose: mlxsw-specific wrapper for the generic TBF-under-PRIO selftest.

Important functions/APIs: provides `sch_tbf_pre_hook`, sets `TCFLAGS=skip_sw`, and sources forwarding `sch_tbf_prio.sh`.

Control flow: delegated generic test runs after the hook prevents external DCB ownership conflicts. Hardware-only execution is requested through `skip_sw`.

State/dependencies: no local persistent state; the sourced script owns qdisc and traffic setup. Risks mirror the ETS wrapper: implicit source-time contract and environmental DCB interference. Test signals are generic TBF PRIO assertions executed against mlxsw offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_prio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_root.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_root.sh

Purpose: mlxsw-specific wrapper for the generic root TBF qdisc offload selftest.

Important functions/APIs: defines `sch_tbf_pre_hook`, sets `TCFLAGS=skip_sw`, and sources forwarding `sch_tbf_root.sh`.

Control flow: local code only prepares environment constraints; the sourced generic test creates the root TBF and validates rate behavior/offload.

State/dependencies: qdisc state is managed by the generic test. It depends on mlxsw qdisc offload, iproute2 TBF support, and no lldpad DCB management. Risks are source-order coupling and failures caused by non-test qdisc state. Test signals are generic root TBF pass/fail logs under `skip_sw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer.sh

Purpose: validates devlink shared-buffer occupancy reporting for physical ingress pools/TCs and CPU egress pools/TCs when IP and ARP packets traverse mlxsw.

Important functions/APIs: `h1_create`, `h2_create`, occupancy helpers `sb_occ_pool_check`, `sb_occ_itc_check`, `sb_occ_etc_check`, tests `port_pool_test`, `port_tc_ip_test`, `port_tc_arp_test`, `setup_prepare`, `cleanup`. It uses forwarding `lib.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, `devlink sb occupancy clearmax/snapshot/show`, `devlink_cell_size_get`, tc egress filters, and mausezahn.

Control flow: two ports are initialized with IPs and egress drop filters so generated packets are isolated. Each test clears max occupancy, sends one crafted packet, snapshots occupancy, then checks expected one-cell maximums in specific pools/TCs on the destination or CPU port.

State/dependencies: persistent state is tc clsact filters and devlink SB max occupancy snapshots; cleanup deletes filters and VRFs. It depends on devlink SB support, jq, accurate cell size, and deterministic CPU copy behavior. Risks include noisy background packets, stale occupancy snapshots, and hard-coded TC/pool IDs that are hardware-specific. Test signals are exact occupancy equality and per-case `log_test` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer_configuration.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer_configuration.py

Purpose: Python selftest for mlxsw devlink shared-buffer configuration mutability. It randomly changes pool sizes/types, TC bindings, and port-pool thresholds, verifies only intended objects changed, then restores recorded defaults.

Important classes/APIs: `RandomValuePicker`, `RecordValuePicker`, `CommonItem`, `CommonList`, `Pool`, `TcBind`, `PortPool`, `Port`, and list wrappers. Key functions include `run_cmd`, `run_json_cmd`, `log_test`, `get_pools`, `do_check_pools`, `check_pools`, `get_tcbinds`, `do_check_tcbind`, `check_tcbind`, `get_portpools`, `do_check_portpool`, `check_portpool`, `get_ports`, `get_device`, and `test_sb_configuration`.

Control flow: seed is fixed with `random.seed(0)`, first mlxsw Spectrum devlink device is selected, physical ports and pools are enumerated, then each resource class is randomized and restored. Mutable fields are compared via `var_tuple`, while `weak_eq` ignores variable fields to locate the same object after changes.

State/dependencies: modifies devlink SB configuration in-place, then restores it using recorded values. It depends on `devlink -j`, shell commands via `subprocess.check_output`, JSON schema stability, and Spectrum driver presence. Risks include no `finally` restoration on exception, shell=True command construction, hard-coded immutable pool/TC rules, and Python assertion reliance. Test signals are printed `[ OK ]`/`[FAIL]` lines for object existence, exact value matches, and no collateral configuration changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer_configuration.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/mirror_gre_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/mirror_gre_scale.sh

Purpose: Spectrum-2 resource-scale target provider for the generic mlxsw mirror GRE scale test.

Important functions/APIs: sources `../mirror_gre_scale.sh` and overrides `mirror_gre_get_target`. It queries `devlink_resource_size_get span_agents`.

Control flow: when `should_fail=0`, returns the supported span agent count; when `should_fail=1`, returns one more than capacity so the parent scale harness can assert graceful overflow failure.

State/dependencies: no local state. Depends on the shared scale test contract and devlink resource naming. Risks are stale resource names or capacity affected by prior tests. Test signals are inherited from the sourced mirror GRE scale setup, insertion, overflow, cleanup, and optional traffic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/mirror_gre_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_range_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_range_scale.sh

Purpose: Spectrum-2 target provider for generic port-range register scale testing.

Important functions/APIs: sources `../port_range_scale.sh`; defines `port_range_get_target` using `devlink_resource_size_get port_range_registers`.

Control flow: returns exact capacity for normal scale run and capacity plus one for overflow run.

State/dependencies: stateless wrapper tied to devlink resource availability. Risks are shared occupancy from earlier tests and resource name drift. Test signals are inherited offload counts and overflow rejection from the generic port-range scale test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_range_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_scale.sh

Purpose: Spectrum-2 target provider for physical port scale resource tests.

Important functions/APIs: sources `../port_scale.sh`; defines `port_get_target` from `devlink_resource_size_get physical_ports`.

Control flow: returns physical port resource capacity or capacity plus one depending on overflow mode.

State/dependencies: no local state; depends on shared generic `port_*` hooks. Risks are hotplug/resource differences and prior test occupancy. Test signals come from generic port scale setup and overflow verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/resource_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/resource_scale.sh

Purpose: Spectrum-2 aggregate scale runner that executes multiple resource exhaustion tests under current Spectrum-2 resource layout.

Important functions/APIs: sources forwarding `lib.sh`, `tc_common.sh`, `devlink_lib.sh`, and `../mlxsw_lib.sh`; gates with `mlxsw_only_on_spectrum 2+`; uses dynamic test modules `router_scale.sh`, `tc_flower_scale.sh`, `mirror_gre_scale.sh`, `tc_police_scale.sh`, `port_scale.sh`, `rif_mac_profile_scale.sh`, `rif_counter_scale.sh`, and `port_range_scale.sh`. Per-test hooks are `${name}_get_target`, `${name}_setup_prepare`, `${name}_test`, optional `${name}_traffic_test`, and `${name}_cleanup`.

Control flow: iterates selected `TESTS` or `ALL_TESTS`, sources each module, computes required netif count, runs normal-capacity and overflow-capacity passes, waits for setup, recomputes target after setup, logs scale/overflow, cleans up, and reloads devlink after each pass to avoid router aborts.

State/dependencies: highly stateful across devlink resources, tc filters, routing tables, and hardware tables. Cleanup dispatch is based on `current_test`; devlink reload is a persistence boundary. Risks include source-time namespace collisions, incomplete cleanup on sourced-module failures, long runtimes, and capacity changes from occupancy. Test signals are per-resource scale logs, overflow rejection logs, optional traffic checks, and final `RET_FIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/resource_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_counter_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_counter_scale.sh

Purpose: Spectrum-2 target provider for RIF counter scale testing, selecting the limiting resource between available RIFs and counter slots.

Important functions/APIs: sources `../rif_counter_scale.sh`; defines `rif_counter_get_target`; queries `devlink_resource_size_get rifs`, `devlink_resource_size_get counters rif`, and `devlink_resource_occ_get rifs`.

Control flow: subtracts existing RIF occupancy, divides counter capacity by 20 because ingress and egress counters use 10 KVD slots each, skips overflow if counters exceed RIF capacity, then returns target or target plus one.

State/dependencies: reads but does not locally mutate devlink state. Risks are incorrect accounting if counter slot cost changes, existing RIF occupancy from environment, and overflow skip hiding a class of failures. Test signals are inherited RIF creation/counter attachment and overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_counter_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_mac_profile_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_mac_profile_scale.sh

Purpose: Spectrum-2 target provider for generic RIF MAC profile scale testing.

Important functions/APIs: sources `../rif_mac_profile_scale.sh`; defines `rif_mac_profile_get_target` from `devlink_resource_size_get rif_mac_profiles`.

Control flow: returns capacity for success mode and capacity plus one for overflow mode.

State/dependencies: stateless wrapper. Risks are resource name changes or nonzero occupancy outside the test. Test signals are inherited from RIF MAC profile setup/test/cleanup hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_mac_profile_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/router_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/router_scale.sh

Purpose: Spectrum-2 router scale target provider using total KVD size rather than the Spectrum-1 hash partition.

Important functions/APIs: sources `../router_scale.sh`; defines `router_get_target` using `devlink_resource_size_get kvd`.

Control flow: for normal mode returns 85 percent of KVD capacity to avoid exact-limit instability; for overflow mode returns capacity plus one.

State/dependencies: stateless wrapper for the generic router scale module. Risks include the 85 percent heuristic being too aggressive or too conservative on future resource layouts. Test signals are inherited route programming/offload and overflow rejection checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/router_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower.sh

Purpose: comprehensive Spectrum-2 ACL TC flower test for A-TCAM, C-TCAM, eRP state machine, delta masks, Bloom filter behavior, rehash/migration, and resource limits.

Important functions/APIs: topology helpers `h1_create`, `h2_create`, `setup_prepare`, `cleanup`; perf helpers `tp_record`, `tp_record_all`, `tp_check_hits`, `tp_check_hits_any`; tests `single_mask_test`, `identical_filters_test`, `two_masks_test`, `multiple_masks_test`, `ctcam_edge_cases_test`, `delta_simple_test`, `delta_two_masks_one_key_test`, `delta_simple_rehash_test`, `bloom_simple_test`, `bloom_complex_test`, `bloom_delta_test`, `max_erp_entries_test`, `max_group_size_test`, and `collision_test`. It uses `tc filter flower`, `tc chain`, `devlink dev param acl_region_rehash_interval`, perf tracepoints (`mlxsw:*`, `objagg:*`), and `tc_check_packets`.

Control flow: first runs with `tcflags=skip_hw` to validate software-visible semantics, then if `tc_offload_check` passes, reruns with `skip_sw` for hardware offload. Tests add/delete filters in controlled orders, send crafted packets with mausezahn, inspect packet counters, and use tracepoint hit counts for internal TCAM/eRP transitions.

State/dependencies: modifies tc filters, chains, devlink runtime params, and perf data. Cleanup removes qdisc and VRF, but interrupted tests may leave ACL state. Risks include perf tracepoint availability, timing of rehash traces, high scale loops, and source code containing additional helper tests not listed in `ALL_TESTS` (`delta_simple_ipv6_rehash_test`, `delta_massive_ipv6_rehash_test`). Test signals are packet counter correctness, expected tracepoint hits/non-hits, insertion failure at limits, and final offload-check rerun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower_scale.sh

Purpose: Spectrum-2 target provider for generic flower rule scale testing, bounded by available flow counters.

Important functions/APIs: sources `../tc_flower_scale.sh`; defines `tc_flower_get_target`; queries `devlink_resource_size_get counters flow` and `devlink_resource_occ_get counters flow`.

Control flow: subtracts existing flow counter occupancy, divides by two because each rule uses packet and byte counters, then returns target or target plus one for overflow.

State/dependencies: reads devlink counter state. Risks are counter accounting changes, background counter occupancy, and overflow target exceeding other resources first. Test signals are inherited batch insertion, `in_hw` counts, and traffic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_police_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_police_scale.sh

Purpose: Spectrum-2 target provider for generic tc police scale testing.

Important functions/APIs: sources `../tc_police_scale.sh`; defines `tc_police_get_target` from `devlink_resource_size_get global_policers single_rate_policers`.

Control flow: returns exact policer capacity for normal mode and capacity plus one for overflow mode.

State/dependencies: stateless except for devlink resource reads. Risks include shared policer occupancy and resource naming changes. Test signals are inherited police rule offload count and overflow failure checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_police_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/vxlan_flooding_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/vxlan_flooding_ipv6.sh

Purpose: Spectrum-2 IPv6 VXLAN flooding test for flood record linked-list handling where each record stores four remote VTEP IPv6 addresses.

Important functions/APIs: topology helpers `h1_create`, `switch_create`, `router1_create`, `router2_create`, `setup_prepare`, `cleanup`; flooding helpers `flooding_remotes_add`, `flooding_filters_add`, `flooding_filters_del`, `flooding_check_packets`, and `flooding_test`. It uses bridge FDB append/delete on `vxlan0`, IPv6 routes, tc flower counters on `$rp2`, and mausezahn.

Control flow: creates a bridge with `vxlan0`, local loopback VTEP address, underlay routing, and 16 remote flood entries. It sends BUM traffic, then deletes middle, first, last, and single entries while expected packet-count arrays track which remotes should receive each flood.

State/dependencies: state includes bridge/VXLAN devices, loopback IPv6 address, route, tc qdiscs/filters, and FDB flood entries. Risks include cleanup after partial FDB deletion, tc counter noise, and exact record-size assumptions tied to Spectrum-2. Test signals are tc packet counters for each remote after every deletion stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/vxlan_flooding_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_lib_spectrum.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_lib_spectrum.sh

Purpose: Spectrum-1 devlink KVD resource helper library used by resource profile and scale tests.

Important functions/APIs: sources forwarding `devlink_lib.sh` and `../mlxsw_lib.sh`; gates with `mlxsw_only_on_spectrum 1`; defines `KVD_DEFAULTS`, `KVD_CHILDREN`, `KVDL_CHILDREN`, `KVD_PROFILES`; functions `devlink_sp_resource_minimize`, `devlink_sp_size_kvd_to_default`, `devlink_sp_read_kvd_defaults`, and `devlink_sp_resource_kvd_profile_set`.

Control flow: defaults are read into an associative array, resource partitions can be minimized, restored to defaults, or set to predefined `default`, `scale`, and `ipv4_max` profiles followed by `devlink_reload` when needed.

State/dependencies: persistently changes devlink resource sizes and reloads the device. Requires jq and Spectrum-1 resource tree names. Risks include leaving non-default resource partitions if callers skip restore, hard-coded sizes becoming stale, and reload disruption to active tests. Test signals are normally produced by callers through successful resource set/reload and cleanup restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_lib_spectrum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh

Purpose: Spectrum-1 devlink KVD resource partition selftest for profiles, minimum sizing, and maximum/overflow rejection.

Important functions/APIs: sources forwarding `lib.sh` and `devlink_lib_spectrum.sh`; defines `setup_prepare`, `cleanup`, `profiles_test`, `resources_min_test`, and `resources_max_test`.

Control flow: reads KVD defaults, installs cleanup restore, tests each named profile, then minimizes each child resource and reloads, then computes per-child maximum by subtracting other children minima, tests almost-max, overflow rejection, and max sizing where supported.

State/dependencies: persistently changes hardware resource partitions and reloads the device repeatedly. Cleanup restores defaults. Risks include skipped exact max for hash resources due known issue, arithmetic tied to resource tree schema, and disruptive reloads. Test signals are `log_test` entries for each profile, min, almost-max, overflow rejection, and max case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/mirror_gre_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/mirror_gre_scale.sh

Purpose: Spectrum-1 target provider for generic mirror GRE scale testing.

Important functions/APIs: sources `../mirror_gre_scale.sh`; defines `mirror_gre_get_target` from `devlink_resource_size_get span_agents`.

Control flow: normal mode returns span-agent capacity; overflow mode returns capacity plus one.

State/dependencies: stateless wrapper around generic scale hooks. Risks are resource capacity altered by KVD profile or prior tests. Test signals are inherited mirror GRE creation/offload/overflow checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/mirror_gre_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_range_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_range_scale.sh

Purpose: Spectrum-1 target provider for generic port range register scale testing.

Important functions/APIs: sources `../port_range_scale.sh`; defines `port_range_get_target` using `devlink_resource_size_get port_range_registers`.

Control flow: returns capacity or capacity plus one for overflow.

State/dependencies: stateless except devlink reads. Risks are occupancy/resource layout changes under different KVD profiles. Test signals are inherited from generic port range scale checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_range_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_scale.sh

Purpose: Spectrum-1 target provider for physical port scale tests.

Important functions/APIs: sources `../port_scale.sh`; defines `port_get_target` from `devlink_resource_size_get physical_ports`.

Control flow: returns exact capacity or capacity plus one for overflow.

State/dependencies: no local state. Risks are hardware-specific port resource reporting and prior occupancy. Test signals are inherited physical port scale/overflow outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/q_in_vni_veto.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/q_in_vni_veto.sh

Purpose: Spectrum-1-specific negative test that verifies VXLAN cannot be configured on top of an 802.1ad VLAN-aware bridge in a way unsupported by mlxsw.

Important functions/APIs: uses forwarding `lib.sh`; defines `setup_prepare`, `cleanup`, and `create_vxlan_on_top_of_8021ad_bridge`. It uses `ip link` bridge/VXLAN setup and `bridge vlan add`.

Control flow: creates an 802.1ad bridge and VXLAN device, enslaves a physical port and VXLAN, then expects `bridge vlan add ... pvid untagged` on the VXLAN to fail and include `mlxsw_spectrum` extack text.

State/dependencies: temporary bridge, VXLAN, and port master state. Risks include extack wording changes, Spectrum-version applicability, and cleanup after failure. Test signals are failure of unsupported VLAN mapping plus extack presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/q_in_vni_veto.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/resource_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/resource_scale.sh

Purpose: Spectrum-1 aggregate resource-scale runner that tests multiple resource consumers across predefined KVD partition profiles.

Important functions/APIs: sources forwarding `lib.sh`, `tc_common.sh`, and `devlink_lib_spectrum.sh`; uses dynamic modules for router, tc flower, mirror GRE, tc police, port, RIF MAC profile, RIF counter, and port range. Relies on per-module hook names matching `${current_test}_*`.

Control flow: reads KVD defaults, installs cleanup restore, iterates tests, then for each KVD profile sets resource sizes and executes success and overflow target runs. It recomputes target after setup, logs normal and overflow tests, optionally runs a traffic test, and calls per-module cleanup.

State/dependencies: very stateful because KVD partitioning and hardware tables are changed across profiles. Cleanup restores KVD defaults. Risks include long runtime, cascading failures from sourced hooks, KVD profile sizes becoming stale, and failure to restore if interrupted outside trap. Test signals are per-profile scale logs, overflow logs, optional traffic logs, and final aggregate status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/resource_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_counter_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_counter_scale.sh

Purpose: Spectrum-1 target provider for RIF counter scale testing.

Important functions/APIs: sources `../rif_counter_scale.sh`; defines `rif_counter_get_target` using RIF and RIF-counter devlink resources.

Control flow: subtracts current RIF occupancy, converts counter slots to RIF count by dividing by 20, skips impossible overflow when counters outnumber RIFs, and returns target or target plus one.

State/dependencies: stateless wrapper, but target depends on live devlink occupancy and active KVD profile. Risks include stale slot-cost assumptions and profile-dependent capacity. Test signals are inherited RIF/counter scale and overflow checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_counter_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_mac_profile_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_mac_profile_scale.sh

Purpose: Spectrum-1 target provider for RIF MAC profile scale testing.

Important functions/APIs: sources `../rif_mac_profile_scale.sh`; defines `rif_mac_profile_get_target` from `devlink_resource_size_get rif_mac_profiles`.

Control flow: returns normal or overflow target based on capacity.

State/dependencies: stateless wrapper whose values can change with resource partitioning. Risks are resource occupancy and schema changes. Test signals are inherited RIF MAC profile allocation/offload/overflow outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_mac_profile_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/router_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/router_scale.sh

Purpose: Spectrum-1 router scale target provider that sizes route stress from the `kvd/hash_single` partition.

Important functions/APIs: sources `../router_scale.sh`; defines `router_get_target` using `devlink_resource_size_get kvd hash_single`.

Control flow: returns 85 percent of hash-single capacity in normal mode and capacity plus one in overflow mode.

State/dependencies: stateless wrapper but capacity depends on current KVD profile. Risks include heuristic mismatch and profile-induced target variation. Test signals are inherited route programming, offload, traffic, and overflow logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/router_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_flower_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_flower_scale.sh

Purpose: Spectrum-1 target provider for generic tc flower scale testing with a fixed theoretical ACL-rule target.

Important functions/APIs: sources `../tc_flower_scale.sh`; defines `tc_flower_get_target` with hard-coded normal target `5631`.

Control flow: normal mode returns 5631, derived from theoretical 6144 rules minus one 512-rule bank and one catch-all; overflow mode returns 5632.

State/dependencies: stateless but assumes Spectrum-1 ACL bank layout. Risks include hard-coded capacity mismatch under different profiles or firmware. Test signals are inherited flower batch insertion, `in_hw` counting, and traffic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_flower_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_police_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_police_scale.sh

Purpose: Spectrum-1 target provider for generic single-rate policer scale testing.

Important functions/APIs: sources `../tc_police_scale.sh`; defines `tc_police_get_target` from `global_policers/single_rate_policers`.

Control flow: returns exact capacity or capacity plus one for overflow.

State/dependencies: stateless wrapper around devlink reads. Risks are existing policer occupancy and resource schema changes. Test signals are inherited policer insertion/offload-count/overflow checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_police_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/vxlan_flooding_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/vxlan_flooding_ipv6.sh

Purpose: Spectrum-1 IPv6 VXLAN flooding test for flood records containing five remote VTEP IPv6 addresses per record.

Important functions/APIs: defines the same topology and helper set as the Spectrum-2 variant: host/router/switch setup, FDB remote insertion, tc filter counters, deletion stages, and packet checking.

Control flow: creates 20 remote VTEPs, sends one flood packet, then deletes a middle record, first record, last record, and individual entries from a remaining record, updating expected packet arrays after each stage.

State/dependencies: bridge, VXLAN, loopback IPv6, route, FDB, and tc filter state. Risks include exact record-size assumptions, IPv6 route/offload timing, and noisy counters. Test signals are per-remote packet counts after each flood stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/vxlan_flooding_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_action_hw_stats.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_action_hw_stats.sh

Purpose: verifies mlxsw handling of tc action `hw_stats` modes and corresponding devlink flow-counter occupancy.

Important functions/APIs: `h1_create`, `switch_create`, `hw_stats_test`, mode wrappers `default_hw_stats_test`, `immediate_hw_stats_test`, `delayed_hw_stats_test`, `disabled_hw_stats_test`, `setup_prepare`, `cleanup`, and `check_tc_action_hw_stats_support`. Uses `tc filter flower skip_sw`, `devlink_resource_get counters flow`, jq, mausezahn, and `tc_check_packets`.

Control flow: for supported modes, records flow-counter occupancy, installs a drop rule with the requested hw_stats setting, checks occupancy delta, sends one packet, verifies packet stats match expected visibility, then deletes the rule. Delayed mode is expected to be rejected.

State/dependencies: one clsact qdisc and flow counters. Risks are changed counter accounting, delayed stats support evolution, and exact occupancy deltas. Test signals are rule insertion success/failure, flow counter occupancy, and tc packet counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_action_hw_stats.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_flower_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_flower_scale.sh

Purpose: generic mlxsw scale-test module for offloaded flower rules. It is intended to be sourced by architecture-specific resource-scale runners that provide target counts.

Important functions/APIs: `TC_FLOWER_NUM_NETIFS`, setup/cleanup hooks `tc_flower_setup_prepare`, `tc_flower_cleanup`, address generator `tc_flower_addr`, batch writer `tc_flower_rules_create`, internal `__tc_flower_test`, public `tc_flower_test`, and `tc_flower_traffic_test`.

Control flow: setup initializes two interfaces with clsact qdiscs. The test writes a temporary tc batch with one IPv6 destination flower drop rule per count, runs `tc -b`, verifies insertion outcome based on `should_fail`, counts `in_hw` entries from JSON, and optionally sends traffic to logarithmically sampled rule indices.

State/dependencies: temporary batch file, clsact qdiscs, flower filters, and VRF state. Risks include temp file cleanup only if variable exists, address/priority count limit 65536, parsing `in_hw`, and offload check dependency. Test signals are batch insertion status, offloaded rule count, and traffic counter hits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_flower_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_occ.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_occ.sh

Purpose: validates reference counting of mlxsw single-rate policer resources when tc filters create, share, and delete police actions.

Important functions/APIs: topology helpers `h1_create`, `switch_create`, `setup_prepare`, `cleanup`; `tc_police_occ_get`; `tc_police_occ_test`. Uses `devlink_resource_occ_get global_policers single_rate_policers` and `tc filter flower skip_sw action police`.

Control flow: records initial policer occupancy, adds a rule with a unique policer and expects +1, deletes it and expects baseline, then adds two filters sharing `index 10`, confirms occupancy stays +1 until the last reference is removed.

State/dependencies: clsact qdisc, police actions, devlink resource occupancy. Risks include shared action index collisions with pre-existing actions and changed policer accounting. Test signals are exact occupancy comparisons after each add/delete step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_occ.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_scale.sh

Purpose: generic mlxsw scale-test module for offloaded tc police actions, sourced by resource-scale runners.

Important functions/APIs: `TC_POLICE_NUM_NETIFS`, setup/cleanup hooks, `tc_police_addr`, `tc_police_rules_create`, `__tc_police_test`, and `tc_police_test`.

Control flow: initializes one host and one switch port, writes a temporary tc batch containing IPv6 flower rules with police actions, executes it, and verifies JSON offload count equals the requested count unless overflow was expected.

State/dependencies: batch file, clsact qdisc, police actions, VRF state. Risks include no explicit batch-file removal in local cleanup, high rule counts, parsing `.options.in_hw`, and policer resource sharing changes. Test signals are tc batch insertion and offloaded filter count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_scale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_restrictions.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_restrictions.sh

Purpose: negative/positive suite for mlxsw tc offload restrictions around shared blocks, mirred redirect/mirror, matchall sampling, protocol matching, and police limits.

Important functions/APIs: tests include `shared_block_drop_test`, `egress_redirect_test`, `multi_mirror_test`, `matchall_sample_egress_test`, ingress/egress matchall-behind-flower helpers, `matchall_proto_match_test`, `police_limits_test`, and `multi_police_test`. It uses forwarding `tc_common.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, `check_tc_shblock_support`, and `mlxsw_only_on_spectrum`.

Control flow: each test builds minimal clsact/shared-block state on two switch ports, verifies allowed configurations first, then attempts unsupported combinations expecting `check_fail`, and cleans qdiscs/filters inline.

State/dependencies: temporary tc qdiscs, shared blocks, filters, police and mirror actions. Risks are extant shared block IDs, spectrum-specific skips, and cleanup ordering when a negative step unexpectedly succeeds. Test signals are exact success/failure of tc commands for each restriction boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_restrictions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_sample.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_sample.sh

Purpose: verifies mlxsw tc sample offload behavior and psample metadata, including rate accuracy, group conflicts, ingress/egress interface metadata, LAG metadata, output traffic class, queue occupancy, latency, and flower-policy sampling.

Important functions/APIs: topology helpers for four hosts and four router ports with two LAG paths; `psample_capture_start/stop`; tests `tc_sample_rate_test`, `tc_sample_max_rate_test`, `tc_sample_conflict_test`, `tc_sample_group_conflict_test`, metadata tests, ACL group/rate/max-rate tests. Requires external `psample` tool, mausezahn, tc matchall/flower `action sample`, jq, and mlxsw version gates.

Control flow: setup creates routed VRF paths and 802.3ad bonds. Tests install one or more sampling filters, capture psample output to a temp file, generate traffic, then grep for expected group counts or metadata fields. Some tests configure qdiscs to force output TC or occupancy.

State/dependencies: routes, bonds, clsact qdiscs, sample filters, psample background process, temp capture file. Risks include sampling randomness/tolerance, process cleanup, external psample availability, timing under high packet counts, and Spectrum-version feature differences. Test signals are sampled packet count tolerance, expected metadata strings, conflict insertion failures, and rate limit boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_sample.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan.sh

Purpose: large mlxsw VXLAN offload suite covering configuration sanitization and offload indication for bridge FDB entries, decap routes, replay/cleanup, and VLAN-aware VNI mapping.

Important functions/APIs: configurable environment (`ADDR_FAMILY`, `LOCAL_IP_*`, `PREFIX_LEN`, checksum flags, multicast IP); sanitization helpers for single and multiple VXLAN devices; offload setup/destroy; FDB tests; decap-route tests; join-order tests; VLAN-aware sanitization/offload tests. Uses `ip link`, `bridge fdb`, `bridge vlan`, `busywait wait_for_offload`, `grep_bridge_fdb`, and common forwarding `lib.sh`.

Control flow: setup brings two switch ports up. Sanitization tests create valid/invalid bridge+VXLAN combinations and assert attach success/failure. Offload tests build VXLAN bridges, add FDB entries, wait for offload flags, remove/re-add entries from bridge or VXLAN layers, toggle device/route/port/bridge state, and verify decap route offload tracks active VXLAN presence. VLAN-aware tests verify one VNI per VLAN and offload under tagged/pvid mappings.

State/dependencies: many temporary bridges, VXLAN devices, FDB entries, loopback local routes, and port masters. Risks include extensive mutation, offload wait timing, extant local addresses, extack/offload flag format changes, and wrapper overrides for IPv6. Test signals are command success/failure, offload flag presence/absence, and bridge/VXLAN FDB state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto.sh

Purpose: tests mlxsw veto/rollback paths for unsupported VXLAN FDB entries and VXLAN changelink parameters.

Important functions/APIs: env variables for local/remote IPs, checksum flags, and multicast IP; `setup_prepare`, `cleanup`, `fdb_create_veto_test`, `fdb_replace_veto_test`, `fdb_append_veto_test`, `fdb_changelink_veto_test`.

Control flow: creates a bridge with one physical port and a VXLAN device, then verifies multicast MAC, explicit UDP port on replace/append, and multicast-group changelink are rejected and include `mlxsw_spectrum` extack. Valid baseline FDB entries are added before replace/append negative checks.

State/dependencies: bridge, VXLAN, port state, FDB entries. Risks are extack text matching, rollback correctness after failed operations, and wrapper-provided IPv6 parameter differences. Test signals are expected failures plus extack presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto_ipv6.sh

Purpose: IPv6 wrapper for the VXLAN FDB veto suite.

Important functions/APIs: sets IPv6 `LOCAL_IP`, `REMOTE_IP_1`, `REMOTE_IP_2`, IPv6 zero-checksum flags, and multicast `MC_IP`, then sources `vxlan_fdb_veto.sh`.

Control flow: source-time variable overrides make the base veto tests create IPv6 VXLAN and remote VTEP entries.

State/dependencies: inherited entirely from the base script. Risks are implicit source contract and IPv6-specific checksum/multicast behavior. Test signals are base veto pass/fail logs under IPv6 parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_flooding.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_flooding.sh

Purpose: IPv4 VXLAN flooding correctness test for mlxsw flood records containing three remote VTEP addresses per record.

Important functions/APIs: topology helpers for host, switch bridge/VXLAN, underlay routers, setup/cleanup; flooding helpers for FDB remote insertion, tc counter filters, packet checking, and `flooding_test`.

Control flow: configures VXLAN local address on loopback, route to remote VTEPs through a router port, and 12 flood remotes. It sends BUM traffic to a dummy destination MAC, verifies all remotes get one packet, deletes middle/first/last records and individual entries, then verifies updated packet arrays.

State/dependencies: bridge/VXLAN/loopback/route/VRF state plus tc filters on router and isolation filters on host/bridge. Risks include exact record packing assumption, tc counter noise, missing cleanup on failed deletion, and route/offload timing. Test signals are per-remote tc packet counters after each flood stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_flooding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_ipv6.sh

Purpose: IPv6 wrapper and override layer for the general mlxsw VXLAN sanitization/offload suite.

Important functions/APIs: sets IPv6 address family, local IPs, prefix length, UDP zero-checksum flags, multicast IP, and `IP_FLAG=-6`; overrides `sanitization_single_dev_learning_enabled_ipv6_test` and `sanitization_single_dev_udp_checksum_ipv6_test`; sources `vxlan.sh`.

Control flow: base suite runs with IPv6 parameters. The wrapper changes learning-enabled behavior to expected failure and tests both missing RX and missing TX zero-checksum flags.

State/dependencies: inherited from `vxlan.sh`, with IPv6 route/FDB semantics. Risks are source-order coupling and differing IPv6 offload constraints. Test signals are base VXLAN logs plus IPv6-specific sanitization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id.py

Purpose: Python kselftest that verifies accepted TCP sockets report a nonzero `SO_INCOMING_NAPI_ID` via the companion C helper.

Important functions/APIs: `test_napi_id` chooses a random port, starts `napi_id_helper` in the background, connects to it from the remote endpoint with `socat`, and asserts helper exit status; `main` runs through `NetDrvEpEnv`, `ksft_run`, and `ksft_exit`.

Control flow: the C helper signals readiness, Python sends one byte through the test endpoint pair, waits for the server process, and checks it returned zero.

State/dependencies: relies on the net driver Python selftest library, compiled helper in `cfg.test_dir`, endpoint namespaces/remote host, and `socat`. Risks include helper binary not built, endpoint transport not traversing NAPI, and race if server readiness fails. Test signals are helper return code and ksft equality assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id_helper.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id_helper.c

Purpose: companion TCP server for `napi_id.py` that validates `SO_INCOMING_NAPI_ID` on an accepted socket.

Important functions/APIs: single `main` uses `getaddrinfo`, `socket`, `setsockopt(SO_REUSEADDR)`, `bind`, `listen`, `ksft_ready`, `accept`, `getsockopt(SO_INCOMING_NAPI_ID)`, `read`, `ksft_wait`, and cleanup closes.

Control flow: resolves bind address/port from argv, starts a listening socket, announces readiness to the Python harness, accepts one client, reads the incoming NAPI ID socket option, drains one read, waits for harness synchronization, and fails if NAPI ID is zero.

State/dependencies: only socket descriptors. Depends on kernel support for `SO_INCOMING_NAPI_ID` and ksft sync helpers. Risks include missing argc validation, returning `-1` for `EAFNOSUPPORT`, and not closing sockets on early errors. Test signals are process exit status and stderr diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_threaded.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_threaded.py

Purpose: Python netdev selftest for persistent NAPI threaded state across device-level toggles and queue count changes.

Important functions/APIs: assertions `_assert_napi_threaded_enabled/disabled`, `_set_threaded_state`, `_setup_deferred_cleanup`, tests `napi_init`, `enable_dev_threaded_disable_napi_threaded`, `change_num_queues`, and `main`. Uses `NetDrvEnv`, `NetdevFamily` netlink, `ethtool -L`, sysfs `/sys/class/net/$ifname/threaded`, and ksft assertions.

Control flow: each test records current combined queue count and threaded sysfs state for deferred restore, toggles device threaded mode, changes queue count down and back up, then dumps NAPI netlink objects and checks `threaded` state and pid presence.

State/dependencies: mutates queue count and sysfs threaded flag, restored through `defer`. Requires at least two combined queues and NAPI netlink support. Risks include hardware that cannot change queues, sysfs state formatting, netlink schema changes, and persistent threaded state not scoped per test if cleanup fails. Test signals are ksft equality/non-equality/ge assertions on NAPI objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_threaded.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/Makefile -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/Makefile

Purpose: kselftest makefile registering netconsole shell tests and shared include dependencies.

Important variables/APIs: `TEST_INCLUDES` lists `../../../net/lib.sh` and `../lib/sh/lib_netcons.sh`; `TEST_PROGS` lists basic, cmdline, fragmented message, overflow, resume, sysdata, and torture tests; includes `../../../lib.mk`.

Control flow: no runtime logic; kselftest build/install infrastructure uses the variables to copy and execute scripts.

State/dependencies: depends on relative paths in kselftest tree and lib.mk conventions. Risks are missing new scripts if not added to `TEST_PROGS`, and included helper path drift. Test signals are make/kselftest discovery of all intended scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/config -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/config

Purpose: declares kernel configuration prerequisites for netconsole selftests.

Important entries: `CONFIG_CONFIGFS_FS=y`, `CONFIG_IPV6=y`, `CONFIG_NETCONSOLE=m`, `CONFIG_NETCONSOLE_DYNAMIC=y`, `CONFIG_NETCONSOLE_EXTENDED_LOG=y`, and `CONFIG_NETDEVSIM=m`.

Control flow: consumed by kselftest/config tooling rather than executed.

State/dependencies: requires configfs, dynamic/extended netconsole, IPv6, and netdevsim. Risks are tests being skipped or failing noisily if config fragments are not applied. Test signals are kernel config availability before running the shell tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_basic.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_basic.sh

Purpose: basic dynamic netconsole delivery test over IPv4 and IPv6, in both basic and extended output formats.

Important functions/APIs: sources `lib_netcons.sh`; uses `check_for_dependencies`, `set_network`, `create_dynamic_target`, optional `set_user_data`, `listen_port_and_save_to`, `wait_for_port`, `validate_result`, `pkill_socat`, and `cleanup`. Loads `netdevsim` and `netconsole`.

Control flow: loops over `FORMAT=basic/extended` and `IP_VERSION=ipv6/ipv4`, configures printk levels, creates namespace and simulated interfaces, creates dynamic target, listens with socat, writes a message to `/dev/kmsg`, waits for output file, validates received message, and cleans up before next iteration.

State/dependencies: modules, net namespace, netdevsim interfaces, configfs target, `/tmp/$TARGET`, printk level, and socat process. Risks include polluting dmesg, leftover namespace/targets, timing waiting for UDP delivery, and shared `/tmp` filename collisions. Test signals are non-empty output file and format-specific validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_cmdline.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_cmdline.sh

Purpose: verifies netconsole module parameter parsing and cmdline target initialization for interface-name and MAC binding modes.

Important functions/APIs: sources `lib_netcons.sh`; uses `check_netconsole_module`, `set_network`, `create_cmdline_str`, `listen_port_and_save_to`, `wait_local_port_listen`, `validate_msg`, `pkill_socat`, `do_cleanup`, `modprobe netconsole "$CMDLINE"`, and `rmmod netconsole`.

Control flow: unloads netconsole, sets up network once, then for each bind mode loads netconsole with constructed parameters, listens for UDP output, writes to `/dev/kmsg`, waits for capture, validates message, kills socat, unloads module, and repeats.

State/dependencies: netconsole module lifecycle, netdevsim network, printk level, namespace, `/tmp` captures. Risks include module unload blocked by existing users, no dynamic configfs cleanup for cmdline mode, and missing busywait failure check before validation. Test signals are message capture and validation for both bind modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_cmdline.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_fragmented_msg.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_fragmented_msg.sh

Purpose: validates netconsole fragmentation and receiver-side reconstruction behavior for long messages and long userdata, with and without release-version appending.

Important functions/APIs: `header_to_regex`, `extract_msg`, `validate_fragmented_result`; helper calls `check_for_dependencies`, `set_network`, `create_dynamic_target`, `set_user_data`, `disable_release_append`, `listen_port_and_save_to`, `wait_local_port_listen`, and cleanup.

Control flow: configures netconsole with long userdata, sends an oversized message to `/dev/kmsg`, captures fragments, strips generated `ncfrag` headers, and verifies body plus userdata. Then disables release append and repeats with a smaller but still fragmented message.

State/dependencies: dynamic target, userdata configfs, `/tmp/$TARGET`, socat listener, printk level. Risks include regex fragility around header format, not explicitly cleaning between two captures, and fragmented UDP timing. Test signals are reconstructed message body and userdata presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_fragmented_msg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_overflow.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_overflow.sh

Purpose: tests netconsole userdata capacity limit enforcement.

Important functions/APIs: `MAX_USERDATA_ITEMS=256`, `create_userdata_max_entries`, `verify_entry_limit`, plus helper calls `check_for_dependencies`, `set_network`, `create_dynamic_target`, `set_user_data`, and cleanup.

Control flow: creates a dynamic target, creates 256 userdata entries successfully by changing `USERDATA_KEY`, then attempts to create one more directory under configfs and expects failure.

State/dependencies: configfs userdata directories, dynamic netconsole target, netdevsim network. Risks include hard-coded limit drift, pre-existing userdata entries affecting count, and direct mkdir bypassing helper validation. Test signals are no failure while creating max entries and failure when exceeding the limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_overflow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_resume.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_resume.sh

Purpose: validates that cmdline netconsole targets disabled by source/destination interface disappearance automatically resume when netdevsim interfaces return.

Important functions/APIs: local `cleanup`, `trigger_deactivation`, `trigger_reactivation`; helper calls `cleanup_netcons`, `do_cleanup`, `check_netconsole_module`, `set_network`, `create_cmdline_str`, `wait_target_state`, `listen_port_and_save_to`, `wait_local_port_listen`, and `validate_msg`.

Control flow: for ifname and MAC binding modes, creates network, loads netconsole cmdline target, exposes `cmdline0` in configfs, waits for enabled state, unloads netdevsim to force disabled state, reloads netdevsim and restores MACs/names as needed, waits for enabled state, then captures a `/dev/kmsg` message.

State/dependencies: netconsole/netdevsim module lifecycle, configfs cmdline target, saved MAC addresses, namespace and interfaces. Risks include module unload side effects, race in device recreation, MAC-bound rename behavior, and cleanup invoked inside loop plus trap. Test signals are target state transitions and successful message capture in both bind modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_resume.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_sysdata.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_sysdata.sh

Purpose: validates netconsole extended sysdata fields for CPU number, task name, kernel release, msgid, and interaction with userdata.

Important functions/APIs: setters/unsetters for `cpu_nr_enabled`, `taskname_enabled`, `release_enabled`, `msgid_enabled`; validators `validate_sysdata`, `validate_release`, `validate_no_sysdata`; `runtest`; helper calls `check_for_dependencies`, `check_for_taskset`, `set_network`, `create_dynamic_target`, `set_user_data`, and UDP listener helpers.

Control flow: creates dynamic target, then runs three captures. Test 1 enables sysdata fields and sends from a random CPU with `taskset`; Test 2 adds userdata while sysdata remains enabled; Test 3 disables sysdata and verifies none of the fields are present. Each test writes to `/dev/kmsg`, waits for capture, and greps expected fields.

State/dependencies: configfs sysdata/userdata toggles, random CPU selection, `taskset`, `/tmp` capture files, socat process. Risks include random CPU greater than allowed cpuset, grep format assumptions, release field timing, and cleanup of captures/socat on validator failure. Test signals are field presence/absence and matching CPU/task/release/msgid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_sysdata.sh -->
