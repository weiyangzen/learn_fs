# sources/cloud-native/moby/contrib/syscall-test/ns.c

## Purpose
Exercises namespace-related syscalls for Docker security profile validation.

## APIs, Types, And Functions
The C file uses Linux namespace APIs such as clone, unshare, or setns style calls through system headers. Its process exit result indicates whether the syscall path was allowed.

## Control Flow, State, And Integration
The program attempts namespace operations from inside a container and exits based on success or failure. Runtime state is limited to attempted namespace changes in the process.

## Risks And Test Signals
Risks include kernel capability requirements, seccomp blocking, and host configuration differences. Integration is with tests for namespace isolation and default syscall policy.
