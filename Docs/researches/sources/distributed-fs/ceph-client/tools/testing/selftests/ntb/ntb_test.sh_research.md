# sources/distributed-fs/ceph-client/tools/testing/selftests/ntb/ntb_test.sh

Purpose: hardware-oriented NTB selftest runner for a pair of non-transparent bridge endpoints. It can test two local loopback devices or coordinate with a remote host via SSH.

Important APIs/functions: `_modprobe()` loads/unloads modules locally and remotely; `split_remote()`, `read_file()`, `write_file()`, and `check_file()` abstract debugfs paths with optional `host:/path` syntax; `find_pidx()` maps peer ports; test functions cover port enumeration, link toggling, doorbells, scratchpads, messages, memory windows, ping-pong counters, MSI, and performance.

Control flow: the script parses options in three phases so options may appear before, between, or after local/remote device arguments. It cleans any already loaded NTB test modules, verifies root, optionally lists devices, then runs `ntb_tool_tests`, `ntb_pingpong_tests`, `ntb_msi_tests`, and `ntb_perf_tests`. `ntb_tool_tests()` derives peer indices, forces link events, exercises doorbells and shared data mechanisms, then removes `ntb_tool`. Performance tests run without DMA and optionally with DMA.

State and persistence: it writes debugfs control files under `${DEBUGFS:-/sys/kernel/debug}` and may write remote debugfs via SSH. It loads and unloads `ntb_tool`, `ntb_perf`, `ntb_pingpong`, `ntb_transport`, and `ntb_msi_test`, with cleanup controlled by `-C`. Temporary comparison files may be created under `/tmp` for remote memory-window reads.

Dependencies/integration: requires root, NTB hardware/drivers, mounted debugfs, working module loading, `dd`, `cmp`, and optionally passwordless root SSH to the remote host. It integrates with kernel NTB test modules and exposes failures through shell exit.

Risks: this is destructive to NTB test module state and link state, and remote command quoting/path handling is simple. A bug in remote temp cleanup uses string comparison against `/tmp/*`, so remote copied files may remain. The line `if ! [[ $$DONT_CLEANUP ]]; then` appears intended to test `DONT_CLEANUP` but expands `$$`, which can make cleanup trap behavior surprising.

Test signals: successful subtests print `Passed`; unsupported optional features print `Unsupported` or module-availability messages; mismatches print to stderr and exit nonzero due to `set -e` or explicit `exit`.
