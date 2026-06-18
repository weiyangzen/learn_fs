<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_attach_probe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_attach_probe.c

## Purpose
`freplace_attach_probe.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 757 bytes across 40 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/ptrace.h>`, `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `VAR_NUM`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_map_lookup_elem`, `bpf_spin_lock`, `bpf_spin_unlock`.
Map/type declarations observed:
- line 17 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 21 `SEC(".maps")` -> int new_handle_kprobe(struct pt_regs *ctx)
- line 23 `SEC("freplace/handle_kprobe")` -> int new_handle_kprobe(struct pt_regs *ctx)
- line 40 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 24 `new_handle_kprobe`: `int new_handle_kprobe(struct pt_regs *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `freplace/handle_kprobe`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `new_handle_kprobe`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `int var[VAR_NUM];`
- line 27 `int key = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_attach_probe.c -->
