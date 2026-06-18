# sources/distributed-fs/ceph-client/include/linux/kobject_api.h

## Purpose

`kobject_api.h` is a one-line compatibility/include-forwarding header for the kobject API. It simply includes `linux/kobject.h`. The source was read as a complete 1-line file.

## Important APIs, Types, and Functions

It directly exposes all declarations from `kobject.h`; no independent APIs or types are defined here.

## Control Flow

There is no local flow. Include processing forwards consumers to the main kobject header.

## State and Persistence Behavior

No state is owned by this file. Runtime behavior is entirely that of `kobject.h`.

## Dependencies and Integration Points

Its sole dependency and integration point is `linux/kobject.h`. It likely exists for include path compatibility with code expecting a `_api` wrapper.

## Risks and Edge Cases

The only meaningful risk is include-cycle or compatibility breakage if this forwarding header is removed or stops including `kobject.h`.

## Test Signals

Compile coverage for code including `linux/kobject_api.h` and include-order tests are sufficient.
