# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hypevents.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hypevents.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hypevents.h

### Purpose
`kvm_hypevents.h` declares ARM64 KVM hypervisor trace events that can be emitted from hyp context and consumed through the remote event machinery.

### Important APIs, Types, And Functions
It defines trace-event include protection, imports tracepoint helpers, and lists `HYP_EVENT` declarations with field/assignment/print blocks for hyp-visible events.

### Control Flow
At build time, the event declarations are expanded by `kvm_define_hypevents.h`. At runtime, hyp instrumentation writes event records into the remote trace infrastructure when configured.

### State, Persistence, And Dependencies
Runtime state is trace buffers and event metadata, not header-owned storage. It depends on remote event macros and tracepoint infrastructure.

### Integration Points
Links EL2 KVM events to ftrace/tracefs observability and debugging of protected or nVHE paths.

### Risks
Trace field layout must remain compatible with remote readers. Logging from hyp context must be low overhead and safe under restricted mappings.

### Test Signals
Build with tracing; enable KVM hyp events; exercise guest entry/exit or pKVM operations; verify event fields and timestamps appear in tracefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hypevents.h -->
