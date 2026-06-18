# Group Research: subset-b-006827

This grouped report covers Linux kselftest driver selftests under `tools/testing/selftests/drivers`. Each section is keyed by source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/udmabuf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/udmabuf.c

Purpose: C kselftest for `/dev/udmabuf`, covering invalid `UDMABUF_CREATE` arguments, normal udmabuf creation from sealed memfds, and migration/list creation behavior for base pages and huge pages.

Important APIs/types/functions: `memfd_create`, `F_ADD_SEALS`, `F_SEAL_SHRINK`, `ftruncate`, `mmap`, `ioctl(UDMABUF_CREATE)`, `ioctl(UDMABUF_CREATE_LIST)`, `struct udmabuf_create`, `struct udmabuf_create_list`, `create_memfd_with_seals()`, `create_udmabuf_list()`, `write_to_memfd()`, `mmap_fd()`, `compare_chunks()`, and kselftest helpers from `kselftest.h`.

Control flow: `main()` opens `/dev/udmabuf`, creates a sealed memfd, executes three negative tests for unaligned offset, unaligned size, and non-memfd input, then creates a valid udmabuf. It then exercises list creation with four chunks from a large memfd, writes after pinning, maps both memfd and udmabuf, and compares page-granular data. Later tests repeat this with 2 MiB huge pages, including a case where the udmabuf is pinned before writing the memfd.

State and persistence: State is process-local file descriptors and mappings. The test mutates memfd contents, maps DMA buffers shared, and unmaps/closes between cases. No persistent repository state is written.

Dependencies and integration points: Requires `/dev/udmabuf`, memfd sealing, hugetlb availability for huge-page cases, Linux UAPI headers, and kselftest result conventions. It directly tests dma-buf/udmabuf kernel ABI validation.

Risks and test signals: Failures indicate broken input validation, fd type checks, page alignment handling, list/chunk migration, huge-page migration, or DMA buffer data coherency. Huge-page allocation may skip/fail depending on host configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/udmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/gpu/drm_mm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/gpu/drm_mm.sh

Purpose: Shell kselftest wrapper for the DRM range-manager unit test module `test-drm_mm`.

Important APIs/functions: `/sbin/modprobe -n -q`, `/sbin/modprobe -q`, `/sbin/modprobe -q -r`, `uname -r`, and kselftest exit code `77` for skip.

Control flow: The script first dry-runs module lookup. If the module is unavailable, it prints a skip message and exits `77`. If load succeeds, it immediately unloads the module and reports `drivers/gpu/drm_mm: ok`; otherwise it reports failure and exits `1`.

State and persistence: It transiently loads and removes `test-drm_mm`. No files are written.

Dependencies and integration points: Requires root/module privileges, the test module in `/lib/modules/$(uname -r)`, and kernel module selftests compiled for DRM.

Risks and test signals: Failure means the module selftest failed to load or unload cleanly. A skip means the module is absent, not necessarily a DRM allocator regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/gpu/drm_mm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/gpu/i915.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/gpu/i915.sh

Purpose: Shell wrapper for hardware-independent i915 mock selftests exposed through module load parameter `mock_selftests=-1`.

Important APIs/functions: `/sbin/modprobe -q -r i915`, `/sbin/modprobe -q i915 mock_selftests=-1`, module unload, skip exit `77`.

Control flow: It tries to remove an already-loaded `i915`; inability to remove is treated as skip because hardware/users may be using the module. It then reloads `i915` with mock selftests enabled. Success is followed by module removal and an `ok` message; load failure exits `1`.

State and persistence: Transiently unloads and reloads the `i915` module. No repository or filesystem state is persisted.

Dependencies and integration points: Requires module control privileges and an i915 build with mock selftests. Integrates with kselftest GPU driver coverage.

Risks and test signals: Risk is disruptive module cycling on systems using i915. Failures indicate i915 mock selftest regressions or module load problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/gpu/i915.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/Makefile

Purpose: Build/install manifest for driver network kselftests in `drivers/net`.

Important APIs/variables: `CFLAGS += $(KHDR_INCLUDES)`, `TEST_INCLUDES`, `TEST_GEN_FILES`, `TEST_PROGS`, `YNL_GEN_FILES`, `YNL_GENS`, inclusion of `../../lib.mk` and `../../net/ynl.mk`.

Control flow: Make collects Python and shell library includes, builds `napi_id_helper` plus YNL-generated `psp_responder`, and registers multiple Python/shell test programs such as `gro.py`, `hds.py`, `macsec.py`, `napi_threaded.py`, `psp.py`, `queues.py`, and `xdp.py`.

State and persistence: Make outputs generated binaries/YNL artifacts under the kselftest output tree; it does not alter runtime kernel state itself.

Dependencies and integration points: Depends on kselftest core `lib.mk`, network YNL generation, kernel headers, and helper libraries in `net/lib.py` and shell libs.

Risks and test signals: Misdeclared `TEST_PROGS`, `TEST_GEN_FILES`, or includes cause install/run gaps. YNL ordering before `lib.mk` is important for generated Netlink family helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/Makefile

Purpose: Build/install manifest for bonding driver selftests.

Important APIs/variables: `TEST_PROGS` for executable tests, `TEST_FILES` for reusable topology/library files, `TEST_INCLUDES` for shared net/forwarding/netconsole helpers, and inclusion of `../../../lib.mk`.

Control flow: The manifest registers bonding behavior/regression tests including ARP interval panic, LACP, IPsec offload, macvlan/ipvlan over bond, option matrix tests, passive LACP, stacked header parsing, dev address lists, recovery updelay, and netconsole-over-bonding.

State and persistence: Build/install only. Runtime state is created by individual scripts.

Dependencies and integration points: Integrates bonding tests with common `net/lib.sh`, forwarding helpers, and netconsole helper scripts.

Risks and test signals: Missing helper files break many tests. Incorrect `TEST_FILES` classification would omit topology libraries needed at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-arp-interval-causes-panic.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-arp-interval-causes-panic.sh

Purpose: Regression test for a kernel panic in `bond_rr_gen_slave_id` when changing bond mode/options around ARP monitoring.

Important APIs/functions: `finish()`, `trap`, `ip netns`, `ip link add type bond`, `miimon`, `all_slaves_active`, `arp_interval`, `arp_ip_target`, `ping`, and `/proc/sys/kernel/panic`.

Control flow: The script creates `server` and `client` namespaces connected by veth, validates active-backup traffic, detaches the slave, recreates bond settings as round-robin with ARP interval and target, reattaches the slave, and validates traffic again.

State and persistence: It writes `/proc/sys/kernel/panic` to 180, which persists beyond the process until changed. Network namespaces are deleted by `finish()` on exit.

Dependencies and integration points: Requires bonding, veth, namespace support, root privileges, and IPv4 ping. It targets bonding mode transition and ARP monitor kernel paths.

Risks and test signals: The panic sysctl side effect is notable. A kernel crash or script failure indicates regressions in bond mode changes, slave reattachment, ARP monitor setup, or round-robin slave selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-arp-interval-causes-panic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-break-lacpdu-tx.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-break-lacpdu-tx.sh

Purpose: Regression test ensuring LACPDU transmission continues after setting a bond MAC address.

Important APIs/functions: forwarding `lib.sh`, `cleanup()`, bridge creation, `ip link add ... type bond mode 4`, bond `ad_actor_sys_prio`, `lacp_rate fast`, `tc qdisc clsact`, flower filter for protocol `0x8809`, `slowwait_for_counter`, and `tc_rule_handle_stats_get`.

Control flow: It deletes stale test devices, creates bridge `fab-br0`, creates 802.3ad bond `fbond`, sets its MAC and LACP parameters, enslaves two veth ports, brings links up, attaches a TC ingress counter to the peer, and waits for at least two LACPDUs.

State and persistence: Creates bridge, bond, veths, and TC filters; `cleanup()` removes devices on exit.

Dependencies and integration points: Requires bonding 802.3ad, veth, bridge, TC flower, and forwarding library wait/stat helpers.

Risks and test signals: Failure means LACPDUs are not observed after MAC/config changes. Timing can be sensitive to LACP timers and TC counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-break-lacpdu-tx.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-eth-type-change.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-eth-type-change.sh

Purpose: Tests bond device ARPHRD type transitions while a bond is enslaved to another bond, ensuring `MASTER` and `SLAVE` flags remain correct.

