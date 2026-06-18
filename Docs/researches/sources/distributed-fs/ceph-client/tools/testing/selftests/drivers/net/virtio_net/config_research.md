# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/config

## Purpose
Kernel config fragment for virtio_net selftests. It requests features needed by forwarding/BPF helpers and the virtio feature-filter tests.

## Important APIs, Types, And Functions
Sets `CONFIG_BPF_SYSCALL`, `CONFIG_CGROUP_BPF`, `CONFIG_IPV6`, `CONFIG_IPV6_MULTIPLE_TABLES`, `CONFIG_NET_L3_MASTER_DEV`, `CONFIG_NET_VRF=m`, `CONFIG_VIRTIO_DEBUG`, and `CONFIG_VIRTIO_NET`.

## Control Flow
Consumed by kselftest/kernel config tooling; not executable.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Aligns with `basic_features.sh` requirements for IPv6/VRF and virtio debugfs feature filtering.

## Risks
It does not request debugfs itself, so runtime environments still need debugfs mounted and accessible. `CONFIG_NET_VRF=m` may require module loading.

## Test Signals
Config satisfiability is a prerequisite signal; runtime skip/failure comes from missing debugfs or non-virtio interfaces.
