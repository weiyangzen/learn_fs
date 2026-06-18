# sources/distributed-fs/ceph-client/tools/perf/jvmti/libjvmti.c

### Purpose
`libjvmti.c` is the actual JVM agent entry point. It registers JVMTI callbacks for compiled Java methods and dynamic code, resolves method/class/source metadata, and forwards JIT code and optional line mappings to `jvmti_agent.c`.

### Important APIs, Types, And Functions
`Agent_OnLoad()` and `Agent_OnUnload()` are the JVM entry points. `compiled_method_load_cb()` handles `JVMTI_EVENT_COMPILED_METHOD_LOAD`; `code_generated_cb()` handles dynamic generated code. When `HAVE_JVMTI_CMLR` is available, `get_line_numbers()` walks compiled-method-load inline records and `do_get_line_number()` maps bytecode indices to source lines. `get_source_filename()`, `copy_class_filename()`, and `fill_source_filenames()` build source file paths for debug records.

### Control Flow
On load, the agent opens the jitdump writer, gets a JVMTI v1 environment, requests compiled-method-load capability, optionally requests line/source capabilities when JVM location format is BCI, installs callbacks, and enables events. For each compiled method, it optionally extracts line info, obtains class signature and method name/signature, writes debug info first, then writes a code load record named as class+method+signature. On unload it closes the jitdump writer.

### State And Persistence
Global `jvmti_agent` stores the writer handle and `has_line_numbers` records optional capability availability. Persistent data is written through the jitdump writer.

### Dependencies And Integration Points
It depends on JVMTI/JNI, optional `jvmticmlr.h`, perf's jitdump writer API, and JVM callback semantics. It integrates with perf report through the jitdump format produced by the writer.

### Risks
Callback error handling logs and returns, so missing metadata can reduce symbol/debug quality without failing the JVM. `Agent_OnLoad()` returns after some failure paths without closing an already opened writer. Source filename construction assumes Java class signatures map naturally to paths. Inline caller frames are ignored; only leaf methods are recorded.

### Test Signals
Load the built agent into HotSpot with JIT compilation enabled, record with perf, and verify Java method symbols and optional line information appear. Exercise builds with and without `HAVE_JVMTI_CMLR`.
