# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/find/TestHelper.java

Purpose: Small package-private helper class for find expression unit tests.

Important APIs/types/functions: `addArgument(Expression, String)` and `getArgs(String)`.

Control flow: `addArgument` wraps a single string in a `LinkedList` and calls `Expression.addArguments`. `getArgs` splits a command string by spaces and returns a mutable `LinkedList`.

State/persistence: Stateless; all structures are created per call.

Dependencies/integration: Used by `TestName` and `TestIname` to configure expressions consistently with parser-style argument deques. Also mirrors command splitting used in `TestFind`.

Risks: The split helper does not support quoting, escaping, or repeated whitespace. It is appropriate for unit tests with simple tokens only.

Test signals: Indirect: expression tests relying on helper-produced argument lists pass/fail according to expression configuration.
