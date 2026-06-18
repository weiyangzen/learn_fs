# Research: subset-b-006831

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_torture.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_torture.sh

Purpose: Stress-tests dynamic netconsole target lifetime and transmit paths under concurrent reconfiguration. It repeatedly writes kernel log messages while enabling/disabling the primary configfs target, creating/removing extra dynamic targets, and flapping the source interface.

Important APIs/functions: Uses `lib_netcons.sh` for `check_for_dependencies`, `set_network`, `create_dynamic_target`, `_create_dynamic_target`, and `cleanup`. Local helpers are `create_and_delete_random_target`, `toggle_netcons_target`, and `toggle_iface`. Kernel integration is through `/dev/kmsg`, `/proc/sys/kernel/printk`, configfs under `NETCONS_CONFIGFS`, `ip link`, and `modprobe netconsole/netdevsim`.

Control flow: The script fixes extended IPv6 mode, prepares a namespace/interface topology, creates one target, then loops `ITERATIONS` times writing ten messages per iteration. Every 30/50/70 iterations it starts a background target toggle, random target churn, or interface down/up job. A final `wait` synchronizes all background work before returning `EXIT_STATUS`.

State and persistence: State is transient kernel configfs directories, printk level, namespaces, and netdevsim links. The `trap cleanup EXIT` path is the persistence boundary and should remove dynamic targets and network setup.

Dependencies and integration: Requires root, configfs netconsole dynamic support, netdevsim, netconsole, `iproute2`, and the netconsole shell library. It is most valuable with LOCKDEP, KASAN, and kmemleak enabled because success is mainly absence of kernel diagnostics.

Risks: Races are intentional; writes to `enabled` can fail under lock contention and are tolerated. `mktemp -u` has a small name collision risk, partly checked before use. Failures may appear as kernel warnings rather than shell errors.

Test signals: PASS is clean completion with no lockdep/KASAN/kmemleak reports, no leaked configfs targets, no stuck namespace/device state, and successful concurrent message emission under target churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_torture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/Makefile

Purpose: Registers the netdevsim driver selftests with the kselftest build/run harness.

Important APIs/variables: `TEST_PROGS` lists executable test programs for devlink, ethtool, FIB, nexthop, peer, psample, qdisc visibility, and UDP tunnel offload coverage. `TEST_FILES` declares the shared helper `ethtool-common.sh`. `include ../../../lib.mk` imports kselftest install and run rules.

Control flow: There is no runtime logic. During `make` or kselftest installation, `lib.mk` consumes these variables to copy scripts into the test output and run `TEST_PROGS` as separate tests.

State and persistence: No state is created by the Makefile itself. It only determines which files are installed and therefore which scripts can be invoked by the harness.

Dependencies and integration: Integrates this directory with Linux kselftest. It assumes each listed script is self-contained or includes declared helper files. Kernel feature requirements are expressed separately in `config`.

Risks: A script omitted from `TEST_PROGS` will not run in normal kselftest flows. A helper omitted from `TEST_FILES` may be missing from installed test trees. Ordering is mostly independent, but many scripts require root and mutable netdevsim state.

Test signals: Build/install output should include every listed program and `ethtool-common.sh`; kselftest runners should discover the same program set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/config

Purpose: Documents kernel configuration options needed for the netdevsim selftests.

Important entries: Requires `CONFIG_NETDEVSIM=m`, `CONFIG_DUMMY=y`, IPv6, scheduler qdiscs (`MQPRIO`, `MULTIQ`, `PRIO`), `CONFIG_PSAMPLE=y`, tunnel modules (`VXLAN`, `GENEVE`), `CONFIG_MACSEC=m`, and `CONFIG_PTP_1588_CLOCK_MOCK=y`.

Control flow: No executable flow. Kselftest config tooling can merge these symbols into a test kernel configuration.

State and persistence: No runtime state. It influences whether modules and kernel subsystems are available when tests run.

Dependencies and integration: Directly supports scripts in the same directory. Devlink, FIB, nexthop, ethtool, psample, UDP tunnel NIC, and qdisc tests all assume these kernel facilities are present.

Risks: Some scripts also require userspace tools (`ip`, `devlink`, `ethtool`, `jq`, `tc`, `socat`, `udevadm`) that are not represented here. A built-in/module mismatch can matter when scripts expect `modprobe` and `modprobe -r` to work.

Test signals: A suitable kernel should expose `/sys/bus/netdevsim`, debugfs netdevsim controls, PSAMPLE netlink, qdisc kinds, and tunnel device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink.sh

Purpose: Provides broad devlink API regression coverage using a controllable netdevsim device.

Important APIs/functions: Exercises `devlink dev flash`, parameters, default parameter values, regions/snapshots, reload, namespace reload, resources, resource dumps, `devlink dev info`, health reporters, port resources, eswitch/rate objects, and rate attributes including `tx_share`, `tx_max`, parent, and `tc-bw`. Helpers include `param_get`, `param_set`, `check_value`, `res_val_get`, `check_reporter_info`, rate accessors, and `devlink_wait`.

Control flow: `setup_prepare` loads netdevsim and creates `netdevsim10` with four ports. `tests_run` executes `ALL_TESTS`; each test mutates devlink state and verifies either devlink JSON output, debugfs mirrors, or expected command failure. Cleanup deletes the device and unloads the module.

State and persistence: Uses `/sys/bus/netdevsim/new_device`, debugfs knobs under `/sys/kernel/debug/netdevsim/netdevsim10`, devlink objects, network namespaces, SR-IOV VFs, and devlink resource sizes. All should be reverted by test-local cleanup or device deletion.

Dependencies and integration: Sources forwarding `lib.sh` for `check_err`, `check_fail`, `cmd_jq`, `busywait`, `tests_run`, and logging. Requires `devlink`, `jq`, namespace support, debugfs, firmware files for flash, and netdevsim devlink implementation.

Risks: It depends on exact devlink CLI JSON shape and feature availability; several subtests skip when CLI support is missing. Namespace reload and resource tests can leave namespaces if interrupted before cleanup. Health/rate checks rely on debugfs values matching devlink state.

Test signals: Expected passes include correct parameter commit-on-reload behavior, rejected invalid flashes/resources, snapshot read bounds, reporter state/recovery counters, resource visibility by scope, and rate object debugfs/API consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_in_netns.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_in_netns.sh

Purpose: Verifies that a netdevsim devlink instance created inside a network namespace is visible and has usable port-to-netdev mappings from that namespace.

