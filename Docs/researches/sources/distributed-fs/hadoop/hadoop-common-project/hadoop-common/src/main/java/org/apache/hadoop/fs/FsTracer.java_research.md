# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsTracer.java

Purpose: `FsTracer` provides the singleton HTrace `Tracer` used by filesystem client operations.

Important APIs: synchronized static `get(Configuration)` and private constructor.

Control flow and state: the first `get` call builds a `Tracer` named `FSClient` from `CommonConfigurationKeys.FS_CLIENT_HTRACE_PREFIX`; subsequent calls return the same static instance regardless of later configurations. There is no explicit close or reset method here.

Dependencies and integration: used by `Globber` and filesystem APIs needing tracing, with configuration wrapped through `TraceUtils`.

Risks: singleton configuration is first-writer-wins, which can surprise tests or applications with multiple configurations. Global lifecycle is intentionally a workaround for `FileContext`/DFSClient creation patterns.

Test signals: singleton reuse, trace prefix configuration on first call, concurrency around first initialization, and no accidental tracer recreation.
