# sources/cloud-native/moby/contrib/syscall-test/userns.c

## Purpose
Exercises user-namespace creation or entry behavior for security testing.

## APIs, Types, And Functions
The C program uses Linux namespace syscalls and user namespace constants through system headers, reporting results via exit status.

## Control Flow, State, And Integration
The program attempts user namespace operations inside a container. State is process namespace membership and credential mapping behavior for the lifetime of the process.

## Risks And Test Signals
Risks include host sysctl restrictions, rootless differences, seccomp blocks, and kernel version differences. Integration is with Docker user namespace and default security policy tests.
