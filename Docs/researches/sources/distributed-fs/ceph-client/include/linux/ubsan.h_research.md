# sources/distributed-fs/ceph-client/include/linux/ubsan.h

## Purpose
Declares a helper for reporting UBSAN failure descriptions when trap or KVM EL2 UBSAN handling is enabled.

## Important APIs, Types, And Functions
Exports `report_ubsan_failure(u32 check_type)` under `CONFIG_UBSAN_TRAP` or `CONFIG_UBSAN_KVM_EL2`; otherwise an inline stub returns `NULL`.

## Control Flow
Callers pass a UBSAN check type and receive a string description when supported. Disabled configs return no description.

## State, Persistence, And Dependencies
No state is stored. It depends on base `u32` visibility from including context.

## Integration Points
Used by UBSAN trap/reporting paths, including hypervisor/EL2 contexts that need compact failure reporting.

## Risks And Test Signals
Risks include missing declarations when callers assume a string is always available, and unsupported check types returning unexpected values in implementations. Test signals include UBSAN trap tests, KVM EL2 build coverage, and disabled-config compile tests.
