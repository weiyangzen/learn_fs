# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/psample.sh

Purpose: Tests netdevsim PSAMPLE packet sampling enablement and metadata export.

Important APIs/functions: Uses netdevsim debugfs `psample` controls (`enable`, `group_num`, `in_ifindex`, `out_ifindex`, `out_tc`, occupancy, latency fields) and `psample_capture` to read sampled packets. Tests are `psample_enable_test`, `psample_group_num_test`, and `psample_md_test`.

Control flow: Setup loads netdevsim, creates one device, moves it into `testns1`, and locates debugfs. Each test toggles sampling, captures packets, and asserts expected metadata. Group number changes are verified to take effect only after sampling restart. Metadata tests add/remove optional fields and verify capture filters.

State and persistence: Mutates debugfs psample controls and namespace/device state. Cleanup removes namespace, device, and module.

Dependencies and integration: Requires `CONFIG_PSAMPLE`, psample userspace capture support from forwarding/devlink libs, netdevsim debugfs, and devlink namespace reload.

Risks: Packet capture timing can be flaky. Enabling/disabling failure cases depend on netdevsim one-shot fault behavior. Metadata fields such as out-tc occupancy and latency must match kernel limits exactly.

Test signals: PASS shows packets captured only when enabled, group numbers match and do not change while active, in/out ifindex and optional queue/latency metadata are present or absent as configured.
