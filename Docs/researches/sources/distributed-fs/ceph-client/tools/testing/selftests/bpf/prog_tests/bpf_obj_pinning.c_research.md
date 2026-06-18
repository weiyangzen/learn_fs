# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_pinning.c

## Purpose
This selftest validates BPF object pin/get behavior through both detached bpffs mounts and normally mounted bpffs paths. It specifically exercises the newer `BPF_F_PATH_FD` path mode for `bpf_obj_pin_opts()` and `bpf_obj_get_opts()`.

## Important APIs, Types, And Functions
Important wrappers are `sys_fsopen()`, `sys_fsconfig()`, `sys_fsmount()`, and unused `sys_move_mount()`. Test helpers include `bpf_obj_pinning_detached()`, `validate_pin()`, `validate_get()`, `bpf_obj_pinning_mounted()`, and `test_bpf_obj_pinning()`. It uses `bpf_map_create()`, `bpf_obj_pin_opts()`, `bpf_obj_get_opts()`, `bpf_obj_pin()`, `bpf_obj_get()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `open(O_PATH)`, `chdir()`, and `unlink()`.

## Control Flow
The detached subtest creates a detached bpffs mount with the new mount API, creates an array map, pins it relative to the detached mount FD, retrieves it relative to that same mount FD, and verifies both FDs access the same map contents. Mounted subtests create an array map and validate pin/get through three path forms: absolute string, cwd-relative string under `/sys/fs/bpf`, and directory-FD-relative path using `BPF_F_PATH_FD`.

## State And Persistence Behavior
Persistent state is intentionally short-lived: bpffs pins under `/sys/fs/bpf/<map_name>` for mounted cases and an unexposed detached mount for the detached case. Cleanup closes map, fs, and mount FDs and unlinks mounted pins. Relative-path tests temporarily change cwd and restore it.

## Dependencies And Integration Points
It depends on bpffs mounted at `/sys/fs/bpf`, support for `fsopen/fsconfig/fsmount`, `BPF_F_PATH_FD`, array maps, and libbpf internal headers for option structures. It integrates BPF syscalls with Linux VFS mount and path resolution behavior.

## Risks And Edge Cases
The detached mount path depends on modern mount API availability and privileges. Relative-path tests can affect process cwd if restoration fails, so cleanup is important. The mounted pin name is fixed and can collide with stale pins from interrupted runs.

## Test Signals
Passing signals are successful detached bpffs creation, successful pin/get through mount FD, successful pin/get through absolute, relative, and FD-relative mounted paths, and matching map values read through a second FD after updates through the first FD.
