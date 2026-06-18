# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCallBenchmark.java

Purpose: smoke-tests the `RPCCallBenchmark` command-line tool with protobuf engine settings.

Important APIs/types/functions: `RPCCallBenchmark`, `ToolRunner.run()`, JUnit timeout, and benchmark arguments `--clientThreads`, `--serverThreads`, `--time`, `--serverReaderThreads`, `--messageSize`, `--engine protobuf`.

Control flow: invokes the benchmark tool with 30 client threads, 30 server threads, 5 second duration, 4 server reader threads, 1024-byte messages, and protobuf engine, then asserts exit code 0.

State and persistence behavior: benchmark runtime state is internal to the tool: local server/client threads and timing counters. No persistent output is asserted by this test.

Dependencies and integration points: validates the CLI parser, benchmark setup, protobuf engine path, thread configuration, and ToolRunner integration.

Risks and test signals: coarse signal that benchmark invocation completes successfully under a 20s timeout. It can expose startup/runtime regressions but not detailed throughput or latency changes.
