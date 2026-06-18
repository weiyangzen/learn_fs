# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestTail.java

Purpose: Unit tests for FS shell `Tail` option parsing around follow mode delay.

Important APIs/types/functions: `Tail.processOptions`, `Tail.getFollowDelay`, `LinkedList<String>` command argument mutation.

Control flow: `testSleepParameter` builds arguments `-f -s 10000 /path`, processes them, and expects follow delay `10000`. `testFollowParameter` processes `-f /path` and expects the default delay `5000`.

State/persistence: No filesystem state; tests only mutate a fresh `Tail` instance and an argument list.

Dependencies/integration: Integrates with the shell command option parser for `tail`, particularly the `-f` and `-s` flags.

Risks: Narrow coverage: it does not assert remaining positional arguments, invalid delay values, missing `-s` argument handling, or non-follow mode. It will catch regressions in the public delay getter and default constant.

Test signals: Exact millisecond values after option parsing.
