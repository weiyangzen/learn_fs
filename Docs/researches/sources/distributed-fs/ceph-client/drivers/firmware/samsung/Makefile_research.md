# sources/distributed-fs/ceph-client/drivers/firmware/samsung/Makefile

## Purpose
The Makefile builds the Samsung ACPM protocol as a composite object.

## Important Build Rules
- `acpm-protocol-objs := exynos-acpm.o`
- Adds `exynos-acpm-pmic.o` and `exynos-acpm-dvfs.o`.
- `obj-$(CONFIG_EXYNOS_ACPM_PROTOCOL) += acpm-protocol.o`

## Control Flow And Integration
The core queue/mailbox driver and PMIC/DVFS command helpers are linked together when ACPM protocol support is enabled, making the ops table in `exynos-acpm.c` able to reference both helper modules.

## State And Persistence
No runtime state; linkage only.

## Risks
Removing helper objects would break ops setup or leave clients without PMIC/DVFS operations.

## Test Signals
Successful build should produce the composite `acpm-protocol` object and resolve `acpm_pmic_*` and `acpm_dvfs_*` references.
