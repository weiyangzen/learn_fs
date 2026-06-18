<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/decap_sanity.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/decap_sanity.c

## Purpose
`decap_sanity.c` is a packet decapsulation sanity selftest for skb/tunnel metadata changes. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1716 bytes across 68 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `"bpf_tracing_net.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- Important macros/constants: `UDP_TEST_PORT`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_cast_to_kern_ctx`, `bpf_skb_adjust_room`, `bpf_skb_load_bytes`.
Attach sections and exported entry points:
- line 31 `SEC("tc")` -> int decap_sanity(struct __sk_buff *skb)
- line 68 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 16 `skb_headlen`: `static unsigned int skb_headlen(const struct sk_buff *skb)`
- line 21 `skb_headroom`: `static unsigned int skb_headroom(const struct sk_buff *skb)`
- line 26 `skb_checksum_start_offset`: `static int skb_checksum_start_offset(const struct sk_buff *skb)`
- line 32 `decap_sanity`: `int decap_sanity(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `skb_headlen`, `skb_headroom`, `skb_checksum_start_offset`, `decap_sanity`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `bool init_csum_partial = false;`
- line 13 `bool final_csum_none = false;`
- line 14 `bool broken_csum_start = false;`
- line 37 `int err;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/decap_sanity.c -->
