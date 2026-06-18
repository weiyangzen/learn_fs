## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-tracepoints.c

### Purpose
`opal-tracepoints.c` manages OPAL call tracepoint enablement and recursion-safe trace emission around OPAL entry/exit.

### Important APIs, Types, And Functions
Key functions are `opal_tracepoint_regfunc()`, `opal_tracepoint_unregfunc()`, `__trace_opal_entry()`, and `__trace_opal_exit()`. Depending on configuration it uses either `struct static_key opal_tracepoint_key` or the TOC-visible `opal_tracepoint_refcount`.

### Control Flow
Tracepoint registration increments a static key or refcount; unregistration decrements it. Entry and exit trace helpers save local IRQ state, check a per-CPU recursion depth, emit `trace_opal_entry()` or `trace_opal_exit()` only at depth zero, and restore IRQ state. Entry disables preemption before tracing, and exit re-enables it after tracing.

### State, Persistence, And Dependencies
State is the tracepoint enable counter/static key and per-CPU recursion depth. It depends on Linux tracepoint infrastructure, jump labels, per-CPU storage, local IRQ control, and the assembly OPAL call wrapper hooks.

### Integration Points
OPAL call wrappers can call these helpers when tracepoints are enabled. Trace subscribers use the standard tracing subsystem to observe firmware call opcodes, arguments, and returns.

### Risks
The preemption disable/enable pairing is split across entry and exit helpers, so wrapper call paths must invoke them in balanced order. Recursion suppression is necessary because tracing itself may invoke OPAL calls. Non-jump-label refcount manipulation assumes tracepoint mutex serialization.

### Test Signals
Test tracepoint enable/disable transitions, nested OPAL calls during tracing, IRQ/preemption state balance, jump-label and non-jump-label builds, and tracing of both successful and failing OPAL calls.
