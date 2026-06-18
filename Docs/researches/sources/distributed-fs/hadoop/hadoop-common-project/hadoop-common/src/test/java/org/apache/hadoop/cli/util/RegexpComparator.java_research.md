# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpComparator.java

Purpose: line-oriented regular expression comparator for CLI output.

Important APIs: `compare` compiles expected as a `Pattern`, tokenizes actual output on CR/LF, and uses `Matcher.matches()` against each line.

Control flow: succeeds only when a whole line matches the regex. It stops scanning after the first match.

State and persistence: stateless.

Dependencies/integration: reflectively loaded by the CLI harness.

Risks and test signals: `matches()` requires full-line match, unlike a substring search; empty lines are ignored by `StringTokenizer`. Tests should distinguish full-line regex from contains-style expectations and cover CRLF output.
