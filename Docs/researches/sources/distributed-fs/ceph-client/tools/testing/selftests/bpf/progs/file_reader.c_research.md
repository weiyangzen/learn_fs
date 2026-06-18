<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader.c

## Purpose
`file_reader.c` is a file-dynptr selftest using LSM hooks and dynptr reads against kernel file contents. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3538 bytes across 145 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<string.h>`, `<stdbool.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"errno.h"`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers; task or cgroup reference kfuncs.
- Helper/kfunc calls: `bpf_dynptr_adjust`, `bpf_dynptr_file_discard`, `bpf_dynptr_from_file`, `bpf_dynptr_read`, `bpf_for`, `bpf_get_current_pid_tgid`, `bpf_get_current_task_btf`, `bpf_get_task_exe_file`, `bpf_map_lookup_elem`, `bpf_put_file`, `bpf_task_work_schedule_signal`.
Map/type declarations observed:
- line 14 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 11 `SEC("license")` -> struct {
- line 18 `SEC(".maps")` -> struct elem {
- line 34 `SEC("lsm/file_open")` -> int on_open_expect_fault(void *c)
- line 65 `SEC("lsm/file_open")` -> int on_open_validate_file_read(void *c)
Key functions/subprograms:
- line 35 `on_open_expect_fault`: `int on_open_expect_fault(void *c)`
- line 66 `on_open_validate_file_read`: `int on_open_validate_file_read(void *c)`
- line 85 `task_work_callback`: `static int task_work_callback(struct bpf_map *map, void *key, void *value)`
- line 100 `verify_dynptr_read`: `static int verify_dynptr_read(struct bpf_dynptr *ptr, u32 off, char *user_buf, u32 len)`
- line 116 `validate_file_read`: `static int validate_file_read(struct file *file)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `lsm/file_open`, `lsm/file_open`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `on_open_expect_fault`, `on_open_validate_file_read`, `task_work_callback`, `verify_dynptr_read`, `validate_file_read`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 25 `char user_buf[256000];`
- line 26 `char tmp_buf[256000];`
- line 28 `int pid = 0;`
- line 29 `int err, run_success = 0;`
- line 39 `int local_err = 1;`
- line 70 `int key = 0;`
- line 102 `int i;`
- line 119 `int loc_err = 1, off;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- BPF LSM hooks may require sleepable attachment and kernel security/IMA configuration.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader.c -->
