# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Makefile

## Purpose
Maps Qualcomm pinctrl Kconfig symbols to the corresponding driver objects.

## Important APIs, Types, And Functions
Build rules cover the common `pinctrl-msm.o`, many TLMM SoC drivers, PMIC SPMI/SSBI GPIO and MPP drivers, LPASS LPI core and variants, `tlmm-test.o`, and newer platform objects such as `pinctrl-qcs8300.o`, `pinctrl-milos.o`, and `pinctrl-sm8750.o`.

## Control Flow
Kbuild includes each object when its `CONFIG_PINCTRL_*` symbol is enabled. Shared symbols can build multiple objects, for example SPMI PMIC builds both GPIO and MPP drivers.

## State And Persistence
The file controls build artifacts only. It does not create runtime state directly.

## Dependencies And Integration Points
Must stay in sync with `qcom/Kconfig` and `qcom/Kconfig.msm`, source filenames, and module expectations. It integrates TLMM, PMIC, LPASS, and test drivers into the pinctrl subsystem build.

## Risks
Missing or stale object mappings produce configured-but-unbuilt drivers or build failures. Formatting inconsistencies are low risk but make new entries harder to audit. Shared Kconfig symbols that build multiple objects must preserve both pieces.

## Test Signals
Build with representative Qualcomm symbols enabled as modules and built-ins, run `allmodconfig`, and verify every Kconfig symbol has a matching object when expected.
