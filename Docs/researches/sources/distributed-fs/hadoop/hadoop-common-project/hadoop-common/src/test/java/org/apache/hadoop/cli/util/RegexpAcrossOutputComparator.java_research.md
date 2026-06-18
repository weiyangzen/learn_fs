# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpAcrossOutputComparator.java

Purpose: comparator that searches a regular expression across the entire command output, including multi-line spans.

Important APIs: `compare` normalizes carriage returns on Windows, compiles expected as a regex, and calls `matcher(actual).find()`.

Control flow: unlike `RegexpComparator`, does not tokenize by line and uses substring regex search rather than full-line match.

State and persistence: stateless.

Dependencies/integration: depends on `Shell.WINDOWS` and Java regex; reflectively loaded by CLI tests.

Risks and test signals: regex syntax errors propagate to the harness as comparator instantiation/use failures; no DOTALL flag is set unless the pattern requests it. Tests should cover CRLF normalization and true multi-line patterns.
