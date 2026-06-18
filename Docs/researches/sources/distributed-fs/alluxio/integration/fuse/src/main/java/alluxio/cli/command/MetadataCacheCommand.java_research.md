# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/MetadataCacheCommand.java

Purpose: top-level FUSE special command for inspecting or mutating the client metadata cache.

Important APIs and helpers: static `SUB_COMMANDS` maps `dropAll`, `drop`, and `size` to constructors. Constructor instantiates subcommands with the same `FileSystem`, configuration, and parent command name. Overrides `getSubCommands`, `getCommandName`, `getUsage`, and `getDescription`.

Control flow and state: command execution is delegated entirely to subcommands by `FuseShell`. Usage is generated as a synthetic `ls -l` path under default FUSE mount and `.alluxiocli.metadatacache.(...)`.

Dependencies and integration: depends on `DropAllCommand`, `DropCommand`, `SizeCommand`, `Constants`, and `TwoKeyConcurrentMap.TriFunction` constructor references.

Risks and test signals: subcommand map iteration order is unspecified, so usage command order may vary. The command is thread-safe in annotation, but `HashMap` contents are mutable after construction if exposed through `getSubCommands`.
