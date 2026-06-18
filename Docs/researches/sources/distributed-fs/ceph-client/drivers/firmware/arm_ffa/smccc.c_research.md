# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/smccc.c

## Purpose
Provides the FF-A transport initializer for SMCCC conduits. It selects whether FF-A calls should use SMC or HVC based on firmware-reported SMCCC conduit information.

## APIs, Types, And Functions
Defines private wrappers `__arm_ffa_fn_smc()` and `__arm_ffa_fn_hvc()` around `arm_smccc_1_2_smc()` and `arm_smccc_1_2_hvc()`. Implements `ffa_transport_init(ffa_fn **invoke_ffa_fn)`.

## Control Flow
Initialization checks for SMCCC v1.2 or newer, asks for the SMCCC conduit, rejects `SMCCC_CONDUIT_NONE`, and stores the appropriate wrapper function pointer for the FF-A driver to call.

## State, Persistence, And Dependencies
No persistent state is owned here; the selected function pointer is stored by the caller. Dependencies are SMCCC v1.2 register ABI and conduit discovery.

## Integration Points
`driver.c` calls `ffa_transport_init()` before any FF-A ABI call. The function is built only when `CONFIG_ARM_FFA_SMCCC` enables this transport.

## Risks And Test Signals
Risks are incorrect conduit selection or running on firmware without SMCCC v1.2 support. Test signals are FF-A driver initialization success on SMC and HVC systems and graceful `-EOPNOTSUPP` on unsupported systems.
