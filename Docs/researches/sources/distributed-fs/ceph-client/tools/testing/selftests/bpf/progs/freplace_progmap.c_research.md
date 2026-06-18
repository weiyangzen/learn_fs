<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_progmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_progmap.c

## Purpose
`freplace_progmap.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 473 bytes across 24 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_redirect_map`.
Map/type declarations observed:
- line 6 declares map type `BPF_MAP_TYPE_CPUMAP`
Attach sections and exported entry points:
- line 10 `SEC(".maps")` -> int xdp_drop_prog(struct xdp_md *ctx)
- line 12 `SEC("xdp/cpumap")` -> int xdp_drop_prog(struct xdp_md *ctx)
- line 18 `SEC("freplace")` -> int xdp_cpumap_prog(struct xdp_md *ctx)
- line 24 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 13 `xdp_drop_prog`: `int xdp_drop_prog(struct xdp_md *ctx)`
- line 19 `xdp_cpumap_prog`: `int xdp_cpumap_prog(struct xdp_md *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `xdp/cpumap`, `freplace`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `xdp_drop_prog`, `xdp_cpumap_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_progmap.c -->
