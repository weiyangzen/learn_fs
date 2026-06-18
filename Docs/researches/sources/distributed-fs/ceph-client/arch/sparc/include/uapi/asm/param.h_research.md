<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/param.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/param.h

Purpose: Defines SPARC UAPI process/system parameter constants.

Important APIs and control flow: sets `EXEC_PAGESIZE` to 8192 for historical sun4 compatibility, then includes generic parameter definitions for HZ and related constants.

State, dependencies, and risks: no runtime state, but values are ABI-visible. Dependencies include `asm-generic/param.h`. Risks are userspace page/executable assumptions if changed. Test signals are header compile tests and legacy binary compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/param.h -->
