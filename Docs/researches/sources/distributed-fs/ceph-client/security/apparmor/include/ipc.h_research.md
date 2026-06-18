# sources/distributed-fs/ceph-client/security/apparmor/include/ipc.h

## Purpose
This header declares AppArmor IPC signal mediation and defines signal mapping constants used by signal audit/permission code.

## Important APIs
`SIGUNKNOWN` and `MAXMAPPED_SIG` describe signal mapping bounds. `aa_may_signal` checks whether a sender label/cred may signal a target label/cred with a given signal.

## Control flow and integration
Signal LSM hooks call `aa_may_signal`; domain code depends indirectly on IPC/ptrace mediation for transition safety checks.

## State and persistence
No state is defined here. Signal decisions are computed from loaded policy and current credentials.

## Dependencies
It depends on Linux scheduler types and AppArmor labels through function parameters.

## Risks
Signal number mapping must stay aligned with audit strings and policy encoding. Unknown or out-of-range signals need deterministic handling.

## Test signals
Test allowed/denied signal sends across labels, unknown signal mapping, and audit output for mapped/unmapped signals.
