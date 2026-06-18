# sources/distributed-fs/ceph-client/arch/powerpc/kvm/Kconfig

## Purpose
Defines the PowerPC KVM configuration surface: generic virtualization menu visibility, shared KVM enablement, Book3S PR/HV variants, BookE/e500 variants, interrupt-controller support, timing/debug options, nested PMU workaround, and hypervisor PMU support.

## Important APIs, Types, And Functions
This is Kconfig data rather than C APIs. Key symbols are `VIRTUALIZATION`, `KVM`, `KVM_BOOK3S_HANDLER`, `KVM_BOOK3S_32`, `KVM_BOOK3S_64`, `KVM_BOOK3S_64_HV`, `KVM_BOOK3S_64_PR`, `KVM_BOOK3S_HV_P9_TIMING`, `KVM_BOOK3S_HV_P8_TIMING`, `KVM_BOOK3S_HV_NESTED_PMU_WORKAROUND`, `KVM_BOOK3S_HV_PMU`, `KVM_E500V2`, `KVM_E500MC`, `KVM_MPIC`, `KVM_XICS`, and `KVM_XIVE`.

## Control Flow
Kconfig dependency resolution selects common KVM support and one or more architecture implementations. Book3S 32-bit depends on uniprocessor non-64-bit PTE Book3S and excludes context tracking. Book3S 64 selects hash MMU support and optionally SPAPR TCE IOMMU. HV mode is powernv-only and selects CMA and the HV PMU; PR mode excludes context tracking and is hash-only. Timing options depend on debugfs and HV or e500 support. XICS/XIVE depend on interrupt-controller capabilities and Book3S 64 support.

## State And Persistence
The only persistent state is the kernel configuration. Selected symbols drive object inclusion, exported module capabilities, `/dev/kvm` availability, and runtime feature sets.

## Dependencies And Integration Points
Integrates with `virt/kvm/Kconfig`, PowerPC platform symbols, MMU mode symbols, IOMMU support, pseries/powernv platform support, debugfs, PMU, MPIC, XICS, and XIVE code. It directly feeds the local KVM Makefile object lists.

## Risks And Edge Cases
Bad dependency combinations can build unsupported KVM modes, omit required MMU or interrupt-controller code, or enable PR KVM with host features it cannot tolerate. PR KVM has platform-wide side effects called out in help text, including SCV and AIL behavior. Timing options add overhead and are not production defaults.

## Test Signals
Primary signals are `olddefconfig` and build coverage for Book3S 32 PR, Book3S 64 PR, Book3S 64 HV, pseries/powernv hash and radix combinations, e500v2/e500mc, and XICS/XIVE variants. Runtime signals are `/dev/kvm`, module load, guest boot, interrupt controller creation, and timing/debugfs file presence when selected.
