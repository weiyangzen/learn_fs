# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyptrace.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyptrace.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyptrace.h

### Purpose
`kvm_hyptrace.h` provides the ARM64 KVM hyp-side trace integration include point.

### Important APIs, Types, And Functions
It defines the include guard and pulls together hyp trace definitions/macros used by EL2 code. The exported surface is intentionally small and macro-driven.

### Control Flow
There is no standalone runtime flow. Hyp code includes this header so trace macros compile to remote event emission or no-op code depending on configuration.

### State, Persistence, And Dependencies
No storage is owned here. State lives in trace buffers and remote-event metadata. Dependencies are KVM hyp trace declarations and generic tracing support.

### Integration Points
Included by ARM64 KVM hyp C files to emit safe trace events from hypervisor context.

### Risks
The main risk is configuration drift where hyp code expects trace macros unavailable in a given build, or trace calls assume mappings not present at EL2.

### Test Signals
Compile KVM with hyp tracing enabled and disabled; run a guest and confirm trace events appear only in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyptrace.h -->
