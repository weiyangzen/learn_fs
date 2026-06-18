# sources/cloud-native/moby/daemon/oci_opts.go

## Purpose
This file defines a small OCI spec option for initial TTY console sizing.

## Important APIs, Types, And Functions
`WithConsoleSize(c *container.Container)` returns a containerd OCI `SpecOpts` closure.

## Control Flow
When either configured console dimension is greater than zero, the closure ensures `s.Process` exists and sets `s.Process.ConsoleSize` from `HostConfig.ConsoleSize[0]` height and `[1]` width.

## State, Persistence, And Dependencies
It mutates only the in-memory OCI spec. Dependencies include containerd OCI option types, container model, and runtime-spec `specs.Box`.

## Integration Points
`oci_linux.go` appends this option when `c.Config.Tty` is true, so terminal containers can receive an initial size.

## Risks And Edge Cases
Zero dimensions are ignored. The function assumes the host config array indexes follow Docker's height/width convention.

## Test Signals
No direct tests in this item; behavior is covered indirectly by OCI spec creation tests or TTY integration tests.
