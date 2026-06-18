# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/xdp.py

## Purpose
Python kselftest suite for native XDP support in network drivers. It loads shared BPF objects and validates XDP PASS, DROP, TX, head/tail adjustment, queue statistics accounting, and multi-buffer program replacement behavior.

## Important APIs, Types, And Functions
Enums `TestConfig`, `XDPAction`, and `XDPStats` encode BPF map keys/actions/stat counters. `BPFProgInfo` stores object, section, and MTU. Core helpers are `_exchg_udp()`, `_test_udp()`, `_load_xdp_prog()`, `_get_stats()`, `_test_pass()`, `_test_drop()`, `_test_xdp_native_tx()`, `_test_xdp_native_tail_adjst()`, `_test_xdp_native_head_adjst()`, `get_hds_thresh()`, and `_validate_res()`. It uses `NetDrvEpEnv`, `EthtoolFamily`, `NetdevFamily`, `bkg`, `cmd`, `ip`, `defer`, and BPF map helpers from `lib.py`.

## Control Flow
`main()` creates a network-driver endpoint environment, attaches ethtool/netdev generic netlink families, then runs the test list. Each test loads `xdp_native.bpf.o` or `xdp_dummy.bpf.o` with the requested section and MTU, programs `map_xdp_setup`, exchanges UDP traffic with `socat`, reads `map_xdp_stats`, and asserts action-specific counters and data transformations. Qstats tests compare netdev qstats before/after 1000 packets and after channel count toggling. Update tests prove jumbo MTU multi-buffer XDP cannot be force-replaced with an incompatible single-buffer program.

## State And Persistence
Runtime state includes XDP programs attached to `cfg.ifname`, BPF maps, temporary MTU changes on local and remote interfaces, netdev qstats, and deferred cleanup actions. No files are persisted.

## Dependencies And Integration Points
Requires driver native XDP, BPF syscall/tooling, `ip`, `socat`, endpoint topology from `NetDrvEpEnv`, shared BPF object files in `selftests.net.lib`, and generic netlink ethtool/netdev families.

## Risks
The test is timing-sensitive around UDP listeners and hardware stat settlement. Data adjustment checks aggregate stats without per-case snapshots, so an early failure can dominate later reporting. HDS threshold handling intentionally stops head-shrink exploration when packet size exceeds header split constraints.

## Test Signals
Signals are UDP delivery or intentional loss, exact BPF stats matches, expected transformed payload bytes, qstats packet deltas, preserved stats across channel changes, and expected failure for incompatible multi-buffer to single-buffer replacement.
