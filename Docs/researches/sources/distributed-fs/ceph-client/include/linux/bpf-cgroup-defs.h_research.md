# sources/distributed-fs/ceph-client/include/linux/bpf-cgroup-defs.h

Purpose: Defines the cgroup BPF attachment type namespace and the per-cgroup BPF state container used by cgroup hooks. It is split from `bpf-cgroup.h` to provide definitions without pulling the full runtime wrapper surface.

Important APIs/types/functions: `enum cgroup_bpf_attach_type` enumerates ingress/egress skb hooks, socket create/release, sock_ops, device, bind/connect/sendmsg/recvmsg/getpeername/getsockname, sysctl, getsockopt/setsockopt, and optional per-cgroup LSM slots. `CGROUP_LSM_NUM` is 10 only with `CONFIG_BPF_LSM`, otherwise 0, and `MAX_CGROUP_BPF_ATTACH_TYPE` sizes arrays. `struct cgroup_bpf` stores RCU-protected effective program arrays per attach type, attached program lists, flags, revision counters, shared storage list, inactive temporary array for attach/detach rebuilds, a percpu refcount, and work item for release.

Control flow: Cgroup creation embeds this structure. Attach/detach operations update `progs[]`, rebuild `effective[]`, advance revisions, and use `inactive` as a staging array. Cgroup removal drops refs and schedules release work after the refcount drains.

State/persistence: State is per-cgroup and persists for the lifetime of the cgroup. Effective arrays are RCU-read by hot paths; program lists and flags are management state. When `CONFIG_CGROUP_BPF` is disabled, `struct cgroup_bpf` is empty.

Dependencies/integration: Depends on lists, percpu refs, workqueues, `struct bpf_prog_array`, and cgroup core. It integrates with socket, device, sysctl, and LSM hook call sites via `bpf-cgroup.h`.

Risks/test signals: Risks include attach type enum ordering mismatches with UAPI conversion, RCU lifetime bugs in effective arrays, stale revisions, release-work races, and optional LSM slot sizing errors. Test signals include cgroup BPF selftests for attach/query/detach, cgroup deletion while programs run, multi/override attach flags, and BPF LSM enabled/disabled build coverage.
