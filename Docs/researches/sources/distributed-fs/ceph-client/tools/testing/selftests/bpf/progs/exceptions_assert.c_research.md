<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_assert.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_assert.c

## Purpose
`exceptions_assert.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4020 bytes across 135 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<limits.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `<bpf/bpf_endian.h>`, `"bpf_misc.h"`, `"bpf_experimental.h"`.
- Important macros/constants: `check_assert`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_assert`, `bpf_assert_range`, `bpf_assert_with`, `bpf_cmp_unlikely`, `bpf_ktime_get_ns`.
Attach sections and exported entry points:
- line 12 `SEC("?tc")` -> int check_assert_##name(void *ctx) \
- line 60 `SEC("?tc")` -> int check_assert_range_s64(struct __sk_buff *ctx)
- line 76 `SEC("?tc")` -> int check_assert_range_u64(struct __sk_buff *ctx)
- line 87 `SEC("?tc")` -> int check_assert_single_range_s64(struct __sk_buff *ctx)
- line 104 `SEC("?tc")` -> int check_assert_single_range_u64(struct __sk_buff *ctx)
- line 115 `SEC("?tc")` -> int check_assert_generic(struct __sk_buff *ctx)
- line 127 `SEC("?fentry/bpf_check")` -> int check_assert_with_return(void *ctx)
- line 135 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 63 `check_assert_range_s64`: `int check_assert_range_s64(struct __sk_buff *ctx)`
- line 79 `check_assert_range_u64`: `int check_assert_range_u64(struct __sk_buff *ctx)`
- line 90 `check_assert_single_range_s64`: `int check_assert_single_range_s64(struct __sk_buff *ctx)`
- line 107 `check_assert_single_range_u64`: `int check_assert_single_range_u64(struct __sk_buff *ctx)`
- line 118 `check_assert_generic`: `int check_assert_generic(struct __sk_buff *ctx)`
- line 128 `__msg`: `__failure __msg("At program exit the register R1 has smin=64 smax=64")`
- line 129 `check_assert_with_return`: `int check_assert_with_return(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?fentry/bpf_check`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `check_assert_range_s64`, `check_assert_range_u64`, `check_assert_single_range_s64`, `check_assert_single_range_u64`, `check_assert_generic`, `__msg`, `check_assert_with_return`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 66 `s64 num;`
- line 81 `u64 num = ctx->len;`
- line 93 `s64 num;`
- line 109 `u64 num = ctx->len;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `R{{.}}=0xffffffff80000000`, `R{{.}}=0x7fffffff`, `R{{.}}=0`, `R{{.}}=0x8000000000000000`, `R{{.}}=0x7fffffffffffffff`, plus 18 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_assert.c -->
