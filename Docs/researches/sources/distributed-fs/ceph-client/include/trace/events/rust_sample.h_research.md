# sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h

Purpose: Provides a minimal tracepoint used by Rust kernel sample code to report that the sample module loaded.

Important APIs/types/functions: `TRACE_SYSTEM rust_sample`; `rust_sample_loaded` takes a `const char *message`, copies it with `__string`, and prints it.

Control flow: The Rust sample module can call the generated trace function during initialization or demonstration code. The trace event stores the sample message in the ring buffer.

State and persistence: No state is owned. It observes a transient string from sample code.

Dependencies and integration points: Depends on tracepoints and `trace/define_trace.h`. It integrates with Rust-for-Linux sample build paths and the generic tracepoint generation machinery.

Risks and test signals: Risks are mostly build-system and FFI contract issues: string lifetime, Rust/C tracepoint binding drift, and sample availability under config changes. Test Rust sample module load/unload, tracepoint enablement, and builds with Rust support toggled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h` completely for this pass (31 lines, 683 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h_research.md`.