Important APIs/functions: `port_netdev_get` parses `devlink -N testns1 port show -j` with `cmd_jq`. `check_devlink_test` runs `devlink -N testns1 dev show`. `check_ports_test` validates each port netdev exists with `ip -n testns1 link show`.

Control flow: `setup_prepare` loads netdevsim, creates `testns1`, and writes `BUS_ADDR PORT_COUNT` to `/sys/bus/netdevsim/new_device` from inside the namespace. After sysfs net directory appears, `tests_run` executes the two checks. Cleanup deletes the netdevsim device, namespace, and module.

State and persistence: Creates one namespace and one netdevsim device with four ports. State is expected to disappear after writing `BUS_ADDR` to `del_device` and deleting the namespace.

Dependencies and integration: Uses forwarding `lib.sh`, `devlink`, `ip netns`, `jq`, `/sys/bus/netdevsim`, and root privileges.

Risks: The script busy-waits without sleep for sysfs visibility. Device deletion is written from the initial namespace and assumes the bus device remains reachable. Failures in namespace creation or device creation before trap setup could leave state.

Test signals: Devlink device show succeeds in the namespace, every devlink port reports a netdev name, and each reported netdev is found by namespaced `ip link`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_in_netns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_trap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_trap.sh

Purpose: Tests devlink trap, group, policer, statistics, metadata, and lifecycle behavior implemented by netdevsim.

Important APIs/functions: Sources `devlink_lib.sh` for trap helpers such as `devlink_traps_get`, action/group setters, metadata checks, stats idle checks, policer helpers, and trap group operations. Local tests cover initialization, valid/invalid trap actions, metadata, stats, group actions/stats, policers, policer binding, port deletion, and device deletion.

Control flow: The script validates netdevsim support and device-id availability, creates a netdevsim device and associated netdev, then runs `ALL_TESTS`. Tests iterate over registered traps/groups/policers and use debugfs fault knobs such as `fail_trap_drop_counter_get`. Cleanup removes device/module state.

State and persistence: Mutates devlink trap action/group/policer settings, interface up/down state, and netdevsim debugfs failure toggles. Port and device deletion tests intentionally remove resources to validate devlink cleanup.

Dependencies and integration: Requires `devlink`, `udevadm`, `iproute2`, `jq`, netdevsim debugfs, and forwarding test libraries. The device under test is `netdevsim1337`.

Risks: Trap stats behavior depends on whether the netdev is up; the script forcibly downs it if necessary. Devlink trap names and metadata are kernel ABI-sensitive. Tests that delete ports/devices must be ordered so later tests do not expect removed objects.

Test signals: PASS requires registered traps, immutable action for non-drop traps, mutable drop traps, expected metadata, invalid operation rejection, stats counters changing or idling as specified, policer binding correctness, and clean devlink object removal after port/device deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_trap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-coalesce.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-coalesce.sh

Purpose: Validates ethtool coalescing configuration on a generated netdevsim netdev.

Important APIs/functions: Sources `ethtool-common.sh` for `make_netdev`, `check`, and cleanup. `SETTINGS_MAP` maps ethtool `-C` option names to `ethtool -c` output labels. `get_value` reads current settings via `awk`; `update_current_settings` refreshes an associative array for comparison.

Control flow: The script skips if ethtool lacks coalesce support, creates a netdevsim netdev, captures initial expected values, then iterates over all coalesce knobs assigning random 32-bit values with `ethtool -C`. After each change it compares the full current settings vector to the expected vector. It separately tests `adaptive-rx` and `adaptive-tx` display formatting.

State and persistence: Mutates coalesce settings on the temporary netdevsim port. The helper trap should delete the netdevsim device on exit.

Dependencies and integration: Requires bash associative arrays, ethtool text output format, netdevsim, and the local common helper.

Risks: Parsing is text-based and sensitive to ethtool label changes. Iterating `${!SETTINGS_MAP[@]}` has unspecified order, but both expected/current arrays are expanded consistently in the same shell. Random high values assume netdevsim accepts the full range.

Test signals: Each knob update must be observable in `ethtool -c`, adaptive booleans must report expected paired status, and final output reports all checks passed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-coalesce.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-common.sh

Purpose: Shared shell helper for netdevsim ethtool tests.

Important APIs/functions: Defines counters `num_passes` and `num_errors`; `check` compares a command status/current value/expected value tuple and reports errors; `make_netdev` loads netdevsim if needed, writes a random id plus optional arguments to `/sys/bus/netdevsim/new_device`, waits for udev, and returns the interface name from the new device's `net/` directory. Cleanup removes the simulated device with `del_device`.

Control flow: Test scripts source the file, call `make_netdev`, then use `check` for assertions. The helper snapshots `/sys/class/net` before adding a port to detect the newly-created netdev.

State and persistence: Creates `/sys/bus/netdevsim/devices/netdevsim*` state and a netdevsim port. The installed `trap cleanup EXIT` removes it with `del_device`; it does not unload the module.

Dependencies and integration: Requires `modprobe`, `/sys/bus/netdevsim`, debugfs/sysfs availability, and root. It is used by coalesce, feature, FEC, pause, and qdisc visibility scripts.

Risks: New-netdev detection by set difference can be confused by unrelated interface churn. `modprobe -r netdevsim` may fail if other tests/devices hold the module. Helper-global counters require sourcing scripts not to redefine them unexpectedly.

Test signals: A caller receives a usable netdev name, cleanup removes the device, and `check` counts and reports pass/fail totals consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-features.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-features.sh

Purpose: Verifies the baseline ethtool feature advertisement for a generated netdevsim netdev.

Important APIs/functions: Sources `ethtool-common.sh`, creates `NSIM_NETDEV`, queries `ethtool --json -k`, and parses JSON with `jq`. The `FEATS` list covers `tx-checksum-ip-generic`, `tx-scatter-gather`, `tx-tcp-segmentation`, `generic-segmentation-offload`, and `generic-receive-offload`.

Control flow: After creating the netdevsim interface and enabling pipefail, the script iterates over the feature list. For each feature it checks JSON `.active` is `true` and `.fixed` is `false`, then prints aggregate pass/fail status.

State and persistence: Does not mutate feature flags; it only creates the temporary netdevsim interface. Cleanup is inherited from the common helper.

Dependencies and integration: Depends on ethtool feature reporting format and netdevsim's software implementation of feature state. It complements `udp_tunnel_nic.sh`, which tests the functional tunnel table effects.

