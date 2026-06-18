# sources/distributed-fs/ceph-client/tools/perf/tests/config-fragments/config

Purpose: this config fragment declares kernel tracing features expected by perf test/config fragment workflows.

Important entries: it enables tracepoints, stacktrace support, nop tracer, ring buffer, event tracing, context-switch tracer, generic tracing, ftrace, syscall ftrace, kprobes, kprobe events, and uprobe events, while selecting `CONFIG_BRANCH_PROFILE_NONE`.

Control flow and state: there is no executable logic. The file is consumed as static configuration input by build or test tooling that assembles required kernel config fragments.

Dependencies, integration, risks, and tests: it integrates with perf tests that need ftrace, tracepoints, syscall tracing, kprobes, and uprobes. Risks are stale config expectations if perf tests begin requiring additional tracing features or if a target architecture names options differently. Test signals are kernel builds/config checks where this fragment satisfies perf tracing test prerequisites.
