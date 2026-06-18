<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dmabuf_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dmabuf_iter.c

## Purpose
`dmabuf_iter.c` is a BPF iterator selftest that emits DMA-BUF metadata through seq output. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2341 bytes across 101 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_core_read.h>`, `<bpf/bpf_helpers.h>`.
- Important macros/constants: `DMA_BUF_NAME_LEN`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_core_read`, `bpf_for`, `bpf_for_each`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel_str`.
Map/type declarations observed:
- line 13 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 10 `SEC("license")` -> struct {
- line 17 `SEC(".maps")` -> /*
- line 30 `SEC("iter/dmabuf")` -> int dmabuf_collector(struct bpf_iter__dmabuf *ctx)
- line 62 `SEC("syscall")` -> int iter_dmabuf_for_each(const void *ctx)
Key functions/subprograms:
- line 23 `sanitize_string`: `static void sanitize_string(char *src, size_t size)`
- line 31 `dmabuf_collector`: `int dmabuf_collector(struct bpf_iter__dmabuf *ctx)`
- line 63 `iter_dmabuf_for_each`: `int iter_dmabuf_for_each(const void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `iter/dmabuf`, `syscall`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `sanitize_string`, `dmabuf_collector`, `iter_dmabuf_for_each`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 38 `char name[DMA_BUF_NAME_LEN] = {'\0'};`
- line 68 `char name[DMA_BUF_NAME_LEN];`
- line 70 `bool *found;`
- line 71 `long len;`
- line 72 `int i;`
- line 94 `bool t = true;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dmabuf_iter.c -->
