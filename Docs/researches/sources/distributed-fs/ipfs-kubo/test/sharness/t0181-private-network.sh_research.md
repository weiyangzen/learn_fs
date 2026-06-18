## sources/distributed-fs/ipfs-kubo/test/sharness/t0181-private-network.sh

Purpose: tests private network `swarm.key` enforcement and its conflict with AutoConf.

Important APIs and helpers: defines `pnet_key`, `set_key`, `run_single_file_test`, and `check_file_fetch`. Uses `ipfs daemon`, IPTB, `ipfsi config`, `iptb connect`, `ipfsi swarm peers`, generated data, and AutoConf config.

Control flow and state: disables AutoConf for private-network tests, checks daemon failure diagnostics for incompatible setup, creates a multi-node testbed with public and two distinct private-network keys, attempts cross-network connections and verifies they fail, connects nodes sharing the same key and verifies peer counts, then creates a repo with AutoConf enabled plus `swarm.key` and asserts daemon startup fails with a clear conflict message.

Dependencies and integration points: covers pnet protector setup, swarm connection gating, testbed key distribution, AutoConf safety checks, and daemon startup diagnostics.

Risks and test signals: catches private-network isolation bypass, unclear startup errors, and incompatible AutoConf use. Signals are failed cross-key connects, empty peer lists, successful same-key peer counts, and error text mentioning AutoConf/private network conflict.
