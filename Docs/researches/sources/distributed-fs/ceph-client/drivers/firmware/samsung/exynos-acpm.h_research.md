# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.h

## Purpose
This private header defines the ACPM transfer descriptor and declares the core synchronous transfer function used by PMIC and DVFS helpers.

## Important APIs And Types
- `struct acpm_xfer` contains counted TX/RX word pointers, TX/RX word counts, and ACPM channel ID.
- `struct acpm_handle` is forward declared.
- `int acpm_do_xfer(struct acpm_handle *handle, const struct acpm_xfer *xfer);`

## Control Flow And Integration
Helper modules build `acpm_xfer` structures and pass them to `acpm_do_xfer()` in `exynos-acpm.c`. Public clients use ops stored in `struct acpm_handle`, not this private header directly.

## State And Persistence
The header owns no state. `acpm_xfer` is per-call state whose buffers must remain valid for the synchronous transfer.

## Risks
The counted pointer annotations document buffer sizes but runtime validation still depends on the core checking counts against channel message length.

## Test Signals
Compile-time type checking of PMIC/DVFS helpers and successful synchronous transfers validate this interface.
