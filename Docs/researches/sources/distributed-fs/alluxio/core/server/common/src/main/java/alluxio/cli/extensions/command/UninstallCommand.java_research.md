# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/extensions/command/UninstallCommand.java

## Purpose
`UninstallCommand` removes an extension jar from every configured master and worker host.

## Important APIs, Types, And Functions
It implements `Command` with name `uninstall`, usage `uninstall <JAR>`, and remote removal in `run`. `validateArgs` requires one non-null jar name ending in `Constants.EXTENSION_JAR`. `PathUtils.concatPath` combines the extension directory and jar argument for the remote `rm`.

## Control Flow, State, Dependencies, Risks, And Tests
For each server host, the command executes `ssh ... rm <extensionsDir>/<jar>`, records failed hosts, and returns `-1` on any failure. It mutates remote extension directory contents and does not alter service classloaders already running. Dependencies include ssh, shell command execution, configuration, and host discovery. Risks include shell injection via jar names, partial uninstall, no existence precheck, and removal of unintended paths if path joining or arguments are unsafe. Tests should mock command execution, validate jar suffix rules, verify failed-host reporting, and cover host-list iteration.
