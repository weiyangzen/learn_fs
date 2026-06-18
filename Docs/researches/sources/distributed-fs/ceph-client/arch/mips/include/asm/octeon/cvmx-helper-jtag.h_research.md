# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-jtag.h

## Purpose
`cvmx-helper-jtag.h` declares QLM JTAG utilities used by Octeon helper code to initialize, shift, and update serial configuration state in QLM blocks. It is a low-level support interface for serdes/QLM tuning rather than a packet I/O API.

## Important APIs, Types, And Functions
The exported calls are `cvmx_helper_qlm_jtag_init()`, `cvmx_helper_qlm_jtag_shift(int qlm, int bits, uint32_t data)`, `cvmx_helper_qlm_jtag_shift_zeros(int qlm, int bits)`, and `cvmx_helper_qlm_jtag_update(int qlm)`. The shift function returns shifted-out data, letting callers read or verify QLM scan-chain state.

## Control Flow
Typical use is initialize the JTAG helper, shift a command or field sequence into a selected QLM, optionally shift zeros for padding, then issue update to latch the scan-chain value into live QLM controls. The header itself contains only declarations.

## State And Persistence
State is the QLM JTAG scan chain and latched QLM hardware configuration. Partial shifts are order-dependent and persist in the scan chain until completed or reset. No C storage is defined here.

## Dependencies And Integration Points
The functions integrate with QLM errata workarounds, SGMII/XAUI lane configuration, and any helper code that cannot configure QLM behavior through ordinary CSRs. They depend on Octeon low-level register access and correct model-specific scan-chain layout in the implementation.

## Risks
Wrong bit counts or QLM indexes can leave a lane group in a bad analog state. Because shifting is sequential, interrupted or reordered calls can corrupt configuration. Tests must account for silicon revisions with different scan-chain fields.

## Test Signals
Useful validation includes readback from `cvmx_helper_qlm_jtag_shift`, successful link training after update, idempotent init/update sequences, and regression coverage for every QLM index present on the target model.
