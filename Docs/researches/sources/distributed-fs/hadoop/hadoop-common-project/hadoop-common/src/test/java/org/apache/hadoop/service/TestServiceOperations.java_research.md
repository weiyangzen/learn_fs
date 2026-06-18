# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceOperations.java

Purpose: tests the quiet stop utility path when `Service.stop()` itself throws, ensuring logging and stack trace handling occur instead of rethrowing.

Important APIs/types/functions: `ServiceOperations.stopQuietly(Logger, Service)`, Mockito mocks for `Service` and `RuntimeException`, `GenericTestUtils.LogCapturer.captureLogs`, and AssertJ string assertions.

Control flow: the mocked service is configured to throw a mocked runtime exception from `stop()`. `stopQuietly` is invoked with a test logger. The test then inspects captured log output and verifies the exception's `printStackTrace(PrintWriter)` was called once.

State and persistence behavior: all state is in-memory mock invocation state and the temporary log-capture buffer. No durable state is written.

Dependencies and integration points: integrates `ServiceOperations` with SLF4J/log4j capture and Mockito. It guards the operational behavior expected by teardown code across service tests and production utility use.

Risks and test signals: the main risk is swallowing stop failures without diagnostic detail. The test signal is narrow but precise: a failure message naming the service is logged and stack trace rendering is requested exactly once.
