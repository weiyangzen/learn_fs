## sources/distributed-fs/ceph-client/arch/arm64/Kbuild

### Purpose
Top-level ARM64 Kbuild file selecting architecture subdirectories and disabling branch profiling where unsafe.

### Important APIs, Types, And Functions
Adds `kernel/`, `mm/`, and `net/` unconditionally; conditionally adds `kvm/`, `xen/`, `hyperv/`, and `crypto/`. Adds `-DDISABLE_BRANCH_PROFILING` under `CONFIG_TRACE_BRANCH_PROFILING`.

### Control Flow
Kbuild evaluates config symbols and descends into selected subdirectories. Cleaning also covers `boot`.

### State, Persistence, And Dependencies
Build metadata only. Depends on configuration symbols for virtualization and crypto subsystems.

### Integration Points
Defines the ARM64 architecture build shape used by the global kernel build.

### Risks
Subdirectory selection errors omit entire architecture subsystems. Branch profiling must remain disabled for noinstr-sensitive code.

### Test Signals
Build ARM64 configs with KVM, Xen, Hyper-V, crypto, and trace branch profiling enabled.
