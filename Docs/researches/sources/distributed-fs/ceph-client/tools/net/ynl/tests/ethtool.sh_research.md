# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.sh

Purpose: shell wrapper for the compiled ethtool C selftest. It prepares netdevsim through the shared helper and executes the `ethtool` binary in the tests directory.

Control flow/state: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, then runs the binary by absolute script-relative path. Cleanup is delegated to the helper trap.

Dependencies/integration: requires root/network privileges, `netdevsim`, `ip`, `udevadm`, and a compiled `ethtool` test. It aligns with `tests/config` entries for netdevsim, IPv6, and net namespaces.

Risks/test signals: setup failures should be interpreted separately from generated ethtool binding failures. Successful wrapper setup provides a device for `ethtool.c` dumps.
