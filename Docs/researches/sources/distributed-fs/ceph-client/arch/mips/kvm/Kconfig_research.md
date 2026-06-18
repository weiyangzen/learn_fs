## sources/distributed-fs/ceph-client/arch/mips/kvm/Kconfig

Purpose: Defines the MIPS architecture KVM configuration menu and feature gates.

Important APIs, types, and functions: The main symbol is `CONFIG_KVM`, a tristate dependent on `CPU_SUPPORTS_VZ` and `MIPS_FP_SUPPORT`. It selects common KVM infrastructure (`KVM_COMMON`, `KVM_MMIO`, dirty-log read-protect, generic hardware enabling, readonly memory support, and `EXPORT_UASM`). `CONFIG_KVM_MIPS_DEBUG_COP0_COUNTERS` optionally enables COP0 access histograms.

Control flow: `VIRTUALIZATION` is a menuconfig wrapper. If disabled, all nested KVM options are hidden/disabled. Enabling KVM pulls in common virtualization support and allows the KVM MIPS module objects to build.

State and persistence: No runtime state. It controls compile-time inclusion and selected common KVM features.

Dependencies and integration points: Ties the MIPS backend to `virt/kvm/Kconfig` and CPU feature detection. The FPU dependency is important because MIPS KVM context handling expects FPU support paths even when guest FPU exposure is capability-gated.

Risks: Incorrect dependencies can expose KVM on CPUs without VZ/FPU support, producing build or runtime failures. Debug COP0 counters can add overhead and log noise when enabled.

Test signals: Kconfig matrix builds with virtualization disabled, KVM module built-in/module, missing VZ, missing FPU, and debug counters enabled.
