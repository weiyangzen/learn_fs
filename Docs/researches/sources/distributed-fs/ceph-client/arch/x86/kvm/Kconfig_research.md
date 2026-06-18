# sources/distributed-fs/ceph-client/arch/x86/kvm/Kconfig

Purpose: declares x86 KVM virtualization configuration options, dependencies, selected common capabilities, processor vendor modules, confidential-computing features, emulation features, and debug/proof options.

Important APIs/types/functions: Kconfig symbols include `VIRTUALIZATION`, `KVM_X86`, `KVM`, `KVM_WERROR`, `KVM_SW_PROTECTED_VM`, `KVM_INTEL`, `KVM_INTEL_PROVE_VE`, `X86_SGX_KVM`, `KVM_INTEL_TDX`, `KVM_AMD`, `KVM_AMD_SEV`, `KVM_IOAPIC`, `KVM_SMM`, `KVM_HYPERV`, `KVM_XEN`, `KVM_PROVE_MMU`, `KVM_EXTERNAL_WRITE_TRACKING`, and `KVM_MAX_NR_VCPUS`.

Control flow: enabling `VIRTUALIZATION` exposes the submenu. `KVM_X86` is auto-selected when either vendor backend may be built and selects common KVM capabilities. `KVM` depends on local APIC support and provides `/dev/kvm`. Vendor options select VMX or SVM support, with optional SGX, TDX, SEV/SEV-ES/SEV-SNP, Hyper-V, Xen, SMM, IOAPIC/PIC/PIT, and proof/debug features layered by dependency.

State and persistence: Kconfig choices persist into `.config` and drive compiled objects, module availability, selected generic KVM features, maximum vCPU range, and whether warning builds are fatal.

Dependencies and integration: sources generic `virt/kvm/Kconfig`, ties x86 KVM into APIC, PM, performance events, guest memory fd, memory attributes, VFIO, async page faults, IRQ routing, dirty logging, and vendor CPU support.

Risks: dependency mistakes can expose unsupported feature combinations or hide required infrastructure. Defaults for confidential-computing options are enabled when their host prerequisites are met, so build and runtime testing must cover those paths. `KVM_WERROR` can break randomized or sanitizer builds if selected too broadly.

Test signals: `olddefconfig` and randconfig coverage, module build matrix for `kvm`, `kvm-intel`, and `kvm-amd`, feature-specific configs for TDX/SEV/SGX/Hyper-V/Xen/SMM/IOAPIC, and validation of `KVM_MAX_NR_VCPUS` bounds.
