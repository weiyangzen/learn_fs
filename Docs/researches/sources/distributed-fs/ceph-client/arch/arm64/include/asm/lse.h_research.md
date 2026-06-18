# sources/distributed-fs/ceph-client/arch/arm64/include/asm/lse.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lse.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/lse.h

### Purpose
`lse.h` gates ARM64 Large System Extensions support for atomic instructions.

### Important APIs, Types, And Functions
It includes alternative/capability machinery and defines the compile-time hooks used by atomic/percpu/cmpxchg code to select LSE instructions or LL/SC fallbacks.

### Control Flow
Atomic helpers use alternatives to patch in LSE sequences on capable CPUs. This header contributes selection macros rather than standalone control flow.

### State, Persistence, And Dependencies
State is CPU capability detection and patched instruction text. It depends on `asm/alternative.h`, CPU feature bits, and atomic instruction implementations.

### Integration Points
Used by atomic and per-CPU operations that underpin scheduler, locking, MM, networking, and Ceph client concurrency.

### Risks
Incorrect LSE gating can execute unsupported instructions or miss faster atomics. Alternative patching must be safe during boot and CPU hotplug.

### Test Signals
Build/run on LSE and non-LSE ARM64 systems; stress atomics, lock primitives, and CPU hotplug; inspect alternatives patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/lse.h -->
