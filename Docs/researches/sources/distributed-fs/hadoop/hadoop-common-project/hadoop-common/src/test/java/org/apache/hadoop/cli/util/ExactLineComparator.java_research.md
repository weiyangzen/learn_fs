# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactLineComparator.java

Purpose: comparator that passes when any actual output line exactly equals expected.

Important APIs: `compare` tokenizes actual output on `\n` and `\r` via `StringTokenizer` and checks line equality.

Control flow: scans until a match is found or tokens are exhausted.

State and persistence: stateless.

Dependencies/integration: reflectively used by CLI XML tests.

Risks and test signals: `StringTokenizer` drops empty lines and treats CR/LF as delimiters rather than preserving line endings. Tests should include multi-line output, empty-line expectations, and Windows CRLF output.