Important APIs/functions: `bond_check_flags()`, `bond_test_enslave_type_change()`, `bond_test_unsuccessful_enslave_type_change()`, `bond_test_successful_enslave_type_change()`, `ip link add type nlmon`, `ip link add type bond`, `ip -d link`, and forwarding `tests_run`.

Control flow: Each case creates nested bond devices and a non-Ethernet `nlmon` device. It optionally switches the inner bond to active-backup so non-Ethernet enslave can succeed, attempts type changes through enslave/nomaster cycles, restores Ethernet type by enslaving another bond, verifies flags, and deletes devices.

State and persistence: Temporary link devices are removed in-test. The global `RET`/`EXIT_STATUS` convention comes from `lib.sh`.

Dependencies and integration points: Requires bonding, nlmon, iproute support for detailed JSON/link flags, and forwarding test harness.

Risks and test signals: Failures indicate bond type restoration or flag propagation regressions. Cleanup is manual within the test body, so early command failures rely on harness behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-eth-type-change.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-lladdr-target.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-lladdr-target.sh

Purpose: Regression test that a bond using IPv6 link-local `ns_ip6_target` can come up and pass traffic.

Important APIs/functions: `cleanup()`, `wait_lladdr_dad()`, `wait_bond_up()`, `ip netns`, bridge/veth setup, bond `arp_interval`, `ns_ip6_target`, IPv6 DAD state, and `ping6`.

Control flow: The script builds a small namespace bridge topology with veth ports, assigns IPv6 link-local addressing, creates a bond with neighbor-solicitation monitoring target, waits for DAD and bond carrier/up state, then validates connectivity.

State and persistence: Temporary namespaces, bridge, veth, and bond are cleaned on exit. State lives in kernel link and IPv6 neighbor/DAD state during the run.

Dependencies and integration points: Requires IPv6, bonding, bridge/veth, iproute support for `ns_ip6_target`, and root privileges.

Risks and test signals: Failures point at IPv6 monitor target parsing, DAD wait handling, bond carrier state, or IPv6 neighbor solicitation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-lladdr-target.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_ipsec_offload.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_ipsec_offload.sh

Purpose: Validates XFRM/IPsec offload lifecycle when traffic traverses a bond, especially offload migration/removal on active slave changes.

Important APIs/functions: `active_slave_changed()`, `test_offload()`, `setup_env()`, `setup_bond()`, `ip xfrm state/policy`, bond active-backup setup, netns/veth/dummy or netdevsim-style links, and `check_fail`/`check_err`.

Control flow: The script creates namespaces and a bond topology, configures IPsec SAs/policies with offload on a bond/slave path, verifies traffic/offload behavior, changes active slave state, retests, and then deletes the bond while checking that security associations are removed from the driver.

State and persistence: Mutates netns links, XFRM state/policy, and bond slave state; cleanup removes transient kernel objects.

Dependencies and integration points: Requires bonding, XFRM user API, ESP offload support, veth/dummy/netdevsim-style devices, and iproute2 XFRM offload syntax.

Risks and test signals: Failures indicate stale driver offload SAs, active slave transition bugs, or incorrect offload binding to the bond/slave.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_ipsec_offload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_lacp_prio.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_lacp_prio.sh

Purpose: Tests 802.3ad actor port priority handling and aggregator reselection.

Important APIs/functions: `setup_links()`, `test_port_prio_setting()`, `test_agg_reselect()`, `setup_ns`, `cmd_jq`, `ip -d -j link`, bond mode `802.3ad`, `ad_select actor_port_prio`, and `actor_port_prio`.

Control flow: Three namespaces emulate a client and two switches. The client bond has four slaves, split across switch and backup-switch bonds. The test sets per-slave actor priorities, verifies JSON-reported values, toggles a link to trigger aggregator reselection, then reverses priorities and verifies selection moves to the expected slave.

State and persistence: Temporary namespaces, veth links, and bonds are cleaned by `cleanup_all_ns`.

Dependencies and integration points: Requires bonding 802.3ad, LACP, iproute JSON fields for bond slave data, `jq`, and net library namespace helpers.

Risks and test signals: Failures indicate actor priority not being applied, bad aggregator reporting, or aggregator reselection regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_lacp_prio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_macvlan_ipvlan.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_macvlan_ipvlan.sh

Purpose: Tests macvlan and ipvlan devices layered over a bond in active-backup, balance-tlb, and balance-alb modes.

Important APIs/functions: `bond_topo_2d1c.sh`, `cleanup()`, `check_connection()`, `xvlan_over_bond()`, `bond_reset()`, `ip link add link bond0 type macvlan/ipvlan`, namespace moves, IPv4/IPv6 ping, and `log_test`.

Control flow: It creates the common 2-downlink bond topology plus two extra namespaces. For each bond mode, it resets the bond, creates two macvlan bridge-mode or ipvlan l2 devices on the server bond, moves them into namespaces, assigns IPv4/IPv6 addresses, and checks bidirectional connectivity among client, server, and xvlan namespaces.

State and persistence: Temporary namespaces and virtual devices are cleaned on exit. Neighbor caches are flushed between scenarios.

Dependencies and integration points: Requires bonding, macvlan, ipvlan, IPv6, veth, bridge, and the shared topology helper.

Risks and test signals: Failures identify layered L2/L3 forwarding issues over bond modes or stale neighbor/MAC learning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_macvlan_ipvlan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_options.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_options.sh

Purpose: Broad option matrix selftest for bonding modes active-backup, balance-tlb, and balance-alb using a three-link topology.

Important APIs/functions: `skip_prio()`, `skip_ns()`, `active_slave_changed()`, `check_active_slave()`, `prio_test()`, `prio_miimon()`, `prio_arp()`, `prio_ns()`, `arp_validate_test()`, `arp_validate_mcast()`, `garp_test()`, `num_grat_arp()`, fail-over-MAC check helpers, `do_active_backup_failover()`, `vlan_over_bond_arp()`, `vlan_over_bond_ns()`, `vlan_over_bond()`, and `tests_run`.

Control flow: The script sources `bond_topo_3d1c.sh`, prepares a server/gateway/client topology, then runs `ALL_TESTS`. Priority cases reset bonds with miimon/ARP/NS monitoring and primary reselection modes, validate per-slave priority, active slave choices, and connectivity. ARP validate cases inspect MII state and multicast group joins. GARP cases count gratuitous ARP packets via TC filters. Fail-over-MAC cases validate MAC inheritance under all policy modes. VLAN cases verify ARP and IPv6 NS monitoring over VLAN devices.

State and persistence: Uses temporary namespaces, bond resets, TC clsact/flower filters, VLAN devices, multicast memberships, and link state transitions. Cleanup is inherited from the topology.

Dependencies and integration points: Requires bonding options support in kernel and iproute2, `jq`, TC flower, IPv6, VLAN, bridge/veth, and forwarding test helpers.

Risks and test signals: This is timing-sensitive around failover and monitoring intervals. Failures map to option parsing, active slave selection, monitor target handling, multicast membership propagation, GARP counts, fail-over-MAC semantics, or VLAN encapsulation handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_options.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_passive_lacp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_passive_lacp.sh

Purpose: Tests that an 802.3ad bond with `lacp_active=off` behaves as a passive LACP participant.

Important APIs/functions: `check_port_state()`, `check_pkt_count()`, `setup()`, forwarding `lib.sh`, `tc` egress counters, `jq` inspection of `ad_actor_oper_port_state_str`, and `slowwait_for_counter`.

Control flow: It builds client/server namespaces connected by veth pairs and 802.3ad bonds, attaches TC filters to count LACPDUs, checks that the passive side does not initiate packets while waiting, then validates expected LACP state and packet exchange when the active peer exists.

State and persistence: Temporary namespaces, bonds, veths, and TC filters are removed by cleanup.

Dependencies and integration points: Requires bonding 802.3ad, TC flower/action pass, JSON bond slave state, and relatively long waits for LACP timers.

Risks and test signals: Long timing windows can be slow. Failure indicates passive LACP transmission/state-machine regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_passive_lacp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_stacked_header_parse.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_stacked_header_parse.sh

Purpose: Regression test for bond transmit hash/header parsing with stacked tunnel/VLAN-style headers.

Important APIs/functions: `bond_test_stacked_header_parse()`, namespace/veth setup, bond creation, encapsulation device setup, traffic generation, and kselftest logging helpers.

