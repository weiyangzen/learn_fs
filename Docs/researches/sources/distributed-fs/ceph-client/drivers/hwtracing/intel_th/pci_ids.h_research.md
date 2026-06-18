
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci_ids.h

Purpose: local Intel NPK/Trace Hub PCI device ID definitions used by `pci.c`.

Important APIs/types/functions: defines `PCI_DEVICE_ID_INTEL_NPK_*` constants for multiple Intel generations and PCH/CPU variants, from older Broxton/Apollo/Kaby families through newer Meteor/Nova/Panther Lake IDs.

Control flow: no runtime logic. The constants feed `PCI_DEVICE_DATA(INTEL, NPK_..., drvdata)` entries in the PCI ID table.

State and persistence: none.

Dependencies and integration: included only by the Intel TH PCI driver. Names must match the `PCI_DEVICE_DATA` macro's expected `PCI_DEVICE_ID_INTEL_*` expansion.

Risks: stale or incorrect IDs prevent driver binding or apply wrong quirks. The file comment says Intel TH debugging despite containing PCI IDs, which can mislead maintainers.

Test signals: build the PCI ID table, verify module aliases with `modinfo`, and confirm probe on hardware for newly added IDs.
