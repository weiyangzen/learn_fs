<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timeriomem-rng.h -->
# sources/distributed-fs/ceph-client/include/linux/timeriomem-rng.h

## Purpose
defines platform data for timeriomem RNG devices that sample an MMIO register after a configured period.

## Important APIs, Types, and Functions
The file is 22 lines and exports these visible symbol families: types/enums `timeriomem_rng_data`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Platform code supplies register address, sampling period, quality estimate, and endianness through `timeriomem_rng_data`; the RNG driver polls the register and feeds hwrng output.

## State and Persistence Behavior
The structure is initialization data; runtime sampling state lives in the hwrng driver.

## Dependencies and Integration Points
It depends on IO memory pointers and hwrng platform-device registration. Direct includes are none.

## Risks and Edge Cases
Incorrect period or quality overstates entropy. Wrong endianness or MMIO address can return deterministic or unrelated data.

## Test Signals
Probe with platform data, verify MMIO reads in little/big-endian modes, run hwrng health/throughput tests, and check entropy quality configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timeriomem-rng.h -->
