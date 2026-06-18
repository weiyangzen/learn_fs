<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/securebits.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/securebits.h

Purpose: defines per-process securebits controlling legacy root privilege behavior, setuid capability fixups, keep-caps, ambient capability raising, and check_exec restrictions.

Important APIs, types, and functions: each setting has a bit and a locked companion bit. Macros include `issecure_mask`, `SECUREBITS_DEFAULT`, `SECURE_NOROOT`, `SECURE_NO_SETUID_FIXUP`, `SECURE_KEEP_CAPS`, `SECURE_NO_CAP_AMBIENT_RAISE`, `SECURE_EXEC_RESTRICT_FILE`, `SECURE_EXEC_DENY_INTERACTIVE`, their `SECBIT_*` masks, `SECURE_ALL_BITS`, `SECURE_ALL_LOCKS`, and `SECURE_ALL_UNPRIVILEGED`.

Control flow: privileged userspace or security runtimes set securebits through prctl. Kernel credential and exec paths consult these bits when handling UID 0 special cases, setuid transitions, capability retention, ambient capabilities, and check_exec policy.

State and persistence behavior: securebits are task credential state. Lock bits make corresponding settings immutable for the task and descendants according to credential inheritance rules. The header owns no storage.

Dependencies and integration points: integrates with Linux capabilities, `prctl(PR_SET_SECUREBITS)`, exec credential recalculation, ambient capabilities, and check_exec documentation/policy.

Risks and edge cases: settings are paired with locks by adjacent bits, so masks must stay aligned. `SECURE_KEEP_CAPS` clears on exec unless locked. New unprivileged exec-restriction bits must be included in aggregate masks without changing old semantics.

Test signals: capability selftests for setuid transitions, no-root mode, keep-caps across exec, ambient raise denial, locked-bit immutability, and check_exec restriction/interactive denial behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/securebits.h -->