Risks: Feature names and JSON schema must remain stable. The test assumes these features are active and mutable by default in netdevsim; driver default changes require updating expectations.

Test signals: PASS requires every listed feature to be reported active and non-fixed in ethtool JSON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-features.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-fec.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-fec.sh

Purpose: Validates ethtool Forward Error Correction configuration and reporting through netdevsim.

Important APIs/functions: Uses `ethtool-common.sh`, `make_netdev`, `ethtool --show-fec`/`--set-fec` or equivalent short options, and `check` counters. It verifies supported FEC modes, auto/off settings, and resulting active/configured mode display.

Control flow: After creating a netdevsim netdev, the script probes ethtool FEC support, applies valid FEC settings, checks they are reflected in ethtool output, and verifies invalid or unsupported combinations are rejected when applicable.

State and persistence: Changes only transient netdevsim FEC state associated with the generated port. Cleanup deletes the backing simulated device.

Dependencies and integration: Requires ethtool FEC support in userspace and the netdevsim kernel driver hooks. This is paired with broader standard-stat checks in `stats.py`.

Risks: Ettool output wording for FEC modes is version-sensitive. If netdevsim capabilities change, expected modes must be updated. Tests that assume all modes exist can over-fail on reduced kernel configs.

Test signals: A successful run shows valid FEC mode transitions, consistent displayed configured/active modes, correct rejection of invalid settings, and a final all-checks-passed report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-fec.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-pause.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-pause.sh

Purpose: Tests pause-frame statistics reporting through ethtool JSON on netdevsim.

Important APIs/functions: Sources `ethtool-common.sh`; requires ethtool `--include-statistics` support; creates `NSIM_NETDEV`; toggles debugfs `ethtool/pause/report_stats_tx` and `report_stats_rx`; reads `ethtool --json -a` and `ethtool -I --json -a` with `jq`.

Control flow: The script disables both stats in debugfs and verifies normal JSON reports `statistics: null` while include-statistics reports `{}`. It enables Tx stats and checks one stat with `tx_pause_frames == 2`, then enables Rx stats and checks both `rx_pause_frames == 1` and `tx_pause_frames == 2`.

State and persistence: Mutates only temporary netdevsim debugfs flags controlling pause stat reporting. The shared cleanup path removes the simulated device.

Dependencies and integration: Requires ethtool pause support and netdevsim pause ops. It provides narrower command-line coverage than `stats.py`, which checks standard pause statistics over netlink.

Risks: Depends on ethtool JSON and `-I` semantics. Expected counter values are netdevsim constants. It does not test changing pause configuration, only statistics visibility.

Test signals: PASS means statistics are absent without include-statistics, empty when disabled with include-statistics, and populated with the expected Tx/Rx counters when debugfs reporting flags are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-pause.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib.sh

Purpose: Exercises netdevsim FIB offload/resource behavior for IPv4 and IPv6 routes, including replay, overflow, delete-failure, and flag-change notification paths.

Important APIs/functions: Uses `devlink resource set/show`, `devlink dev reload`, namespaced `ip route`, sysctls `fib_notify_on_flag_change`, and debugfs FIB failure controls. Local helpers check route flags, resource occupancy, route add/delete/replay outcomes, and notification settings.

Control flow: `setup_prepare` creates netdevsim, moves it into `testns1`, creates dummy interfaces, and sets command prefixes. Tests run with notification disabled and enabled, covering route additions, route replacements, route offload failure, IPv6 error replay, delete failure injection, and reload after resource resizing.

State and persistence: Mutates devlink FIB resource sizes, namespaced routes, dummy links, sysctls, and debugfs failure flags. Cleanup deletes namespace/device/module state.

Dependencies and integration: Requires netdevsim FIB offload support, devlink resources, `iproute2`, jq/cmd helpers from forwarding `lib.sh`, and namespace support.

Risks: FIB offload notifications are asynchronous, so sleeps and monitor timing are important. Resource limits and route counts must match netdevsim accounting. Failure injection must be reset or later tests can cascade fail.

Test signals: Expected outcomes include correct `trap`/`offload_failed` route flags, occupancy values, rejected routes over resource limits, clean replay after reload, and no stale state after failed delete/reload scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib_notifications.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib_notifications.sh

Purpose: Verifies route netlink notification behavior when FIB offload flags change for IPv4 and IPv6 netdevsim routes.

Important APIs/functions: Helpers `route_addition_check`, `route_deletion_check`, and `route_replacement_check` run `ip monitor route` and inspect emitted lines. `route_notify_check` validates notification count and flag sequence via `check_rt_trap` or `check_rt_offload_failed`. Tests toggle `net.ipv4/ipv6.fib_notify_on_flag_change` and debugfs `fib/fail_route_offload`.

Control flow: Setup creates one netdevsim device, moves it into `testns1`, and adds `dummy1`. For each IP family, tests cover route add, delete, replace, and offload-failed addition under notify modes 0, 1, and 2. Monitors are started before the route mutation, killed after a short wait, and the temp output is checked.

State and persistence: Uses namespaced sysctls, temporary routes/devices, temp files, and netdevsim debugfs fault flags. Cleanup removes `dummy1`, namespace, device, and module.

Dependencies and integration: Relies on forwarding `lib.sh` process helpers, `ip monitor route` output strings, devlink namespace reload, and netdevsim FIB offload flags.

Risks: Monitor timing can be flaky on slow systems. Parsing text flags (`rt_trap`, `rt_offload_failed`) depends on iproute2 output. A killed monitor job must not leave background processes.

Test signals: Correct runs see one notification for normal add/delete/replace when flag-change notification is disabled, two notifications with flag-change enabled, and two failed-offload notifications when notify mode is failure-only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib_notifications.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/hw_stats_l3.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/hw_stats_l3.sh

Purpose: Tests L3 offload hardware statistics request/reporting, failure rollback, counters, and monitor events with multiple netdevsim instances.

Important APIs/functions: Instance helpers `nsim_add`, `nsim_reload`, `nsim_hwstats_enable/disable/fail_next_enable`; netdev queries using `ip -j stats show ... group offload subgroup hw_stats_info`; counter reads from `${type}_stats`; test wrappers `reporting_test`, `fail_next_test`, `counter_test`, `rollback_test`, and `l3_monitor_test`.

