# sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_ethtool.sh

Purpose: KTAP shell selftest for the Python `ethtool.py` YNL utility. It exercises human-facing show/set paths under a temporary namespace with netdevsim and veth devices.

Important functions: `ethtool_device_info`, `ethtool_statistics`, `ethtool_ring_params`, `ethtool_coalesce_params`, `ethtool_pause_params`, `ethtool_features_info`, `ethtool_channels_info`, and `ethtool_time_stamping` run the utility and validate output or set-command success. `setup()` mirrors the CLI test setup with netdevsim ID 1337 and a veth pair; `cleanup()` removes both.

Control flow/state: validates tool existence, traps cleanup, prints KTAP plan, sets up devices, then runs eight tests. Some tests mutate ethtool state on netdevsim (`set-ring`, `set-coalesce`, `set-pause`, `set-channels`) without restoring original values.

Dependencies/integration: requires root, netdevsim, veth, iproute2, kselftest helpers, and ethtool genetlink support exposed through pyYNL.

Risks/test signals: output matching is intentionally loose, so it is a smoke/integration test rather than exact formatting validation. Mutating settings can fail depending on driver support. It is a good signal for `ethtool.py` argument-to-request conversion and common operation names.
