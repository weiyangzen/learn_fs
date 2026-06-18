# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_define_hypevents.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_define_hypevents.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_define_hypevents.h

### Purpose
`kvm_define_hypevents.h` adapts KVM hyp event declarations into the remote trace event generator.

### Important APIs, Types, And Functions
It defines `REMOTE_EVENT_INCLUDE_FILE`, `REMOTE_EVENT_SECTION`, `HE_STRUCT`, `HE_PRINTK`, `he_field`, `HYP_EVENT()`, and `HYP_EVENT_MULTI_READ`, then includes `trace/define_remote_events.h`.

### Control Flow
Trace event generation includes this file to transform `HYP_EVENT` declarations in `kvm_hypevents.h` into remote event metadata placed in `_hyp_events`.

### State, Persistence, And Dependencies
There is no runtime state. The persistent output is generated trace metadata in the built kernel image. Dependencies are the trace remote-event generator and `kvm_hypevents.h`.

### Integration Points
Connects ARM64 KVM hyp tracepoints to the Linux trace infrastructure, especially for events emitted from EL2.

### Risks
Macro signature drift breaks trace generation. Section name or include mismatch can make hyp events invisible.

### Test Signals
Build with hyp tracing enabled; inspect generated event formats; enable/read KVM hyp trace events under ftrace/tracefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_define_hypevents.h -->
