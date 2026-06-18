<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader_fail.c

## Purpose
`file_reader_fail.c` is a file-dynptr selftest using LSM hooks and dynptr reads against kernel file contents. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1047 bytes across 52 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<string.h>`, `<stdbool.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers.
- Helper/kfunc calls: `bpf_dynptr_file_discard`, `bpf_dynptr_from_file`, `bpf_dynptr_from_xdp`, `bpf_get_current_task_btf`, `bpf_get_task_exe_file`.
Attach sections and exported entry points:
- line 10 `SEC("license")` -> int err;
- line 15 `SEC("lsm/file_open")` -> int on_nanosleep_unreleased_ref(void *ctx)
- line 31 `SEC("xdp")` -> int xdp_wrong_dynptr_type(struct xdp_md *xdp)
- line 43 `SEC("xdp")` -> int xdp_no_dynptr_type(struct xdp_md *xdp)
Key functions/subprograms:
- line 18 `on_nanosleep_unreleased_ref`: `int on_nanosleep_unreleased_ref(void *ctx)`
- line 34 `xdp_wrong_dynptr_type`: `int xdp_wrong_dynptr_type(struct xdp_md *xdp)`
- line 46 `xdp_no_dynptr_type`: `int xdp_no_dynptr_type(struct xdp_md *xdp)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `lsm/file_open`, `xdp`, `xdp`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `on_nanosleep_unreleased_ref`, `xdp_wrong_dynptr_type`, `xdp_no_dynptr_type`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `int err;`
- line 13 `void *user_ptr;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- BPF LSM hooks may require sleepable attachment and kernel security/IMA configuration.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `Unreleased reference id=`, `Expected a dynptr of type file as arg #0`, `Expected an initialized dynptr as arg #0`.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader_fail.c -->
