# sources/distributed-fs/ceph-client/tools/perf/jvmti/jvmti_agent.h

### Purpose
This header declares the jitdump writer interface shared between the JVMTI callback layer and the low-level writer implementation.

### Important APIs, Types, And Functions
`jvmti_line_info_t` carries a program counter, source line number, discriminator, and `jmethodID`. The public functions open/close an agent writer and emit code load and debug-info records: `jvmti_open`, `jvmti_close`, `jvmti_write_code`, and `jvmti_write_debug_info`.

### Control Flow
The intended lifecycle is open once during `Agent_OnLoad`, write code/debug records from compiled-method callbacks, then close during `Agent_OnUnload`.

### State And Persistence
The header defines no state. The opaque `void *agent` returned by `jvmti_open()` is owned by the implementation and currently represents a `FILE *`.

### Dependencies And Integration Points
It includes `<jvmti.h>` for `jmethodID` and uses `extern "C"` guards for C++ consumers. `libjvmti.c` is the primary caller.

### Risks
Because the handle is opaque but not type-safe, callers can pass invalid pointers. The comment on the final include guard names `__JVMTI_H__` instead of `__JVMTI_AGENT_H__`, a cosmetic mismatch.

### Test Signals
Build the JVMTI agent, load it into a JVM, and verify the callback layer links against these declarations and writes jitdump records successfully.
