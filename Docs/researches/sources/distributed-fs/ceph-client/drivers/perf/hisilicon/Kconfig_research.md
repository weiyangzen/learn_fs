# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Kconfig

Purpose: Defines build-time configuration entries for HiSilicon SoC and PCIe PMU drivers and the HNS3 PMU driver.

Important APIs/types/functions: The file has three tristate symbols: `HISI_PMU` for ACPI ARM64 uncore L3C/HHA/DDRC and related SoC PMUs, `HISI_PCIE_PMU` for HiSilicon PCIe RCiEP PMUs, and `HNS3_PMU` for HNS3 PCI PMUs.

Control flow: Kconfig symbols control which objects the sibling Makefile builds. `HISI_PMU` depends on `ARM64 && ACPI`; `HISI_PCIE_PMU` depends on `PCI && ARM64`; `HNS3_PMU` depends on PCI and either ARM64 or compile testing.

State and persistence: No runtime state; selections persist through kernel configuration.

Dependencies and integration: Integrates with the kernel Kconfig system and `drivers/perf/hisilicon/Makefile`.

Risks and test signals: Dependency mistakes can hide drivers on supported systems or allow unsupported builds. Test with `make olddefconfig`, `allyesconfig`, `COMPILE_TEST`, ARM64 ACPI builds, and checking expected object inclusion.
