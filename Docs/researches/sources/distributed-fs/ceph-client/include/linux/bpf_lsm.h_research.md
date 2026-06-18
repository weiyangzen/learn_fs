# sources/distributed-fs/ceph-client/include/linux/bpf_lsm.h

Purpose: Declares BPF LSM hook entry points and helper interfaces for verifying and running BPF programs attached to Linux Security Module hooks. It also exposes inode local storage support and cgroup LSM shim helpers.

Important APIs/types/functions: Under `CONFIG_BPF_LSM`, `LSM_HOOK()` expansion declares `bpf_lsm_<hook>()` functions for every hook in `lsm_hook_defs.h`. `struct bpf_storage_blob` holds an RCU local-storage pointer for security blobs. `bpf_lsm_blob_sizes` identifies offsets in LSM blobs. `bpf_lsm_verify_prog()` validates BPF LSM programs. `bpf_lsm_is_sleepable_hook()` and `bpf_lsm_is_trusted()` classify hooks/programs. `bpf_inode()` computes the BPF storage blob inside `inode->i_security`. Inode storage helper prototypes, cgroup shim lookup, retval range lookup, and locked dentry xattr helpers are declared. Disabled stubs return false, NULL, or `-EOPNOTSUPP`.

Control flow: LSM dispatch invokes generated `bpf_lsm_*` hook functions. Program load calls verification helpers to enforce hook-specific constraints and return ranges. Inode lifecycle frees BPF inode storage. Cgroup LSM integration can locate a shim trampoline for per-cgroup LSM hooks.

State/persistence: BPF LSM storage is held in LSM security blobs and RCU-protected local storage. Hook program attachments and blob offsets persist while the BPF LSM facility and objects exist.

Dependencies/integration: Depends on scheduler types, core BPF/verifier APIs, LSM hooks/blobs, inode/dentry structures, BPF local storage, and optional cgroup BPF LSM slots.

Risks/test signals: Risks include wrong blob offset arithmetic, hook sleepability mismatches, verifier return-range mistakes, xattr locking misuse, and disabled-config behavior drift. Test signals include BPF LSM selftests, LSM hook coverage, inode storage get/delete/free tests, cgroup LSM attach tests, xattr helper tests under lockdep, and config builds without `CONFIG_BPF_LSM`.
