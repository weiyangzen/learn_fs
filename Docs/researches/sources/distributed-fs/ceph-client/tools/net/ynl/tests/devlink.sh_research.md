# sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.sh

Purpose: shell wrapper for the devlink C selftest. It prepares a netdevsim device through the shared helper and then executes the local `devlink` binary.

Important flow: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, then runs `$(dirname realpath "$0")/devlink`.

State/dependencies: setup creates `/sys/bus/netdevsim/new_device`, renames the simulated netdev to `nsim0`, assigns IPv4/IPv6 addresses, and installs cleanup via trap. Requires root privileges, `netdevsim`, `ip`, `udevadm`, and the compiled test binary.

Risks/test signals: failures before binary execution are environment/setup issues, not generated devlink binding issues. A successful wrapper proves the test has a deterministic devlink device.
