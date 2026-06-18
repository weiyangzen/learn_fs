## sources/distributed-fs/ceph-client/rust/kernel/security.rs

Purpose: exposes Rust wrappers for selected Linux Security Module hooks and a managed security-context string returned by secid translation.

Important APIs/types/functions: binder hook wrappers are `binder_set_context_mgr`, `binder_transaction`, `binder_transfer_binder`, and `binder_transfer_file`. `SecurityCtx` owns a `bindings::lsm_context` and provides `from_secid`, `is_empty`, `len`, and `as_bytes`.

Control flow: binder functions pass credential and file raw pointers into corresponding `security_binder_*` hooks and convert integer status with `to_result`. `SecurityCtx::from_secid` zero-initializes an `lsm_context`, calls `security_secid_to_secctx`, and on success stores it. `Drop` releases it with `security_release_secctx`.

State/persistence: `SecurityCtx` temporarily owns kernel-allocated LSM context bytes; release happens on drop. Binder wrappers persist no state.

Dependencies/integration: integrates with `Credential`, `File`, `to_result`, and C LSM bindings from `include/linux/security.h`.

Risks: lifetime correctness relies on `Credential` and `File` shared references guaranteeing live refcounts. `as_bytes` must handle null context pointers for empty contexts because `slice::from_raw_parts` cannot take null even for zero length. Drop must only run for contexts produced by successful `security_secid_to_secctx`.

Test signals: no local tests. Useful validation includes LSM-enabled binder paths, secid conversion success/failure, empty contexts, and ensuring release is called once.
