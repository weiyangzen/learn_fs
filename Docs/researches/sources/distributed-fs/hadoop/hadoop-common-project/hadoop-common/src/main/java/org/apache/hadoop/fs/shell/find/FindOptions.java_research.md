# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/FindOptions.java

Purpose: mutable options holder shared by `Find` and expression instances.

Important APIs and types: getters/setters for output, error, input streams, depth-first flag, follow-link flags, start time, min/max depth, `CommandFactory`, and `Configuration`.

Control flow: `Find.createOptions()` initializes streams, command factory, and configuration. Expressions read these options during prepare/apply to control output, symlink handling, depth behavior, and future time-based predicates.

State and persistence: in-memory per-command mutable configuration. `startTime` defaults to object creation time; `configuration` defaults to a new `Configuration`.

Dependencies and integration: uses `PrintStream`, `InputStream`, `Date`, Hadoop `Configuration`, and `CommandFactory`.

Risks: setters do no validation for null streams, min/max consistency, or negative depths. Defaults may differ from the actual command environment if `Find` does not initialize options. Future expressions relying on start time need deterministic test control.

Test signals: cover defaults, `Find` initialization, all setters/getters, depth bounds, follow flags, null handling expectations, and start time override.
