# sources/distributed-fs/ceph-client/samples/ftrace/Makefile

Purpose: builds several ftrace direct-call, ftrace ops, and trace-array sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_FTRACE_DIRECT` to `ftrace-direct.o`, `ftrace-direct-too.o`, and `ftrace-direct-modify.o`; maps `CONFIG_SAMPLE_FTRACE_DIRECT_MULTI` to multi-direct variants; maps `CONFIG_SAMPLE_FTRACE_OPS` and `CONFIG_SAMPLE_TRACE_ARRAY`. Adds `-I$(src)` for `sample-trace-array.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on ftrace, architecture trampoline support, and trace event headers.

Risks: architecture-specific assembly in the C files controls actual build success.

Test signals: enable each sample config and build; unsupported architectures should fail at Kconfig or compile gates.
