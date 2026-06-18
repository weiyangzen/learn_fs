# sources/distributed-fs/ceph/src/rgw/rgw_s3select.h

## Purpose
`rgw_s3select.h` is the minimal public factory header for RGW S3 Select. It hides the concrete implementation class in `rgw_s3select_private.h` and exposes a single operation factory.

## Important APIs, Types, and Functions
The only declaration is `rgw::s3select::create_s3select_op()`, returning an `RGWOp*`. The implementation allocates `RGWSelectObj_ObjStore_S3`, which derives from the S3 GET object operation.

## Control Flow
REST routing code can include this header and call the factory when dispatching SelectObjectContent, without depending on the private class definition or the external s3select engine headers.

## State and Persistence Behavior
The header declares no state and no persistence. Ownership of the returned raw pointer follows existing RGW operation allocation conventions.

## Dependencies and Integration Points
The declaration depends on `RGWOp` being visible before inclusion. It integrates with S3 REST operation registration and keeps heavy select dependencies out of broader compile units.

## Risks
Because the function returns a raw pointer and the header does not include the `RGWOp` definition, callers must include it in the correct context and manage operation lifetime according to RGW conventions.

## Test Signals
Build tests should verify the factory is visible to REST dispatch code. Runtime tests should confirm the returned op executes SelectObjectContent rather than normal GET behavior.
