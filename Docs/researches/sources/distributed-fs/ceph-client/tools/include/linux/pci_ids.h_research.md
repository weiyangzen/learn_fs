<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pci_ids.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/pci_ids.h

## Purpose
`pci_ids.h` is a registry of PCI vendor, device, subvendor, class, and related numeric identifiers shared with tools.

## APIs And Flow
The file is macro data only. It defines thousands of `PCI_VENDOR_ID_*`, `PCI_DEVICE_ID_*`, `PCI_SUBVENDOR_ID_*`, and `PCI_SUBDEVICE_ID_*` constants covering common vendors and devices, including storage, audio, network, bridge, GPU, and platform devices. There is no executable control flow.

## State, Dependencies, Risks, Tests
State is compile-time numeric identity mapping that becomes persistent wherever tools encode device tables. There are no includes. Integration points include PCI decoders, perf tooling, tracing, and imported drivers or hardware tables. Risks are stale IDs relative to the kernel copy, duplicate or reused names, and consumers assuming the list is complete. Tests should compare the tools copy to the kernel header, compile table users, and spot-check recently added IDs and duplicate values with intentional aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pci_ids.h -->
