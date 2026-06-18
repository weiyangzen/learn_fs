# sources/distributed-fs/ceph-client/include/linux/fault-inject-usercopy.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fault-inject-usercopy.h` exposes a tiny wrapper for injecting failures into user memory copy paths. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

The main API is `should_fail_usercopy()`. With `CONFIG_FAULT_INJECTION_USERCOPY` it is an external function; otherwise it is a static inline returning `false`.

## Control Flow

Callers in usercopy paths invoke `should_fail_usercopy()` before or during copy operations. Disabled builds compile the branch away to a constant no-fail result.

## State and Persistence Behavior

The header owns no state. Fault policy is owned by the fault injection subsystem when enabled.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with hardened/usercopy and fault-injection debug/config control points.

## Risks and Edge Cases

Enabled tests must avoid leaking synthetic failures into production configurations. Disabled stubs should keep call sites buildable without altering behavior.

## Test Signals

Fault-injection KUnit or selftests that force usercopy failures, plus allnoconfig/tinyconfig builds verifying the stub path.
