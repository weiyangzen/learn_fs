# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/testConf.xml

## Purpose
`testConf.xml` is a command-output specification for Hadoop `fs` shell help tests. It describes commands to run and comparators for expected help text.

## Important Structure
The top-level mode is `test`, with comments indicating `nocompare` can run commands and dump output. Each `<test>` contains a description, `<test-commands>`, optional cleanup commands, and comparators. Comparator types include `SubstringComparator`, `RegexpComparator`, `TokenComparator`, and `RegexpAcrossOutputComparator`.

The covered commands are mostly `hadoop fs -help` variants: general `-help`, `ls`, deprecated `lsr`, `du`, deprecated `dus`, `count`, `mv`, `cp`, `rm`, `rmdir`, deprecated `rmr`, `put`, `copyFromLocal`, `moveFromLocal`, `get`, `getmerge`, `cat`, `checksum`, `copyToLocal`, `moveToLocal`, `mkdir`, `setrep`, `touch`, `touchz`, `test`, `stat`, `tail`, `chmod`, `chown`, `chgrp`, `find`, and `help`.

## Control Flow
The XML is interpreted by Hadoop's command test harness. For each test, the harness invokes the listed `hadoop fs` command, captures output, and applies the configured comparators in order. Most tests assert regex fragments of help output; `find` uses a cross-output comparator for a larger multi-line help block.

## State And Persistence
The file is static expected-output data. Most tests are read-only help commands and have empty cleanup. Runtime state is limited to captured command output and test framework reports.

## Dependencies And Integration Points
It integrates with FsShell help text, command-line parser behavior, and the comparator framework. It also encodes compatibility expectations for deprecated aliases such as `lsr`, `dus`, and `rmr`.

## Risks
Help text changes can break tests even when command behavior is unchanged. Several comparators are sensitive to whitespace and regex escaping. There is a malformed-looking nested comparator under the `put` test, which may be accepted by the historical harness but is structurally fragile. Long multi-line expectations for `find` can become stale when help text evolves.

## Test Signals
Passing command tests show that user-facing help syntax, option lists, deprecated command messages, and selected descriptions remain stable. Failures should be triaged as either intentional documentation/help updates requiring fixture changes or regressions in command registration.
