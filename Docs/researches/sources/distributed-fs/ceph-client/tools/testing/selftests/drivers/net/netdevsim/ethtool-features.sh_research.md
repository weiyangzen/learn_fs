# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-features.sh

Purpose: Verifies the baseline ethtool feature advertisement for a generated netdevsim netdev.

Important APIs/functions: Sources `ethtool-common.sh`, creates `NSIM_NETDEV`, queries `ethtool --json -k`, and parses JSON with `jq`. The `FEATS` list covers `tx-checksum-ip-generic`, `tx-scatter-gather`, `tx-tcp-segmentation`, `generic-segmentation-offload`, and `generic-receive-offload`.

Control flow: After creating the netdevsim interface and enabling pipefail, the script iterates over the feature list. For each feature it checks JSON `.active` is `true` and `.fixed` is `false`, then prints aggregate pass/fail status.

State and persistence: Does not mutate feature flags; it only creates the temporary netdevsim interface. Cleanup is inherited from the common helper.

Dependencies and integration: Depends on ethtool feature reporting format and netdevsim's software implementation of feature state. It complements `udp_tunnel_nic.sh`, which tests the functional tunnel table effects.

Risks: Feature names and JSON schema must remain stable. The test assumes these features are active and mutable by default in netdevsim; driver default changes require updating expectations.

Test signals: PASS requires every listed feature to be reported active and non-fixed in ethtool JSON.
