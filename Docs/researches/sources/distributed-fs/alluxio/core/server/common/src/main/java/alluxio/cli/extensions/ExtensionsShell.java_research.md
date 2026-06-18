# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/ExtensionsShell.java

## Purpose
`ExtensionsShell` is the top-level shell for managing Alluxio extension jars.

## Important APIs, Types, And Functions
The package-private constructor passes the global configuration to `AbstractShell`. `main` creates the shell and exits with the shell return code. `getShellName` returns `extensions`, and `loadCommands` discovers command implementations from the same package.

## Control Flow, State, Dependencies, Risks, And Tests
The shell delegates parsing, help, and command dispatch to `AbstractShell`; this class only wires discovery and naming. It has no persistence itself, but commands it loads mutate extension directories on local and remote hosts. Dependencies include `CommandUtils`, `Configuration`, and the CLI command package. Risks are classpath/service discovery failures and command packages being renamed without updating loader assumptions. Tests should verify command loading, shell name, dispatch to `install`, `ls`, and `uninstall`, and process exit propagation.
