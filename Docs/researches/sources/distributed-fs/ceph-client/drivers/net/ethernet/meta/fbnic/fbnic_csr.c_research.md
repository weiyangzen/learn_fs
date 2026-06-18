# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.c

## Purpose

`fbnic_csr.c` implements fbnic CSR register dumping and register self-test logic. It provides ethtool/debug style register snapshots across normal CSR sections and RPC RAM, calculates dump length, and validates selected queue registers by writing known patterns and checking writable/read-only bit behavior.

## Important APIs, Types, And Functions

`struct fbnic_csr_bounds` describes start/end register ranges. `fbnic_csr_sects[]` lists CSR sections to dump, including interrupt, queue manager, TCE, TMI, PTP, RXB, RPC, fabric, master, PCS, RSFEC, MAC, signal, PCIe, PUL, queue, and RPC RAM. `fbnic_csr_get_regs()` writes a version and a sequence of section start/end markers plus register values into a caller-supplied buffer. `fbnic_csr_regs_len()` returns the expected u32 count including two marker words per section.

`fbnic_csr_get_regs_rpc_ram()` handles RPC RAM specially because it is not linearly dumped; it iterates TCAM action, MACDA, outer/inner IP source/destination tables, and RSS table entries through indexed register macros. `struct fbnic_csr_reg_test_data` and `pattern_test[]` define queue register self-test targets, strides, array lengths, readable masks, and writable masks. `fbnic_csr_regs_test()` runs the pattern test across all described queue instances.

## Control Flow

Register dumping skips the final RPC_RAM section in the linear loop, dumps all ordinary sections by reading every CSR between start and end, then appends the special RPC_RAM dump. A `WARN_ON` verifies that the number of u32s written matches `fbnic_csr_regs_len()`.

The self-test loops over each register descriptor and each array index, computes the actual register address from base plus stride, writes patterns `~0`, `0x5A5A5A5A`, `0xA5A5A5A5`, and `0`, masks expected values by readable/writable masks, reads back, logs an error on mismatch, and returns the failing register number. Success returns `FBNIC_REG_TEST_SUCCESS`.

## State And Persistence

The file does not own persistent state. It reads and writes hardware CSRs through the `fbnic_dev` accessors. The self-test intentionally mutates queue-related registers and is documented for offline use where reset after test can restore device state.

## Dependencies And Integration Points

It depends on `fbnic.h` for accessors and device logging, and on generated CSR macros from `fbnic_csr.h`. It integrates with ethtool register dump and driver self-test paths declared in `fbnic.h`.

## Risks And Edge Cases

The dump length must stay synchronized with section bounds and RPC RAM table dimensions; mismatches trigger `WARN_ON` and can corrupt caller expectations. RPC RAM table constants duplicate hardware dimensions and must track CSR macro definitions. The register self-test writes to hardware and should only run when the interface is offline and reset afterward. A failure on register offset zero would be ambiguous with success, but the code documents that such a register is not included.

## Test Signals

Useful tests include ethtool register dump length/version validation, RPC RAM dump coverage, self-test success on known-good offline hardware, intentional fault or mask mismatch detection, and ensuring reset restores queue registers after test. No local executable tests were run for this research item.
