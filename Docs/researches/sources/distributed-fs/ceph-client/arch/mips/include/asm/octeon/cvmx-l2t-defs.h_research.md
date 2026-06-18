# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2t-defs.h

## Purpose
`cvmx-l2t-defs.h` maps the Octeon L2 tag array error CSR. It exposes ECC enable/status, lock-error reporting, failed address/set/syndrome fields, and model-specific field widths for older Octeon families.

## Important APIs, Types, And Functions
The sole address macro is `CVMX_L2T_ERR`. `union cvmx_l2t_err` contains generic fields `ecc_ena`, single/double-error interrupt enables and status, syndrome, failed address/set, lock error bits, second lock-error bits, and `fadru`. It also provides model-specific layouts for CN30XX, CN31XX, CN38XX, CN50XX, and CN52XX where failed address and set widths differ.

## Control Flow
The header has no functions. Platform code reads this CSR during ECC or lock-error interrupts, decodes the model-appropriate union view, and writes back as required to clear latches or control interrupt enables.

## State And Persistence
Persistent state is the L2 tag ECC enable, interrupt enables, and latched tag/lock error information. The reported failed address and syndrome are hardware-captured until cleared or overwritten by later faults.

## Dependencies And Integration Points
It includes `<uapi/asm/bitfield.h>`. It integrates with L2 cache error handling, lock/unlock routines from `cvmx-l2c.h`, and platform RAS diagnostics.

## Risks
Using the generic layout on older chips with different field widths can misreport the failing address or set. Lock-error fields are coupled to cache-lock operations and may be triggered by unsafe concurrent debug/lock use. Clearing status without logging loses important failure information.

## Test Signals
Validate boot ECC enable state, interrupt enable behavior, model-specific field decoding, lock-error reporting for forced invalid operations, and ECC syndrome/address logging through injected or simulated tag faults.
