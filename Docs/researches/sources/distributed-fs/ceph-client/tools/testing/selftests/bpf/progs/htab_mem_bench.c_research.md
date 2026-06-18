<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_mem_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_mem_bench.c

## Purpose
`htab_mem_bench.c` is a hash-map selftest or benchmark covering lookup, update, delete, reuse, or memory pressure behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2256 bytes across 105 lines.

## Important APIs, Types, and Functions
- Dependencies: `<stdbool.h>`, `<errno.h>`, `<linux/types.h>`, `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `OP_BATCH`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; bounded callback iteration.
- Helper/kfunc calls: `bpf_get_smp_processor_id`, `bpf_loop`, `bpf_map_delete_elem`, `bpf_map_update_elem`.
Map/type declarations observed:
- line 18 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 21 `SEC(".maps")` -> unsigned char zeroed_value[4096];
- line 23 `SEC("license")` -> unsigned char zeroed_value[4096];
- line 55 `SEC("?tp/syscalls/sys_enter_getpgid")` -> int overwrite(void *ctx)
- line 67 `SEC("?tp/syscalls/sys_enter_getpgid")` -> int batch_add_batch_del(void *ctx)
- line 83 `SEC("?tp/syscalls/sys_enter_getpgid")` -> int add_only(void *ctx)
- line 95 `SEC("?tp/syscalls/sys_enter_getppid")` -> int del_only(void *ctx)
Key functions/subprograms:
- line 29 `write_htab`: `static int write_htab(unsigned int i, struct update_ctx *ctx, unsigned int flags)`
- line 37 `overwrite_htab`: `static int overwrite_htab(unsigned int i, struct update_ctx *ctx)`
- line 42 `newwrite_htab`: `static int newwrite_htab(unsigned int i, struct update_ctx *ctx)`
- line 47 `del_htab`: `static int del_htab(unsigned int i, struct update_ctx *ctx)`
- line 56 `overwrite`: `int overwrite(void *ctx)`
- line 68 `batch_add_batch_del`: `int batch_add_batch_del(void *ctx)`
- line 84 `add_only`: `int add_only(void *ctx)`
- line 96 `del_only`: `int del_only(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `license`, `?tp/syscalls/sys_enter_getpgid`, `?tp/syscalls/sys_enter_getpgid`, `?tp/syscalls/sys_enter_getpgid`, `?tp/syscalls/sys_enter_getppid`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `write_htab`, `overwrite_htab`, `newwrite_htab`, `del_htab`, `overwrite`, `batch_add_batch_del`, `add_only`, `del_only`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 27 `long op_cnt = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_mem_bench.c -->
