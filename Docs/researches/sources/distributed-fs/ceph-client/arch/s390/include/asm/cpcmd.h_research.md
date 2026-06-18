<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpcmd.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpcmd.h

Purpose: Declares helpers for issuing z/VM CP commands.

Important APIs/types/functions: `__cpcmd()` low-level command execution and `cpcmd()` wrapper with response buffer and response-code pointer. Source-visible declarations include: #define _ASM_S390_CPCMD_H; int __cpcmd(const char *cmd, char *response, int rlen, int *response_code);; int cpcmd(const char *cmd, char *response, int rlen, int *response_code);.

Control flow: Callers pass a CP command string and optional response buffer; implementation issues the hypervisor command and returns CP response status.

State and persistence behavior: State is z/VM control program state and caller response buffers.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates VM-only management paths, hypfs, diagnostics, and s390 virtualization support..

Risks: Command strings are privileged hypervisor interface inputs; response buffer lengths and non-VM behavior must be handled carefully.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 32 lines, 1135 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpcmd.h -->
