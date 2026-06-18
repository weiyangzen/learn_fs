# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseCommand.java

Purpose: command interface for FUSE special commands exposed through synthetic Alluxio CLI paths.

Important APIs and helpers: extends the general `Command` interface and adds default `validateArgs(String[])` and `run(AlluxioURI, String[])` methods. The default validator is a no-op; the default runner returns `null`.

Control flow and state: concrete commands override validation and run behavior as needed. The interface itself has no mutable state or persistence.

Dependencies and integration: depends on `AlluxioURI`, `URIStatus`, and `InvalidArgumentException`. It is consumed by `FuseShell` and command implementations under `alluxio.cli.command`.

Risks and test signals: default `run` returning null can hide incomplete command implementations until runtime. There are no direct tests here; behavior is validated through concrete command and shell tests elsewhere.
