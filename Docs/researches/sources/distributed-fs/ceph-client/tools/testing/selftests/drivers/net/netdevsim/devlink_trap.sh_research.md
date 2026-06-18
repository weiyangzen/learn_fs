# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_trap.sh

Purpose: Tests devlink trap, group, policer, statistics, metadata, and lifecycle behavior implemented by netdevsim.

Important APIs/functions: Sources `devlink_lib.sh` for trap helpers such as `devlink_traps_get`, action/group setters, metadata checks, stats idle checks, policer helpers, and trap group operations. Local tests cover initialization, valid/invalid trap actions, metadata, stats, group actions/stats, policers, policer binding, port deletion, and device deletion.

Control flow: The script validates netdevsim support and device-id availability, creates a netdevsim device and associated netdev, then runs `ALL_TESTS`. Tests iterate over registered traps/groups/policers and use debugfs fault knobs such as `fail_trap_drop_counter_get`. Cleanup removes device/module state.

State and persistence: Mutates devlink trap action/group/policer settings, interface up/down state, and netdevsim debugfs failure toggles. Port and device deletion tests intentionally remove resources to validate devlink cleanup.

Dependencies and integration: Requires `devlink`, `udevadm`, `iproute2`, `jq`, netdevsim debugfs, and forwarding test libraries. The device under test is `netdevsim1337`.

Risks: Trap stats behavior depends on whether the netdev is up; the script forcibly downs it if necessary. Devlink trap names and metadata are kernel ABI-sensitive. Tests that delete ports/devices must be ordered so later tests do not expect removed objects.

Test signals: PASS requires registered traps, immutable action for non-drop traps, mutable drop traps, expected metadata, invalid operation rejection, stats counters changing or idling as specified, policer binding correctness, and clean devlink object removal after port/device deletion.
