# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-errata.c

## Purpose
Applies the CN52XX pass 1 erratum workaround for broken second-order CDR by programming QLM JTAG lane fields.

## Important APIs, Types, And Functions
The exported `__cvmx_helper_errata_qlm_disable_2nd_order_cdr(int qlm)` uses the QLM JTAG helpers to shift a 1072-bit image into four lanes.

## Control Flow
The function initializes QLM JTAG, then for each lane shifts zeros around `cfg_cdr_incx<67:64> = 3` and `cfg_cdr_secord<77> = 1`. It commits the full chain with `cvmx_helper_qlm_jtag_update()`.

## State, Persistence, And Dependencies
The programmed state persists in QLM hardware. There is no software state. Correctness depends on exact erratum bit positions and caller-side model gating.

## Integration Points
`cvmx_helper_initialize_packet_io_global()` invokes this for `OCTEON_CN52XX_PASS1_0` before packet I/O initialization.

## Risks
The function does not check chip model itself. Incorrect JTAG programming is explicitly dangerous and may damage hardware or break links.

## Test Signals
Confirm the function is only called on affected hardware, JTAG operations complete, and CN52XX pass 1 links initialize successfully afterward.
