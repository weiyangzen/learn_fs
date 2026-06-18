<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFormat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFormat.java

## Purpose
Parses simple FsShell command options and validates remaining positional argument counts.

## Important APIs, Types, And Functions
Constructors define min/max parameters and allowed options. `addOptionWithValue`, `parse`, `getOpt`, `getOptValue`, and `getOpts` are the API. Nested exceptions report too many/few arguments, unknown options, and duplicate options.

## Control Flow
Parsing destructively walks the argument list until a non-option, `-` stdin marker, or `--`. Known boolean options are removed and marked true. Known value options remove their value if present and not option-looking; otherwise they store an empty string. Unknown options are skipped only when `null` was supplied as a possible option. After option removal, positional count bounds are enforced.

## State And Persistence
Parser instances retain option states and option values, so they are not automatically reset between parses.

## Dependencies And Integration Points
Used by shell commands such as ACL commands and many FsShell operations.

## Risks
Options with values cannot accept values beginning with `-` except the literal `-`. Reusing a `CommandFormat` instance across parses can leak prior option state. `args.size() > minPar` influences value consumption, so edge cases near minimum positional counts need coverage.

## Test Signals
Boolean options, value options, `--`, stdin `-`, unknown-ignore mode, duplicate option declaration, min/max failures, value missing, and parser reuse behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFormat.java -->
