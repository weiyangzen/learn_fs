# sources/distributed-fs/ceph-client/include/linux/atmel-isc-media.h

## Purpose
Defines custom V4L2 control IDs for Microchip/Atmel ISC white-balance gain and offset controls.

## Important APIs, Types, And Functions
`enum atmel_isc_ctrl_id` allocates four gain controls for R, B, GR, and GB Bayer components and four offset controls for the same components starting at `V4L2_CID_USER_ATMEL_ISC_BASE`.

## Control Flow, State, And Persistence
The comments describe control semantics: auto white balance clusters the controls, AWB-on makes manual controls inactive but volatile/readable, AWB-off allows manual gain/offset, and a one-shot white-balance action can update coefficients. The header itself only assigns IDs; control state lives in the ISC V4L2 driver.

## Dependencies And Integration Points
Requires V4L2 control base definitions in including code. Integrated by the Atmel ISC media driver and userspace V4L2 control APIs.

## Risks And Test Signals
Control ID mismatch breaks userspace ABI. Tests should verify V4L2 control enumeration, AWB auto/manual cluster behavior, volatile reads, one-shot white balance update, value ranges/formats, and persistence of saved coefficients across driver reload where userspace restores them.
