## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Makefile

Purpose: Object list for Mobiveil PCIe controller support.

Important APIs, types, and functions: `obj-$(CONFIG_PCIE_MOBIVEIL)` builds `pcie-mobiveil.o`; `obj-$(CONFIG_PCIE_MOBIVEIL_HOST)` builds `pcie-mobiveil-host.o`; `obj-$(CONFIG_PCIE_MOBIVEIL_PLAT)` builds `pcie-mobiveil-plat.o`; `obj-$(CONFIG_PCIE_LAYERSCAPE_GEN4)` builds `pcie-layerscape-gen4.o`.

Control flow: no runtime flow. Kbuild includes objects according to Kconfig symbols.

State and persistence: no runtime state. The file persists the mapping between config symbols and compilation units.

Dependencies and integration points: Kbuild and the Kconfig symbols in the same directory. The layering mirrors the code architecture: common CSR/window helpers, host-mode shared code, and platform-specific front ends.

Risks: If a platform driver selects `PCIE_MOBIVEIL_HOST` but not the common symbol, build would fail; Kconfig currently selects correctly. Adding endpoint support would need new object mappings and symbols.

Test signals: build logs should include the common and host objects when either platform option is enabled; disabling both platform options should not build platform drivers.
