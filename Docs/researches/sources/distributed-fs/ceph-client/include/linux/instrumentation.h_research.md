<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumentation.h -->
# sources/distributed-fs/ceph-client/include/linux/instrumentation.h

Purpose: Defines annotation macros that mark code regions where compiler or runtime instrumentation is allowed or forbidden.

Important APIs/types/functions: Macros such as `instrumentation_begin()` and `instrumentation_end()` create annotation boundaries; validation helpers interact with objtool/KCSAN/KASAN-style instrumentation constraints depending on configuration.

Control flow: Low-level entry/exit, noinstr, and sensitive code bracket instrumentable sections so tooling can validate that unsafe instrumentation is absent.

State/persistence: No runtime state in normal builds; annotations become metadata or compiler barriers/tool hints.

Dependencies/integration: Integrates compiler attributes, objtool validation, tracing, sanitizers, and architecture entry code.

Risks: Missing or misplaced annotations can introduce recursion, tracing in noinstr paths, or false validation failures.

Test signals: Objtool noinstr validation, sanitizer-enabled builds, ftrace/perf entry tests, and architecture entry smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumentation.h -->
