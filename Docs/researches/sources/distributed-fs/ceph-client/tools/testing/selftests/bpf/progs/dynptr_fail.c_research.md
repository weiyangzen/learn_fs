<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_fail.c

## Purpose
`dynptr_fail.c` is a negative dynptr verifier suite covering invalid dynptr state, bounds, helper argument, and reference-lifetime cases. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 45226 bytes across 2110 lines.

## Important APIs, Types, and Functions
- Dependencies: `<errno.h>`, `<string.h>`, `<stdbool.h>`, `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<linux/if_ether.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers; bounded callback iteration.
- Helper/kfunc calls: `bpf_dynptr_adjust`, `bpf_dynptr_clone`, `bpf_dynptr_data`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`, `bpf_dynptr_from_skb_meta`, `bpf_dynptr_from_xdp`, `bpf_dynptr_is_null`, `bpf_dynptr_is_rdonly`, `bpf_dynptr_read`, `bpf_dynptr_size`, `bpf_dynptr_slice`, `bpf_dynptr_slice_rdwr`, `bpf_dynptr_write`, `bpf_get_current_comm`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, plus 8 more.
Map/type declarations observed:
- line 22 declares map type `BPF_MAP_TYPE_ARRAY`
- line 29 declares map type `BPF_MAP_TYPE_ARRAY`
- line 36 declares map type `BPF_MAP_TYPE_ARRAY`
- line 43 declares map type `BPF_MAP_TYPE_ARRAY`
- line 56 declares map type `BPF_MAP_TYPE_RINGBUF`
Attach sections and exported entry points:
- line 14 `SEC("license")` -> struct test_info {
- line 26 `SEC(".maps")` -> struct {
- line 33 `SEC(".maps")` -> struct {
- line 40 `SEC(".maps")` -> struct {
- line 47 `SEC(".maps")` -> struct sample {
- line 58 `SEC(".maps")` -> int err, val;
- line 80 `SEC("?raw_tp")` -> int ringbuf_missing_release1(void *ctx)
- line 93 `SEC("?raw_tp")` -> int ringbuf_missing_release2(void *ctx)
- line 129 `SEC("?raw_tp")` -> int ringbuf_missing_release_callback(void *ctx)
- line 138 `SEC("?raw_tp")` -> int ringbuf_release_uninit_dynptr(void *ctx)
- line 151 `SEC("?raw_tp")` -> int use_after_invalid(void *ctx)
- line 171 `SEC("?raw_tp")` -> int ringbuf_invalid_api(void *ctx)
- plus 85 more entries of the same pattern.
Key functions/subprograms:
- line 62 `get_map_val_dynptr`: `static int get_map_val_dynptr(struct bpf_dynptr *ptr)`
- line 81 `__msg`: `__failure __msg("Unreleased reference id=2")`
- line 82 `ringbuf_missing_release1`: `int ringbuf_missing_release1(void *ctx)`
- line 94 `__msg`: `__failure __msg("Unreleased reference id=4")`
- line 95 `ringbuf_missing_release2`: `int ringbuf_missing_release2(void *ctx)`
- line 117 `missing_release_callback_fn`: `static int missing_release_callback_fn(__u32 index, void *data)`
- line 130 `__msg`: `__failure __msg("Unreleased reference id")`
- line 131 `ringbuf_missing_release_callback`: `int ringbuf_missing_release_callback(void *ctx)`
- line 139 `__msg`: `__failure __msg("arg 1 is an unacquired reference")`
- line 140 `ringbuf_release_uninit_dynptr`: `int ringbuf_release_uninit_dynptr(void *ctx)`
- line 152 `__msg`: `__failure __msg("Expected an initialized dynptr as arg #2")`
- line 153 `use_after_invalid`: `int use_after_invalid(void *ctx)`
- plus 177 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `?raw_tp`, `?raw_tp` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `get_map_val_dynptr`, `__msg`, `ringbuf_missing_release1`, `__msg`, `ringbuf_missing_release2`, `missing_release_callback_fn`, `__msg`, `ringbuf_missing_release_callback` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 17 `int x;`
- line 50 `int pid;`
- line 51 `long value;`
- line 52 `char comm[16];`
- line 60 `int err, val;`
- line 64 `__u32 key = 0, *map_val;`
- line 156 `char read_data[64];`
- line 199 `int key = 0;`
- line 217 `int key = 0;`
- line 235 `void *data;`
- plus 47 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Uses `__success` annotations; a passing test is successful verifier load despite nearby edge cases.
- Expected verifier messages include `Unreleased reference id=2`, `Unreleased reference id=4`, `Unreleased reference id`, `arg 1 is an unacquired reference`, `Expected an initialized dynptr as arg #2`, plus 81 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_fail.c -->
