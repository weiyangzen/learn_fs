<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandUtils.java

## Purpose
Provides a tiny formatting helper for multi-line command descriptions.

## Important APIs, Types, And Functions
`formatDescription(String usage, String... desciptions)` builds `usage: first` followed by tab-indented continuation lines. The parameter name contains a typo but does not affect behavior.

## Control Flow
The method assumes at least one description string, appends the first after the usage, then appends remaining descriptions on new indented lines.

## State And Persistence
Stateless package-private utility class.

## Dependencies And Integration Points
Used by shell command classes that want consistent help text formatting.

## Risks
Calling with zero descriptions throws `ArrayIndexOutOfBoundsException`. It hardcodes tab indentation and newline formatting.

## Test Signals
Format one-line and multi-line descriptions and verify zero-description behavior if callers can reach it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandUtils.java -->
