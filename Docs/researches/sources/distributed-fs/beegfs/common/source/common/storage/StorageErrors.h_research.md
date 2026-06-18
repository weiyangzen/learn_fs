# sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.h

## Purpose
Declares BeeGFS operation error codes, their mapping table type, conversion toolkit, serialization width, and vector typedefs.

## Important APIs, Types, And Functions
`FhgfsOpsErrListEntry`, `FhgfsOpsErr`, `SerializeAs<FhgfsOpsErr>`, `FhgfsOpsErrTk`, and stream operator declaration are exported.

## Control Flow
No implementation logic in the header beyond table-size macro and constructors being private for toolkit class.

## State, Persistence, And Dependencies
The enum is signed via a negative dummy to avoid bad casts from negative return values. It must stay in sync with the client module and `__FHGFSOPS_ERRLIST`.

## Integration Points
Used almost everywhere an operation can return BeeGFS-level status.

## Risks
Adding/reordering errors is protocol-visible and must update both table and client module. Serializes as `int`.

## Test Signals
Compile-time/table-size checks, client sync, and serialization of negative dummy avoidance should be covered.
