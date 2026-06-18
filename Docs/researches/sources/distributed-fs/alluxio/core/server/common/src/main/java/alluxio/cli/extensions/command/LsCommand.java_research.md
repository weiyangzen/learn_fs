# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/LsCommand.java

## Purpose
`LsCommand` lists installed extension jar names from the configured extension directory.

## Important APIs, Types, And Functions
It implements `Command` with name and usage `ls`. `validateArgs` requires zero arguments. `run` calls `ExtensionUtils.listExtensions` with `PropertyKey.EXTENSIONS_DIR` and prints each returned file name.

## Control Flow, State, Dependencies, Risks, And Tests
The command has read-only behavior against local extension directory state. Dependencies are `Configuration`, `PropertyKey`, and `ExtensionUtils`. The declared logger is unused. Risks are silent empty output when the directory is inaccessible or absent depending on `ExtensionUtils` behavior, and local-only visibility while install/uninstall operate across hosts. Tests should cover zero-argument validation, sorted or unsorted output contract from `ExtensionUtils`, absent directory behavior, and jar filtering.
