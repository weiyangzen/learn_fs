## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hypervisor.h

Purpose: collects arm64 hypervisor service initialization hooks.

Important APIs/types/functions: includes Xen hypervisor support and declares `kvm_init_hyp_services`, `kvm_arm_hyp_service_available`, `kvm_arm_target_impl_cpu_init`, optional `pkvm_init_hyp_services`, and `kvm_arch_init_hyp_services`.

Control flow: KVM initialization registers available hyp services, optionally initializes pKVM services, and performs target CPU initialization.

State and persistence: service availability state is maintained by implementation code; this header defines callers' interface.

Dependencies and integration: integrates KVM, pKVM, Xen detection, and CPU initialization.

Risks: missing service initialization can disable KVM capabilities or expose unavailable hypercalls. Test signals are KVM selftests, pKVM boots, Xen guest boots, and service availability probes.
