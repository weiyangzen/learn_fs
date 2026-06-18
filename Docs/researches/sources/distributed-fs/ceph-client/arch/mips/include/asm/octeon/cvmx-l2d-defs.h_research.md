# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2d-defs.h

## Purpose
`cvmx-l2d-defs.h` defines the small CSR set for the Octeon L2 data array error and fuse/control state. It is part of the broader L2 cache diagnostics surface.

## Important APIs, Types, And Functions
The address macros are `CVMX_L2D_ERR` and `CVMX_L2D_FUS3`. `union cvmx_l2d_err` exposes ECC enable, single-error interrupt enable/status, double-error interrupt enable/status, and a BMH selector bit. `union cvmx_l2d_fus3` exposes `ema_ctl` and a fuse field `q3fus`.

## Control Flow
There is no executable code. Error handlers and initialization code read or write these CSRs through generic CSR accessors.

## State And Persistence
State is hardware error latch, interrupt enable, ECC enable, and fuse/control state. Changing ECC enable or fuse-related controls affects L2 data-array behavior until reset or reprogramming.

## Dependencies And Integration Points
The unions use `__BITFIELD_FIELD`, so callers must include the bitfield macro environment through surrounding headers. The file integrates with L2 cache ECC handling, boot diagnostics, and cache-controller initialization.

## Risks
Disabling ECC or clearing error bits incorrectly can hide real data-array faults. Fuse/control fields are hardware-specific and should not be modified without model documentation. Error status handling must coordinate with L2T/L2C error sources.

## Test Signals
Test signals include expected ECC enable state at boot, correct interrupt delivery for injected single/double-bit data errors, stable readback of `CVMX_L2D_ERR`, and no unexpected changes to fuse/control fields during normal cache operations.
