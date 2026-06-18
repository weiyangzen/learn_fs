<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern.c

## Purpose
`core_kern.c` is a CO-RE runtime program validating BTF type reads, trace/fentry/fexit attachment, and prototype relocations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3034 bytes across 120 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_core_read.h>`, `"test_jhash.h"`.
- Important macros/constants: `ATTR`, `C`, `C30`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_core_type_exists`, `bpf_get_prandom_u32`, `bpf_map_lookup_elem`.
Map/type declarations observed:
- line 13 declares map type `BPF_MAP_TYPE_ARRAY`
- line 20 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 17 `SEC(".maps")` -> struct {
- line 24 `SEC(".maps")` -> static __noinline int randmap(int v, const struct net_device *dev)
- line 42 `SEC("tp_btf/xdp_devmap_xmit")` -> int BPF_PROG(tp_xdp_devmap_xmit_multi, const struct net_device
- line 50 `SEC("fentry/eth_type_trans")` -> int BPF_PROG(fentry_eth_type_trans, struct sk_buff *skb,
- line 57 `SEC("fexit/eth_type_trans")` -> int BPF_PROG(fexit_eth_type_trans, struct sk_buff *skb,
- line 74 `SEC("tc")` -> int balancer_ingress(struct __sk_buff *ctx)
- line 110 `SEC("raw_tracepoint/sys_enter")` -> int core_relo_proto(void *ctx)
- line 120 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 26 `randmap`: `static __noinline int randmap(int v, const struct net_device *dev)`
- line 43 `BPF_PROG`: `int BPF_PROG(tp_xdp_devmap_xmit_multi, const struct net_device`
- line 51 `BPF_PROG`: `int BPF_PROG(fentry_eth_type_trans, struct sk_buff *skb,`
- line 58 `BPF_PROG`: `int BPF_PROG(fexit_eth_type_trans, struct sk_buff *skb,`
- line 75 `balancer_ingress`: `int balancer_ingress(struct __sk_buff *ctx)`
- line 111 `core_relo_proto`: `int core_relo_proto(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `.maps`, `tp_btf/xdp_devmap_xmit`, `fentry/eth_type_trans`, `fexit/eth_type_trans`, `tc`, `raw_tracepoint/sys_enter`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `randmap`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `balancer_ingress`, `core_relo_proto`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 30 `int *val;`
- line 64 `volatile const int never;`
- line 67 `int len;`
- line 79 `void *ptr;`
- line 80 `int nh_off, i = 0;`
- line 108 `int proto_out[3];`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern.c -->
