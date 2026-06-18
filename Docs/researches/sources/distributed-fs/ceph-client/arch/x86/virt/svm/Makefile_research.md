<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/svm/Makefile

## Purpose
`virt/svm/Makefile` selects AMD SVM virtualization support outside KVM proper.

## Important APIs, types, and functions
It builds `sev.o` for `CONFIG_KVM_AMD_SEV` and `cmdline.o` for `CONFIG_CPU_SUP_AMD`.

## Control flow
Kbuild includes SEV-SNP RMP host support and SEV command-line parsing according to configuration.

## State and persistence behavior
No runtime state is held here.

## Dependencies and integration points
It depends on AMD CPU and KVM AMD SEV config symbols.

## Risks and edge cases
A wrong dependency can omit SEV command-line parsing or RMP support from capable hosts.

## Test signals
Signals are AMD SEV/SNP configured builds and symbol availability for CCP/KVM modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/Makefile -->
