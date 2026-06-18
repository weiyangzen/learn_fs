# sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/Kconfig

## Purpose
This Kconfig entry controls the Intel MEI PXP client driver, which supplies Protected Xe Path services for Intel graphics through the ME firmware interface.

## Important APIs, types, and functions
It defines `CONFIG_INTEL_MEI_PXP` as a tristate option named "Intel PXP services of ME Interface". It depends on `INTEL_MEI_ME` and on at least one Intel graphics stack being enabled (`DRM_I915!=n` or `DRM_XE!=n`) or `COMPILE_TEST`.

## Control flow and state
There is no runtime flow. Build selection determines whether `mei_pxp.o` can be compiled and loaded.

## State and persistence behavior
No runtime state or persistence exists in this file. It influences build configuration only.

## Dependencies and integration points
The option integrates with the MEI ME transport and Intel graphics drivers. The `COMPILE_TEST` allowance lets broader build testing cover the driver without a full graphics runtime.

## Risks and test signals
Risks are incorrect dependency gating causing unresolved symbols or missing PXP support. Test signals are allmodconfig/allyesconfig builds, `COMPILE_TEST` builds, and configurations with i915 or Xe enabled as modules or built-ins.
