# sources/distributed-fs/ceph-client/arch/x86/kvm/Makefile

Purpose: builds the x86 KVM core and vendor modules, wires shared KVM make logic, generates assembly offsets, and enforces KVM export-symbol policy.

Important APIs/types/functions: build variables include `ccflags-y`, `kvm-y`, `kvm-intel-y`, `kvm-amd-y`, conditional object additions for feature configs, `obj-$(CONFIG_KVM_X86)`, `obj-$(CONFIG_KVM_INTEL)`, `obj-$(CONFIG_KVM_AMD)`, `AFLAGS_*`, `targets`, `clean-files`, and make macros `get_kvm_exports`/`check_kvm_exports`.

Control flow: the file adds the local include path and optional `-Werror`, includes `virt/kvm/Makefile.kvm`, lists core x86 KVM objects, conditionally adds TDP MMU, IOAPIC/PIC/PIT, Hyper-V, Xen, SMM, SGX, TDX, SEV, and on-Hyper-V objects, then registers the core/vendor modules. It declares dependencies from VMX/SVM assembly entry objects to generated `kvm-asm-offsets.h`, generated from `kvm-asm-offsets.s`. When KVM_X86 is enabled, recursive grep checks fail the build if unwanted `EXPORT_SYMBOL_GPL` or `EXPORT_SYMBOL` usages appear outside an allowlist.

State and persistence: no runtime state. Persistent outputs are built objects/modules and generated offset headers; clean rules remove generated headers.

Dependencies and integration: depends on Kbuild, generic KVM make fragments, arch/x86/kvm and virt/kvm source trees, vendor subdirectories, config symbols from Kconfig, and assembly offset generation for vmenter code.

Risks: missing object gating can produce unresolved symbols or absent feature code. Offset header dependencies are critical for assembly/C ABI sync. Export policy grep can be brittle but protects KVM-internal symbol hygiene.

Test signals: successful builds for built-in and module KVM, Intel-only, AMD-only, Hyper-V host, TDX, SEV, SGX, IOAPIC/SMM/Xen combinations, clean rebuilds regenerating `kvm-asm-offsets.h`, and intentional forbidden exports causing the expected make error.
