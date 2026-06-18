# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsShellPermissions.java

Purpose: `FsShellPermissions` hosts `-chmod`, `-chown`, and `-chgrp` shell commands separate from the main shell class.

Important APIs: `registerCommands`, nested `Chmod`, `Chown`, and `Chgrp`, `processOptions`, `processPath`, and owner/group parsing helpers. `Chmod` uses `ChmodParser`; `Chown` and `Chgrp` use regex validation with platform-specific allowed characters.

Control flow and state: each command parses `-R`, validates the first non-option argument, then walks path arguments through `FsCommand` mechanics. `Chmod.processPath` computes a new permission and calls `setPermission` only when it changes. `Chown.processPath` sends null for unchanged owner/group so filesystem implementations mutate only needed fields. Command instances keep parsed owner/group/parser state for the run.

Dependencies and integration: integrates with `CommandFactory`, `CommandFormat`, `PathData`, `FsPermission`, `ChmodParser`, `Shell.WINDOWS`, and the active filesystem behind each `PathData`.

Risks: regex differences between Windows and Unix affect accepted names. The chmod error message intentionally retains legacy prefixing. Local filesystems using shell `chown` can interpret dotted usernames unexpectedly, as documented. Recursive behavior is delegated to `FsCommand`.

Test signals: mode parser acceptance/rejection, octal sticky-bit forms, recursive option handling, unchanged-permission no-ops, owner/group parsing including empty owner or group, Windows spaces in names, and error message compatibility.