Control flow: Setup creates three netdevsim devices, moves all into `testns1`, and adds `dummy1`. Tests first verify request/used state transitions, then inject failures on each instance, validate counter reset behavior around disable/failure, and test rollback when the second of three providers fails. The monitor test delegates to `hw_stats_monitor_test`.

State and persistence: Mutates per-instance debugfs hwstats lists keyed by ifindex, namespaced `ip stats set` requests, and simulated counters. Cleanup removes dummy, namespace, all three devices, and module.

Dependencies and integration: Requires netdevsim hwstats debugfs, `ip stats`, `jq`, forwarding libraries, and kernel offload stats infrastructure.

Risks: Counter assertions are time-sensitive and assume netdevsim's 10 pps simulated ingress. Multi-provider rollback assumes notification ordering hits instance 2 between 1 and 3. Failure toggles must be one-shot as expected.

Test signals: PASS means `used` and `request` booleans match combined device/kernel requests, injected failures return errors without partial state, counters restart after reenable/failure, and monitor events appear for enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/hw_stats_l3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/nexthop.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/nexthop.sh

Purpose: Provides extensive netdevsim nexthop offload/resource testing, including single nexthops, groups, resilient groups, bucket replacement, deletion, and replay after reload.

Important APIs/functions: Uses namespaced `ip nexthop`, `ip route`, `devlink resource`, `devlink dev reload`, and debugfs FIB failure controls. Helpers check nexthop textual output, occupancy, group membership, resilient bucket counts, idle timers, and injected bucket replace failures.

Control flow: Setup creates a netdevsim device in `testns1`, adds `dummy1` with an IPv4 address, and binds `IP`/`DEVLINK` prefixes. `xfail_on_slow tests_run` runs a large `ALL_TESTS` suite covering add/replace/delete for single nexthops, groups, resilient groups, resource overflow, invalid operations, single-member deletion, and reload/replay success/failure.

State and persistence: Mutates namespaced nexthop objects, routes, devlink nexthop resource size, debugfs fault injection, and dummy interface state. Tests generally flush nexthops after each scenario. Cleanup deletes namespace/device/module.

Dependencies and integration: Requires iproute2 nexthop support, devlink netdevsim resources, forwarding `lib.sh`, and kernel resilient nexthop APIs.

Risks: The suite is timing-sensitive for resilient idle timers and can be slow, hence `xfail_on_slow`. Text matching of `ip nexthop show` output is brittle. Resource counts must track netdevsim accounting exactly.

Test signals: PASS requires expected `trap` offload markings, resource occupancy after each mutation, rejected over-limit/replacement failures, correct resilient bucket counts, and restored nexthop state after successful reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/nexthop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/peer.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/peer.sh

Purpose: Tests the netdevsim `link_device` peer facility across network namespaces, including validation of bad link arguments and data connectivity through linked simulated devices.

Important APIs/functions: Local helpers create/delete namespaces, test carrier state via `/sys/class/net/.../carrier`, and require `socat`. Sysfs controls are `/sys/bus/netdevsim/new_device`, `del_device`, `link_device`, and `unlink_device`.

Control flow: The script loads netdevsim, creates two devices, moves them into server/client namespaces, assigns IPv4 addresses, and brings links up. It verifies linking fails for non-existent peer ifindex, non-existent namespace fd, self-link, and malformed arguments. It then links devices, checks carrier propagation across down/up and unlink/relink, runs a TCP transfer with `socat`, unlinks, deletes devices, removes namespaces, and unloads the module.

State and persistence: Creates two netdevsim devices, two namespaces, namespace file descriptors, and a temp file for received data. Cleanup is mostly explicit at the end rather than trap-heavy.

Dependencies and integration: Requires `socat`, root, namespace support, sysfs netdevsim controls, and TCP stack in namespaces.

Risks: Lack of a comprehensive trap means interruption can leave namespaces/devices. Carrier checks are synchronous and can race with link updates. The hard-coded TCP port can collide inside the test namespace.

Test signals: Expected results are rejected invalid link requests, successful valid link, carrier changes matching peer state, successful `HI` transfer, and zero final error count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/peer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/psample.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/psample.sh

Purpose: Tests netdevsim PSAMPLE packet sampling enablement and metadata export.

Important APIs/functions: Uses netdevsim debugfs `psample` controls (`enable`, `group_num`, `in_ifindex`, `out_ifindex`, `out_tc`, occupancy, latency fields) and `psample_capture` to read sampled packets. Tests are `psample_enable_test`, `psample_group_num_test`, and `psample_md_test`.

Control flow: Setup loads netdevsim, creates one device, moves it into `testns1`, and locates debugfs. Each test toggles sampling, captures packets, and asserts expected metadata. Group number changes are verified to take effect only after sampling restart. Metadata tests add/remove optional fields and verify capture filters.

State and persistence: Mutates debugfs psample controls and namespace/device state. Cleanup removes namespace, device, and module.

Dependencies and integration: Requires `CONFIG_PSAMPLE`, psample userspace capture support from forwarding/devlink libs, netdevsim debugfs, and devlink namespace reload.

Risks: Packet capture timing can be flaky. Enabling/disabling failure cases depend on netdevsim one-shot fault behavior. Metadata fields such as out-tc occupancy and latency must match kernel limits exactly.

Test signals: PASS shows packets captured only when enabled, group numbers match and do not change while active, in/out ifindex and optional queue/latency metadata are present or absent as configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/psample.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/tc-mq-visibility.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/tc-mq-visibility.sh

Purpose: Checks visibility and child qdisc accounting for multi-queue qdiscs when netdevsim channel counts change.

Important APIs/functions: Sources `ethtool-common.sh`. `n_children` counts qdisc child lines, `tcq` wraps `tc qdisc`, and `n_child_assert` compares expected child counts. Uses `ethtool -L` to change combined queues and `ip link set` to bring the device up.

Control flow: Creates a netdevsim device, inspects default qdisc children, changes combined channels to several values, validates multiq/mq/prio child visibility, and tests transitions while the interface is up and down. Final pass/fail counters are printed from the common helper variables.

State and persistence: Mutates channel count and qdisc state on the temporary netdevsim interface. Cleanup from `ethtool-common.sh` deletes the simulated device.

Dependencies and integration: Requires `tc`, ethtool channel support, `CONFIG_NET_SCH_MQPRIO`, `MULTIQ`, and `PRIO`, plus netdevsim queue support.

Risks: Qdisc output parsing can break with `tc` format changes. Queue count changes may be rejected by some driver state if netdevsim behavior changes. Child count assumptions depend on qdisc implementation details.

