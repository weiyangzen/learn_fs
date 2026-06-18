# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/TouchCommands.java

Purpose: registers `touchz` and Unix-like `touch` commands for creating zero-length files and updating access/modification times.

Important APIs and types: nested `Touchz` and `Touch`; `Touchz.processPath()`, `processNonexistentPath()`, `touchz()`; `Touch.processOptions()`, `touch()`, and `updateTime()`.

Control flow: `touchz` requires paths, rejects directories, rejects existing nonzero files, and creates zero-length files if missing and parent exists. `touch` parses `-a`, `-m`, `-t yyyyMMdd:HHmmss`, and `-c`; it creates missing files unless `-c`, then updates both times or only one time using `-1` sentinel for unchanged time.

State and persistence: mutates file creation and timestamps. Per-run state stores selected time flags, timestamp string, and no-create flag.

Dependencies and integration: uses `PathData.parentExists()`, `fs.create()`, `fs.setTimes()`, `SimpleDateFormat`, and Hadoop path exceptions.

Risks: timestamp parsing uses default timezone and lenient `SimpleDateFormat` behavior unless configured elsewhere. Creating a file before timestamp update can leave current timestamps if update fails. `touchz` calls `create()` without explicit overwrite control but only after validating zero-length existing file.

Test signals: cover missing parent, existing directory, existing nonzero/zero files, `touch -c`, `-a`, `-m`, both flags, explicit timestamp parse success/failure, timezone/leniency expectations, and creation followed by timestamp update.
