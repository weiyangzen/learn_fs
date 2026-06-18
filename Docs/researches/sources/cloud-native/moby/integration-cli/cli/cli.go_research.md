# sources/cloud-native/moby/integration-cli/cli/cli.go

## Purpose
Command helper layer for invoking Docker CLI commands in integration tests.

## Important APIs and Types
Defines global `testEnv`, `SetTestEnvironment`, `CmdOperator`, `DockerCmd`, `BuildCmd`, `InspectCmd`, `WaitRun`, `WaitExited`, `Docker`, `Args`, and command modifiers like `Daemon`, `WithTimeout`, `WithEnvironmentVariables`, `WithFlags`, `InDir`, `WithStdout`, and `WithStdin`.

## Control Flow, State, and Persistence
Helpers build `icmd.Cmd` values using the configured Docker binary and daemon host, apply modifiers with undo closures, run commands, and assert exit status where appropriate. Wait helpers poll `docker inspect` output until expected state appears.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `internal/test/environment`, `gotest.tools/icmd`, and daemon helper package. It shells out to Docker and therefore mutates daemon state according to commands. Risks include global environment races, argument validation gaps, command timeouts, and cleanup relying on callers. Nearly every integration-cli file validates this helper path.
