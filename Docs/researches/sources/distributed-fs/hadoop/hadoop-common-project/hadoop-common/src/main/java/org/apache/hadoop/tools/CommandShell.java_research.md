# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/CommandShell.java

Purpose: `CommandShell` is an abstract base for Hadoop CLI utilities implemented as `Tool`s with optional subcommands and injectable output streams.

Important APIs and types: subclasses implement `getCommandUsage()` and `init(String[])`. The base class exposes `setSubCommand`, `setOut`, `getOut`, `setErr`, `getErr`, `run`, `printShellUsage`, `printException`, and nested abstract `SubCommand` with `validate`, `execute`, and `getUsage`.

Control flow: `run` calls subclass `init`; if initialization fails or no subcommand is selected, it prints usage and returns the init exit code. If a subcommand is selected, it validates and executes it, printing usage and returning 1 on validation failure or any exception.

State and persistence behavior: stores current `PrintStream`s and selected subcommand only. It writes to streams but persists no data.

Dependencies and integration points: extends `Configured`, implements `Tool`, and is intended for command implementations run by `ToolRunner` or Hadoop scripts.

Risks: any exception prints a stack trace by default, which may be too verbose for user-facing commands. `SubCommand` is a non-static inner class, so it holds the enclosing shell. A subcommand can return no status except by throwing.

Test signals: cover init failure, no subcommand usage, validate false path, execute exception path, stream injection, and command-specific usage selection.
