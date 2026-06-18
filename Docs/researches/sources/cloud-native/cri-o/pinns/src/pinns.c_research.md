# sources/cloud-native/cri-o/pinns/src/pinns.c

Purpose: command-line helper that creates/unshares selected Linux namespaces, optionally configures user mappings and sysctls, and bind-mounts namespace handles into a pin directory for CRI-O namespace lifecycle management.

Important APIs/types/functions: `main`; option parsing for `--uts`, `--ipc`, `--net`, `--user`, `--cgroup`, `--mnt`, `--dir`, `--filename`, `--uid-mapping`, `--gid-mapping`, and `--sysctl`; helpers `is_host_ns`, `setup_unbindable_bindpath`, `create_bind_root`, `bind_ns`, `directory_exists_or_create`, and `write_mapping_file`.

Control flow: parses requested namespaces and paths, validates mappings, creates the pin directory, then either unshares in-process or forks when user/mount namespaces require a child. User namespace creation synchronizes parent/child over a `SOCK_SEQPACKET` socketpair so parent can write uid/gid maps before the child unshares remaining namespaces and pauses. The parent then bind-mounts `/proc/<pid>/ns/<name>` or `/proc/self/ns/<name>` into `$dir/${ns}ns/$filename`, makes mount namespace bind roots unbindable, kills/waits child when done, and exits.

State and persistence: creates namespace pin directories/files, bind mounts namespace descriptors, writes `/proc/<pid>/uid_map` and `gid_map`, applies sysctls inside newly created namespaces, and may create a temporary child process. Pinned namespace mounts persist after the helper exits until unmounted by CRI-O cleanup.

Dependencies/integration: uses Linux namespace syscalls, mount APIs, procfs namespace files, `sysctl.c`, and `utils.h`. `pkg/config/config_linux.go` validates the executable path; CRI-O namespace manager invokes it.

Risks: privileged syscall-heavy code with many host side effects. `sysctls` allocation is based on `argc/2`, which matches expected option/value pairs but is not independently bounds-checked. `open(..., O_CREAT|O_EXCL, 0)` creates mode-000 pin files before bind mounting. `write_mapping_file` writes a NUL byte because it uses `it - content + 1`; proc mapping files may reject unexpected bytes depending on kernel behavior. Path concatenation relies on `PATH_MAX` truncation discipline rather than rejecting overlong inputs.

Test signals: no direct tests in this subset; validation is mainly compile/build plus integration tests that create and clean pinned namespaces.
