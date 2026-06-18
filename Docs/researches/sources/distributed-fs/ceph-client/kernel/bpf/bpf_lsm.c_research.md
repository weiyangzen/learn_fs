# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm.c

## Purpose
`bpf_lsm.c` wires BPF programs into Linux Security Module hooks. It creates attachable weak BPF LSM hook symbols, builds BTF ID allow/deny sets for verifier checks, exposes LSM-specific helper prototypes, classifies hooks as sleepable/trusted/current-cgroup/socket-option-capable, and constrains verifier return ranges for LSM programs.

## Important APIs, Types, and Functions
The `LSM_HOOK` macro expansion over `<linux/lsm_hook_defs.h>` emits weak `bpf_lsm_<hook>()` functions returning each hook default value and builds the `bpf_lsm_hooks` BTF set. `bpf_lsm_verify_prog()` enforces GPL-compatible programs, rejects disabled hooks, and verifies that `attach_btf_id` is in the BPF LSM hook set. Under `CONFIG_CGROUP_BPF`, `bpf_lsm_find_cgroup_shim()` chooses the cgroup shim runner based on hook arguments and cgroup/current hook sets. Helper implementations and prototypes include `bpf_bprm_opts_set`, `bpf_ima_inode_hash`, `bpf_ima_file_hash`, and `bpf_get_attach_cookie`. `bpf_lsm_func_proto()` exposes those helpers plus inode/sk storage, spin locks, cgroup helpers, sockopt helpers for selected cgroup LSM hooks, and generic tracing helpers. `bpf_lsm_is_sleepable_hook()`, `bpf_lsm_is_trusted()`, and `bpf_lsm_get_retval_range()` are verifier-facing policy APIs.

## Control Flow
At build time, BTF ID macros assemble hook sets. During program verification, the verifier calls `bpf_lsm_verify_prog()` and `lsm_verifier_ops.get_func_proto`. Helper availability is determined by function id, expected attach type, attach BTF id, and optional kernel configuration. During runtime attach and execution, the trampoline/cgroup code uses the hook symbol and, for cgroup LSM, a selected shim to run programs against current, socket, or sock contexts.

## State and Persistence Behavior
This file does not persist dynamic state. The important state is static BTF ID sets and helper prototype tables compiled into the kernel. `bpf_bprm_opts_set()` mutates `linux_binprm->secureexec` for the current exec path; IMA helpers fill caller-provided buffers; `bpf_get_attach_cookie()` reads the active trace run context. These effects last only for their kernel operation context.

## Dependencies and Integration Points
The file depends on BTF/BTF ID infrastructure, BPF verifier and trampoline support, LSM hook definitions, IMA, cgroup BPF, socket storage, inode storage, tracing helper policy, and optional network/audit/key/security-path configuration. It integrates with `kernel/bpf/verifier.c` for attach checks, sleepable checks, trusted pointer decisions, and return-value ranges, and with LSM hook registration through the generated `bpf_lsm_*` symbols.

## Risks
Hook-set drift is the central risk: adding or changing an LSM hook without updating disabled, sleepable, cgroup-current, sockopt, trusted, or bool-return sets can expose unsafe helpers or reject valid programs. Sleepable classification must match hook execution context because IMA helpers may sleep. Sockopt helper exposure is intentionally limited to hooks where the socket is locked or early-init unlocked; misclassification can introduce locking bugs. Return range constraints must stay aligned with hook semantics, especially bool hooks and void hooks. Disabled hooks document ABI and verifier safety exclusions that should be revisited carefully.

## Test Signals
Relevant tests include BPF LSM selftests for attach success/failure, GPL license rejection, disabled hook rejection, sleepable helper availability, IMA hash helper use, cgroup LSM current/socket/sock dispatch, sockopt helper availability only on the named hooks, attach-cookie reads through trampoline-attached programs, and verifier return-range diagnostics for bool and errno-returning hooks.
