# sources/distributed-fs/ceph-client/drivers/acpi/Kconfig

## Purpose
This Kconfig file defines the ACPI subsystem feature matrix: global ACPI enablement, debugger and table features, power-management pieces, bus/device drivers, platform-specific helpers, and exported ACPI table/opregion options.

## Important APIs, Types, And Functions
Important symbols in this file include `ACPI`, `ACPI_DEBUGGER`, `ACPI_DEBUGGER_USER`, `ACPI_SPCR_TABLE`, `ACPI_FPDT`, `ACPI_LPIT`, `ACPI_SLEEP`, `ACPI_EC`, `ACPI_AC`, `ACPI_BATTERY`, `ACPI_BUTTON`, `ACPI_TAD`, `ACPI_PROCESSOR`, `ACPI_IPMI`, `ACPI_HOTPLUG_CPU`, `ACPI_PROCESSOR_AGGREGATOR`, `ACPI_THERMAL`, `ACPI_TABLE_UPGRADE`, `ACPI_CONFIGFS`, `ACPI_EXTLOG`, `ACPI_ADXL`, `ACPI_PCC`, `ACPI_FFH`, `ACPI_MRRM`, and `X86_PM_TIMER`. It also sources nested ACPI submenus for NFIT, NUMA, APEI, DPTF, ARM64, RISC-V, PMIC, and other architecture-specific support.

## Control Flow
Kconfig dependency and selection rules determine which source files in `drivers/acpi/Makefile` are built. `menuconfig ACPI` gates most symbols. Tristate driver symbols become modules when selected as `m`; bool helper symbols are compiled into the ACPI core or architecture-specific paths. Defaults enable common x86 ACPI support, processor, battery, AC adapter, fans, and thermal support where dependencies are met.

## State And Persistence
The file contributes persistent build configuration through `.config`. Those choices alter kernel ABI visibility such as sysfs/debugfs/configfs nodes, module availability, power management support, and architecture-specific ACPI behavior.

## Dependencies And Integration Points
It integrates with architecture capability symbols (`ARCH_SUPPORTS_ACPI`, `ACPI_SYSTEM_POWER_STATES_SUPPORT`, `ARCH_HAS_ACPI_TABLE_UPGRADE`), subsystem dependencies such as `POWER_SUPPLY`, `INPUT`, `THERMAL`, `PCC`, `MAILBOX`, `CONFIGFS_FS`, `DEBUG_FS`, `IPMI_HANDLER`, `EDAC`, and kernel documentation referenced in help text.

## Risks
Incorrect dependencies can create build failures or expose drivers without required core subsystems. Defaults matter because ACPI controls power, hotplug, and firmware interfaces; overly broad defaults can expose risky debug/configfs functionality, while missing `select` statements can remove required support. Help text must stay aligned with actual module names and behavior.

## Test Signals
Validation comes from Kconfig dependency checks across x86, ARM64, LoongArch, and RISC-V configurations, allmodconfig/allyesconfig builds, module name checks, and targeted builds toggling debugger, configfs, IPMI, FPDT, LPIT, PCC, FFH, MRRM, and processor options.
