# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs.h

- Purpose: Declares attribute arrays for PCI card, input, and output sysfs groups selected by module type.
- Important APIs/types/functions: `mgb4_pci_attrs`, `mgb4_fpdl3_in_attrs`, `mgb4_gmsl3_in_attrs`, `mgb4_gmsl1_in_attrs`, `mgb4_fpdl3_out_attrs`, `mgb4_gmsl3_out_attrs`, `mgb4_gmsl1_out_attrs`.
- Control flow: Core and vin/vout create device groups using generated `ATTRIBUTE_GROUPS` around these arrays.
- State and persistence: No state; attribute handlers live in sysfs implementation files.
- Dependencies and integration points: Connects core/vin/vout registration with sysfs files.
- Risks: Missing NULL-terminated arrays or wrong module selection would expose wrong knobs.
- Test signals: Probe and sysfs enumeration tests for each module type.
