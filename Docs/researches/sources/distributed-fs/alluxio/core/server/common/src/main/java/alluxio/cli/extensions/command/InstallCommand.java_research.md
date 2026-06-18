# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/InstallCommand.java

## Purpose
`InstallCommand` installs an Alluxio extension jar to every configured master and worker host.

## Important APIs, Types, And Functions
It implements `Command` with name `install`, usage `install <URI>`, and `run`/`validateArgs`. `run` ensures the configured extension directory exists locally, then executes remote `rsync` over ssh for each host from `ConfigurationUtils.getServerHostnames`.

## Control Flow, State, Dependencies, Risks, And Tests
Argument validation requires exactly one non-null argument ending with `Constants.EXTENSION_JAR`. Runtime state is the local extension directory plus remote extension jar copies. Dependencies include configuration, `ShellUtils`, ssh/rsync, and host files. Risks include shell-string injection through URI or directory values, partial installation across hosts, local directory creation not guaranteeing remote parent existence, and reliance on external commands. Tests should mock host lists and command execution, check jar suffix validation, verify partial failure reporting, and cover directory creation failure.
