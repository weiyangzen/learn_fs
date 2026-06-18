# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/MoveCommands.java

Purpose: registers move commands `moveFromLocal`, unimplemented `moveToLocal`, and `mv`.

Important APIs and types: nested `MoveFromLocal`, `MoveToLocal`, and `Rename`. `MoveFromLocal` extends `CopyFromLocal`; `Rename` extends `CommandWithDestination`.

Control flow: `MoveFromLocal` rejects `-t`, delegates `put`-style copy options, refuses to merge into an existing target directory, and deletes the local source in `postProcessPath()` after copy. `MoveToLocal.processOptions()` always throws not implemented. `Rename` parses source/destination, resolves remote destination, validates source and target filesystem scheme/host strings match, rejects existing targets, and calls `target.fs.rename()`.

State and persistence: `MoveFromLocal` creates remote targets and deletes local sources. `Rename` mutates filesystem namespace through rename. No durable internal state.

Dependencies and integration: reuses `CopyCommands.CopyFromLocal`, `CommandWithDestination`, `PathData`, and path exceptions.

Risks: `MoveFromLocal` delete happens after copy, so partial success can leave both source and target if delete fails. `mv` filesystem equality compares only scheme and host, not port, authority details, or filesystem implementation identity. `mv` rejects overwrite unconditionally. `moveToLocal` is registered but always fails.

Test signals: cover `moveFromLocal` delete-after-copy, target directory rejection, `-t` rejection, `moveToLocal` not implemented, `mv` cross-filesystem rejection including authority edge cases, existing target rejection, and failed rename mapping.
