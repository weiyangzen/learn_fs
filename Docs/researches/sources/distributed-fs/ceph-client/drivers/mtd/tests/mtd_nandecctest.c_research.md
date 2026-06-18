# sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_nandecctest.c

## Purpose
Self-tests software Hamming NAND ECC correction/detection logic without requiring an MTD device. It covers no-error, correctable single-bit data/ECC errors, and detectable double-bit scenarios for 256-byte and 512-byte data blocks.

## Important APIs, Types, and Functions
`struct nand_ecc_test` defines each prepare/verify pair. Error injection helpers include `single_bit_error_data()`, `double_bit_error_data()`, `single_bit_error_ecc()`, and `double_bit_error_ecc()`. Verification uses `ecc_sw_hamming_calculate()` and `ecc_sw_hamming_correct()`. `nand_ecc_test_run()` allocates buffers, generates random data, runs `nand_ecc_test[]`, and dumps diagnostic data on failure.

## Control Flow
`ecc_test_init()` runs the suite for 256 and 512 byte blocks. For each case the module generates correct data/ECC, applies a prepared corruption pattern, recalculates ECC, checks whether correction returns the expected code, and verifies data contents. If raw NAND support is disabled, the run function is stubbed to success.

## State and Persistence
No flash state is touched. Runtime buffers are allocated per test run and freed before returning. Random data and random bit positions make coverage variable across loads.

## Dependencies and Integration Points
It depends on `CONFIG_MTD_RAW_NAND`, `CONFIG_MTD_NAND_ECC_SW_HAMMING_SMC`, the NAND ECC software Hamming implementation, kernel random APIs, and `mtdtest_relax()`.

## Risks
Randomized bit positions can make exact failures non-reproducible unless logs are captured. The test only covers Hamming ECC behavior and not controller-specific ECC engines or real OOB layouts.

## Test Signals
Loading the module should print `ok` lines for each case/size. Failures dump corrupted and correct data/ECC buffers and return an error from module init.
