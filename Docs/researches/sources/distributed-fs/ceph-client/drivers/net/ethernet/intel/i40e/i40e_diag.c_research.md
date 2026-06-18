# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.c

## Purpose

`i40e_diag.c` implements low-level hardware diagnostics for selected registers and EEPROM/NVM validity. It is used by driver self-test paths to detect register access failures and invalid EEPROM checksum state.

## Important APIs, Types, And Functions

- `i40e_diag_reg_pattern_test()` writes a fixed pattern set through a mask, verifies reads, restores the original register value, and verifies restore.
- `i40e_reg_list[]` lists register offsets, writable/testable masks, element counts, and strides.
- `i40e_diag_reg_test()` iterates the register list and adapts element counts for dynamically allocated queues and MSI-X vectors.
- `i40e_diag_eeprom_test()` reads the NVM control word and validates checksum when the valid bit is set.

## Control Flow

Register testing loops over `i40e_reg_list[]` until the sentinel offset `0`. For queue/vector-backed registers, element counts are replaced with hardware capability values. Each selected register address is tested by writing `0x5A5A5A5A`, `0xA5A5A5A5`, zero, and all ones masked by the register’s safe mask, then restoring the original value. The first failure stops the scan and returns `-EIO`.

EEPROM testing reads `I40E_SR_NVM_CONTROL_WORD`; if the valid bit matches the expected control-word bit, it calls `i40e_validate_nvm_checksum()`, otherwise it returns `-EIO`.

## State And Persistence

The register test temporarily mutates hardware registers and attempts to restore their original values. EEPROM test reads NVM state and checksum but does not write persistent state. Diagnostic failures are logged through `i40e_debug()` when the diagnostic debug mask is enabled.

## Dependencies And Integration Points

The file depends on `i40e_diag.h`, `i40e_prototype.h`, register macros, hardware capability fields, `rd32()`/`wr32()`, NVM helpers, and debug logging. It is typically reached from ethtool self-test or internal diagnostic paths.

## Risks

- Register pattern tests are intrusive and should run only when hardware state can tolerate temporary writes.
- Masks must remain accurate; testing reserved or side-effect bits can destabilize hardware.
- Dynamic element calculation uses `num_msix_vectors - 1`, so zero is guarded but off-by-one behavior should match hardware vector layout.
- A failed restore leaves hardware in an unexpected state and reports `-EIO`.

## Test Signals

Run ethtool offline diagnostics on supported hardware, inject mocked `rd32()` mismatches for failure paths, verify masks against hardware documentation, and test EEPROM invalid control word and checksum failure cases.
