<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/elf.h

Purpose: Defines x86 ELF note metadata for extended CPU feature components.

Important APIs/types/functions: `struct x86_xfeat_component` and its static alignment assertion.

Control flow: ELF core-dump and tooling paths consume arrays of component descriptors to describe XSAVE/xfeature state layout.

State and persistence behavior: No runtime state. The structure persists in ELF notes or userspace-visible metadata describing saved CPU state.

Dependencies and integration points: Depends on Linux UAPI types. Integrates with core dumps, ptrace/regset consumers, debuggers, and XSAVE feature enumeration.

Risks and test signals: Risks are layout or alignment changes that break debuggers. Test core dumps with extended xfeatures, `readelf`/gdb interpretation, and compile-time size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/elf.h -->