Test signals: Expected qdisc child counts equal queue count minus one for relevant roots, and counts adjust correctly after channel reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/tc-mq-visibility.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/udp_tunnel_nic.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/udp_tunnel_nic.sh

Purpose: Regression-tests UDP tunnel port offload table synchronization between tunnel devices, ethtool feature state, and netdevsim NIC tables.

Important APIs/functions: Defines helpers for creating/deleting VxLAN and Geneve devices, encoding/printing table entries, reading netdevsim debugfs UDP port tables, checking ethtool `--show-tunnels`, discovering new netdev names, and cleanup. Uses debugfs modes such as `udp_ports_open_only`, `sync_all`, `ipv4_only`, `shared`, `static_iana_vxlan`, per-port `inject_error`, and `reset`.

Control flow: The script runs multiple scenarios: basic tunnel add/delete and link state, module unload cleanup, port add/delete, open-only/sync-all/IPv4-only behavior, error injection, feature toggling, table reset, shared tables across two ports, overflow handling, and static IANA VxLAN ports. It compares expected arrays to debugfs and ethtool output after each mutation.

State and persistence: Creates netdevsim devices/ports, VxLAN/Geneve netdevs, toggles ethtool offload features, loads/unloads tunnel modules, and mutates debugfs table controls. Cleanup removes tunnels and devices.

Dependencies and integration: Requires netdevsim, vxlan/geneve/udp_tunnel modules, ethtool tunnel display support for full coverage, `iproute2`, debugfs, and root.

Risks: This is highly stateful and long; missed cleanup can poison later scenarios. Table ordering and overflow behavior must match netdevsim exactly. It conditionally degrades when ethtool lacks `show-tunnels`.

Test signals: PASS means debugfs NIC tables and ethtool tunnel dumps match expected encoded entries through all tunnel lifecycle, feature toggle, error, reset, shared-table, and static-port scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/udp_tunnel_nic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netpoll_basic.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netpoll_basic.py

Purpose: Attempts to trigger and observe the netpoll TX-side polling path (`netpoll_poll_dev`) by congesting a NIC while sending netconsole messages.

Important APIs/functions: Uses `NetDrvEpEnv`, `GenerateTraffic`, ethtool queue/ring helpers, configfs netconsole target helpers, and `bpftrace` kprobe collection. Key functions are `configure_network`, `netcons_configure_target`, `do_netpoll_flush`, `do_netpoll_flush_monitored`, `bpftrace_any_hit`, and `test_netpoll`.

Control flow: Main loads netconsole, checks configfs, enters a local/remote endpoint environment, reduces queues/rings where possible, starts background traffic, creates a netconsole target, repeatedly writes batches to `/dev/kmsg` while recreating the target, and checks whether bpftrace saw `netpoll_poll_dev`.

State and persistence: Mutates ethtool channel/ring settings, configfs netconsole target directories, `/dev/kmsg`, global `MAPS`/`BPF_THREAD`, and traffic generator state. Deferred cleanup restores rings/queues and removes the target.

Dependencies and integration: Requires dynamic netconsole configfs, bpftrace/kprobe support, ethtool JSON support, root, and a driver/environment capable of hitting the rare netpoll path.

Risks: The expected path is environment-dependent; lack of hits becomes `XFAIL`, not necessarily a kernel failure. Ring/queue reduction may be unsupported on real NICs, and repeated configfs target recreation can leave stale targets if interrupted before deferred cleanup.

Test signals: Success is at least one bpftrace hit for `netpoll_poll_dev`; skip covers missing configfs/bpftrace setup, and xfail covers environments that do not trigger the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netpoll_basic.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/basic_qos.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/basic_qos.sh

Purpose: Tests basic QoS classification on Ocelot switch ports for default port priority, VLAN PCP, and IP DSCP.

Important APIs/functions: Sources forwarding `tc_common.sh` and `lib.sh`. Topology helpers create host interfaces, VLAN subinterfaces, and a bridge over `swp1/swp2`. `run_test` sends IPv4 and IPv6 traffic and checks priority behavior. `port_default_prio_get`, `test_port_default`, `test_vlan_pcp`, and `test_ip_dscp` implement the scenarios.

Control flow: Setup brings host/switch ports up, creates bridge and VLAN devices, and installs egress filters to shape packet priority markings. Tests alter default priority, VLAN PCP, or DSCP markings, send traffic across the bridge, and log separate IPv4/IPv6 results. Cleanup removes qdiscs, VLANs, hosts, and bridge.

State and persistence: Mutates live switch port state, bridge membership, VLAN interfaces, and TC filters. All state is transient and removed by `trap cleanup EXIT`.

Dependencies and integration: Requires an Ocelot hardware test topology with exported `h1`, `h2`, `swp1`, `swp2`, `tc`, `bridge`, and forwarding library variables.

Risks: Hardware counters/classification can be timing-sensitive. Test correctness depends on the topology being wired as expected. DSCP-to-ToS conversion and VLAN priority propagation must match Ocelot offload semantics.

Test signals: Expected logs show IPv4 and IPv6 traffic classified with the configured priority source for default port, VLAN PCP, and DSCP cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/basic_qos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/psfp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/psfp.sh

Purpose: Tests Per-Stream Filtering and Policing gate behavior on Ocelot hardware using TC flower, ETF/txtime scheduling, and time-sensitive traffic.

Important APIs/functions: Sources `tc_common.sh`, `lib.sh`, and `tsn_lib.sh`. `PSFP` returns the hardware chain id. Helpers create PSFP chains, inspect hardware filter drops, set up bridge/VLAN forwarding, configure txtime with `mqprio` and `etf`, and debug incorrect packet receipt/drop.

Control flow: Setup builds host and switch topology, attaches a PSFP chain on ingress, creates an Ocelot bridge with VLAN filtering, configures traffic classes and ETF for the stream priority, and then runs gate in-band and out-of-band tests. `run_test` sends isochronous traffic with expected receive counts and checks drops.

State and persistence: Mutates TC qdiscs/filters, bridge/VLAN state, txtime/ETF scheduling, and hardware PSFP entries. Cleanup tears down txtime, chains, bridge, hosts, and interfaces.

Dependencies and integration: Requires Ocelot hardware with PSFP offload, `tc` flower offload, ETF/mqprio qdiscs, time synchronization good enough for scheduled packets, and forwarding TSN helpers.

