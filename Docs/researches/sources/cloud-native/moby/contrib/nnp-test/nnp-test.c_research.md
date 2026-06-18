# sources/cloud-native/moby/contrib/nnp-test/nnp-test.c

## Purpose
Provides a tiny C program used to observe whether privilege elevation is blocked under no-new-privileges.

## APIs, Types, And Functions
The file contains a minimal `main`-style program that reports or exits based on effective identity behavior. It uses standard C and Unix process credential APIs.

## Control Flow, State, And Integration
The program runs inside a container and checks runtime privilege state. It persists no state; its exit code/output is the signal consumed by tests or manual checks.

## Risks And Test Signals
Risks include platform assumptions, setuid/capability setup differences, and too-simple diagnostics. Integration is with Docker runtime security options and the accompanying Dockerfile image.
