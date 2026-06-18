# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/Kconfig

## Purpose
This Kconfig fragment declares Marvell MVEBU pinctrl support symbols for the shared MVEBU core and SoC-specific drivers.

## Important APIs, Types, and Entries
- `PINCTRL_MVEBU` is the common bool selected by legacy MVEBU table drivers and selects `PINMUX` and `PINCONF`.
- SoC bools `PINCTRL_DOVE`, `PINCTRL_KIRKWOOD`, `PINCTRL_ARMADA_370`, `PINCTRL_ARMADA_375`, `PINCTRL_ARMADA_38X`, `PINCTRL_ARMADA_39X`, `PINCTRL_ARMADA_AP806`, `PINCTRL_ARMADA_CP110`, `PINCTRL_ARMADA_XP`, `PINCTRL_ORION`, and `PINCTRL_AC5` select `PINCTRL_MVEBU`; Dove also selects `MFD_SYSCON`.
- `PINCTRL_ARMADA_37XX` is separate and selects `GENERIC_PINCONF`, `MFD_SYSCON`, `PINCONF`, and `PINMUX`.

## Control Flow
No runtime control flow exists. These symbols decide which objects Kbuild compiles and which frameworks are selected.

## State and Persistence
State is build configuration only. The bool symbols typically build the selected pinctrl drivers into the kernel image.

## Dependencies and Integration Points
The fragment integrates MVEBU platform/SoC symbols from architecture code with the local Makefile and shared pinctrl frameworks.

## Risks
Most SoC symbols have no explicit architecture or OF dependency in this fragment, so they are expected to be selected by platform Kconfig rather than manually configured. Armada 37xx bypasses `PINCTRL_MVEBU`, which is correct for its custom driver but means shared-core assumptions do not apply.

## Test Signals
Kernel config/build tests should verify each SoC symbol pulls in the right object and framework symbols. `COMPILE_TEST` coverage must come from parent Kconfig selections if desired.
