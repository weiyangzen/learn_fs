# sources/distributed-fs/ceph-client/security/apparmor/include/domain.h

## Purpose
`domain.h` declares AppArmor domain transition flags and public functions for exec-time and self-directed profile changes.

## Important APIs
Flags include `AA_CHANGE_TEST`, `AA_CHANGE_CHILD`, `AA_CHANGE_ONEXEC`, and `AA_CHANGE_STACK`. Public functions are `x_table_lookup`, `apparmor_bprm_creds_for_exec`, `aa_change_hat`, and `aa_change_profile`.

## Control flow and integration
The exec LSM path calls `apparmor_bprm_creds_for_exec`. Procattr or AppArmor task interfaces call `aa_change_hat` and `aa_change_profile`. File policy transition code uses `x_table_lookup` to resolve transition table entries.

## State and persistence
This header owns no state, but the declared functions mutate task credentials and AppArmor task context fields.

## Dependencies
It depends on Linux binprm/types and AppArmor labels.

## Risks
Flag values are part of internal API contracts with procattr parsing and domain code. Misusing `AA_CHANGE_TEST` could accidentally perform a real transition or suppress one.

## Test signals
Compile callers and run change_profile/change_hat test and real modes, including stack and onexec combinations.
