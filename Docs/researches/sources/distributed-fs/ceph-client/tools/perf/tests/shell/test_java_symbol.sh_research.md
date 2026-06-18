## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_java_symbol.sh

Purpose: verifies Java JIT symbolization through perf's JVMTI agent and `perf inject -j`.
Important behavior: requires `jshell`, locates `libperf-jvmti.so` across source, installed, and prefix paths, records a jshell Fibonacci snippet with the JVMTI agent, injects JIT symbols, and reports them.
Control flow: missing jshell or JVMTI library skips; record/inject/report failures exit `1`.
State and persistence: temp perf.data and injected perf.data are cleaned.
Dependencies and integration: JDK/jshell, libperf-jvmti, perf record/inject/report, JIT symbol DSOs.
Risks: library path heuristics are distribution-specific; report regex assumes symbols like `Interpreter` or `jdk.internal`.
Test signals: report output contains percentage rows with Java/JIT symbols.
