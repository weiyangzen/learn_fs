# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe.c

## Purpose

`wait-pipe.c` is a simple synchronization helper for Landlock tests that need a child process to announce readiness and then block until the parent completes its assertion.

## Important APIs, Types, and Functions

It uses `atoi()` to parse two pipe FDs, `write()` to send a one-byte ready marker, and `read()` to wait for the parent. It reports errors with `fprintf()` and `perror()`.

## Control Flow and State

The program requires exactly two arguments after its name. It writes `"."` to the child pipe, reads one byte from the parent pipe, then exits 0. It does not create Landlock domains or persistent files.

## Dependencies and Integration Points

It integrates with Landlock filesystem layout tests, especially cases that need a stable child process while the parent manipulates mounts or checks sandbox behavior.

## Risks and Test Signals

Risks are invalid FD arguments or broken pipes. Success is silent exit 0 after both synchronization events; failure exits 1 with a diagnostic.
