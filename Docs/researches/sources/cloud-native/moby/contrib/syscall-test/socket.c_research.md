# sources/cloud-native/moby/contrib/syscall-test/socket.c

## Purpose
Exercises socket syscalls for container security-profile validation.

## APIs, Types, And Functions
The C program uses socket-related system headers and attempts to create or use a socket type selected for policy testing.

## Control Flow, State, And Integration
At runtime it performs the socket operation, exits with status reflecting success or denial, and persists no state beyond any transient descriptor.

## Risks And Test Signals
Risks include kernel/network namespace variation and capability requirements. Integration is with Docker seccomp and network capability policy tests.
