
# sources/distributed-fs/ceph-client/arch/x86/include/asm/emulate_prefix.h

Purpose: byte prefixes that mark hypervisor instruction-emulation escape sequences.

Important APIs and control flow: defines `__XEN_EMULATE_PREFIX` and `__KVM_EMULATE_PREFIX` as `ud2` followed by ASCII tags. Callers embed these bytes before code sequences that a hypervisor recognizes and emulates.

State, dependencies, and risks: no software state, but emitted bytes become executable instruction stream metadata. Dependencies are Xen/KVM emulation decoders. Risks include corrupting instruction streams, hypervisor mismatch, and intentional UD2 trapping on native execution. Test signals are paravirtualization boot tests and KVM/Xen emulation path tests.
