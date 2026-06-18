<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fib_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fib_lookup.c

## Purpose
`fib_lookup.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 496 bytes across 22 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/types.h>`, `<linux/bpf.h>`, `<linux/pkt_cls.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_fib_lookup`.
Attach sections and exported entry points:
- line 13 `SEC("tc")` -> int fib_lookup(struct __sk_buff *skb)
- line 22 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `fib_lookup`: `int fib_lookup(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `fib_lookup`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `int fib_lookup_ret = 0;`
- line 11 `int lookup_flags = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fib_lookup.c -->
