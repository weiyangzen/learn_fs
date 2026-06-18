# sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/config

## Purpose
Kselftest configuration fragment declaring that the TDX guest driver is required.

## Important APIs, Types, and Functions
Contains `CONFIG_TDX_GUEST_DRIVER=y`.

## Control Flow
There is no executable flow. Kselftest/config tooling can use the fragment to identify kernel config requirements.

## State and Persistence Behavior
Static build/runtime requirement only; no state is modified.

## Dependencies and Integration Points
Integrates with kernel selftest config aggregation and the TDX guest test that opens `/dev/tdx_guest`.

## Risks and Edge Cases
The option being present is necessary but not sufficient; the system must also be running as a TDX guest with the device node available.

## Test Signals
Signal is kernel config coverage for `CONFIG_TDX_GUEST_DRIVER=y`.
