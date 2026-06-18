# sources/cloud-native/nydus/smoke/tests/texture/golang/entrypoint.sh

## Purpose
This shell entrypoint drives the Go language texture container smoke check. It changes to the mounted source directory and runs the Go program provided by `main.go`.

## Important APIs, Types, And Functions
The script has two commands: `cd /src` and `go run main.go`. It has no functions or arguments.

## Control Flow
When invoked by `tool.runCmdStdoutContainer`, the shell starts in the container, enters `/src`, compiles/runs the Go file with `go run`, and exits with the Go command status.

## State And Persistence
No persistent state is written intentionally. Go may create build cache state in the container depending on its environment.

## Dependencies And Integration Points
It is mounted into Go-capable container images by `tool/container.go` for the `golang` recipe. It assumes `/src/main.go` exists and the image has `go` in `PATH`.

## Risks
The script has no shebang and no strict shell flags. It relies on the caller invoking `sh /src/entrypoint.sh`. If `cd /src` fails, the next command still runs unless the shell exits due to caller settings, which it does not here.

## Test Signals
A zero exit from `go run main.go` proves the mounted source was readable and the Go runtime could execute the texture program.