Control flow: The script creates a virtual topology, configures a bond and stacked protocol headers, sends traffic that forces the bond xmit path to parse inner headers, and checks expected delivery/hash behavior.

State and persistence: Temporary namespaces and network devices are created and cleaned during the test.

Dependencies and integration points: Requires bonding, veth, tunnel/VLAN parsing support used by the script, and net selftest helpers.

Risks and test signals: Failures indicate regressions in `skb_flow_dissect`/bond hash parsing for encapsulated traffic or missing kernel feature support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_stacked_header_parse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_2d1c.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_2d1c.sh

Purpose: Shared two-downlink, one-client bonding topology library for mode 1/5/6 tests.

Important APIs/functions: `gateway_create()`, `gateway_destroy()`, `server_create()`, `bond_reset()`, `server_destroy()`, `client_create()`, `client_destroy()`, `setup_prepare()`, `cleanup()`, `bond_check_connection()`, forwarding `lib.sh`, `simple` namespace/veth/bridge operations, and TC clsact setup.

Control flow: Callers use `setup_prepare()` to create gateway, server, and client namespaces. The server owns `bond0` with two veth slaves connected to a gateway bridge; the client connects to the same bridge. `bond_reset()` deletes and recreates `bond0` with caller-supplied options while preserving slave links and IP addresses.

State and persistence: Defines global namespace names, IPv4/IPv6 addresses, MAC array, and helper functions. It creates transient namespaces, bridge, veths, bond, addresses, and TC qdiscs; `cleanup()` removes them.

Dependencies and integration points: Used by `bond_macvlan_ipvlan.sh` and can be extended by `bond_topo_3d1c.sh`. Requires forwarding library, bonding, bridge, veth, IPv6, and TC.

Risks and test signals: As a shared fixture, bugs in cleanup or `bond_reset()` cascade into many tests. IPv6 DAD wait is handled with `slowwait`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_2d1c.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_3d1c.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_3d1c.sh

Purpose: Extends the two-downlink topology to three server downlinks for bonding option tests.

Important APIs/functions: Sources `bond_topo_2d1c.sh`, overrides `setup_prepare()`, appends `mac[2]`, creates `eth2`/`s2`, enslaves it to `bond0`, and attaches TC clsact to gateway side `s2`.

Control flow: The overridden setup calls base gateway/server/client creation, then adds the third veth pair between server and gateway bridge. Base cleanup dynamically counts `eth*` links, so it removes the extra slave too.

State and persistence: Adds one extra MAC and transient veth/TC state. No persistent files.

Dependencies and integration points: Used by `bond_options.sh` for three-slave failover, priority, and GARP scenarios.

Risks and test signals: The helper relies on base functions counting links in real time; if link names differ, cleanup/reset behavior can break downstream tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_3d1c.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/config

Purpose: Kselftest kernel config fragment for bonding tests.

Important entries: `CONFIG_BONDING`, `CONFIG_BRIDGE`, `CONFIG_DUMMY`, `CONFIG_INET_ESP`, `CONFIG_INET_ESP_OFFLOAD`, `CONFIG_IPV6`, `CONFIG_IPVLAN`, `CONFIG_MACVLAN`, `CONFIG_NET_ACT_GACT`, `CONFIG_NET_CLS_FLOWER`, `CONFIG_NET_CLS_MATCHALL`, `CONFIG_NETCONSOLE`, `CONFIG_NETDEVSIM`, `CONFIG_NET_IPGRE`, `CONFIG_NET_SCH_INGRESS`, `CONFIG_NLMON`, `CONFIG_VETH`, `CONFIG_VLAN_8021Q`, and `CONFIG_XFRM_USER`.

Control flow: No executable flow; it declares kernel capabilities expected for the bonding test suite.

State and persistence: Build-time/test-environment configuration only.

Dependencies and integration points: Maps directly to the devices and subsystems used by bonding scripts: veth/dummy/nlmon, bridge/VLAN, TC, XFRM/IPsec, netconsole, netdevsim, and IPv6.

Risks and test signals: Missing config causes skips or false failures. Offload tests need ESP/XFRM and netdevsim support beyond basic bonding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/dev_addr_lists.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/dev_addr_lists.sh

Purpose: Tests that bonding updates underlying device address lists correctly, especially LACPDU multicast membership in different bond modes and carrier states.

Important APIs/functions: `destroy()`, `cleanup()`, `bond_cleanup_mode1()`, `bond_cleanup_mode4()`, `bond_listen_lacpdu_multicast()`, `bond_listen_lacpdu_multicast_case_down()`, `bond_listen_lacpdu_multicast_case_up()`, `ip maddr show`, bond modes 1 and 4, and test logging helpers.

Control flow: The script creates dummy devices and a bond, configures slaves, then checks multicast address list membership for LACPDU multicast under down/up cases and after cleanup. Separate cleanup paths account for active-backup and 802.3ad behavior.

State and persistence: Creates temporary dummy/bond devices and multicast memberships; cleanup deletes devices.

Dependencies and integration points: Requires bonding, dummy interfaces, multicast address inspection, and shell test helpers.

Risks and test signals: Failures point at leaked or missing hardware/multicast address list entries on slaves, especially after mode changes or link state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/dev_addr_lists.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/lag_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/lag_lib.sh

Purpose: Shared LAG helper library for bonding/team cleanup and recovery tests.

Important APIs/functions: `test_LAG_cleanup()`, `lag_setup2x2()`, `lag_cleanup()`, `lag_setup_network()`, `lag_reset_network()`, `create_bond()`, `test_bond_recovery()`, global `NAMESPACES`, dummy/veth creation, bridge setup, and connectivity checks.

Control flow: `test_LAG_cleanup()` creates bonding or team LAG devices over dummy slaves, adds IPv6/multicast addresses, then verifies addresses added to slaves are removed after LAG teardown. Recovery helpers create a two-host/two-link topology, reset a bond with caller-supplied options, force link changes, and verify traffic recovers after updelay scenarios.

State and persistence: Tracks namespaces in `NAMESPACES`, creates temporary links/bridges/bonds/team devices, and removes them in cleanup.

Dependencies and integration points: Shared by mode recovery scripts. Requires bonding, optionally team, dummy/veth/bridge, IPv6, and common net selftest assertions.

Risks and test signals: A helper failure affects recovery scripts. Tests reveal LAG address-list leaks, bond recovery timing regressions, or cleanup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/lag_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-1-recovery-updelay.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-1-recovery-updelay.sh

Purpose: Exercises active-backup bond recovery with varied `updelay` values.

Important APIs/functions: Sources `lag_lib.sh`, `cleanup()`, `test_bond_recovery`, bond parameters `mode 1 miimon 100 updelay N`, and trap cleanup.

Control flow: The script sets cleanup trap, then calls `test_bond_recovery` for mode 1 with `updelay` values 0, 200, 500, 1000, 2000, 5000, and 10000 ms.

State and persistence: Network namespaces and bond topology are created/reset by `lag_lib.sh`; cleanup removes them.

Dependencies and integration points: Requires bonding active-backup, miimon, veth/bridge topology, and helper recovery assertions.

Risks and test signals: Failures indicate active-backup carrier recovery or `updelay` timing regressions. Runtime can be long for high updelay values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-1-recovery-updelay.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-2-recovery-updelay.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-2-recovery-updelay.sh

Purpose: Exercises balance-xor bond recovery with varied `updelay` values.

Important APIs/functions: Sources `lag_lib.sh`, `cleanup()`, `test_bond_recovery`, bond parameters `mode 2 miimon 100 updelay N`, and trap cleanup.

Control flow: It runs the shared recovery helper for mode 2 with `updelay` values from 0 through 10000 ms, checking traffic recovery after link disturbances.

State and persistence: Temporary network topology and bond state are created by `lag_lib.sh`; cleanup removes namespaces/devices.

Dependencies and integration points: Requires bonding balance-xor mode, veth/bridge, miimon support, and helper library.

Risks and test signals: Failures indicate mode 2 recovery, hashing, carrier, or updelay regressions. High delay cases intentionally extend runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/mode-2-recovery-updelay.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/netcons_over_bonding.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/netcons_over_bonding.sh

Purpose: Disruptive regression test for netpoll/netconsole interactions with bonding, including allowed netconsole on a bond and rejected netconsole on enslaved or unsupported interfaces.

