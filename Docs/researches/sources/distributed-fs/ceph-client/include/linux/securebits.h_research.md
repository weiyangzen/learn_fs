# sources/distributed-fs/ceph-client/include/linux/securebits.h

Purpose: `securebits.h` wraps UAPI securebits definitions and provides the kernel `issecure(X)` helper for checking the current credentials' securebits mask.

Important APIs/types/functions: It includes `<uapi/linux/securebits.h>` and defines `issecure(X)` as `issecure_mask(X) & current_cred_xxx(securebits)`. The UAPI header supplies bit numbers and masks controlling capability behavior across uid transitions and exec.

Control flow: Capability and credential-changing paths call `issecure()` to decide whether securebits alter default capability fixups. This header does not implement transitions itself.

State and persistence behavior: State lives in current credentials' `securebits` field and persists according to credential copy/commit semantics. Securebits are per-credential, not global.

Dependencies and integration points: It depends on current credential accessors and capability code. It integrates with `security_task_fix_setuid()`, `cap_task_prctl()`, setuid/setgid handling, and user namespace capability rules.

Risks: The helper references current credentials, so it is only appropriate for current-task decisions. Incorrect use for arbitrary target credentials can check the wrong security state.

Test signals: Securebits prctl operations, setuid/setgid transitions, keep-caps/no-setuid-fixup behavior, locked bit enforcement, and namespace capability tests.
