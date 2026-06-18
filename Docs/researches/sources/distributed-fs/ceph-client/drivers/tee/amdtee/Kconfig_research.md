# sources/distributed-fs/ceph-client/drivers/tee/amdtee/Kconfig

## Purpose
Declares the AMD-TEE backend configuration option.

## Important APIs, Types, and Constants
`config AMDTEE` is a tristate named "AMD-TEE", defaults to module, and depends on `CRYPTO_DEV_SP_PSP` plus `CRYPTO_DEV_CCP_DD`. Its help text identifies it as AMD's TEE driver.

## Control Flow and State
No runtime flow. This option controls whether `drivers/tee/amdtee/` objects are built.

## Dependencies and Integration Points
Integrates AMDTEE with the AMD Secure Processor/PSP and CCP driver stack. It is sourced by the top-level TEE Kconfig only when `TEE` is enabled.

## Risks and Test Signals
Defaulting to module can expose build/link issues on systems with PSP/CCP enabled. Test signals are Kconfig dependency resolution for AMD and COMPILE_TEST builds, successful module builds, and backend probe only when required PSP services exist.
