<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Makefile

Purpose: maps Intel WMI Kconfig symbols to build targets in this directory.

Important targets: `intel-wmi-sbl-fw-update-y := sbl-fw-update.o` and `obj-$(CONFIG_INTEL_WMI_SBL_FW_UPDATE) += intel-wmi-sbl-fw-update.o`; `intel-wmi-thunderbolt-y := thunderbolt.o` and `obj-$(CONFIG_INTEL_WMI_THUNDERBOLT) += intel-wmi-thunderbolt.o`.

Control flow/build behavior: kernel kbuild composes each module from its single object file when the corresponding config is `m` or links it built-in when `y`.

State/persistence: no runtime state. The target names define module names visible to userspace and modprobe.

Dependencies/integration: must remain in sync with `Kconfig` symbols and source filenames. The selected module names match help text in Kconfig and `wmi_driver.driver.name` values in the C sources.

Risks: typo in target variable naming or config symbol would silently omit a driver or produce unexpected module names. Current file is minimal and direct.

Test signals: `make M=drivers/platform/x86/intel/wmi` with each config enabled should build the expected `.ko` or built-in object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Makefile -->