Important APIs/functions: `setup_bonding_ifaces()`, `create_ifaces_bond()`, `link_ifaces_bond()`, `create_all_ifaces()`, `configure_ifaces_ips()`, `test_enable_netpoll_on_enslaved_iface()`, `test_delete_bond_and_reenable_target()`, `test_send_netcons_msg_through_bond_iface()`, `test_enslave_netcons_enabled_iface`, `test_enslave_iface_to_bond`, `test_enslave_iff_disabled_netpoll_iface`, `enable_netcons_ns()`, and `lib_netcons.sh` helpers.

Control flow: The script loads netdevsim, netconsole, bonding, and veth; creates TX/RX namespaces; creates four netdevsim ports and links them through netdevsim sysfs; bonds two TX and two RX ports; configures IPs; creates a dynamic netconsole target; sends a `/dev/kmsg` message through the bond; then tests rejection and disablement scenarios when netpoll is attached to enslaved devices or when enslaving devices into netpoll-enabled bonds.

State and persistence: Mutates kernel modules, configfs netconsole targets, namespaces, netdevsim devices, bonds, veths, `/proc/sys/kernel/printk`, and temporary output under `/tmp`. Cleanup removes targets and devices.

Dependencies and integration points: Requires configfs, netconsole dynamic target support, netdevsim, bonding, veth, socat, namespace helpers, and root privileges.

Risks and test signals: Highly stateful and disruptive. Failures indicate netpoll reference/eligibility bugs, bonding/netconsole coexistence issues, or cleanup ordering problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/netcons_over_bonding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/config

Purpose: Kernel config fragment for generic driver network selftests.

Important entries: `CONFIG_CONFIGFS_FS`, `CONFIG_DEBUG_INFO_BTF`, `CONFIG_INET_PSP`, `CONFIG_IPV6`, `CONFIG_MACSEC`, `CONFIG_NETCONSOLE`, `CONFIG_NETCONSOLE_DYNAMIC`, `CONFIG_NETCONSOLE_EXTENDED_LOG`, `CONFIG_NETDEVSIM`, `CONFIG_VLAN_8021Q`, and `CONFIG_XDP_SOCKETS`.

Control flow: No executable flow; declares required kernel capabilities.

State and persistence: Build/test configuration only.

Dependencies and integration points: Supports PSP, MACsec, netconsole, netdevsim, VLAN, XDP socket, BTF, and IPv6 tests listed in the parent Makefile.

Risks and test signals: Missing entries convert tests into skips or build/run failures. BTF and netdevsim are especially important for Python driver tests and BPF-adjacent coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/Makefile

Purpose: Build/install manifest for DSA-specific wrappers around forwarding selftests.

