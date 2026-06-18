<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf_simple.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf_simple.c

## Purpose
`fexit_bpf2bpf_simple.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 488 bytes across 27 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 13 `SEC("fexit/test_pkt_md_access")` -> int BPF_PROG(test_main2, struct sk_buff *skb, int ret)
- line 27 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `BPF_PROG`: `int BPF_PROG(test_main2, struct sk_buff *skb, int ret)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `fexit/test_pkt_md_access`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `__u64 test_result = 0;`
- line 16 `int len;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf_simple.c -->
