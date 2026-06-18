## sources/distributed-fs/ceph-client/arch/arm64/kvm/Makefile

### Purpose
`arch/arm64/kvm/Makefile` builds the ARM64 KVM host module/core objects, hyp subdirectory, generated hyp constants, VGIC implementation, and optional feature objects.

### Important APIs, Types, And Functions
It adds include flags, includes `virt/kvm/Makefile.kvm`, builds `kvm.o` and `hyp/`, lists `kvm-y` objects such as `arm.o`, `mmu.o`, `psci.o`, `arch_timer.o`, VGIC files, nested virtualization files, TRNG/VMID/PV time, and optional PMU, pointer-auth, ptdump, and hyp tracing objects. It also defines rules for `hyp_constants.h` from `hyp-constants.c`.

### Control Flow
Kbuild compiles hyp constants to assembly, extracts offsets into `hyp_constants.h`, then makes KVM objects depend on that generated header. The final KVM object aggregates core ARM64 KVM and VGIC objects based on configuration.

### State, Persistence, And Dependencies
State is build artifacts and generated `hyp_constants.h`. Runtime state is owned by the compiled objects, not this Makefile.

### Integration Points
It connects ARM64 KVM source files to generic KVM build logic, hyp include paths, VGIC subdirectory objects, PMU, pointer authentication, stage-2 ptdump, and nVHE tracing.

### Risks
Missing generated constants break host/hyp ABI assumptions. Object ordering and conditional inclusion must match config dependencies. Warning suppressions for generated sys-reg initializers are intentional.

### Test Signals
Build KVM with PMU, pointer-auth, ptdump, nested virtualization, VGICv5, and nVHE tracing variations; verify generated hyp constants update when hyp structures change.
