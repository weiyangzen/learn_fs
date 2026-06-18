<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions.c

## Purpose
`exceptions.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 7384 bytes across 382 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `<bpf/bpf_endian.h>`, `"bpf_misc.h"`, `"bpf_experimental.h"`.
- Important macros/constants: `ETH_P_IP`, `check_assert`.
- BPF API surface: exception unwinding; program-array dispatch.
- Helper/kfunc calls: `bpf_assert`, `bpf_assert_range`, `bpf_assert_range_with`, `bpf_assert_with`, `bpf_cmp_unlikely`, `bpf_ktime_get_ns`, `bpf_ntohs`, `bpf_tail_call_static`, `bpf_throw`.
Map/type declarations observed:
- line 15 declares map type `BPF_MAP_TYPE_PROG_ARRAY`
Attach sections and exported entry points:
- line 19 `SEC(".maps")` -> static __noinline int static_func(u64 i)
- line 45 `SEC("tc")` -> int exception_throw_always_1(struct __sk_buff *ctx)
- line 56 `SEC("tc")` -> int exception_throw_always_2(struct __sk_buff *ctx)
- line 62 `SEC("tc")` -> int exception_throw_unwind_1(struct __sk_buff *ctx)
- line 68 `SEC("tc")` -> int exception_throw_unwind_2(struct __sk_buff *ctx)
- line 74 `SEC("tc")` -> int exception_throw_default(struct __sk_buff *ctx)
- line 81 `SEC("tc")` -> int exception_throw_default_value(struct __sk_buff *ctx)
- line 88 `SEC("tc")` -> int exception_tail_call_target(struct __sk_buff *ctx)
- line 104 `SEC("tc")` -> int exception_tail_call(struct __sk_buff *ctx) {
- line 118 `SEC("tc")` -> int exception_throw_from_void_global(struct __sk_buff *ctx)
- line 138 `SEC("tc")` -> int exception_ext(struct __sk_buff *ctx)
- line 164 `SEC("tc")` -> int exception_ext_mod_cb_runtime(struct __sk_buff *ctx)
- plus 7 more entries of the same pattern.
Key functions/subprograms:
- line 21 `static_func`: `static __noinline int static_func(u64 i)`
- line 27 `global2static_simple`: `__noinline int global2static_simple(u64 i)`
- line 33 `global2static`: `__noinline int global2static(u64 i)`
- line 40 `static2global`: `static __noinline int static2global(u64 i)`
- line 46 `exception_throw_always_1`: `int exception_throw_always_1(struct __sk_buff *ctx)`
- line 57 `exception_throw_always_2`: `int exception_throw_always_2(struct __sk_buff *ctx)`
- line 63 `exception_throw_unwind_1`: `int exception_throw_unwind_1(struct __sk_buff *ctx)`
- line 69 `exception_throw_unwind_2`: `int exception_throw_unwind_2(struct __sk_buff *ctx)`
- line 75 `exception_throw_default`: `int exception_throw_default(struct __sk_buff *ctx)`
- line 82 `exception_throw_default_value`: `int exception_throw_default_value(struct __sk_buff *ctx)`
- line 89 `exception_tail_call_target`: `int exception_tail_call_target(struct __sk_buff *ctx)`
- line 96 `exception_tail_call_subprog`: `int exception_tail_call_subprog(struct __sk_buff *ctx)`
- plus 31 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `static_func`, `global2static_simple`, `global2static`, `static2global`, `exception_throw_always_1`, `exception_throw_always_2`, `exception_throw_unwind_1`, `exception_throw_unwind_2` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Exception paths deliberately leave normal fall-through through `bpf_throw`, so expected behavior includes unwind/default-return handling as well as rejection in unsafe contexts.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 98 `volatile int ret = 10;`
- line 106 `volatile int ret = 0;`
- line 128 `volatile int ret = 0;`
- line 146 `volatile int ret = 0;`
- line 217 `volatile u64 cookie = c;`
- line 225 `volatile u64 cookie = c;`
- line 233 `volatile s64 cookie = c;`
- line 241 `volatile s64 cookie = c;`
- line 249 `volatile s64 cookie = c;`
- line 257 `volatile s64 cookie = c;`
- plus 6 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Exception cases are sensitive to lock, RCU, preemption, IRQ, callback, and reference-lifetime restrictions.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions.c -->
