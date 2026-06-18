# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/stubs.S

## Purpose
Supplies no-op helper symbols needed by copied copy-user loops.

## Important APIs, Types, and Functions
Defines `enter_vmx_ops`, `exit_vmx_ops`, and `__copy_tofrom_user_base` as immediate-return functions.

## Control Flow
There is no operational control flow beyond `blr` returns.

## State and Persistence
No state is persisted or intentionally modified.

## Dependencies and Integration Points
Included in validation link sets to satisfy kernel helper references outside the tested code path.

## Risks and Test Signals
Risk is accidental execution of a no-op helper hiding missing behavior; validation mismatches or missing VMX setup would reveal issues.
