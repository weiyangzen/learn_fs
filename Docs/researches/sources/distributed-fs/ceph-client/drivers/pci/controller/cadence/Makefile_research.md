# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Makefile

Purpose: builds Cadence PCIe shared, host, endpoint, platform, and vendor-specific controller objects.

Important build rules: `pcie-cadence-mod-y` combines HPA and common Cadence core objects; `pcie-cadence-host-mod-y` combines host common, host, and host-HPA objects; `pcie-cadence-ep-mod-y` builds endpoint support. `obj-$(CONFIG_PCIE_CADENCE)` links the shared module, host/EP symbols add their modules, platform support adds `pcie-cadence-plat.o`, and vendor symbols add `pci-j721e.o`, `pcie-sg2042.o`, and `pci-sky1.o`.

Control flow/state: no runtime behavior, but module composition controls symbol availability for wrapper drivers. Core, host, and endpoint are separated so vendor/platform drivers can select only the required mode.

Dependencies/integration: consumes Cadence Kconfig symbols and ties shared infrastructure to concrete SoC wrappers. Risks include missing objects from composite modules, assignment versus append semantics for `obj-$(CONFIG_PCIE_CADENCE) =`, and host/EP wrappers selecting an incomplete common set. Test signals are incremental builds for each symbol, module link checks, and boot/probe tests for platform, J721E, SG2042, and SKY1 configurations.
