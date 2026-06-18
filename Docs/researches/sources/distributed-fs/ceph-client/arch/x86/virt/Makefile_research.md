<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/Makefile

## Purpose
`virt/Makefile` selects x86 virtualization support directories and common hardware enablement glue.

## Important APIs, types, and functions
It always descends into `svm/` and `vmx/`; it builds `hw.o` when `CONFIG_KVM_X86` is built-in or modular.

## Control flow
Kbuild composes vendor-specific virtualization support and common VMX/SVM enablement code for KVM consumers.

## State and persistence behavior
No runtime state is held in the Makefile.

## Dependencies and integration points
It depends on KVM and vendor virtualization configuration symbols.

## Risks and edge cases
Wrong conditional substitution would omit `hw.o` for modular KVM, breaking exported virtualization reference APIs.

## Test signals
Signals are built-in and modular KVM builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/Makefile -->
