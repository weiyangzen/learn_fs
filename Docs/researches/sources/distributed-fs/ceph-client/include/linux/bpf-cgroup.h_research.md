# sources/distributed-fs/ceph-client/include/linux/bpf-cgroup.h

Purpose: Provides the runtime API and fast-path macros for executing BPF programs attached to cgroups. It maps UAPI attach types to internal cgroup attach slots, defines cgroup storage structures, declares attach/query operations, and gives networking/device/sysctl call sites cheap static-key-guarded wrappers.

Important APIs/types/functions: `to_cgroup_bpf_attach_type()` maps `enum bpf_attach_type` to `enum cgroup_bpf_attach_type`. `cgroup_bpf_enabled_key[]` and `cgroup_bpf_enabled()` gate hot paths with static branches. `struct bpf_cgroup_storage` links per-program storage to a cgroup and map through rb/list nodes and RCU. `struct bpf_prog_list` carries a program/link plus cgroup storage slots and attach flags. Declared execution functions include skb, sock, sockaddr, sock_ops, device, sysctl, setsockopt, and getsockopt filters. Macros such as `BPF_CGROUP_RUN_PROG_INET_INGRESS()`, `BPF_CGROUP_RUN_PROG_INET_BIND_LOCK()`, and `BPF_CGROUP_RUN_PROG_GETSOCKOPT()` perform enable checks, socket fullsock validation, locking where needed, and call the underlying executor.

Control flow: Subsystems call a macro at hook points. The macro first checks the static key and often `cgroup_bpf_sock_enabled()`, then invokes the correct `__cgroup_bpf_run_filter_*()` implementation. Management paths call `cgroup_bpf_prog_attach()`, `cgroup_bpf_prog_detach()`, `cgroup_bpf_link_attach()`, and `cgroup_bpf_prog_query()`.

State/persistence: Per-cgroup effective arrays live in `struct cgroup_bpf`; storage objects persist per attached program/map/cgroup and are RCU-freed. Static keys reflect whether any program of a given attach type exists. With `CONFIG_CGROUP_BPF` disabled, all wrappers compile to inert stubs returning pass/default values or `-EINVAL`.

Dependencies/integration: Integrates with sockets, sk_buffs, sysctl, device cgroups, sockptr, cgroup core, BPF maps/progs/links, and TCP bypass hooks.

Risks/test signals: Risks are incorrect default return semantics, missing socket locking, cgroup storage lifetime leaks, attach type conversion gaps, and bypass logic around getsockopt. Test signals include BPF cgroup selftests across all attach types, socket bind/connect/sendmsg/recvmsg scenarios, sysctl write filtering, device permission checks, link update/detach tests, cgroup teardown under traffic, and disabled-config build tests.
