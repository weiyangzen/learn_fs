# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-jtag.c

## Purpose
Supplies low-level QLM internal JTAG programming primitives through CIU CSRs.

## Important APIs, Types, And Functions
APIs are `cvmx_helper_qlm_jtag_init()`, `cvmx_helper_qlm_jtag_shift()`, `cvmx_helper_qlm_jtag_shift_zeros()`, and `cvmx_helper_qlm_jtag_update()`. They manipulate `CVMX_CIU_QLM_JTGC` and `CVMX_CIU_QLM_JTGD`.

## Control Flow
Initialization computes a clock divider from CPU frequency and configures bypass/select fields. Shift writes up to 32 bits, polls the shift bit clear, and returns shifted-out data. The zero helper chunks long zero runs. Update writes the update bit and polls completion.

## State, Persistence, And Dependencies
State is in the QLM JTAG chain and CIU JTAG CSRs. There is no locking; callers must serialize QLM programming.

## Integration Points
The errata module uses these helpers for CN52XX CDR workaround. Other QLM tuning paths can reuse them.

## Risks
Polling loops have no timeout. Invalid bit counts and concurrent use are unchecked. Comments warn that bad JTAG values may damage hardware.

## Test Signals
Check shift/update completion, expected shifted-out bits where observable, and successful downstream QLM link operation after programming.
