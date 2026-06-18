<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_success.c

## Purpose
`dynptr_success.c` is a positive dynptr suite covering local, ring-buffer, skb, xdp, clone, copy, adjust, memset, and probe-read cases. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 25338 bytes across 1137 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<string.h>`, `<stdbool.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"errno.h"`.
- Important macros/constants: `PAGE_SIZE_64K`, `DYNPTR_MEMSET_VAL`, `min_t`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers; bounded callback iteration.
- Helper/kfunc calls: `bpf_copy_data_from_user_task`, `bpf_copy_data_from_user_task_str`, `bpf_copy_from_user_task_dynptr`, `bpf_copy_from_user_task_str_dynptr`, `bpf_dynptr_adjust`, `bpf_dynptr_clone`, `bpf_dynptr_copy`, `bpf_dynptr_data`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`, `bpf_dynptr_from_skb_meta`, `bpf_dynptr_from_xdp`, `bpf_dynptr_is_null`, `bpf_dynptr_is_rdonly`, `bpf_dynptr_memset`, `bpf_dynptr_read`, `bpf_dynptr_size`, `bpf_dynptr_slice`, plus 15 more.
Map/type declarations observed:
- line 26 declares map type `BPF_MAP_TYPE_RINGBUF`
- line 31 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 14 `SEC("license")` -> int pid, err, val;
- line 28 `SEC(".maps")` -> struct {
- line 35 `SEC(".maps")` -> int test_read_write(void *ctx)
- line 37 `SEC("?tp/syscalls/sys_enter_nanosleep")` -> int test_read_write(void *ctx)
- line 68 `SEC("?tp/syscalls/sys_enter_nanosleep")` -> int test_dynptr_data(void *ctx)
- line 138 `SEC("?tp/syscalls/sys_enter_nanosleep")` -> int test_ringbuf(void *ctx)
- line 171 `SEC("?cgroup_skb/egress")` -> int test_skb_readonly(struct __sk_buff *skb)
- line 193 `SEC("?cgroup_skb/egress")` -> int test_dynptr_skb_data(struct __sk_buff *skb)
- line 214 `SEC("?tc")` -> int test_dynptr_skb_meta_data(struct __sk_buff *skb)
- line 237 `SEC("?tc")` -> int test_dynptr_skb_meta_flags(struct __sk_buff *skb)
- line 269 `SEC("tp/syscalls/sys_enter_nanosleep")` -> int test_adjust(void *ctx)
- line 321 `SEC("tp/syscalls/sys_enter_nanosleep")` -> int test_adjust_err(void *ctx)
- plus 25 more entries of the same pattern.
Key functions/subprograms:
- line 38 `test_read_write`: `int test_read_write(void *ctx)`
- line 69 `test_dynptr_data`: `int test_dynptr_data(void *ctx)`
- line 123 `ringbuf_callback`: `static int ringbuf_callback(__u32 index, void *data)`
- line 139 `test_ringbuf`: `int test_ringbuf(void *ctx)`
- line 172 `test_skb_readonly`: `int test_skb_readonly(struct __sk_buff *skb)`
- line 194 `test_dynptr_skb_data`: `int test_dynptr_skb_data(struct __sk_buff *skb)`
- line 215 `test_dynptr_skb_meta_data`: `int test_dynptr_skb_meta_data(struct __sk_buff *skb)`
- line 238 `test_dynptr_skb_meta_flags`: `int test_dynptr_skb_meta_flags(struct __sk_buff *skb)`
- line 270 `test_adjust`: `int test_adjust(void *ctx)`
- line 322 `test_adjust_err`: `int test_adjust_err(void *ctx)`
- line 380 `test_zero_size_dynptr`: `int test_zero_size_dynptr(void *ctx)`
- line 430 `test_dynptr_is_null`: `int test_dynptr_is_null(void *ctx)`
- plus 32 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `?tp/syscalls/sys_enter_nanosleep`, `?tp/syscalls/sys_enter_nanosleep`, `?tp/syscalls/sys_enter_nanosleep`, `?cgroup_skb/egress`, `?cgroup_skb/egress` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_read_write`, `test_dynptr_data`, `ringbuf_callback`, `test_ringbuf`, `test_skb_readonly`, `test_dynptr_skb_data`, `test_dynptr_skb_meta_data`, `test_dynptr_skb_meta_flags` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `int pid, err, val;`
- line 19 `int pid;`
- line 20 `int seq;`
- line 21 `long value;`
- line 22 `char comm[16];`
- line 40 `char write_data[64] = "hello there, world!!";`
- line 41 `char read_data[64] = {};`
- line 43 `int i;`
- line 71 `__u32 key = 0, val = 235, *map_val;`
- line 73 `__u32 map_val_size;`
- plus 55 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_success.c -->
