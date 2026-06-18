# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c-defs.h

## Purpose
`cvmx-l2c-defs.h` maps Octeon L2 cache controller CSRs for configuration, debugging, performance counters, way partitioning, lock address windows, and tag/data ECC error reporting.

## Important APIs, Types, And Functions
Address macros include `CVMX_L2C_CFG`, `CVMX_L2C_CTL`, `CVMX_L2C_DBG`, `CVMX_L2C_PFCTL`, `CVMX_L2C_PFCX`, `CVMX_L2C_TADX_PFCX`, `CVMX_L2C_TADX_PRF`, `CVMX_L2C_TADX_TAG`, `CVMX_L2C_ERR_TDTX`, `CVMX_L2C_ERR_TTGX`, `CVMX_L2C_WPAR_PPX`, `CVMX_L2C_WPAR_IOBX`, `CVMX_L2C_LCKBASE`, and `CVMX_L2C_LCKOFF`. Unions expose ECC single/double-bit status and syndrome, cache controller config/control, debug selector fields, performance counter selection/enable/clear, tag state, and lock window base/offset.

## Control Flow
There are no runtime functions. L2C helper implementations use these definitions to configure counters, partition ways, inspect tags, lock or unlock regions, and manipulate debug flush features.

## State And Persistence
Persistent state is hardware L2 controller state: performance counter configuration and counts, cache policy/control bits, way partition masks, lock windows, and ECC error latches. The header itself has no data.

## Dependencies And Integration Points
It uses `<uapi/asm/bitfield.h>` and `CVMX_ADD_IO_SEG`. It is consumed by `cvmx-l2c.h` implementations, cache/ECC error handlers, low-level platform initialization, and performance monitoring.

## Risks
Debug and lock registers affect global cache behavior and are not generally safe for concurrent use. Wrong partition masks can starve cores or hardware blocks of evictable ways. ECC status interpretation depends on TAD/block IDs and model-specific geometry.

## Test Signals
Validate performance counter event selection and clear-on-read behavior, way partition readback, lock/unlock operations on test memory, controlled flush behavior, and ECC interrupt/status paths using injected or simulated errors where possible.
