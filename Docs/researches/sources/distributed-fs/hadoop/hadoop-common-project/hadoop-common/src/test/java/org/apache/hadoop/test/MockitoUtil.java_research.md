# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MockitoUtil.java

Purpose: Hadoop-specific Mockito conveniences for IPC protocol mocks and conditional stack-sensitive failures.

Important APIs/types/functions: `mockProtocol(Class<T>)`, `doThrowWhenCallStackMatches(Throwable, String)`, and `verifyZeroInteractions(Object...)`.

Control flow: `mockProtocol` creates a Mockito mock with `Closeable` as an extra interface because Hadoop IPC proxies often require both protocol and close behavior. `doThrowWhenCallStackMatches` installs an answer that sets the throwable stack trace to the current stack, checks each element against a regex, throws if matched, otherwise calls the real method. `verifyZeroInteractions` delegates to `verifyNoInteractions`.

State and persistence behavior: no persistence; state is Mockito stubbing and throwable stack trace mutation.

Dependencies and integration points: integrates with Mockito and Hadoop IPC test patterns.

Risks and test signals: stack-regex behavior is brittle across refactors but useful for targeted failure injection. Mock protocol extra interfaces prevent close-cast failures in tests.
