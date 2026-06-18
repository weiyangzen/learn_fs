# sources/cloud-native/moby/contrib/syscall-test/Dockerfile

## Purpose
Builds small syscall test binaries used for validating seccomp and namespace behavior.

## APIs, Types, And Functions
The Dockerfile compiles C and assembly sources such as `acct.c`, `ns.c`, `raw.c`, `socket.c`, `userns.c`, `setuid.c`, `setgid.c`, and `exit32.s` into runnable test programs.

## Control Flow, State, And Integration
Build steps produce an image containing individual syscall probes. Runtime tests execute those probes under different Docker security profiles and inspect exit codes or syscall denials.

## Risks And Test Signals
Risks include compiler/architecture assumptions, 32-bit assembly support, and kernel syscall availability. Integration is with seccomp profile validation and container security regression tests.
