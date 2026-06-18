# sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/frame.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/frame.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace/frame.h` Defines standard and metadata frame-record layouts for arm64 unwinding. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
FRAME_META_TYPE_NONE/FINAL/PT_REGS, struct frame_record, struct frame_record_meta. The file is 48 lines / 1116 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow; unwinders interpret zero fp/lr plus metadata type to terminate or consume pt_regs frames.

### State, Persistence, And Dependencies
Frame records persist on kernel stacks while functions/traps are active. Used by ptrace pt_regs stackframe field, stacktrace/common, entry assembly, and unwinder implementation.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Layout is ABI with assembly and compiler frame generation; wrong metadata handling breaks backtrace termination or pt_regs unwinds.

### Test Signals
Compile with frame pointers, run oops/backtrace and pt_regs unwind tests, verify final frame records in start_thread_common.
