# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_ssh_test.go

## Purpose
This file tests Dockerfile SSH mounts. It verifies socket ownership/mode parameters and guards against leaking file descriptors to repeated SSH client invocations. It registers `sshTests` into `allTests` and is Linux-only.

## Important APIs, Types, and Functions
Tests are `testSSHSocketParams` and `testSSHFileDescriptorsClosed`. Dependencies include `sshprovider.NewSSHAgentProvider`, BuildKit sessions, generated RSA keys, `ssh-agent`, `os/exec`, socket path management, `client.New`, and `f.Solve`.

## Control Flow and Assertions
`testSSHSocketParams` generates an RSA private key, writes it to a short temp path, constructs an SSH agent provider from that key, and builds a BusyBox Dockerfile that stats `$SSH_AUTH_SOCK` under `RUN --mount=type=ssh,mode=741,uid=100,gid=102`. `testSSHFileDescriptorsClosed` starts a real `ssh-agent` in debug mode on a controlled socket, waits for the socket to appear, mounts it into an Alpine build that installs OpenSSH and calls `ssh -T git@github.com` three times, then checks agent debug output contains socket 1 but not socket 2 or 3.

## State, Persistence, and Dependencies
State includes temporary private keys, ssh-agent socket files, and debug output buffers. The tests depend on Linux Unix sockets, external package install/network access to GitHub in the build step, and BuildKit SSH session forwarding.

## Integration Points
The file exercises Dockerfile SSH mount parsing, session attachable forwarding, executor socket creation with requested metadata, and cleanup of forwarded connections/file descriptors across repeated command invocations.

## Risks and Test Signals
Risks include wrong socket ownership/mode, socket path length failures, fd leaks in SSH forwarding, external network/package flakiness, and Windows unsupported paths. Signals are stat equality and ssh-agent debug-output checks that detect repeated socket descriptors.
