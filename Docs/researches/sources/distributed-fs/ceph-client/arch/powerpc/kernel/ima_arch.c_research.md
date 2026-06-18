# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ima_arch.c

## Purpose
Supplies PowerPC-specific default IMA policy rules based on secure boot and trusted boot state.

## Important APIs, Types, And Functions
Defines policy arrays `secure_rules`, `trusted_rules`, and `secure_and_trusted_rules`, and exports architecture hook `arch_get_ima_policy`. It calls `is_ppc_secureboot_enabled`, `is_ppc_trustedboot_enabled`, and `set_module_sig_enforced`.

## Control Flow
When IMA asks for architecture policy, the function first checks secure boot. Secure boot enforces module signatures and returns appraisal rules, combined with measurement rules if trusted boot is also enabled. Trusted boot alone returns measurement rules. Systems with neither mode return `NULL`.

## State And Persistence
The policy arrays are static read-only strings. The only state mutation is module signature enforcement when secure boot is active. IMA consumes returned rules during policy setup; this file does not persist data.

## Dependencies And Integration Points
Depends on generic IMA policy parsing, PowerPC secure/trusted boot detection, kexec kernel appraisal, module appraisal/measurement hooks, and `CONFIG_MODULE_SIG` to avoid duplicate module appraisal rules.

## Risks And Edge Cases
Incorrect boot-state detection can under- or over-enforce module and kexec appraisal. When `CONFIG_MODULE_SIG` is enabled, module appraisal is intentionally omitted from secure rules to avoid duplicate verification. Policy strings must remain compatible with IMA parser syntax.

## Test Signals
Signals include secure boot returning appraisal policy and enforcing module signatures, trusted boot returning measurement policy, combined secure+trusted using `ima-modsig` template, kexec/module loading tests with signed and unsigned images, and builds with and without `CONFIG_MODULE_SIG`.
