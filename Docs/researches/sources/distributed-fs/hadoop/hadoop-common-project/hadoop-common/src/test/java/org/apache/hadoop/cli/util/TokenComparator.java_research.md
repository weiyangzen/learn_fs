# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/TokenComparator.java

Purpose: comparator that treats expected as a comma/newline/CR-delimited token list and requires every token to occur in actual output.

Important APIs: `compare` tokenizes expected with delimiters `,\n\r` and checks `actual.indexOf(token)`.

Control flow: initializes success true and ANDs each token presence result. If expected has no tokens, it returns true.

State and persistence: stateless.

Dependencies/integration: reflectively used by CLI tests for unordered or partial output checks.

Risks and test signals: token matching is substring-based, not word-boundary or normalized; empty expected can pass vacuously. Tests should cover missing token failure, duplicate tokens, and tokens containing spaces.
