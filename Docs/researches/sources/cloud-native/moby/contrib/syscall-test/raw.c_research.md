# sources/cloud-native/moby/contrib/syscall-test/raw.c

## Purpose
Exercises raw socket creation or related raw networking syscalls for security testing.

## APIs, Types, And Functions
The C program uses socket/syscall headers to attempt a privileged raw operation and returns status for test assertions.

## Control Flow, State, And Integration
At runtime it invokes the raw operation inside the container and exits. It does not persist state, but may require or be denied network capabilities.

## Risks And Test Signals
Risks include host capability differences and expected EPERM/seccomp outcomes. Integration is with Docker networking capability and seccomp default-profile validation.
