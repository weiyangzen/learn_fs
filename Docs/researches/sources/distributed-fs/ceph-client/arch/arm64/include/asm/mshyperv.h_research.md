# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mshyperv.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mshyperv.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mshyperv.h

### Purpose
`mshyperv.h` provides ARM64 Microsoft Hyper-V paravirtualization hooks and hypercall interfaces.

### Important APIs, Types, And Functions
It declares Hyper-V detection/init helpers, hypercall page interfaces, VP assist or synthetic interrupt helpers where supported, and no-op stubs for non-Hyper-V builds.

### Control Flow
Platform init detects Hyper-V, sets up hypercall mechanisms, and later paravirtualized drivers or time/interrupt paths use the helpers to communicate with the hypervisor.

### State, Persistence, And Dependencies
State includes hypercall page address, discovered feature bits, and per-CPU/VP data. It depends on `linux/hyperv.h`, SMCCC/firmware call conventions, and ARM64 paravirt infrastructure.

### Integration Points
Used by Hyper-V guest support, synthetic devices, clocks, interrupts, and potentially storage/network paths used by Ceph deployments in Hyper-V guests.

### Risks
Calling hypercalls before initialization or with wrong calling convention can fail or corrupt registers. Feature detection must match host-advertised capabilities.

### Test Signals
Boot ARM64 under Hyper-V, run Hyper-V device drivers, validate time/interrupt behavior, and build non-Hyper-V configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mshyperv.h -->