Risks: Strongly time-sensitive; scheduler jitter and clock drift can create false failures. Hardware offload counters must be available. Debug helpers assume packet capture buffers from forwarding libs.

Test signals: PASS means packets inside allowed gate windows are received, packets outside windows are dropped with hardware filter counters increasing, and no unexpected packets appear in debug captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/psfp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/tc_flower_chains.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/tc_flower_chains.sh

Purpose: Validates Ocelot TC flower chain mapping across ingress/egress lookup blocks and actions such as VLAN pop/push/modify and skb priority edit.

Important APIs/functions: Chain id helpers `IS1`, `IS2`, and `ES0` encode Ocelot lookup stages. `create_tcam_skeleton` installs goto-chain skeleton filters. Tests are `test_vlan_pop`, `test_vlan_push`, `test_vlan_ingress_modify`, `test_vlan_egress_modify`, and `test_skbedit_priority`.

Control flow: Setup brings host and switch ports up, creates a bridge and VLAN subinterfaces on `h1`, installs TC skeleton and action filters on `swp1`, and prepares traffic expectations. Each test sends traffic and verifies untagged/tagged reception or priority behavior, adding temporary filters and bridge VLAN filtering as needed.

State and persistence: Mutates TC clsact filters on switch ports, bridge VLAN filtering, VLAN subinterfaces, and bridge membership. Cleanup removes VLANs, clsact, and bridge.

Dependencies and integration: Requires Ocelot hardware TCAM offload, `tc` flower skip_sw support, forwarding helper variables, and host/switch topology.

Risks: Chain numbers encode hardware pipeline assumptions and can break if driver mapping changes. TC offload failure should be surfaced by `skip_sw`; incorrect bridge VLAN state can mask action behavior.

Test signals: Correct runs observe VLAN pop producing untagged reception, VLAN push/modify producing expected tags, egress modification on `swp2`, and skbedit priority affecting frame prioritization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/tc_flower_chains.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ping.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ping.py

Purpose: Provides baseline data-plane connectivity tests for driver environments across IPv4, IPv6, TCP, checksum offload states, and XDP modes.

Important APIs/functions: Uses `NetDrvEpEnv`, `EthtoolFamily`, command helpers, `socat`, and BPF object `xdp_dummy.bpf.o`. Helpers `_test_v4`, `_test_v6`, and `_test_tcp` send ping/TCP traffic both directions. Setup helpers toggle checksum offloads and XDP generic/native/offload single-buffer and multi-buffer modes.

Control flow: Main creates endpoint environment, gathers interface info, resets MTU/XDP state, then runs default IPv4/IPv6 tests and XDP variants. Each case disables/enables checksum offload around ping and TCP transfer checks. XDP modes adjust MTUs and defer restoration.

State and persistence: Mutates MTU, XDP programs, checksum offload flags, and remote endpoint listener processes. Deferred cleanup restores offload and link settings.

Dependencies and integration: Requires local/remote endpoint from `NetDrvEpEnv`, `socat`, ethtool, iproute2 XDP attach support, bpftool-compatible BPF object, and optional offload support for native/offloaded cases.

Risks: Uses broad `except` in checksum/offload setup, so unsupported toggles may be silently ignored. Real devices need sleeps for XDP propagation; netdevsim/veth skip that delay. Shell `echo` of random strings assumes no hostile characters beyond lowercase.

Test signals: PASS means bidirectional small and large ping works, 64 KiB TCP payloads match exactly, and the same connectivity holds under each supported checksum/XDP configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ping.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp.py

Purpose: Tests PSP-capable network drivers over the generic netlink PSP family, covering device enumeration, key rotation, associations, data transfer, MSS adjustment, stale keys, and device removal.

Important APIs/functions: Uses `NetDrvEpEnv`, `PSPFamily`, responder process `psp_responder`, and TCP sockets. Helpers manage the control socket (`_send_with_ack`, `_make_clr_conn`, `_make_psp_conn`), SPI/key exchange, careful nonblocking send, receive-length checks, and PSP device initialization. Test cases are selected by name prefixes `dev_`, `assoc_`, `data_`, and `removal_`.

Control flow: Main deploys and starts the responder on the remote endpoint, opens a control socket, builds per-version/per-IP data tests, and runs all matching cases. Device setup discovers the PSP dev id for the local ifindex and enables supported versions with deferred restoration.

State and persistence: Mutates PSP device enabled-version state, per-socket Rx/Tx associations, key rotation counters, TCP sockets, responder process state, and netdevsim reload state for removal tests. Defers restore PSP enablement and closes sockets.

Dependencies and integration: Requires kernel PSP generic netlink support, responder binary, local/remote endpoint connectivity, and netdevsim for reload/removal-specific tests.

Risks: Many tests depend on precise extack errors and version constants. Bad-key/stale-key tests intentionally create queued unsent data, so timing and socket buffer behavior matter. Responder/control protocol must stay in sync with `psp_responder.c`.

Test signals: PASS includes expected device ids/stats, key rotation counter increments and SPI top-bit changes, valid and invalid association behavior, successful encrypted data delivery, bad/stale data not delivered, MSS reduced by PSP overhead after Tx association, and no crash/leak through device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp_responder.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp_responder.c

Purpose: Remote-side helper used by `psp.py` to accept TCP data connections, create PSP associations through YNL, exchange SPI/key material with the client, count received bytes, and expose a simple control protocol.

Important APIs/types/functions: Defines `struct opts`, global quit flag, PSP version descriptors, `conn_setup_psp`, `handle_cmd`, `spawn_server`, `run_responder`, `parse_cmd_opts`, `psp_dev_set_ena`, and `main`. Uses sockets, `poll`, `accept`, `send`, `recv`, YNL generated PSP APIs, and ifindex/port command options.

Control flow: Main parses port/ifindex, opens a YNL PSP socket, enables PSP versions, opens a server socket, and processes commands from the Python control connection. Commands select clear or PSP connection mode, close current data socket, report received length, or exit. PSP mode accepts a data socket, creates Rx assoc, exchanges keys with the client, creates Tx assoc, and then accumulates received data.

State and persistence: Holds server and data sockets, accumulated receive offset in a static buffer, selected PSP versions, and device PSP enablement. All state is process-local and should end with the helper.

Dependencies and integration: Compiles against kernel selftest YNL support and PSP generated headers. It is deployed/run by `NetDrvEpEnv.remote.deploy("psp_responder")`.

