# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsCommand.java

Purpose: base class and registry hub for `hadoop fs` shell commands.

Important APIs and types: static `registerCommands(CommandFactory)`, protected constructors, `getCommandName()`, deprecated `runAll()`, unsupported `run(Path)`, and `processRawArguments()`.

Control flow: registration delegates to command groups including ACL, copy, count, delete, display, find, permissions, usage, listing, mkdir, move, replication, stat, tail/head, test, touch, truncate, snapshots, xattr, and concat. At runtime `processRawArguments()` expands raw strings to `PathData`, optionally warns when `fs.defaultFS` is unset/default, then calls `processArguments()`.

State and persistence: no additional persistent state beyond inherited `Command` fields. It only reads configuration and emits warnings.

Dependencies and integration: extends `Command`, imports `FsShellPermissions` and `find.Find`, and consumes common configuration keys `fs.defaultFS` and shell missing-default-FS warning settings.

Risks: all registered command availability depends on this central list. `run(Path)` intentionally throws and should not be used. The variable `expendedArgs` is a typo but harmless. Warning behavior can affect stderr-sensitive scripts unless configuration disables it.

Test signals: verify command registration coverage, default-FS warning enabled/disabled behavior, default command-name compatibility, and deprecated `runAll()` delegation.
