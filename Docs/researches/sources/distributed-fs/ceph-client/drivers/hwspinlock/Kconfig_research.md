# sources/distributed-fs/ceph-client/drivers/hwspinlock/Kconfig

## Purpose
This Kconfig file defines the generic hardware spinlock framework menu and platform-provider options for OMAP, Qualcomm, Spreadtrum, STM32, and Allwinner sun6i-compatible hardware spinlock blocks.

## Important APIs, Types, And Functions
This is declarative Kconfig rather than C code. Key symbols are `HWSPINLOCK`, `HWSPINLOCK_OMAP`, `HWSPINLOCK_QCOM`, `HWSPINLOCK_SPRD`, `HWSPINLOCK_STM32`, and `HWSPINLOCK_SUN6I`.

## Control Flow
When `HWSPINLOCK` is enabled, the submenu exposes provider selections. Each provider has architecture or `COMPILE_TEST` dependencies. Qualcomm also selects `MFD_SYSCON`, matching its driver's ability to use syscon regmaps.

## State And Persistence
The file affects build-time configuration only. It does not create runtime state, but selected symbols determine which objects are linked and which modules can register hardware spinlock banks.

## Dependencies And Integration Points
The symbols gate the Makefile entries in the same directory. They also align with platform DT/SoC support: OMAP/TI, Qualcomm, Spreadtrum, STM32MP157, and Allwinner sun6i-class SoCs.

## Risks
- Missing architecture dependencies could expose drivers where required subsystems are unavailable.
- Too-strict dependencies could block useful compile testing or cross-platform builds.
- The core `HWSPINLOCK` is a bool, while providers are tristate, so module combinations depend on Kbuild behavior around built-in core versus modular providers.

## Test Signals
Run Kconfig matrix builds for each provider as built-in and module where allowed, plus `COMPILE_TEST`. Confirm Qualcomm pulls `MFD_SYSCON`, and that disabling `HWSPINLOCK` hides all provider options and omits the core object.
