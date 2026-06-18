# sources/distributed-fs/ceph-client/security/apparmor/include/audit.h

## Purpose
`audit.h` defines AppArmor audit modes, audit event types, operation strings, the `apparmor_audit_data` payload, audit initialization macros, and audit helper prototypes.

## Important APIs and types
Key types are `enum audit_mode`, `enum audit_type`, and `struct apparmor_audit_data`. Operation constants cover filesystem, mount, socket, ptrace, signal, exec, change_hat/profile, procattr, rlimit, user namespace, and io_uring events. `DEFINE_AUDIT_DATA` initializes common LSM audit data. `complain_error` converts access denials to success in complain mode.

## Control flow and integration
Mediation code fills this structure and passes it to `aa_audit` or `aa_audit_msg` with optional callbacks. The nested union carries operation-specific fields for file target/owner, rlimit, signal, network peer, interface, mount, and io_uring data.

## State and persistence
The header defines transient audit payloads. It does not own persistent state, though audit rules can hold parsed labels through functions declared here.

## Dependencies
It depends on Linux audit, LSM audit, scheduler/task types, and AppArmor file and label structures.

## Risks
The union layout requires callbacks to interpret only fields valid for the audited class. Operation strings are part of audit-visible behavior; changing them affects tooling. `complain_error` intentionally hides `-EPERM`/`-EACCES` from callers.

## Test signals
Audit output tests should validate operation strings and class-specific fields for each mediation path. Complain-mode tests should assert access succeeds while audit records still show allowed denials.
