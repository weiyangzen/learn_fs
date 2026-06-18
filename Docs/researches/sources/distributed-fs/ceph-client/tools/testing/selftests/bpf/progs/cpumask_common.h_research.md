<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_common.h

## Purpose
`cpumask_common.h` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4228 bytes across 129 lines.

## Important APIs, Types, and Functions
- Dependencies: `"errno.h"`, `<stdbool.h>`.
- Important macros/constants: `_CPUMASK_COMMON_H`, `CPUMASK_KPTR_FIELDS_MAX`, `private`.
- BPF API surface: map lookup/update/delete or map-side state; cpumask ownership/query/mutation kfuncs.
- Helper/kfunc calls: `bpf_cpumask_acquire`, `bpf_cpumask_and`, `bpf_cpumask_any_and_distribute`, `bpf_cpumask_any_distribute`, `bpf_cpumask_clear`, `bpf_cpumask_clear_cpu`, `bpf_cpumask_copy`, `bpf_cpumask_create`, `bpf_cpumask_empty`, `bpf_cpumask_equal`, `bpf_cpumask_first`, `bpf_cpumask_first_and`, `bpf_cpumask_first_zero`, `bpf_cpumask_full`, `bpf_cpumask_intersects`, `bpf_cpumask_or`, `bpf_cpumask_populate`, `bpf_cpumask_release`, plus 13 more.
Map/type declarations observed:
- line 25 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 17 `SEC("#define private(name) SEC(".bss." #name) __attribute__((aligned(8)))")` -> private(MASK) static struct bpf_cpumask __kptr * global_mask;
- line 29 `SEC(".maps")` -> struct bpf_cpumask *bpf_cpumask_create(void) __ksym __weak;
Key functions/subprograms:
- line 36 `bpf_cpumask_first_and`: `u32 bpf_cpumask_first_and(const struct cpumask *src1,`
- line 45 `bpf_cpumask_and`: `bool bpf_cpumask_and(struct bpf_cpumask *cpumask,`
- line 48 `bpf_cpumask_or`: `void bpf_cpumask_or(struct bpf_cpumask *cpumask,`
- line 51 `bpf_cpumask_xor`: `void bpf_cpumask_xor(struct bpf_cpumask *cpumask,`
- line 61 `bpf_cpumask_any_and_distribute`: `u32 bpf_cpumask_any_and_distribute(const struct cpumask *src1,`
- line 100 `cpumask_map_insert`: `static inline int cpumask_map_insert(struct bpf_cpumask *mask)`
- Header fixture content: 0 struct/union/enum/typedef markers provide BTF type material for consumers.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `#define private(name) SEC(".bss." #name) __attribute__((aligned(8)))`, `.maps`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `bpf_cpumask_first_and`, `bpf_cpumask_and`, `bpf_cpumask_or`, `bpf_cpumask_xor`, `bpf_cpumask_any_and_distribute`, `cpumask_map_insert`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 15 `int err;`
- line 95 `u32 key = 0;`
- line 103 `long status;`
- line 105 `u32 key = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Cpumask cases depend on trusted pointer tracking, nullability, and exact ownership/release rules.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_common.h -->
