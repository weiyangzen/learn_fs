<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dev_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dev_cgroup.c

## Purpose
`dev_cgroup.c` is a cgroup device-access policy selftest returning allow or deny from device metadata. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1185 bytes across 59 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<linux/version.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_prog1`, `bpf_trace_printk`.
Attach sections and exported entry points:
- line 12 `SEC("cgroup/dev")` -> int bpf_prog1(struct bpf_cgroup_dev_ctx *ctx)
- line 59 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 13 `bpf_prog1`: `int bpf_prog1(struct bpf_cgroup_dev_ctx *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/dev`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `bpf_prog1`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 18 `char fmt[] = " %d:%d \n";`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dev_cgroup.c -->