Important APIs/variables: `TEST_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, `forwarding.config`, `run_net_forwarding_test.sh`, and inclusion of `../../../lib.mk`.

Control flow: Registers bridge, MDB/MLD, VLAN aware/unaware/mcast, local termination, no-forwarding, TC action, and FDB stress tests. Most scripts are thin wrappers that source corresponding forwarding tests after applying DSA config.

State and persistence: Make-only state; runtime topology is owned by forwarding scripts.

Dependencies and integration points: Depends on `tools/testing/selftests/net/forwarding` scripts and libs, plus DSA-specific `forwarding.config`.

Risks and test signals: Missing includes or config file breaks wrappers. This Makefile is the bridge between driver DSA tests and shared net forwarding coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_locked_port.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_locked_port.sh

Purpose: DSA wrapper for the shared `bridge_locked_port.sh` forwarding selftest.

Important APIs/functions: Resolves `libdir`, derives `testname`, sources `forwarding.config`, changes directory to `../../../net/forwarding/`, and sources the matching forwarding script with passed arguments.

Control flow: No local test logic beyond selecting config and delegating to the shared forwarding test.

State and persistence: Runtime state is created by the delegated forwarding script using DSA topology settings from `forwarding.config`.

Dependencies and integration points: Requires the forwarding script of the same basename and DSA config. Integrates DSA hardware/switch topology with generic locked-port bridge validation.

Risks and test signals: Failures may originate in shared bridge locked-port logic, DSA hardware behavior, or local config resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_locked_port.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mdb.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mdb.sh

Purpose: DSA wrapper for shared bridge MDB forwarding tests.

Important APIs/functions: `readlink -f`, `basename`, source `forwarding.config`, `cd` into `net/forwarding`, and source `./bridge_mdb.sh "$@"`.

Control flow: Delegates all test cases to the common forwarding implementation under a DSA-specific configuration.

State and persistence: Delegated script creates bridge/MDB/runtime topology; wrapper persists nothing.

Dependencies and integration points: Requires DSA forwarding config and shared bridge MDB test. Exercises multicast database handling through DSA switch ports.

Risks and test signals: Failures can signal DSA MDB offload/bridge regressions or wrapper/config path problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mdb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mld.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mld.sh

Purpose: DSA wrapper for shared bridge MLD snooping/forwarding tests.

Important APIs/functions: Same wrapper pattern: resolve script directory/name, source `forwarding.config`, enter `net/forwarding`, and source matching test.

Control flow: Delegates all behavior to the common `bridge_mld.sh` forwarding script.

State and persistence: Runtime bridge/MLD state is created by the delegated script and cleaned there.

Dependencies and integration points: Requires IPv6 multicast support, DSA forwarding config, and shared forwarding libraries.

Risks and test signals: Failure points at DSA MLD handling or generic forwarding test failure under DSA topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_mld.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_aware.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_aware.sh

Purpose: DSA wrapper for bridge VLAN-aware forwarding tests.

Important APIs/functions: Local wrapper variables `libdir`/`testname`, `forwarding.config`, and sourcing `../../../net/forwarding/bridge_vlan_aware.sh`.

Control flow: Applies DSA config and delegates to the generic VLAN-aware bridge scenario.

State and persistence: Delegated test creates VLAN-aware bridge state; wrapper only changes shell working directory.

Dependencies and integration points: Requires VLAN filtering support on bridge/DSA ports and shared forwarding libs.

Risks and test signals: Failures indicate DSA VLAN-aware bridge offload/forwarding issues or config mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_aware.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_mcast.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_mcast.sh

Purpose: DSA wrapper for VLAN multicast bridge forwarding tests.

Important APIs/functions: Sources local `forwarding.config` then sources the shared forwarding test named by the wrapper basename.

Control flow: All test logic is delegated to `net/forwarding/bridge_vlan_mcast.sh`.

State and persistence: Bridge VLAN/multicast state is managed by the delegated script.

Dependencies and integration points: Requires DSA driver VLAN multicast support and generic forwarding helper stack.

Risks and test signals: Failures usually reflect multicast VLAN offload/forwarding regressions in DSA or missing testbed config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_mcast.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_unaware.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_unaware.sh

Purpose: DSA wrapper for bridge VLAN-unaware forwarding tests.

Important APIs/functions: Wrapper path resolution, local `forwarding.config`, `cd` to shared forwarding directory, and `source "./$testname" "$@"`.

Control flow: Delegates to the shared VLAN-unaware bridge test under DSA configuration.

State and persistence: Runtime state belongs to the shared test.

Dependencies and integration points: Requires DSA switch ports and common forwarding libraries.

Risks and test signals: Failures point at VLAN-unaware DSA bridge forwarding behavior or wrapper/config errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_vlan_unaware.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/local_termination.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/local_termination.sh

Purpose: DSA wrapper for local termination forwarding tests.

Important APIs/functions: Resolves local directory, sources `forwarding.config`, enters shared forwarding directory, sources matching `local_termination.sh`.

Control flow: Delegates all scenario setup and assertions to the shared forwarding test.

State and persistence: Delegated script manages interfaces, routes, and cleanup.

Dependencies and integration points: Exercises DSA local host termination paths through generic forwarding test infrastructure.

Risks and test signals: Failures may indicate DSA CPU-port/local-delivery regressions or incorrect config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/local_termination.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/no_forwarding.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/no_forwarding.sh

Purpose: DSA wrapper for shared no-forwarding isolation tests.

Important APIs/functions: Local config source plus forwarding script delegation.

Control flow: Executes the common no-forwarding test under DSA-specific port configuration.

State and persistence: No local state beyond shell variables; delegated test owns network state.

Dependencies and integration points: Requires DSA testbed and shared forwarding scripts.

Risks and test signals: Failures signal traffic leakage when forwarding should be disabled, DSA isolation issues, or wrapper/config failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/no_forwarding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/run_net_forwarding_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/run_net_forwarding_test.sh

Purpose: Generic DSA launcher that runs a named/shared net forwarding test with DSA config.

Important APIs/functions: `readlink -f`, `dirname`, source `forwarding.config`, `cd ../../../net/forwarding/`, and source a target test script.

Control flow: It is a delegation shim rather than a specific test case, allowing the DSA suite to invoke common forwarding tests consistently.

State and persistence: No own runtime network state; delegated test controls setup/cleanup.

Dependencies and integration points: Depends on local `forwarding.config` and the shared forwarding directory. Useful for tests listed as data files or ad hoc invocation.

Risks and test signals: Incorrect working directory or missing target script makes all delegated execution fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/run_net_forwarding_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_actions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_actions.sh

Purpose: DSA wrapper for shared TC actions forwarding tests.

Important APIs/functions: Sources DSA `forwarding.config` and delegates to `net/forwarding/tc_actions.sh`.

Control flow: No local test logic; it routes execution through shared forwarding infrastructure.

State and persistence: TC filters/actions and network state are created by delegated test.

Dependencies and integration points: Requires DSA TC offload/action support as applicable, TC tooling, and forwarding helpers.

Risks and test signals: Failures indicate DSA TC action offload/forwarding regressions or missing offload support expected by config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_actions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_taprio.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_taprio.sh

Purpose: DSA wrapper for a shared TAPRIO/time-aware scheduling forwarding test.

Important APIs/functions: Wrapper path resolution, `forwarding.config`, and source of matching forwarding script in `net/forwarding`.

Control flow: Delegates scenario execution to the shared TAPRIO test with DSA-specific interfaces.

State and persistence: Delegated script manages qdiscs, schedules, links, and cleanup.

Dependencies and integration points: Requires TC TAPRIO support and DSA hardware/testbed support for the scenario.

Risks and test signals: Failures can reflect TAPRIO offload/scheduling issues in DSA or unsupported hardware features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/tc_taprio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/test_bridge_fdb_stress.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/test_bridge_fdb_stress.sh

Purpose: DSA-oriented bridge FDB stress test wrapper.

Important APIs/functions: `cleanup()`, local config loading, bridge/FDB manipulation through shared forwarding helpers, and stress iteration logic in the sourced test path.

Control flow: The script prepares DSA forwarding context and runs an FDB stress scenario that creates/removes many forwarding database entries, then cleans up on exit.

State and persistence: Creates transient bridge/FDB entries and possibly large numbers of dynamic/static MAC entries; cleanup removes test state.

Dependencies and integration points: Requires DSA switch FDB programming support, bridge tooling, and forwarding libraries.

Risks and test signals: Failures indicate FDB resource, aging, add/delete, or offload synchronization problems. Stress volume can expose cleanup leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/test_bridge_fdb_stress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/gro.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/gro.py

Purpose: Python kselftest driver for Generic Receive Offload conformance across software GRO, hardware GRO, and LRO modes, with protocol correctness and capacity coverage.

Important APIs/functions: `NetDrvEpEnv`, `NetdevFamily`, `EthtoolFamily`, `ksft_variants`, `KsftNamedVariant`, `_resolve_dmac()`, `_write_defer_restore()`, `_set_mtu_restore()`, `_set_ethtool_feat()`, `_get_queue_stats()`, `_setup_isolated_queue()`, `_setup_queue_count()`, `_run_gro_bin()`, `_setup()`, `_gro_variants()`, `test()`, `_capacity_variants()`, `test_gro_capacity()`, and `main()`.

Control flow: `main()` creates a local/remote endpoint environment, attaches Netlink families, and runs variant-expanded tests. `_setup()` toggles ethtool features for `sw`, `hw`, or `lro`, adjusts MTU for large tests, and may install generic XDP as a workaround when HW GRO is coupled to SW GRO. `_run_gro_bin()` deploys/runs the compiled `gro` helper as RX locally and TX remotely. Protocol variants cover IPv4, IPv6, IP-in-IP, and IPv6-in-IPv6 with many coalescing/non-coalescing cases. Capacity variants isolate or resize queues and grow flow counts while parsing `STATS` output and queue stats.

State and persistence: Mutates sysfs GRO defer settings, MTU, ethtool features, RSS weights, ntuple filters, channel counts, XDP attachment, and deployed remote helper binaries. Cleanup uses `defer()`.

Dependencies and integration points: Requires net selftest Python library, compiled `gro` helper, ethtool Netlink, netdev qstats, remote endpoint, offload support, RSS/ntuple/channel features for capacity variants, and optional netdevsim handling.

Risks and test signals: Timing/coalescing is flaky, so main tests retry six times. Failures identify GRO protocol correctness, HW feature toggling, qstats reporting, queue steering, or capacity regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/gro.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hds.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hds.py

Purpose: Python kselftest for ethtool Netlink Header Data Split (HDS) ring attributes and their interaction with XDP and legacy ioctl ring changes.

Important APIs/functions: `NetDrvEnv`, `EthtoolFamily`, `NlError`, `ksft_run`, `ksft_eq`, `ksft_raises`, `_get_hds_mode()`, `_xdp_onoff()`, `_ioctl_ringparam_modify()`, `get_hds()`, `get_hds_thresh()`, `_hds_reset()`, `_defer_reset_hds()`, `set_hds_enable()`, `set_hds_disable()`, threshold setters, `set_xdp()`, `enabled_set_xdp()`, `ioctl()`, `ioctl_set_xdp()`, and `ioctl_enabled_set_xdp()`.

Control flow: `main()` creates a local driver environment with three queues and runs HDS get/set cases. Setters read ring capabilities, skip unsupported devices, apply `tcp-data-split` or `hds-thresh`, and verify via Netlink. XDP cases confirm XDP can attach when HDS is auto/unknown and fails when HDS is explicitly enabled. Ioctl cases perturb unrelated ring size through legacy ethtool ioctl and confirm HDS state survives.

State and persistence: Mutates ethtool ring attributes, XDP program attachment, and TX ring size. Deferred cleanup restores prior HDS/ring state.

Dependencies and integration points: Requires ethtool Netlink ring support, optional HDS thresholds, XDP dummy BPF object, and net selftest Python library.

Risks and test signals: The file contains duplicate `set_xdp`/`enabled_set_xdp` definitions; later definitions override earlier ones but behavior is similar. Failures indicate HDS Netlink ABI, validation, reset, XDP compatibility, or ioctl interaction regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hds.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/Makefile

Purpose: Build/install manifest for hardware-focused network driver selftests.

Important APIs/variables: `HAS_IOURING_ZCRX` compile probe, `COND_GEN_FILES`, `TEST_GEN_FILES`, `TEST_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, `YNL_GEN_FILES`, `YNL_GENS`, `../../../lib.mk`, `../../../net/ynl.mk`, `../../../net/bpf.mk`, and `LDLIBS += -luring` for `iou-zcrx`.

Control flow: The Makefile probes whether installed liburing exposes `io_uring_register_ifq`; if yes, it builds `iou-zcrx`, otherwise warns and excludes io_uring zero-copy receive tests. It registers many Python/shell hardware tests, YNL-generated `ncdevmem` and `toeplitz` helpers, BPF objects, and shared ethtool library files.

State and persistence: Produces generated binaries, YNL userspace headers/helpers, and BPF objects in the kselftest output tree.

Dependencies and integration points: Depends on liburing, kernel headers, YNL, BPF build support, net/forwarding libraries, and hardware-capable test environment.

Risks and test signals: Missing liburing silently reduces coverage. Incorrect YNL/BPF ordering breaks generated helper builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/config

Purpose: Kernel config fragment for hardware network driver selftests.

Important entries: BPF syscall, fault injection, ESP/IPsec offload for IPv4/IPv6, io_uring, IPv6/GRE, net classifier/action/BPF, netkit, ingress qdisc, udmabuf, VXLAN, and XFRM user support.

Control flow: No executable flow; declares kernel features required by tests in `hw/`.

State and persistence: Build/test configuration only.

Dependencies and integration points: Enables feature families used by `devmem.py`, `ncdevmem.c`, `iou-zcrx`, IPsec/VXLAN offload, TC tests, XDP/BPF metadata tests, and fault injection tests.

Risks and test signals: Missing entries cause tests to skip, fail at setup, or omit generated helper functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/csum.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/csum.py

