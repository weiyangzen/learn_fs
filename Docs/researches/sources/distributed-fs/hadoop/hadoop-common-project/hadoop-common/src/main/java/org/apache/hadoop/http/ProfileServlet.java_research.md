<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileServlet.java

Purpose: instrumentation servlet that launches async-profiler for a target JVM process and redirects users to the generated profile output.

Important APIs, types, and functions: enums `Event` and `Output` validate profiler event/output parameters. `doGet()` enforces instrumentation access, validates async-profiler home and pid, parses duration/interval/jstackdepth/bufsize/thread/simple/width/height/minwidth/reverse parameters, serializes profiler execution with `profilerLock`, starts `profiler.sh` asynchronously through `ProcessUtils`, writes command details, and sets an auto-refresh to the output URL. Static helpers include `setResponseHeader()`, `getAsyncProfilerHome()`, and test-only `setIsTestRun()`.

Control flow: one profiler process may run per servlet instance. If no profiler is active, the servlet builds a command, creates a unique output file under `java.io.tmpdir/prof-output-hadoop`, optionally starts the process, returns HTTP 202, and points the browser at `ProfileOutputServlet`. Invalid or missing configuration returns HTTP 500. Concurrent profiling returns an error.

State and persistence: mutable state includes a lock, volatile `Process`, configured profiler home, current pid, static output directory, static id generator, and test flag. Persistent artifacts are profiler output files in the temp directory.

Dependencies and integration points: depends on `HttpServer2` instrumentation ACLs, `ProcessUtils`, async-profiler's `profiler.sh`, servlet APIs, and `ProfileOutputServlet`.

Risks and test signals: parameters are parsed leniently, invalid numbers fall back to defaults/null. The command response exposes command text and target pid. Output files can accumulate. Tests should cover access control, missing profiler home, pid fallback, each parameter mapping, invalid event/output defaults, lock contention, already-running process handling, test-run suppression, refresh delay, and output path construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileServlet.java -->
