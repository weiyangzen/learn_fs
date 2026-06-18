# sources/cloud-native/moby/contrib/syscall-test/setuid.c

## Purpose
Tests `setuid` behavior inside a container for security and syscall policy validation.

## APIs, Types, And Functions
The C program calls a user-ID changing API such as `setuid` and exposes the result via process exit status.

## Control Flow, State, And Integration
The program attempts to change its process user identity and exits. State is process-local credential state only.

## Risks And Test Signals
Risks include capability and user-namespace differences causing different legitimate results. Integration is with Docker default capabilities and seccomp policy tests.
