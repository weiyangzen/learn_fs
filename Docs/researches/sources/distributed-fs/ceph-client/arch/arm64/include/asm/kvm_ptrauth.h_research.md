# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_ptrauth.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_ptrauth.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_ptrauth.h

### Purpose
`kvm_ptrauth.h` provides ARM64 KVM pointer-authentication helpers for saving/restoring guest keys and exposing PAuth state when configured.

### Important APIs, Types, And Functions
It declares or defines helpers for guest PAuth key save/restore, `vcpu_has_ptrauth()` integration, system-register key handling, and no-op stubs when `CONFIG_ARM64_PTR_AUTH` is disabled.

### Control Flow
During vCPU context switch, KVM saves host/guest pointer authentication key registers as required and restores the guest-visible keys before running the vCPU. Nested paths may authenticate ERET targets through `kvm_auth_eretax()`.

### State, Persistence, And Dependencies
State is in vCPU sysreg storage and CPU PAuth key registers. It depends on `kvm_host.h`, pointer-auth CPU features, sysreg definitions, and feature bits exposed to the guest.

### Integration Points
Used by world-switch code, nested virtualization, sysreg ioctl paths, and feature finalization.

### Risks
Key leakage between host and guest is security sensitive. Feature gating must match CPU support and VM-visible ID registers. Stubs must not accidentally allow unsupported key access.

### Test Signals
Run PAuth KVM selftests, key save/restore stress across vCPU migration, nested ERET authentication tests, and builds with PAuth disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_ptrauth.h -->
