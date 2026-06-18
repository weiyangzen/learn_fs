# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.h

## Purpose

`i40e_diag.h` declares diagnostic loopback modes, register-test metadata, the exported register list, and public diagnostic test entry points for the i40e driver.

## Important APIs, Types, And Functions

- `enum i40e_lb_mode` maps no loopback and PHY/MAC local/remote loopback modes to AdminQ loopback constants.
- `struct i40e_diag_reg_test_info` describes a base register, safe test mask, element count, and stride.
- `extern const struct i40e_diag_reg_test_info i40e_reg_list[]` exports the diagnostic register list.
- `i40e_diag_reg_test()` and `i40e_diag_eeprom_test()` are the public diagnostic test functions.

## Control Flow

No control flow is implemented in the header. It defines the metadata contract consumed by `i40e_diag.c` and any diagnostic callers.

## State And Persistence

The header owns no state. It describes diagnostic inputs and exposes tests that read/write hardware or NVM state in the implementation.

## Dependencies And Integration Points

It includes `<linux/types.h>` and `i40e_adminq_cmd.h` for fixed-width types and AdminQ loopback constants. It forward-declares `struct i40e_hw` to avoid pulling in the full hardware definition.

## Risks

- Loopback enum values must remain aligned with AdminQ definitions.
- The register test info structure is tightly coupled to hardware register stride and mask semantics.

## Test Signals

Build coverage catches enum/prototype drift. Runtime coverage comes from diagnostics invoking `i40e_diag_reg_test()` and `i40e_diag_eeprom_test()` on real or mocked hardware.