Risks: Static receive buffer/offset require careful reset across connections. The control protocol is binary/string and must match `psp.py`. Socket and YNL errors must be reported back as `ack`/`err` or the Python side can hang.

Test signals: Correct behavior is listening on the requested port, acknowledging commands, returning received byte counts, performing PSP key exchange/associations, and exiting cleanly on `exit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp_responder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/queues.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/queues.py

Purpose: Tests the netdev generic netlink queue/NAPI APIs against sysfs and ethtool channel changes, including AF_XDP queue annotation.

Important APIs/functions: Uses `NetdevFamily.queue_get`, `napi_get`, `EthtoolFamily.channels_get`, `xdp_helper`, and sysfs `/sys/class/net/<ifname>/queues`. Test functions are `get_queues`, `addremove_queues`, `check_down`, and `check_xsk`.

Control flow: Main creates a `NetDrvEnv` with many queues, then runs queue count comparison, channel decrement/restore, down-state checks, and AF_XDP annotation checks. `check_xsk` first probes AF_XDP support, runs `xdp_helper` bound to queue 0, and validates only queue 0 reports `xsk`.

State and persistence: Mutates channel count with `ethtool -L`, interface up/down state, and creates a temporary AF_XDP socket via helper process. Defers restore link state where needed.

Dependencies and integration: Requires netdev generic netlink queue support, ethtool channels, xdp_helper from net selftests, sysfs queue folders, and root.

Risks: Queue count changes may not be supported or can be disruptive. AF_XDP support probing distinguishes unsupported from helper failure by return code. Queue/NAPI ids disappear when the interface is down, which is expected.

Test signals: PASS means netlink queue counts equal sysfs, queue counts track ethtool channel changes, downed devices return ENOENT for queue/NAPI lookups, and AF_XDP annotation appears only on the configured queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/queues.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ring_reconfig.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ring_reconfig.py

Purpose: Validates ethtool netlink channel and ring parameter reconfiguration while preserving traffic functionality.

Important APIs/functions: Uses `NetDrvEpEnv`, `EthtoolFamily.channels_get/set`, `rings_get/set`, `GenerateTraffic`, `defer`, and `NlError`. Tests are `channels` and `ringparam`; `_configure_min_ring_cnt` temporarily reduces channel count to speed ring testing.

Control flow: `channels` discovers supported `rx`, `tx`, and `combined` channel types, tries selected mixes at one queue and max queue counts, and verifies accepted settings read back exactly. `ringparam` records ring maxima/current values, halves each ring parameter until rejected to find the minimum accepted value, sends traffic, then tries max settings and sends traffic again if accepted.

State and persistence: Mutates ethtool channel and ring settings on the device under test. Deferred calls restore original settings.

Dependencies and integration: Requires ethtool netlink support, a local/remote endpoint capable of traffic generation, and driver support for channels/rings.

Risks: Max ring settings may be memory-heavy and are allowed to fail. Some drivers expose partial channel combinations and reject mixed configurations. Traffic generation is needed to catch reconfiguration that succeeds but leaves queues unusable.

Test signals: PASS means accepted channel/ring settings are readable back, traffic completes at minimized rings, and optional max ring settings do not break traffic when accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ring_reconfig.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/shaper.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/shaper.py

Purpose: Tests the netdev shaper generic netlink API for queue, netdev, node, grouping, delegation, duplicate leaves, and queue-update behavior.

Important APIs/functions: Uses `NetshaperFamily` methods `get`, `cap_get`, `set`, `delete`, and `group`. Test functions include `get_shapers`, `get_caps`, `set_qshapers`, `del_qshapers`, `set_nshapers`, `del_nshapers`, `basic_groups`, `qgroups`, `delegation`, `queue_update`, and `dup_leaves`.

Control flow: Main creates a `NetDrvEnv` with four queues, initializes capability flags on `cfg`, then runs tests. Each test first checks capabilities and skips unsupported scopes/metrics. Queue/netdev shapers are created, updated, grouped, deleted, delegated between scopes, and validated through exact netlink object comparisons.

State and persistence: Mutates shaper hierarchy on the tested interface, including queue and netdev handles, node ids, weights, metrics, and channel count during `queue_update`. Tests explicitly delete created shapers; environment cleanup removes netdevsim when used.

Dependencies and integration: Requires kernel netdev shaper netlink API, netdevsim or a driver with shaper support, ethtool channel changes for queue-update, and lib.py netlink wrappers.

Risks: Exact object equality can break when kernel adds optional attributes. Queue-update relies on channel count semantics and `cfg.rx_type`. Capability skips must remain aligned with API names.

Test signals: PASS means capabilities are reported, supported shapers can be set/read/deleted, grouped leaves carry parent/weight attributes, queue delegation/nesting works, duplicate leaves return EINVAL, and shapers tied to removed queues are deleted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/shaper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/stats.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/stats.py

Purpose: Tests standard netdevice statistics APIs, qstats consistency, pause/FEC statistic availability, and race resilience under procfs reads and interface reconfiguration.

Important APIs/functions: Uses `EthtoolFamily.pause_get/fec_get/channels_get`, `NetdevFamily.qstats_get`, `RtnlFamily.getlink`, `ip`, `cmd`, and ksft helpers. Tests include `check_pause`, `check_fec`, `check_fec_hist`, `pkt_byte_sum`, `qstat_by_ifindex`, disruptive `check_down`, `procfs_hammer`, and `procfs_downup_hammer`.

Control flow: Main creates a high-queue-count `NetDrvEnv` and runs tests. It checks stat presence for devices that support pause/FEC config, compares qstats with RTNL stats monotonicity, validates qstats dumps by ifindex and per-queue key continuity, verifies stats do not regress across ifdown, and hammers `/proc/net/dev` while flipping link/channel state.

State and persistence: Mutates interface up/down state and ethtool channel count in disruptive tests. Spawns background shell loops reading procfs and toggling link/queues, killed via deferred cleanup.

Dependencies and integration: Requires ethtool/netdev/RTNL netlink wrappers, `/proc/net/dev`, ethtool channels, and root. Some tests skip when optional stat families are unsupported.

Risks: Monotonic comparisons allow growth but reject decreases and huge jumps; very active devices could make timing noisy. Procfs hammer is crash/race oriented and may expose driver sleeping-in-RCU bugs rather than deterministic assertion failures.

Test signals: PASS means supported drivers report required stats, qstats and RTNL stats are coherent and monotonic, invalid ifindex errors include expected extack fields, per-queue dumps have contiguous unique ids, and procfs/link churn does not crash or regress counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/Makefile

Purpose: Registers team driver selftest scripts and shared includes with kselftest.

Important APIs/variables: `TEST_PROGS` lists team tests for decoupled enablement, address list cleanup, non-Ethernet header ops, options, propagation, refleak, active-backup teamd, and transmit failover. `TEST_INCLUDES` installs `team_lib.sh`, bonding `lag_lib.sh`, forwarding libs, namespace helpers, and defer helpers. `include ../../../lib.mk` wires into kselftest.

Control flow: No runtime flow; `lib.mk` uses the variables during build/install/run.

State and persistence: The Makefile creates no state. It determines test discovery and helper availability in installed selftest trees.

Dependencies and integration: Depends on team and bonding shell libraries and Linux kselftest conventions.

Risks: Missing helper entries can cause installed-tree failures even if source-tree runs work. Adding a new team test requires updating `TEST_PROGS`.

Test signals: Kselftest install should copy all programs and includes, and test runners should discover the listed programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/config

Purpose: Specifies kernel configuration needed by the team driver selftests.

Important entries: Requires bonding, dummy, IPv6, macvlan, netdevsim module, GRE, team core, team modes (`ACTIVEBACKUP`, `BROADCAST`, `LOADBALANCE`, `RANDOM`, `ROUNDROBIN`), and veth.

Control flow: No executable logic. Kselftest config tooling can merge these symbols into a test kernel.

State and persistence: No runtime state; it enables modules/features that team scripts create dynamically.

Dependencies and integration: Supports team, bonding/LAG helper, namespace, GRE-over-bond-over-team, and veth-based topology tests.

Risks: Userspace requirements such as `teamnl`, `teamd`, `tcpdump`, `mz`, `ping`, and `iproute2` are not represented. Some tests can run in IPv4 mode but IPv6 is still a default requirement.

Test signals: A configured kernel should allow creation of team devices/modes, veth peers, dummy/macvlan devices, GRE devices, and bonding stacks used by the tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/decoupled_enablement.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/decoupled_enablement.sh

Purpose: Verifies independent `tx_enabled` and `rx_enabled` behavior for team member ports across team modes.

Important APIs/functions: Uses `team_lib.sh` `setup_team`, forwarding `lib.sh`, `teamnl setoption`, `tcpdump_start/stop/show/cleanup`, namespace setup, and ping. Local helpers include `environment_create`, `set_option_value`, `try_ping`, `did_interface_receive_icmp`, `team_test_mode_tx_enablement`, and `team_test_mode_rx_enablement`.

Control flow: Parses optional `-4` to switch from IPv6 to IPv4, then creates two namespaces connected by a veth pair and team devices. For each tested mode, it sets up sender/receiver teams and runs three scenarios for TX and RX: initially enabled ping succeeds, disabling one side causes ping failure, and re-enabling restores connectivity. Tcpdump distinguishes whether packets were transmitted when RX was disabled.

State and persistence: Creates namespaces, veth, team devices, IP addresses, team member options, and tcpdump captures. `trap cleanup_all_ns EXIT` removes namespaces.

Dependencies and integration: Requires team kernel modes, `teamnl`, `ping`, `tcpdump`, iproute2, and forwarding/team libraries. Default IPv6 uses `nodad`; IPv4 mode adjusts prefixes.

Risks: The receiver team is prepared once while sender teams are recreated per mode, so cleanup between modes depends on helper behavior. Packet capture timing can affect ICMP detection. Single-member topology tests enablement semantics, not load distribution.

Test signals: TX disabled should prevent packet transmission; RX disabled should still transmit packets but ping should fail; re-enabling each option should restore ping for all modes tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/decoupled_enablement.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/dev_addr_lists.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/dev_addr_lists.sh

Purpose: Regression-tests team device cleanup of unicast/multicast address lists using shared LAG cleanup logic.

Important APIs/functions: Sources forwarding `lib.sh` and bonding `lag_lib.sh`. Defines `destroy`, `cleanup`, and `team_cleanup`; `team_cleanup` delegates to `test_LAG_cleanup "team" "lacp"`.

Control flow: The script installs cleanup trap, runs `tests_run` for the single `team_cleanup` test, and exits with `EXIT_STATUS`. Cleanup deletes expected devices (`dummy1`, `dummy2`, `team0`, `mv0`) and runs `pre_cleanup`.

State and persistence: Creates and deletes LAG/team-related dummy/macvlan/team devices through the shared helper. No namespaces are used in this wrapper.

Dependencies and integration: Requires team driver support, forwarding test infrastructure, bonding LAG helper, and iproute2. The helper likely exercises address-list propagation and cleanup.

Risks: Most behavior is hidden in `lag_lib.sh`; this wrapper is thin and assumes device names used by the helper. Cleanup deletes fixed names, so concurrent tests using those names would conflict.

Test signals: PASS is `test_LAG_cleanup` succeeding for team/lacp and cleanup leaving no stale address-list devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/dev_addr_lists.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/non_ether_header_ops.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/non_ether_header_ops.sh

Purpose: Reproduces a non-Ethernet `header_ops` stacking scenario that previously could crash when callbacks inherited the wrong `net_device` context.

Important APIs/functions: Sources net namespace helper `net/lib.sh`, uses `setup_ns`/`cleanup_all_ns`, and creates `dummy`, GRE, bond, and team devices. It triggers IPv6 MLD/report paths using address assignment and multicast ping.

Control flow: Creates namespace `ns1`, adds dummy `d0` with IPv4 address, creates GRE `g0`, bond `b0` in active-backup mode, and team `t0`. It enslaves GRE to bond and bond to team, brings all devices up, assigns IPv6 to team, then sends repeated IPv6 multicast pings on `t0`. If the kernel does not crash, it prints PASS and exits.

State and persistence: All devices live inside the temporary namespace. `trap cleanup_all_ns EXIT` removes the namespace and devices.

Dependencies and integration: Requires GRE, bonding, team, IPv6, iproute2, and namespace support. It is a crash regression rather than a packet-delivery validation.

Risks: Success is absence of a crash; the script ignores ping failures. It assumes IPv6 address assignment triggers MLD joins that call `dev_hard_header` through the stack.

Test signals: PASS output indicates the GRE-over-bond-over-team stack handled IPv6 multicast header generation without crashing or warning fatally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/non_ether_header_ops.sh -->
