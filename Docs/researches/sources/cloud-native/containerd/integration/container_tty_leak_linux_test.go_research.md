# sources/cloud-native/containerd/integration/container_tty_leak_linux_test.go

## Purpose

This Linux integration test checks that TTY/PTY descriptors are not leaked by shim exec and container lifecycle operations. It validates both TTY-only and interactive TTY containers.

## Important APIs, Types, And Functions

- `TestContainerTTYLeakAfterExit` runs subtests for `stdin=false` and `stdin=true`.
- `getShimPid` connects to the shim ttrpc API and returns the shim PID.
- `numTTY` counts `ptmx` descriptors with `lsof`.
- `checkTTY` polls for an expected descriptor count.
- Kubernetes `remotecommand` SPDY executor streams the CRI exec session.

## Control Flow

The test creates a BusyBox sandbox, then for each case creates a TTY container running `sleep 365d`. After start, it checks the shim has one TTY. It then requests an exec session with TTY, opens the returned URL using a SPDY executor, streams stdout and optional stdin, and checks the TTY count remains one. Finally it stops/removes the container and checks the count drops to zero.

## State And Persistence Behavior

The only state observed is the shim file descriptor table. Container and exec sessions are transient; cleanup removes the container after each subtest.

## Dependencies And Integration Points

This test integrates CRI `Exec`, kubelet-style SPDY remotecommand streaming, containerd shim ttrpc connection, and host `lsof`. It uses the `k8s.io` containerd namespace when locating the shim.

## Risks And Edge Cases

It depends on host support for `lsof`, permissions to inspect shim FDs, and remotecommand URL availability. Descriptor counts can be affected by concurrent execs if tests are not isolated.

## Test Signals

Passing shows that TTY descriptors are opened for the main container and closed after exec/container removal without accumulating extra PTYs.