Purpose: Python wrapper for the generic `tools/testing/selftests/net/csum` helper, focused on NIC checksum offload RX/TX behavior.

Important APIs/functions: `NetDrvEpEnv`, `EthtoolFamily`, `test_receive()`, `test_transmit()`, `test_builder()`, `check_nic_features()`, `bkg()`, `wait_port_listen()`, remote helper deployment, and `ksft_run`.

Control flow: `main()` creates a local/remote endpoint, queries active ethtool checksum features, deploys the compiled `csum` helper remotely, dynamically builds IPv4/IPv6 RX/TX test cases, and runs them. RX tests run the local receiver while the remote sends crafted packets; TX tests run the remote verifier while the local NIC transmits offloaded packets.

State and persistence: Only transient background processes and remote-deployed helper binaries. It does not change NIC features.

Dependencies and integration points: Requires checksum offload features, remote endpoint environment, compiled `csum` helper, UDP/TCP traffic, and ethtool Netlink feature reporting.

Risks and test signals: Unsupported offloads skip relevant cases. Failures indicate checksum validation/offload regressions for TCP/UDP, invalid checksum handling, or zero UDP checksum semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/csum.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_port_split.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_port_split.py

Purpose: Standalone Python test for devlink port split behavior based on the `lanes` and `splittable` port attributes.

Important APIs/functions: `run_command()`, `devlink_ports.get_if_names()`, `get_max_lanes()`, `get_split_ability()`, `split()`, `unsplit()`, `exists()`, `exists_and_lanes()`, `test()`, `create_split_group()`, `split_unsplittable_port()`, `split_splittable_port()`, `validate_devlink_output()`, `make_parser()`, and `main()`.

Control flow: It selects a devlink device from `--dev` or the first `devlink -j dev show` entry, enumerates physical ports, skips if no lanes info exists, verifies one-lane ports are unsplittable, and for wider ports iteratively splits to valid counts, waits for udev to settle, verifies split netdev names and lane counts, then unsplits.

State and persistence: Mutates physical devlink port split state and relies on unsplit cleanup after each split. No explicit trap exists, so interruption can leave ports split.

Dependencies and integration points: Requires devlink JSON output with `flavour`, `lanes`, `splittable`, `netdev`, udevadm, and hardware supporting port split.

Risks and test signals: Disruptive to physical port layout. Failures signal devlink lane reporting, split validation, netdev creation, or unsplit regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_port_split.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_rate_tc_bw.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_rate_tc_bw.py

Purpose: Hardware test for devlink rate traffic-class bandwidth distribution through a switchdev/SR-IOV VF, VLAN priorities, and optional mqprio TC mapping.

Important APIs/functions: `BandwidthValidator`, `setup_vf()`, `setup_vlans_on_vf()`, `get_vf_info()`, `setup_bridge()`, `setup_devlink_rate()`, `setup_remote_vlans()`, `setup_test_environment()`, `measure_bandwidth()`, `run_bandwidth_test()`, `calculate_bandwidth_percentages()`, `verify_total_bandwidth()`, `run_bandwidth_distribution_test()`, `test_no_tc_mapping_bandwidth()`, `test_tc_mapping_bandwidth()`, `DevlinkFamily`, and `Iperf3Runner`.

Control flow: `main()` discovers the PCI device for the test NIC, initializes validators for total 1 Gbps and 20/80 TC split, then runs no-mapping and mapping cases. Setup enables switchdev, creates one VF, optionally adds mqprio, creates VLAN 101/102 mapped to TC3/TC4, locates the representor, bridges uplink and representor, configures devlink rate `tx_max` and `rate-tc-bws`, mirrors VLANs on the remote endpoint, then runs two parallel iperf3 measurements and validates distribution.

State and persistence: Disruptively changes eswitch mode, `sriov_numvfs`, bridge membership, VLAN devices, mqprio, and devlink rate state. Cleanup is via `defer()`.

Dependencies and integration points: Requires PCI NIC with switchdev/SR-IOV/devlink-rate support, remote endpoint, iperf3, VLAN, bridge, mqprio, and devlink Netlink family.

Risks and test signals: Highly hardware-specific. The mlx5 no-mapping behavior is expected-fail aware. Failures show rate API, representor discovery, TC mapping, bandwidth enforcement, or measurement regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_rate_tc_bw.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devmem.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devmem.py

Purpose: Python kselftest wrapper for `ncdevmem`, validating TCP device-memory RX/TX and HDS payload-size behavior.

Important APIs/functions: `require_devmem()`, `check_rx()`, `check_tx()`, `check_tx_chunks()`, `check_rx_hds()`, `NetDrvEpEnv`, `ksft_disruptive`, `bkg`, `cmd`, `rand_port`, `wait_port_listen`, `socat`, and `ksft_eq`.

Control flow: `require_devmem()` probes `ncdevmem -f IFACE`. RX test runs `ncdevmem` listening locally and sends a known byte stream from the remote via socat. TX tests run remote socat listener and pipe local text through `ncdevmem`, with and without chunking. HDS test iterates payload sizes from 1 byte to 8192 bytes and verifies `ncdevmem` receive success with `-L` fail-on-linear.

State and persistence: Starts background helpers and uses remote deployment. It relies on `ncdevmem` to mutate NIC devmem binding, queues, RSS, and HDS state.

Dependencies and integration points: Requires `ncdevmem` binary, devmem TCP support, udmabuf, remote endpoint, socat, and disruptive test permissions.

Risks and test signals: Failures identify device memory RX/TX, zerocopy send, header split, queue binding, or chunking regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devmem.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool.sh

Purpose: Hardware link-mode/autonegotiation selftest using two connected interfaces.

Important APIs/functions: `h1_create()`, `h1_destroy()`, `h2_create()`, `h2_destroy()`, `setup_prepare()`, `cleanup()`, `same_speeds_autoneg_off()`, `different_speeds_autoneg_off()`, `combination_of_neg_on_and_off()`, `hex_speed_value_get()`, `subset_of_common_speeds_get()`, `speed_to_advertise_get()`, `advertise_subset_of_speeds()`, `check_highest_speed_is_chosen()`, `different_speeds_autoneg_on()`, and helpers from `ethtool_lib.sh`.

Control flow: The script initializes two interfaces with IPv4 addresses, builds a map of ethtool link mode bit positions, then runs tests for forced matching speeds, forced mismatched speeds, forced-vs-autoneg, advertising subsets, highest speed selection, and incompatible advertised modes. It checks link readiness and ping success/failure.

State and persistence: Changes ethtool speed/autoneg/advertise settings and restores autoneg at the end of cases. Interface IP state is cleaned by forwarding helpers.

Dependencies and integration points: Requires two cabled ports, ethtool link mode reporting, forwarding `lib.sh`, and common speed helper library.

Risks and test signals: Hardware support varies. Failures may indicate driver PHY link mode, autoneg advertisement, forced speed, or reporting regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_extended_state.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_extended_state.sh

Purpose: Tests ethtool extended link state/substate reporting for no partner and forced-mode mismatch scenarios.

Important APIs/functions: `setup_prepare()`, `ethtool_ext_state()`, `autoneg()`, `autoneg_force_mode()`, `no_cable()`, `busywait`, `ethtool_set`, `different_speeds_get`, and forwarding helpers.

Control flow: It selects two connected ports plus `NETIF_NO_CABLE`, checks a single up port reports `Autoneg, No partner detected`, forces different speeds on two ports and checks `No partner detected during force mode`, and checks the no-cable interface reports expected extended state.

State and persistence: Changes link up/down and ethtool speed/autoneg settings; cleanup/restoration comes from helper behavior.

Dependencies and integration points: Requires ethtool extended state strings, cabled and no-cable interfaces, and common ethtool library.

Risks and test signals: String parsing is sensitive to ethtool output format. Failures indicate extended state reporting regressions or unsupported testbed topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_extended_state.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_lib.sh

Purpose: Shared shell helpers for ethtool speed/autoneg tests.

Important APIs/functions: `speeds_arr_get()`, `ethtool_set()`, `dev_linkmodes_params_get()`, `dev_speeds_get()`, `common_speeds_get()`, and `different_speeds_get()`.

Control flow: Helpers parse ethtool supported/advertised link modes, build arrays of speed values or full mode names, identify common supported speeds between devices, and select differing speeds. `ethtool_set()` centralizes command execution and `RET` error tracking.

