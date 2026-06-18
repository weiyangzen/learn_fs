# sources/distributed-fs/ceph-client/security/integrity/integrity_audit.c

Purpose: Provides common audit logging for integrity subsystem events such as IMA PCR updates, policy parsing, and data collection failures.

Important APIs/types/functions: `integrity_audit_setup()` handles the `integrity_audit=` boot parameter. `integrity_audit_msg()` is a convenience wrapper, and `integrity_audit_message()` builds the full audit record including pid, uid, auid, session, LSM context, operation, cause, command, optional file name, optional inode device/inode, result, and errno.

Control flow: Informational records are skipped unless global `integrity_audit_info` is enabled or the caller marks the record non-informational. Otherwise an audit buffer is allocated, populated, and ended.

State and persistence: Only persistent state is the boot-parameter-controlled `integrity_audit_info` flag.

Dependencies and integration: Used by IMA queue, policy, key queue, and template code; depends on audit context, current task credentials, inode metadata, and untrusted string audit helpers.

Risks and test signals: Risks include incorrect suppression of important events, missing errno propagation, unsafe string formatting, and NULL audit buffer handling. Tests should verify boot parameter behavior and representative records for success, failure, inode, and non-inode cases.
