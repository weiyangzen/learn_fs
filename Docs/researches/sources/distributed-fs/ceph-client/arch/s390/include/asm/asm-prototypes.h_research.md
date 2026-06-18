<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-prototypes.h

Purpose: Collects C prototypes needed by assembly-generated calls and modversions.

Important APIs/types/functions: Includes `asm/ftrace.h`, `asm-generic/asm-prototypes.h`, and s390-specific exported assembly helper declarations where configured. Source-visible declarations include: no direct declarations beyond include guards or build directives.

Control flow: Build tooling includes this so assembly-visible symbols have prototypes for checksums and linkage.

State and persistence behavior: No runtime state.

Dependencies and integration points: Direct includes are #include <linux/kvm_host.h>, #include <linux/ftrace.h>, #include <asm/bug.h>, #include <asm/fpu.h>, #include <asm/nospec-branch.h>, #include <asm-generic/asm-prototypes.h>. Integrated with Integrates module versioning, assembly helper exports, ftrace, and generic asm prototype handling..

Risks: Missing prototypes can break modversion CRCs or hide calling convention mismatches.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 15 lines, 405 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-prototypes.h -->
