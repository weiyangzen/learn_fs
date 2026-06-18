## sources/distributed-fs/ceph-client/arch/arm64/kernel/trace-events-emulation.h

### Purpose
`trace-events-emulation.h` defines the ARM64 `emulation:instruction_emulation` tracepoint used when the kernel emulates trapped userspace instructions.

### Important APIs, Types, And Functions
It declares `TRACE_SYSTEM emulation` and `TRACE_EVENT(instruction_emulation)` with fields `instr` and `addr`, then includes `trace/define_trace.h` with `TRACE_INCLUDE_FILE` set to `trace-events-emulation`.

### Control Flow
Callers emit the tracepoint with an instruction name and address. The trace infrastructure records a string copy and address and formats them as `instr="..." addr=0x...`.

### State, Persistence, And Dependencies
Trace state is owned by ftrace/perf tracepoint infrastructure. This header contributes generated trace code when included with the normal trace-event pattern.

### Integration Points
It is used by ARM64 instruction emulation paths such as deprecated instruction or system-register emulation, and integrates with Linux trace events.

### Risks
Tracepoint name or field changes break user tooling. The include guard and `TRACE_INCLUDE_PATH` must remain compatible with generated trace code.

### Test Signals
Build with tracing enabled, enable the emulation tracepoint, trigger instruction emulation from userspace, and validate recorded fields with tracefs/perf.
