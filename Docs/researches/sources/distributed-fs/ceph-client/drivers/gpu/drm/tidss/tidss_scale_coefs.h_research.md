# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.h

## Purpose

`tidss_scale_coefs.h` declares the scaler coefficient data shape and lookup function used by the TIDSS DISPC scaler.

## Important APIs, Types, and Functions

- `struct tidss_scale_coefs` stores `c2[16]`, `c1[16]`, and `c0[9]` coefficient arrays matching the hardware phase layout.
- `tidss_get_scale_coefs()` returns a const table for a FIR increment and 3-tap/5-tap choice.

## Control Flow

`tidss_dispc.c` includes this header, obtains coefficient tables during scaling calculations, and writes the arrays into DISPC FIR coefficient registers.

## State and Persistence Behavior

The header has no state. Returned coefficient tables are immutable static data in the implementation.

## Dependencies and Integration Points

It includes Linux types and forward declares `struct device` for error logging in the lookup function. It is a narrow interface between scaler math and coefficient storage.

## Risks and Edge Cases

- Array sizes must stay synchronized with hardware writer loops: 16 phases for `c1/c2` and 9 entries for `c0`.
- No metadata identifies which ratio bucket was chosen; callers can only observe pointer identity or logs.

## Test Signals

Build tests should catch struct-size mismatches with writer code. Runtime tests should verify coefficient lookup never returns NULL for all ratios accepted by `dispc_plane_check()`.
