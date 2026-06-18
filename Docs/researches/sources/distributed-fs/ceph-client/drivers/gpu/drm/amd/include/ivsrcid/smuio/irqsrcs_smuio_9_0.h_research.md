# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/smuio/irqsrcs_smuio_9_0.h

## Purpose
Declares the SMUIO 9.0 source ID for the GPIO19 interrupt. It is a one-entry hardware source map.

## Important APIs, Types, and Functions
No functions, types, or enums are present. The only exported macro is `SMUIO_9_0__SRCID__SMUIO_GPIO19` with value `83`.

## Control Flow
The file has no executable flow. It influences control flow when interrupt decoding code compares an IH packet source ID with `83` and dispatches SMUIO GPIO handling.

## State and Persistence
There is no state. The value is a build-time hardware constant.

## Dependencies and Integration Points
The include guard is the only local dependency. Integration points are SMUIO interrupt registration and platform GPIO interrupt handling.

## Risks and Test Signals
Risk is low but numeric correctness is critical. Validation should confirm GPIO19 events on SMUIO 9.0 arrive as source ID `83` and do not collide with another registered block source.
