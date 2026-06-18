<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ima.h -->
# sources/distributed-fs/ceph-client/include/linux/ima.h

Purpose: Declares Integrity Measurement Architecture hooks used by file, inode, kexec, critical-data, appraisal, and boot-policy code.

Important APIs/types/functions: Under `CONFIG_IMA`, exports current hash algorithm, file/inode hash calculation, kexec command-line measurement, critical-data measurement, optional appraisal command-line parsing, kexec buffer hooks, appraisal state, signature appraisal, and architecture policy lookup. Disabled builds provide safe stubs returning `HASH_ALGO__LAST`, `-EOPNOTSUPP`, false, or no-op values. `CONFIG_HAVE_IMA_KEXEC` exposes buffer range helpers.

Control flow: Callers invoke hooks at security-sensitive events; Kconfig selects real enforcement or no-op stubs.

State/persistence: IMA measurement lists, hashes, appraisal policy, and kexec buffers are external; this header only exposes access points.

Dependencies/integration: Depends on filesystem/security/kexec/secure-boot/hash headers and integrity policy implementations.

Risks: Disabled stubs can hide missing enforcement in builds; buffer validation must be exact for kexec handoff.

Test signals: Kconfig matrix, file/inode hash success/failure, appraisal enabled state, kexec buffer validation, and secure/trusted boot policy selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ima.h -->
