# sources/cloud-native/moby/contrib/syscall-test/acct.c

## Purpose
Exercises the Linux `acct` syscall for security-profile testing.

## APIs, Types, And Functions
The C program calls the accounting syscall or libc wrapper against a temporary path such as `/tmp/t`. It uses standard Unix headers and returns process exit status as the test signal.

## Control Flow, State, And Integration
At runtime the program attempts process accounting setup from inside a container. It may touch a temporary file path but has no durable intended state. The result indicates whether the syscall is allowed or blocked.

## Risks And Test Signals
Risks include requiring privileges or kernel support and interpreting EPERM correctly. Integration is with Docker seccomp/default profile checks.
