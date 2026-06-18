# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/AbstractFuseShellCommand.java

Purpose: base class for FUSE shell commands, storing common filesystem/configuration context and parent command name.

Important APIs and helpers: constructor accepts `FileSystem`, `AlluxioConfiguration`, and parent command name. `getParentCommandName()` exposes the parent name for usage strings. Fields are protected and final.

Control flow and state: no command execution occurs here; subclasses inherit the stored dependencies and implement `Command`/`FuseCommand` methods. The class is annotated `@ThreadSafe` because state is immutable after construction.

Dependencies and integration: implements `FuseCommand` and depends on Alluxio `FileSystem` and configuration.

Risks and test signals: as a thin base class, risk is mainly constructor contract consistency. No direct tests are present, but all concrete FUSE commands depend on its context wiring.
