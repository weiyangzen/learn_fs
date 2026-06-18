# sources/distributed-fs/ceph/src/rgw/rgw_account.h

## Purpose
Declares RGW account admin helper functions and the `AdminOpState` parameter bundle used by account command handlers.

## Important APIs, Types, and Functions
- `AdminOpState` holds lookup keys, tenant/name/email updates, account limits, quota updates, and `purge_data`.
- Declares lifecycle operations: `create`, `modify`, `remove`, `info`, `stats`, and `list_users`.
- Declares validation helpers and `root_arn()`.

## Control Flow
No implementation flow is present. The header defines operation contracts that accept `DoutPrefixProvider`, SAL driver, formatter, yield context, and error-message outputs.

## State and Persistence
The header itself stores no state. `AdminOpState` is transient command state that drives persistent SAL operations in the implementation.

## Dependencies and Integration Points
Uses `std::optional` for optional numeric/bool updates, forwards the SAL driver and ARN type, and integrates with Ceph formatter/yield conventions.

## Risks and Edge Cases
Because many fields are optional, callers must distinguish unspecified values from explicit zero/false values. `purge_data` is a high-risk switch that changes `remove()` from validation-only to destructive cascade.

## Test Signals
Compile/API tests should catch signature changes. Admin command tests should verify correct `AdminOpState` population for every CLI/REST option, especially false quota-enabled values and purge behavior.
