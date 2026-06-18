# sources/distributed-fs/ceph-client/arch/arm64/kernel/pointer_auth.c

Purpose: this file implements ARM64 pointer-authentication user ABI controls used by `prctl()` and ptrace regsets. It resets per-task PAC keys and enables or disables address-auth key use through the user SCTLR shadow.

Important APIs and state: `ptrauth_prctl_reset_keys()` resets all or selected keys in `task->thread.keys_user`, using `get_random_bytes()` and installing keys for the current task. `ptrauth_set_enabled_keys()` updates `task->thread.sctlr_user` bits corresponding to `PR_PAC_APIAKEY`, `APIBKEY`, `APDAKEY`, and `APDBKEY`. `ptrauth_get_enabled_keys()` exports the enabled-key mask. `arg_to_enxx_mask()` maps prctl bits to `SCTLR_ELx_ENIA/ENIB/ENDA/ENDB`.

Control flow: reset rejects unsupported hardware, compat tasks, unknown bits, and attempts to reset unavailable address or generic keys. Key enable changes validate `enabled` is a subset of `keys`, then update `sctlr_user` with preemption disabled; if the target is current, `update_sctlr_el1()` is called in the same critical section so context switch code cannot observe mismatched software/hardware state.

Dependencies and integration: relies on `system_supports_address_auth()`, `system_supports_generic_auth()`, ARM64 pointer-auth helpers, `update_sctlr_el1()` in `process.c`, and user ABI constants from `linux/prctl.h`. `ptrace.c` uses these routines for `NT_ARM_PAC_ENABLED_KEYS`.

Risks: PAC is unavailable for compat threads, so callers must propagate `-EINVAL` correctly. SCTLR updates are ordering-sensitive; moving preemption boundaries could race with `__switch_to()`. Key resets alter process security state and must not be accepted on unsupported CPUs.

Test signals: user ABI tests for `PR_PAC_RESET_KEYS`, `PR_PAC_SET_ENABLED_KEYS`, ptrace PAC regsets, checkpoint/restore, and mixed compat/native tasks. Runtime signs include correct PAC enable masks in ptrace and no kernel PAC disable while executing kernel code.
