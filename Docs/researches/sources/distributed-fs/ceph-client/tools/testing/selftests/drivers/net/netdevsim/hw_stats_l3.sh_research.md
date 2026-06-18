# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/hw_stats_l3.sh

Purpose: Tests L3 offload hardware statistics request/reporting, failure rollback, counters, and monitor events with multiple netdevsim instances.

Important APIs/functions: Instance helpers `nsim_add`, `nsim_reload`, `nsim_hwstats_enable/disable/fail_next_enable`; netdev queries using `ip -j stats show ... group offload subgroup hw_stats_info`; counter reads from `${type}_stats`; test wrappers `reporting_test`, `fail_next_test`, `counter_test`, `rollback_test`, and `l3_monitor_test`.

Control flow: Setup creates three netdevsim devices, moves all into `testns1`, and adds `dummy1`. Tests first verify request/used state transitions, then inject failures on each instance, validate counter reset behavior around disable/failure, and test rollback when the second of three providers fails. The monitor test delegates to `hw_stats_monitor_test`.

State and persistence: Mutates per-instance debugfs hwstats lists keyed by ifindex, namespaced `ip stats set` requests, and simulated counters. Cleanup removes dummy, namespace, all three devices, and module.

Dependencies and integration: Requires netdevsim hwstats debugfs, `ip stats`, `jq`, forwarding libraries, and kernel offload stats infrastructure.

Risks: Counter assertions are time-sensitive and assume netdevsim's 10 pps simulated ingress. Multi-provider rollback assumes notification ordering hits instance 2 between 1 and 3. Failure toggles must be one-shot as expected.

Test signals: PASS means `used` and `request` booleans match combined device/kernel requests, injected failures return errors without partial state, counters restart after reenable/failure, and monitor events appear for enable/disable.
