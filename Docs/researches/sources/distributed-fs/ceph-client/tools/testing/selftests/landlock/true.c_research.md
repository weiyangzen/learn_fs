# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/true.c

## Purpose

`true.c` is a tiny helper binary for Landlock tests that need an executable which succeeds without side effects.

## Important APIs, Types, and Functions

It defines only `int main(void)` and returns `0`. There are no external APIs, no Landlock calls, and no filesystem or process manipulation.

## Control Flow and State

The control flow is a single return statement. It creates no state and persists nothing.

## Dependencies and Integration Points

It integrates with tests that exec a known-success program, often to check behavior around exec transitions, mount layouts, or sandbox helper orchestration.

## Risks and Test Signals

The only meaningful risk is build or path failure. A successful invocation exits with status 0 and produces no output.
