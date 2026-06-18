<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/MetaRecoveryContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/MetaRecoveryContext.java

## Purpose

`MetaRecoveryContext` holds operator-interaction state during NameNode metadata recovery, especially edit-log loading when corruption or unexpected records require a decision.

## Important APIs and Types

Force modes are `FORCE_NONE`, `FORCE_FIRST_CHOICE`, and `FORCE_ALL`. `ask` prints a prompt and reads a single-line response unless force mode chooses the first option automatically. `editLogLoaderPrompt` logs an error and offers continue, stop, quit, or always-choose-first behavior. `RequestStopException` signals a deliberate stop while preserving earlier edits.

## Control Flow, State, and Persistence

When no recovery context is supplied, `editLogLoaderPrompt` turns the condition into an `IOException`. With context, it asks the user what to do. Continue returns, stop throws `RequestStopException`, quit calls `System.exit(0)`, and always sets force to `FORCE_FIRST_CHOICE`. The only mutable state is the force mode; it is not persisted.

## Dependencies and Integration Points

It integrates with edit-log loader recovery paths, standard input/output/error, SLF4J logging, and operator-driven NameNode recovery commands.

## Risks and Test Signals

Risks include blocking on stdin in noninteractive environments, `System.exit` during tests/tools, and force mode choosing an unsafe default. Tests should cover each prompt response, null recovery behavior, force-mode auto-selection, stop exception propagation, and recovery commands that run with noninteractive flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/MetaRecoveryContext.java -->
