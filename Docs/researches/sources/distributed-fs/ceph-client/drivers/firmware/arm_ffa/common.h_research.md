# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/common.h

## Purpose
Shared private header for FF-A bus, driver, and transport code. It centralizes FF-A call ABI typing, local helper prototypes, and the optional transport-init interface.

## APIs, Types, And Functions
Defines `ffa_value_t` as `struct arm_smccc_1_2_regs` and `ffa_fn` as the function-pointer type used for FF-A calls. Declares `ffa_device_is_valid()`, `ffa_device_match_uuid()`, and `ffa_transport_init()`. When `CONFIG_ARM_FFA_SMCCC` is disabled, `ffa_transport_init()` is an inline stub returning `-EOPNOTSUPP`.

## Control Flow
Consumers include this header to obtain a transport-specific `invoke_ffa_fn` pointer during FF-A driver init, or to use bus helper functions. Compile-time `#ifdef CONFIG_ARM_FFA_SMCCC` selects the real transport initializer or stub.

## State, Persistence, And Dependencies
No state is stored in the header. It depends on public FF-A, SMCCC, and errno definitions.

## Integration Points
`smccc.c` implements the real `ffa_transport_init()`, `driver.c` calls it during `ffa_init()`, and `bus.c` shares the device validation and UUID matching declarations.

## Risks And Test Signals
The main risk is ABI mismatch in `ffa_value_t` or missing transport support causing FF-A init failure. Build tests with `CONFIG_ARM_FFA_SMCCC` enabled and disabled validate the conditional declarations.
