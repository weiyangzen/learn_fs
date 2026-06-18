<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netns_cookie_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netns_cookie_prog.c

## Purpose

Verifies bpf_get_netns_cookie across sockops, sk_msg, tcx ingress, and cgroup skb contexts, with sockmap and socket-storage plumbing to carry socket state.

## Important APIs, Types, and Functions

Attach sections: .maps, sockops, sk_msg, tcx/ingress, cgroup_skb/ingress, license. Map types: BPF_MAP_TYPE_SK_STORAGE, BPF_MAP_TYPE_SOCKMAP. Important local functions/programs: get_netns_cookie_sockops, get_netns_cookie_sk_msg, get_netns_cookie_tcx, get_netns_cookie_cgroup_skb. Helper and kfunc calls: bpf_get_netns_cookie, bpf_sk_storage_get, bpf_sock_map_update. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `get_netns_cookie_sockops` and related routines such as `get_netns_cookie_sk_msg, get_netns_cookie_tcx, get_netns_cookie_cgroup_skb`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE, BPF_MAP_TYPE_SOCKMAP for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u32 key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, sockops, sk_msg, tcx/ingress, cgroup_skb/ingress, license` programs, helper coverage for `bpf_get_netns_cookie, bpf_sk_storage_get, bpf_sock_map_update`, and stable behavior of `get_netns_cookie_sockops, get_netns_cookie_sk_msg, get_netns_cookie_tcx, get_netns_cookie_cgroup_skb` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netns_cookie_prog.c -->
