# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_getset_retval_hooks.h

Purpose: macro data table listing cgroup/BPF hook names, section strings, context types, and representative invalid return values for get/set retval tests.

Important APIs and types: repeated `BPF_RETVAL_HOOK(name, section, ctx_type, invalid_ret)` entries for skb ingress/egress, sock create/release, sockops, dev, bind/connect/sendmsg/recvmsg/getpeername/getsockname, sysctl, getsockopt, and setsockopt.

Control flow: header has no include guard by design for macro-list inclusion. The including file defines `BPF_RETVAL_HOOK` to generate code/data.

State and persistence: no state.

Dependencies and integration points: context type names must exist in BPF UAPI/vmlinux includes; section strings match libbpf cgroup program section names.

Risks: macro-list headers can be misincluded without defining the macro; hook return semantics can change, making invalid return values stale.

Test signals: generated tests should cover each listed hook and validate get/set retval behavior against invalid return handling.
