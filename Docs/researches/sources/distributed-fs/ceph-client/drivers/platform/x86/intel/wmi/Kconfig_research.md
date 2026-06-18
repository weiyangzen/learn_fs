<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Kconfig

Purpose: defines the Intel WMI platform-driver configuration menu entries used by this directory. It introduces a hidden `INTEL_WMI` boolean selected by concrete WMI drivers, plus tristate options for Slim Bootloader firmware-update signaling and Thunderbolt force-power control.

Important symbols: `INTEL_WMI_SBL_FW_UPDATE` depends on `ACPI_WMI`, selects `INTEL_WMI`, and builds the `intel-wmi-sbl-fw-update` module. `INTEL_WMI_THUNDERBOLT` also depends on `ACPI_WMI`, selects `INTEL_WMI`, and builds `intel-wmi-thunderbolt`.

Control flow/build behavior: this file has no runtime control flow. Kconfig determines whether the corresponding WMI drivers are built in, as modules, or omitted, and ensures the ACPI WMI bus is available before enabling them.

State/persistence: no runtime state. Build selection affects module availability and therefore whether matching WMI GUID devices get sysfs attributes.

Dependencies/integration: integrates with the parent platform/x86 Kconfig tree and the WMI bus. The hidden `INTEL_WMI` symbol can serve as a common grouping symbol for Intel WMI extras.

Risks: both drivers expose platform firmware operations; enabling them makes sysfs controls appear on systems with matching GUIDs. Dependency is intentionally only `ACPI_WMI`, so platform specificity is enforced by WMI GUID matching at runtime.

Test signals: Kconfig resolution should allow `m/y/n` choices for both concrete drivers only when `ACPI_WMI` is available; selected modules should match Makefile targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Kconfig -->
