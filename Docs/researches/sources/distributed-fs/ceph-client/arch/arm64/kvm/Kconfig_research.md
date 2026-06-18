## sources/distributed-fs/ceph-client/arch/arm64/kvm/Kconfig

### Purpose
`arch/arm64/kvm/Kconfig` defines ARM64 virtualization configuration entries for KVM, stage-2 page-table debugging, and nVHE/pKVM debug features.

### Important APIs, Types, And Functions
It sources `virt/kvm/Kconfig`, defines `VIRTUALIZATION`, `KVM`, `PTDUMP_STAGE2_DEBUGFS`, `NVHE_EL2_DEBUG`, `NVHE_EL2_TRACING`, `PKVM_DISABLE_STAGE2_ON_PANIC`, and `PKVM_STACKTRACE`, and selects many generic KVM capability symbols.

### Control Flow
Enabling `VIRTUALIZATION` exposes the KVM submenu. Enabling `KVM` selects generic KVM infrastructure, MMIO, irqchip, dirty logging/ring, MSI/routing/bypass, guest memory, perf event, and scheduling support. Debug-only options gate stage-2 ptdump, nVHE tracing, host stage-2 relaxation on panic, and protected KVM stacktraces.

### State, Persistence, And Dependencies
The file contributes build-time configuration state only. No runtime state exists here.

### Integration Points
It controls compilation of `arch/arm64/kvm/Makefile`, generic `virt/kvm`, debugfs ptdump, tracing, pKVM, and related architecture capabilities.

### Risks
Incorrect selects can produce incomplete KVM builds or expose unsafe debug behavior. Panic-time pKVM debug options explicitly weaken isolation and should not be production defaults.

### Test Signals
Run `olddefconfig`/`randconfig` builds for KVM on/off, debug options, protected KVM options, tracing dependencies, and boot KVM selftests under selected configs.