State and persistence: No own persistent state, but helper callers use it to mutate ethtool settings.

Dependencies and integration points: Used by ethtool hardware shell tests. Depends on ethtool text output conventions and global `RET`/`check_err` style from forwarding libs.

Risks and test signals: Parser fragility can produce false skips/failures if ethtool output changes or mode names are unexpected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_mm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_mm.sh

Purpose: Tests MAC Merge / frame preemption configuration and verification through ethtool on two connected interfaces.

Important APIs/functions: `traffic_test()`, `manual_with_verification()`, directional wrappers, `manual_without_verification()`, `manual_failed_verification()`, `smallest_supported_add_frag_size()`, `expected_add_frag_size()`, `lldp_change_add_frag_size()`, `lldp()`, `h1_create()`, `h2_create()`, cleanup/setup helpers, ethtool MM commands, and LLDP traffic handling.

Control flow: The script initializes two interfaces, configures MAC Merge in multiple modes, sends traffic to validate connectivity, checks verification success/failure expectations, calculates supported add-frag-size values, and verifies LLDP interaction with add-frag-size configuration.

State and persistence: Mutates ethtool MM/preemption settings, link state, and possibly LLDP-related state; cleanup restores interface setup through forwarding helpers.

Dependencies and integration points: Requires hardware and driver support for ethtool MM, two connected ports, forwarding helpers, and traffic generation.

Risks and test signals: Failures map to MAC Merge verification, add-frag-size validation, LLDP integration, or ethtool MM reporting regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_mm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_rmon.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_rmon.sh

Purpose: Tests ethtool RMON histogram bucket counters for RX and TX traffic sizes.

Important APIs/functions: `ensure_mtu()`, `bucket_test()`, `rmon_histogram()`, `rmon_rx_histogram()`, `rmon_tx_histogram()`, `setup_prepare()`, `cleanup()`, ethtool statistics, and forwarding traffic helpers.

Control flow: It prepares two interfaces, ensures MTU can support target frame sizes, sends traffic matching bucket boundaries, reads RMON histogram counters, and checks that expected buckets increment for RX/TX directions.

State and persistence: Temporarily changes MTU and uses interface counters. Cleanup restores interface setup.

Dependencies and integration points: Requires ethtool RMON stats support, connected interfaces, traffic generation, and forwarding helper library.

Risks and test signals: Counter settle timing and hardware counter granularity can affect results. Failures indicate RMON stats reporting or bucket classification regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_rmon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_std_stats.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_std_stats.sh

Purpose: Tests standard ethtool counter groups for Ethernet control, MAC, and pause statistics.

Important APIs/functions: `traffic_test()`, `test_eth_ctrl_stats()`, `test_eth_mac_stats()`, `test_pause_stats()`, `setup_prepare()`, `check_ethtool_counter_group_support`, ethtool stats group queries, and forwarding traffic helpers.

Control flow: After setup, the script checks counter group support, sends traffic, reads relevant ethtool standard stat groups, and verifies expected counters increase or remain sane for control/MAC/pause categories.

State and persistence: Uses live interface counters and temporary forwarding topology. No persistent file state.

Dependencies and integration points: Requires ethtool standard statistics groups and two connected test interfaces.

Risks and test signals: Failures identify missing or incorrect standard stat reporting, pause frame accounting, or traffic counter regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_std_stats.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/gro_hw.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/gro_hw.py

Purpose: Hardware GRO selftest focused on device machinery, queue stats, and ordering rather than full protocol conformance.

Important APIs/functions: `NetDrvEpEnv`, `NetdevFamily`, `_get_queue_stats()`, `_resolve_dmac()`, `_setup_isolated_queue()`, `_run_gro_test()`, `_require_hw_gro_stats()`, `_set_ethtool_feat()`, `_setup_hw_gro()`, `_check_gro_stats()`, `test_gro_stats_single()`, `test_gro_stats_full()`, variant `test_gro_order()`, and `ksft_run`.

Control flow: Setup enables HW GRO while disabling SW GRO/LRO, possibly attaching generic XDP if the driver couples features. Tests isolate queue 1 with RSS weights and ntuple steering, require qstats fields, run the `gro` helper, and compare qstats deltas against expected RX/GRO/wire-packet counts. Ordering variants send increasing flow counts with order checking.

State and persistence: Mutates ethtool features, RSS context, ntuple filters, and optional XDP program, restored through `defer()`.

Dependencies and integration points: Requires HW GRO support, netdev queue stats including `rx-hw-gro-*`, compiled `gro` helper, remote endpoint, and ntuple/RSS control.

Risks and test signals: Failures indicate qstats inaccuracies, HW GRO counter semantics, ordering problems, or feature toggling regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/gro_hw.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3.sh

Purpose: Tests L3 hardware statistics enablement/reporting on routed VLAN interfaces for IPv4 and IPv6 RX/TX paths.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, router port create/destroy helpers, `setup_prepare()`, `cleanup()`, `ping_ipv4()`, `ping_ipv6()`, packet send helpers, `___test_stats()`, `__test_stats()`, per-direction/per-IP tests, `respin_enablement()`, `reapply_config()`, `__test_stats_report()`, `test_destroy_enabled()`, and `test_double_enable()`.

Control flow: The script builds a routed two-host/two-router-port topology with VLAN 200 and VRFs/routes, verifies ping, enables L3 hardware stats on RX/TX paths, sends packets, checks stat deltas, toggles/reapplies configuration, verifies report output, tests destruction while enabled, and double-enable semantics.

State and persistence: Creates VLANs, VRFs/routes, L3 stats configuration, TC/common forwarding state, and interface counters. Cleanup removes topology.

Dependencies and integration points: Requires hardware L3 stats support, VLAN, VRF/route setup, forwarding and TC common libraries, IPv4/IPv6 traffic.

Risks and test signals: Failures reveal L3 stats enable/report/delete bugs, stat direction mixups, persistence across reapply, or teardown leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3_gre.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3_gre.sh

Purpose: Tests L3 hardware stats over GRE tunnel traffic.

Important APIs/functions: `setup_prepare()`, `cleanup()`, `ping_ipv4()`, `send_packets_ipv4()`, `test_stats()`, `test_stats_tx()`, `test_stats_rx()`, GRE tunnel setup, and forwarding helper assertions.

Control flow: It prepares a GRE-capable topology, verifies IPv4 reachability, sends GRE-encapsulated packets, and checks L3 hardware stat counters for TX and RX directions.

State and persistence: Creates GRE tunnel interfaces/routes/stat config and removes them in cleanup.

Dependencies and integration points: Requires GRE, hardware L3 stats support, forwarding libs, and IPv4 connectivity.

Risks and test signals: Failures indicate stats accounting issues for tunneled packets or GRE offload/stat integration problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3_gre.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.c

Purpose: C client/server helper for testing io_uring zero-copy receive (`IORING_OP_RECV_ZC`) with network interface queue registration.

Important APIs/types/functions: `liburing`, custom `t_io_uring_zcrx_ifq_reg`, `io_uring_register_ifq`, `io_uring_zcrx_area_reg`, `io_uring_region_desc`, `io_uring_zcrx_rq`, `parse_address()`, `get_refill_ring_size()`, `setup_zcrx()`, `add_accept()`, `add_recvzc()`, `add_recvzc_oneshot()`, `process_accept()`, `process_recvzc()`, `server_loop()`, `run_server()`, `run_client()`, `parse_opts()`, and `main()`.

Control flow: `main()` allocates a deterministic payload, parses server/client options, and runs either a TCP server or client. The server opens an IPv6 socket, initializes an io_uring with CQE32 and task-run flags, registers an interface queue and user refill ring/memory area, accepts one connection, posts multishot or one-shot zero-copy receives, validates payload bytes from CQEs against the known pattern, and returns buffers to the refill ring. The client connects and sends the payload in configured chunks.

State and persistence: Uses global config and runtime counters, mmaps receive area and refill ring, owns one TCP connection, and writes refill-ring tail. No persistent files.

Dependencies and integration points: Requires new liburing/kernel ZCRX APIs, io_uring, NIC queue support, optional huge pages for large chunks, and the Python `iou-zcrx.py` orchestrator.

Risks and test signals: Skips with code 42 for unsupported large chunks/huge pages. Failures indicate registration, refill-ring, CQE parsing, payload integrity, oneshot/multishot, or queue binding regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.py

