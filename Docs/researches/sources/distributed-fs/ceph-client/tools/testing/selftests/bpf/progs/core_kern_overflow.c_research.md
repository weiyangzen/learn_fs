<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern_overflow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern_overflow.c

## Purpose
`core_kern_overflow.c` is a CO-RE runtime program validating BTF type reads, trace/fentry/fexit attachment, and prototype relocations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 522 bytes across 22 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_core_read.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_core_type_exists`.
Attach sections and exported entry points:
- line 14 `SEC("raw_tracepoint/sys_enter")` -> int core_relo_proto(void *ctx)
- line 22 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 15 `core_relo_proto`: `int core_relo_proto(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `raw_tracepoint/sys_enter`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `core_relo_proto`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `int proto_out;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern_overflow.c -->
