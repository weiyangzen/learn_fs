# sources/distributed-fs/ceph-client/drivers/acpi/arm64/thermal_cpufreq.c

## Purpose
Provides an ARM64 ACPI hook for platform-specific thermal CPU frequency reduction percentage.

## Important APIs, Types, And Functions
Exports `acpi_arch_thermal_cpufreq_pctg()`. It compares the SMCCC SoC ID against `SMCCC_SOC_ID_T241`.

## Control Flow
The function reads `arm_smccc_get_soc_id_version()`. If the SoC is NVIDIA Tegra241, it returns `5`; otherwise it returns `0` to use default policy.

## State And Persistence
No local state.

## Dependencies And Integration Points
Depends on ARM SMCCC SoC ID support and is consumed by ACPI thermal/cpufreq code through the exported symbol.

## Risks
If SMCCC SoC ID is unavailable or changes encoding, the override is skipped. Hard-coded platform matching must remain narrow to avoid affecting unrelated systems.

## Test Signals
Mock or boot-test Tegra241 SoC ID, non-Tegra IDs, unavailable SMCCC ID behavior, and thermal cpufreq policy use of the returned percentage.
