# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseShell.java

Purpose: dispatcher for FUSE special commands encoded in path suffixes such as `.alluxiocli.metadatacache.size`.

Important APIs and helpers: constructor loads commands from the package using `CommandUtils.loadCommands`. `isSpecialCommand(AlluxioURI)` detects paths whose last segment starts with `Constants.ALLUXIO_CLI_PATH`. `runCommand(AlluxioURI)` parses command tokens, walks subcommands, validates arguments, executes the selected `FuseCommand`, and returns a mock `URIStatus`.

Control flow and state: `runCommand` uses the parent URI as the command target path and splits suffix tokens on dots. It logs usage and throws `InvalidArgumentRuntimeException` for missing, unknown, or invalid commands. For nested commands, it repeatedly descends through `Command.getSubCommands()`.

Dependencies and integration: depends on Alluxio file system, configuration, command loading, constants, logging, and metadata-cache commands.

Risks and test signals: dot-separated path parsing means command names/arguments cannot contain dots without ambiguity. Errors are logged rather than returned as normal status. No direct tests are in this subset.
