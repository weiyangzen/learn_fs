
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/env.py`

## Purpose
Defines reusable test environments for driver networking selftests: single local NIC, local NIC plus remote endpoint, and a specialized netkit container/namespace topology.

## Important APIs, Types, And Functions
- `NetDrvEnvBase` loads `net.config` or environment via `ksft_setup()`, resolves `test_dir` and `net_lib_dir`, and brings the device up on context entry.
- `NetDrvEnv` selects either `NETIF` hardware or a `NetdevSimDev` local device.
- `NetDrvEpEnv` creates or consumes a local/remote endpoint pair, resolves addresses and remote interface name, supports command requirements, IP-version requirements, netdevsim requirements, and hardware stats settling.
- `NetDrvContEnv` extends endpoint topology with a netkit pair, namespace, IPv6 forwarding sysctls, tc ingress BPF forwarding, and queue-lease-friendly addresses.

## Control Flow
Construction loads config, selects hardware vs netdevsim based on `NETIF` and `nsim_test`, creates local netdevsim peer namespaces when needed, creates `Remote(kind, args, src_path)`, resolves interface metadata, and initializes helper state. `NetDrvContEnv` then validates IPv6 and `LOCAL_PREFIX_V6`, creates a netkit pair with rtnetlink, sets namespace routes/sysctls, attaches `nk_forward.bpf.o`, and patches its `.bss` map.

## State And Persistence
The classes create and destroy netdevsim devices, network namespaces, netkit devices, tc qdiscs/filters, BPF programs, routes, addresses, and sysctl values. Cleanup is in `__del__()` and context-manager exit, with internal flags preventing double deletion.

## Dependencies And Integration Points
Depends on common net selftest classes (`NetNS`, `NetdevSimDev`), `ip`, `tc`, ethtool, `RtnlFamily`, `Netlink`, `bpftool`, remote backends, and compiled `nk_forward.bpf.o`. Most hardware tests in this subset rely on `NetDrvEnv` or `NetDrvEpEnv`; netkit tests rely on `NetDrvContEnv`.

## Risks
Destructor-based cleanup depends on object lifetime and can be skipped by hard exits. `NetDrvContEnv` modifies global IPv6 forwarding and accept_ra sysctls, then restores saved values. BPF attachment lookup assumes the tc filter BPF name starts with `nk_forward.bpf`.

## Test Signals
Environment failures become ksft skips/xfails for unsupported netdevsim/hardware combinations or missing config. `wait_hw_stats_settle()` uses ethtool coalesce stats period to improve qstat-based test reliability.
