<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/config

## Purpose
Kernel configuration fragment for mseal system mapping selftests.

## Important APIs, Types, and Functions
- Requires `CONFIG_MSEAL_SYSTEM_MAPPINGS=y`.

## Control Flow
No executable flow; consumed by kselftest config tooling.

## State and Persistence Behavior
Static metadata only.

## Dependencies and Integration Points
Supports the `sysmap_is_sealed` test built by the directory makefile.

## Risks and Edge Cases
If the kernel lacks system mapping mseal support, the runtime test cannot validate the intended behavior.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/config -->
