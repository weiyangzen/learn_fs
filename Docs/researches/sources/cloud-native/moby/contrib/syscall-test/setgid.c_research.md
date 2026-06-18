# sources/cloud-native/moby/contrib/syscall-test/setgid.c

## Purpose
Tests `setgid` behavior inside a container for security and syscall policy validation.

## APIs, Types, And Functions
The C program calls a group-ID changing API such as `setgid` and reports success or failure through its exit code.

## Control Flow, State, And Integration
Execution attempts to change the process group identity. Any state change is limited to the running process credentials and disappears at exit.

## Risks And Test Signals
Risks include capability-dependent behavior and mismatched expectations across root/rootless containers. Integration is with seccomp, capabilities, and user namespace tests.
