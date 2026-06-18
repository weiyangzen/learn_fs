<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_fail.c

## Purpose
`exceptions_fail.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 8207 bytes across 427 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `"bpf_misc.h"`, `"bpf_experimental.h"`.
- Important macros/constants: `private`.
- BPF API surface: map lookup/update/delete or map-side state; exception unwinding; bounded callback iteration.
- Helper/kfunc calls: `bpf_local_irq_restore`, `bpf_local_irq_save`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_preempt_disable`, `bpf_preempt_enable`, `bpf_rbtree_add`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`, `bpf_spin_lock`, `bpf_spin_unlock`, `bpf_throw`, `bpf_timer_set_callback`.
Map/type declarations observed:
- line 28 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 17 `SEC("#define private(name) SEC(".bss." #name) __hidden __attribute__((aligned(8)))")` -> struct foo {
- line 32 `SEC(".maps")` -> private(A) struct bpf_spin_lock lock;
- line 61 `SEC("?tc")` -> int reject_exception_cb_type_1(struct __sk_buff *ctx)
- line 70 `SEC("?tc")` -> int reject_exception_cb_type_2(struct __sk_buff *ctx)
- line 79 `SEC("?tc")` -> int reject_exception_cb_type_3(struct __sk_buff *ctx)
- line 88 `SEC("?tc")` -> int reject_exception_cb_type_4(struct __sk_buff *ctx)
- line 97 `SEC("?tc")` -> int reject_exception_cb_type_5(struct __sk_buff *ctx)
- line 113 `SEC("?tc")` -> int reject_async_callback_throw(struct __sk_buff *ctx)
- line 135 `SEC("?tc")` -> int reject_with_lock(void *ctx)
- line 144 `SEC("?tc")` -> int reject_subprog_with_lock(void *ctx)
- line 151 `SEC("?tc")` -> int reject_with_rcu_read_lock(void *ctx)
- line 167 `SEC("?tc")` -> int reject_subprog_with_rcu_read_lock(void *ctx)
- plus 18 more entries of the same pattern.
Key functions/subprograms:
- line 42 `exception_cb_bad_ret_type2`: `__noinline void exception_cb_bad_ret_type2(u64 cookie)`
- line 46 `exception_cb_bad_arg_0`: `__noinline int exception_cb_bad_arg_0(void)`
- line 51 `exception_cb_bad_arg_2`: `__noinline int exception_cb_bad_arg_2(int a, int b)`
- line 56 `exception_cb_ok_arg_small`: `__noinline int exception_cb_ok_arg_small(int a)`
- line 63 `__msg`: `__failure __msg("Global function exception_cb_bad_ret_type1() return value not void or scalar.")`
- line 64 `reject_exception_cb_type_1`: `int reject_exception_cb_type_1(struct __sk_buff *ctx)`
- line 72 `__msg`: `__failure __msg("exception cb only supports single integer argument")`
- line 73 `reject_exception_cb_type_2`: `int reject_exception_cb_type_2(struct __sk_buff *ctx)`
- line 81 `__msg`: `__failure __msg("exception cb only supports single integer argument")`
- line 82 `reject_exception_cb_type_3`: `int reject_exception_cb_type_3(struct __sk_buff *ctx)`
- line 91 `reject_exception_cb_type_4`: `int reject_exception_cb_type_4(struct __sk_buff *ctx)`
- line 99 `__msg`: `__failure __msg("exception cb cannot return void")`
- plus 62 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `#define private(name) SEC(".bss." #name) __hidden __attribute__((aligned(8)))`, `.maps`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `exception_cb_bad_ret_type2`, `exception_cb_bad_arg_0`, `exception_cb_bad_arg_2`, `exception_cb_ok_arg_small`, `__msg`, `reject_exception_cb_type_1`, `__msg`, `reject_exception_cb_type_2` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.
Exception paths deliberately leave normal fall-through through `bpf_throw`, so expected behavior includes unwind/default-return handling as well as rejection in unsafe contexts.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 127 `volatile int ret = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Exception cases are sensitive to lock, RCU, preemption, IRQ, callback, and reference-lifetime restrictions.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Uses `__success` annotations; a passing test is successful verifier load despite nearby edge cases.
- Expected verifier messages include `Global function exception_cb_bad_ret_type1() return value not void or scalar.`, `exception cb only supports single integer argument`, `exception cb only supports single integer argument`, `exception cb cannot return void`, `cannot be called from callback subprog`, plus 21 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_fail.c -->