Purpose: Python orchestrator for the `iou-zcrx` C helper, covering single queue, RSS context, one-shot receive, and large chunk modes.

Important APIs/functions: `mp_clear_wait()`, `create_rss_ctx()`, `set_flow_rule()`, `set_flow_rule_rss()`, `single()`, `rss()`, `test_zcrx()`, `test_zcrx_oneshot()`, `test_zcrx_large_chunks()`, `NetDrvEpEnv`, `ksft_variants`, `bkg`, `cmd`, `ethtool`, `wait_port_listen`, and `defer`.

Control flow: Setup functions configure memory-provider state, RSS contexts, and ntuple flow rules to steer traffic. `test_zcrx()` starts the local server helper on a queue, waits for the port, and runs the remote client helper. One-shot mode repeats receive submission behavior. Large chunk mode probes/uses larger receive buffers and skips when unsupported.

State and persistence: Mutates ethtool ntuple rules, RSS contexts, and memory-provider state; cleanup uses `defer()` and `mp_clear_wait()`.

Dependencies and integration points: Requires compiled `iou-zcrx`, remote endpoint, ethtool RSS/ntuple support, io_uring ZCRX kernel support, and queue IDs.

Risks and test signals: Failures identify orchestration, flow steering, memory-provider clearing, RSS context, one-shot receive, or large chunk support regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ipsec_vxlan.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ipsec_vxlan.py

Purpose: Tests VXLAN traffic protected by IPsec transport-mode crypto offload, ensuring no physical TX drops and minimum throughput.

Important APIs/functions: `xfrm()`, `check_xfrm_offload_support()`, `check_esp_hw_offload()`, `get_tx_drops()`, `setup_vxlan_ipsec()`, `_vxlan_ipsec_variants()`, `test_vxlan_ipsec_crypto_offload()`, `NetDrvEpEnv`, `Iperf3Runner`, `ksft_variants`, and `defer()`.

Control flow: For each outer/inner IPv4/IPv6 variant, the test checks ESP hardware offload, creates matching VXLAN devices locally/remotely, configures local offloaded XFRM states and mirrored remote software XFRM states, installs UDP dport 4789 policies, validates ping through inner tunnel, measures reverse iperf3 bandwidth, and checks physical TX drops did not increase.

State and persistence: Creates VXLAN links, addresses, XFRM states/policies on local and remote hosts, and reads physical link counters. Deferred cleanup removes all configured objects.

Dependencies and integration points: Requires ESP hardware offload, iproute2 XFRM offload syntax, VXLAN, IPv4/IPv6, remote endpoint, and iperf3.

Risks and test signals: Failures indicate XFRM offload, VXLAN encapsulation, GSO/checksum, drop accounting, or throughput regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ipsec_vxlan.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/irq.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/irq.py

Purpose: Tests driver IRQ reporting and affinity behavior across queue/XDP/link reconfiguration.

Important APIs/functions: `read_affinity()`, `write_affinity()`, `check_irqs_reported()`, `_check_reconfig()`, `check_reconfig_queues()`, `check_reconfig_xdp()`, `check_down()`, `NetDrvEnv`, `EthtoolFamily`, `NetdevFamily`, `ksft_disruptive`, `ip`, `cmd`, and `defer`.

Control flow: The script reads IRQs reported through netdev/ethtool Netlink, writes and restores IRQ affinity, then runs reconfiguration callbacks such as channel count changes, XDP attach/detach, and link down/up while verifying IRQs remain reported and affinity behavior is stable.

State and persistence: Writes `/proc/irq/*/smp_affinity`, changes channels, attaches XDP, and toggles interface state. Defer restores settings where possible.

Dependencies and integration points: Requires IRQ reporting support, writable affinity, ethtool/netdev Netlink families, XDP dummy BPF, and disruptive permissions.

Risks and test signals: Affinity writes are host-sensitive. Failures indicate IRQ Netlink reporting, driver reconfiguration, XDP queue, or affinity persistence regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/irq.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/lib/py/__init__.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/lib/py/__init__.py

Purpose: Re-export layer that makes shared `tools/testing/selftests/net/lib/py` helpers available to hardware driver tests through a local `lib.py` import path.

Important APIs/types: `KSFT_DIR`, `sys.path.append`, and re-exported classes/functions including `NetNS`, `NetdevSimDev`, `EthtoolFamily`, `NetdevFamily`, `DevlinkFamily`, `NlError`, `CmdExitFailure`, `bkg`, `cmd`, `defer`, `ethtool`, `ip`, BPF helpers, `KsftSkipEx`, `KsftFailEx`, `KsftXfailEx`, `ksft_run`, `ksft_exit`, `ksft_variants`, and environment classes.

Control flow: On import, it computes the kselftest root, appends it to `sys.path`, and imports selected helpers one by one from `net.lib.py` to avoid lint false positives.

State and persistence: Mutates Python process import path only.

Dependencies and integration points: Central integration point for most Python files in `drivers/net/hw`, allowing local relative imports while sharing common framework code.

Risks and test signals: Path calculation must remain correct relative to this file. Import failures break most hardware Python tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/lib/py/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/loopback.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/loopback.sh

Purpose: Tests hardware loopback behavior between two interfaces.

Important APIs/functions: `h1_create()`, `h1_destroy()`, `h2_create()`, `h2_destroy()`, `loopback_test()`, `setup_prepare()`, `cleanup()`, forwarding `simple_if_init/fini`, link setup, and ping checks.

Control flow: The script initializes two interfaces, configures loopback mode or relevant hardware state, sends traffic, and verifies packets loop as expected without requiring external forwarding beyond the test setup.

State and persistence: Mutates interface addresses and loopback/link settings, cleaned on exit.

Dependencies and integration points: Requires two test interfaces and driver support for the loopback operation being exercised, plus forwarding lib helpers.

Risks and test signals: Failures indicate loopback mode setup, traffic delivery, or cleanup regressions. Hardware support variability may cause skips or setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/loopback.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ncdevmem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ncdevmem.c

Purpose: C netcat-like helper for TCP device-memory tests using udmabuf as a mock dmabuf provider; supports RX devmem, TX devmem, validation, queue binding, header split, RSS steering, and zerocopy completions.

Important APIs/types/functions: `struct memory_buffer`, `struct memory_provider`, `udmabuf_alloc/free`, DMA_BUF sync ioctls, `validate_buffer()`, command helpers, `ethtool_add_flow()`, `rxq_num()`, `reset_flow_steering()`, `get_ring_config()`, `restore_ring_config()`, `configure_headersplit()`, `configure_rss()`, `check_changing_channels()`, `configure_flow_steering()`, `bind_rx_queue()`, `bind_tx_queue()`, `enable_reuseaddr()`, `parse_address()`, `create_queues()`, `do_server()`, `run_devmem_tests()`, `wait_compl()`, `do_client()`, and `main()`.

Control flow: Without server/client addresses, `main()` runs self-tests that allocate udmabuf memory, discover queues, configure RSS and header split, verify invalid bind cases fail, bind RX queues, and ensure channel deactivation is rejected while queues are bound. In server mode, it enables header split/RSS, installs ntuple steering, binds RX queues to a dmabuf through YNL netdev `bind-rx`, listens for TCP, receives with `MSG_SOCK_DEVMEM`, parses `SCM_DEVMEM_DMABUF`/`SCM_DEVMEM_LINEAR` control messages, validates/copies fragments, and returns tokens with `SO_DEVMEM_DONTNEED`. In client mode, it binds TX dmabuf, enables `SO_ZEROCOPY`, copies stdin into udmabuf, sends `SCM_DEVMEM_DMABUF` with `MSG_ZEROCOPY`, and waits for error-queue zerocopy completion.

State and persistence: Creates udmabuf/memfd mappings, mutates ethtool channels/rings/RSS/ntuple rules, binds netdev RX/TX queues to dmabufs, uses sockets and error queues, and cleans most state via explicit unwind labels.

Dependencies and integration points: Requires `/dev/udmabuf`, DMA_BUF sync, YNL-generated `netdev-user.h` and `ethtool-user.h`, netdev devmem APIs, ethtool Netlink, ntuple support, header split, RSS, zerocopy sockets, and queue-capable hardware.

Risks and test signals: Complex cleanup means partial setup failures can leave device config if unwind is wrong. Failures indicate devmem queue binding, header split, RSS steering, dmabuf token, linear fallback, zerocopy TX completion, or validation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ncdevmem.c -->
