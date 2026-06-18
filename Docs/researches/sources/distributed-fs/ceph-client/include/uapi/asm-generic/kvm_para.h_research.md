# sources/distributed-fs/ceph-client/include/uapi/asm-generic/kvm_para.h

Purpose: Placeholder generic KVM paravirtualization UAPI header for architectures without generic definitions.

Important APIs/types/functions: No API is exported; a comment keeps the file non-empty so patch tooling does not delete it.

Control flow: Included only as a fallback header.

State/persistence: No state.

Dependencies/integration: Participates in UAPI header installation when architecture-specific/generated `kvm_para.h` is absent.

Risks: Adding symbols here would expose them broadly to architectures that may not implement matching KVM features.

Test signals: Headers-install and compile checks for `<asm/kvm_para.h>` on architectures using the placeholder.
