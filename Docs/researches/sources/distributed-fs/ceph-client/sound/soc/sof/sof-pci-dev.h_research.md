# sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.h

Purpose: declares the shared PCI helper interface for SOF PCI platform drivers.

Important APIs/types: exports `sof_pci_pm`, `sof_pci_probe()`, `sof_pci_remove()`, and `sof_pci_shutdown()`. Platform-specific PCI drivers can set these in their `pci_driver` table instead of duplicating common SOF setup.

Control flow/state: no local state. Probe behavior depends on each PCI ID's `driver_data` pointing to a valid `sof_dev_desc`.

Dependencies/integration: requires PCI device and ID types from including code and the common SOF PCI helper implementation. The PM ops are namespace-exported by the C file.

Risks/test signals: build tests should include multiple SOF PCI platform modules to verify namespace imports and PM symbol visibility. Runtime tests should confirm platform PCI IDs carry correct descriptors.
